from opscli.command import match
from opscli.command import token

L = token.LiteralType

groups = [
       ]

tree = match.Tree()
tree.add(match.MatchGroup(
    [L('show'), L('bgp'), L('neighbor')],
    [L('advertised-routes')],
    'bgp-value'))
tree.add(match.MatchGroup(
    [L('show'), L('ospf'), L('neighbor')],
    [L('advertised-routes')],
    'ospf-value'))
tree.add(match.MatchGroup([L('show'), L('aaa')], [], 'aaa-value'))


def dump(tree):
    for word, branch in tree.iteritems():
        if not branch:
            yield [str(word)]
        else:
            for subwords in dump(branch):
                yield [str(word)] + subwords

# Validate preserved order
expected = [
        ['show', 'bgp', 'neighbor', 'advertised-routes'],
        ['show', 'ospf', 'neighbor', 'advertised-routes'],
        ['show', 'aaa']]

print expected == list(dump(tree))

print len(list(tree.match(('show', 'aaa')))) == 1
print len(list(tree.match(('show', ), prefix=True))) == 3

#print grammar.match('test', 'foo') # == True
#print grammar.match('test', 'foo', 'bar') # == False

#print grammar.match('127.0.0.1')
#print grammar.match('127.0.0.1', 'advertised-routes')
#print grammar.match('127.0.0.1', 'paths', '[A-Z]+')
#print grammar.match('127.0.0.1', 'paths', '.*')
#print grammar.match('127.0.0.1', 'policy')
#print grammar.match('127.0.0.1', 'policy', 'detail')
#print grammar.match('127.0.0.1', 'received')                   # == False
#print grammar.match('127.0.0.1', 'received', 'prefix-filter')  # == True
