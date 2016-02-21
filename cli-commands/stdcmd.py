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

from opscli import command
from opscli import output


class Quit(command.Command):
    '''Quit shell'''
    command = 'quit'

    def run(self, opts, flags):
        return False


class Exit(command.Command):
    '''Exit current mode and down to previous mode'''
    command = 'exit'

    def run(self, opts, flags):
        return self.context.leave()


class Pwc(command.Command):
    '''Show current configuration context'''
    command = 'pwc'

    def run(self, opts, flags):
        indent = 0
        for context in reversed(list(self.context.chain())):
            if context.parent is None:
                continue
            output.cli_wrt(' ' * indent * 2)
            output.cli_wrt(context.name)
            if context.obj is not None:
                output.cli_wrt(' ' + str(context.obj))
            output.cli_out()
            indent += 1


command.register_commands((Exit,), 'global')
command.register_commands((Pwc,), 'global')
command.register_commands((Quit,))
