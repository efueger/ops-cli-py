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

from opscli.command import command
from opscli import cli


class Quit(command.Utility):
    """Quit shell"""

    def command(self):
        return cli.ExitMarker


class Exit(command.Utility):
    """Exit current mode and down to previous mode"""

    def command(self):
        return cli.ExitContextMarker


class Pwc(command.Utility):
    """Show current configuration context"""

    def command(self):
        return str(self.context)


def register(unused_root, everywhere):
    everywhere.exit = Exit
    everywhere.pwc = Pwc
    everywhere.quit = Quit
