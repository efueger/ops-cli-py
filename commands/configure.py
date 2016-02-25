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
from opscli.command import context
from opscli.command import token

from tokens import common

L = token.LiteralType


class ConfigureContext(context.Context):
    prompt = '(config)'


class Configure(command.Utility):
    """Configuration from CLI"""

    options = token.construct( [ L('terminal') ] )

    def command(self, *unused_args):
        return self.context.configure()


def register(root, unused_everywhere):
    root.configure = ConfigureContext
    root.configure = Configure
