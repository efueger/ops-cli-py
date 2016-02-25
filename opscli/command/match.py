"""
TODO(bluecmd): Describe how match / partial match works.
"""

import collections


MatchGroup = collections.namedtuple(
    'MatchGroup', ('primary', 'secondary', 'value'))

MatchResult = collections.namedtuple(
    'MatchResult', ('modifiers', 'primary', 'secondary', 'value'))


def match(command, groups):
    # TODO(bluecmd): just placeholder dummy logic for now
    modifiers = {'is_negated': False}
    if command[0] == 'no':
        modifiers['is_negated'] = True
        command = command[1:]
    # TODO, look at first character for now
    options = command[1:]
    for mg in groups:
        if mg.primary[0][0] == command[0][0]:
            yield MatchResult(modifiers, command, options, mg.value)
