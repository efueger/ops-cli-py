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

from opscli.command import get_cmdtree
from opscli import output
from opscli import stringhelp


class Context(object):

    def __init__(self, name, parent=None, obj=None, prompt=None):
        self.name = name
        self.cmdtree = get_cmdtree(name)
        self.obj = obj
        self.prompt = prompt
        self.parent = parent

    def chain(self):
        context = self
        while context:
            yield context
            context = context.parent

    def leave(self):
        if self.parent is None:
            return self
        return self.parent

    def enter(self, name, obj=None, prompt=None):
        return Context(name, self, obj, prompt)

    def make_prompt(self):
        if self.prompt is not None:
            context_string = "(%s)" % self.prompt
        else:
            context_string = ''
            for ctx in reversed(list(self.chain())[:-1]):
                context_string += "(%s)" % ctx.name
        return context_string + output.PROMPT_CHAR

    # Traverse tree starting at cmdobj to find a command for which all words
    # are at least a partial match. Returns list of Command objects that match.
    def find_partial_command(self, cmdobj, words, matches):
        if len(cmdobj.branch) == 0:
            # This branch is a complete match for all words.
            matches.append(cmdobj)
            return matches
        for key in cmdobj.branch:
            if key.startswith(words[0]):
                # Word is a partial match for this command.
                if len(words) == 1:
                    # Found a match on all words.
                    last = cmdobj.branch[key]
                    matches.append(last)
                else:
                    # Continue matching on this branch with the next word.
                    return self.find_partial_command(cmdobj.branch[key],
                                                     words[1:], matches)
        return matches

    def find_command(self, words):
        for context in self.chain():
            matches = self.find_partial_command(
                    context.cmdtree, words, [])
            if matches:
                if context != self:
                    print 'TODO: Found match in higher context'
                return matches

        # Try the 'global' command tree as a last resort.
        global_tree = get_cmdtree('global')
        return self.find_partial_command(global_tree, words, [])

    def helpline(self, cmdobj, prefix=None):
        if prefix:
            words = cmdobj.command[len(prefix):]
        else:
            words = cmdobj.command
        return stringhelp.Str_help((' '.join(words), cmdobj.__doc__))

    def get_help_subtree(self):
        global_tree = get_cmdtree('global')
        items = (
            [self.helpline(x) for x in self.cmdtree.branch.itervalues()] +
            [self.helpline(x) for x in global_tree.branch.itervalues()])
        return items
