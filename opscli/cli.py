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
from opscli.command import context


class OpsContext(context.Context):
    def new(self, ovsdb):
        self.ovsdb = ovsdb


class Opscli(object):
    '''
    This class extends pyrepl's Reader to provide command modules.
    '''
    def __init__(self, ovsdb, module_paths=None, motd='OpenSwitch shell'):
        # Initialize the OVSDB helper.
        self.motd = 'OpenSwitch shell'
        prompt_base = 'Openswitch'

        # TODO shell hangs before prompt if this is down
        try:
            results = ovsdb.get_map('System', column='mgmt_intf_status')
            if 'hostname' in results:
                prompt_base = results['hostname']
        except:
            logging.exception('Failed to get hostname from OVSDB')

        # Initialize command tree.
        for path in module_paths:
            if not os.path.isdir(path):
                logging.warn('Ignoring invalid module path "%s".', path)
                continue
            self.load_commands(path)

        self.root = context.ContextTree(OvsdbContext)
        self.console = console.PyreplConsole(prompt_base, self.root)

    def load_commands(self, path):
        sys.path.insert(0, path)
        for filename in os.listdir(path):
            if filename[-3:] != '.py':
                continue
            # Strip '.py'.
            __import__(filename[:-3])

    def start(self):
        cli_out(self.motd)
        for line in self.console.loop():
            if not self.process_line(line):
                # Received quit, ctrl-d etc.
                break
            # TODO catch all exceptions, log traceback, print error msg

    def process_line(self, line):
        words = line.split()
        dbg(words)
        if words:
            return self.run_command(words)
        return True

    def run_command(self, words):
        if words[0] == 'help':
            self.console.show_help(words[1:])
            return True

        flags = []
        # Negated commands are in the tree without the leading 'no'.
        if words[0] == 'no':
            words.pop(0)
            flags.append(F_NO)

        matches = self.context.find_command(words)
        if len(matches) == 0 or len(matches) > 1:
            # Either nothing matched, or more than one command matched.
            raise Exception(CLI_ERR_NOCOMMAND)
        cmdobj = matches.pop()

        if not hasattr(cmdobj, 'run'):
            # Dummy command node, such as 'show'.
            raise Exception(CLI_ERR_INCOMPLETE)

        tokens = []
        if len(cmdobj.command) != len(words):
            # Some of the words aren't part of the command. The rest must
            # be options.
            opt_words = words[len(cmdobj.command):]
            tokens = tokenize_options(opt_words, cmdobj.options)

        check_required_options(tokens, cmdobj.options)

        for flag in flags:
            if flag not in cmdobj.flags:
                # Something was flagged, but the command doesn't allow it.
                raise Exception(CLI_ERR_NOCOMMAND)

        # Run command.
        cmdobj.context = self.context
        ret = cmdobj.run(tokens, flags)
        if isinstance(ret, context.Context):
            # Command switched context
            self.context = ret
            self.console.set_context(self.context)

        # Most commands just return None, which is fine.
        return ret is not False


