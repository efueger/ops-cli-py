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

    def match(self, words, prefix=False):
        """Returns match groups that match the given words.

        @args prefix If true, only require that words is a subset.
        @yields MatchGroup
        """
        if not words:
            if self.group:
                yield self.group
            if prefix:
                # Grab all available commands on the subtrees
                for branch in self.itervalues():
                    for match in branch.match([], prefix=True):
                        yield match
            return

        word = words[0]
        for token, branch in self.iteritems():
            if token != word:
                continue
            for match in branch.match(words[1:], prefix):
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
