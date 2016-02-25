"""
TODO(bluecmd): Describe how match / partial match works.
"""

import collections


MatchGroup = collections.namedtuple(
    'MatchGroup', ('primary', 'secondary', 'value'))


class SubTree(collections.OrderedDict):

    def __init__(self):
        super(SubTree, self).__init__(self)
        self.group = None

    def match(self, words):
        if not words:
            if self.group:
                yield self.group
            return

        word = words[0]
        for token, branch in self.iteritems():
            if token != word:
                continue
            for match in branch.match(words[1:]):
                yield match


class Tree(SubTree):

    def __init__(self):
        super(Tree, self).__init__()

    def add(self, group):
        combined = list(group.primary + group.secondary)
        tree = self
        for token in combined:
            tree = tree.setdefault(token, SubTree())
        # Should be no duplicates
        assert tree.group is None
        tree.group = group
