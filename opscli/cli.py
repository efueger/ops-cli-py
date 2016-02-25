#
# Copyright (C) 2016 Bert Vermeulen <bert@biot.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys
import os
import logging

from opscli import console
from opscli import linehelper
from opscli.command import context


# Define some globally knwon sentinels
# These are returned by the commands to let the shell react appropriately.

# Causes the program to exit
ExitMarker = object()

# Used to travel backwards to the previous context
ExitContextMarker = object()


class OpsContext(context.Context):
    # TODO(bluecmd): Remove
    prompt = '(root) >'
    def new(self, ovsdb):
        self.ovsdb = ovsdb


class Opscli(object):
    '''
    This class extends pyrepl's Reader to provide command modules.
    '''
    def __init__(self, ovsdb, module_paths=None, motd='OpenSwitch shell'):
        # Initialize the OVSDB helper.
        prompt_base = 'Openswitch'

        # TODO shell hangs before prompt if this is down
        try:
            results = ovsdb.get_map('System', column='mgmt_intf_status')
            if 'hostname' in results:
                prompt_base = results['hostname']
        except:
            logging.exception('Failed to get hostname from OVSDB')

        # Initialize command tree.
        self.root = context.ContextTree(OpsContext)
        self.global_root = context.ContextTree(OpsContext)

        for path in module_paths:
            if not os.path.isdir(path):
                logging.warn('Ignoring invalid module path "%s".', path)
                continue
            self.load_commands(path)

        self.context = self.root(ovsdb)
        self.global_context = self.global_root(ovsdb)
        self.context_stack = []

        # This is the object that advises the console of what commands are
        # possible.
        self.linehelper = linehelper.ContextLineHelper(
                self.context, self.global_context)

        self.console = console.PyreplConsole(prompt_base, motd, self.linehelper)

    def load_commands(self, path):
        sys.path.insert(0, path)
        for filename in os.listdir(path):
            if not filename.endswith('.py') or filename.endswith('_test.py'):
                continue
            module = __import__(filename[:-3])
            if hasattr(module, 'register'):
                module.register(self.root, self.global_root)

    def start(self):
        for line in self.console.loop():
            ret = self.process_line(line)
            if ret is None:
                continue
            elif ret == ExitMarker:
                break
            self.console.output(ret)
            # TODO catch all exceptions, log traceback, print error msg

    def process_line(self, line):
        # TODO(bluecmd): When we implement pipe support this needs to change
        command, options = next(self.linehelper.resolve_commands(line))
        try:
            ret = command(*options)
        except TypeError as e:
            logging.exception(
                    'Tried calling %s but got "%s"', command, str(e))
            # TODO(bluecmd): Raise exception?
            return

        # Step 5) Handle result
        # Does the command want us to go up the context stack?
        if ret.value == ExitContextMarker:
            if self.context_stack:
                self.context = self.context_stack.pop()
                self.linehelper.set_context(self.context)
            return
        # Did we switch context to a new one?
        elif self.context != ret.context:
            self.context_stack.append(self.context)
            logging.info('Switching context to %s', context)
            self.context = ret.context
            self.linehelper.set_context(self.context)
        return ret.value
