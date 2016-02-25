"""
Match trees are mainly used to provide syntax completion.

A match tree is a nested ordered dictionary forming a tree
data structure where each branch key is a string-like object.
In opscli, these string-like objects are always token.Token
objects.

Example:
Given the following commands:
  show bgp neighbor
  show ospf peers
  show aaa

The tree would internally look like:
Tree -- show --- bgp -- neighbors - {MG}*
              |- ospf - peers - {MG}*
              \- aaa - {MG}*
              
Notice that the order is preserved from when the
tokens were inserted.

* MG stands for Match group

# Match group
A match group is a data structure associated with every leaf
in the tree. It contains information used to derive what parts
of the resulting match are command tokens, and what are option
tokens.

It has 3 fields:
- primary   (in opscli; 'command')
- secondary (in opscli; 'option')
- value     (in opscli; carries the bound command)

# Matching

Standard matching is that all tokens must match. If prefix
matching is enabled we only require matching up until the words
run out.

# Usage
Using LiteralToken from token.py, it's easy to do command
completition.

L = token.LiteralType
mg = MatchGroup((L('hello'), L('world')), (,), 'awesome')

t = Tree()
t.add(mg)
t.match(('hel', 'wo')) => [mg]
t.match(('hel',)) => []
t.match(('hel',), prefix=True) => [mg]
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
