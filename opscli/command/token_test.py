import token

L = token.LiteralType

tokens = token.InOrder(
        [ token.IPv4Address | token.IPv6Address ] +
        [
            L('advertised-routes') |
            L('paths') + [ token.Regex ] |
            L('policy') + [ L('detail') ] |
            L('received') + L('prefix-filter') |
            L('routes')
        ])

print 'Token tree: ',
print repr(tokens)
print 'Token dump: ',
print str(tokens)


class Any(token.Token):
    def match(self, word):
        return True

class StartsWithF(token.Token):
    def match(self, word):
        return word[0] == 'f'


words = ('test', 'foo', bar)
