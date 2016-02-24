import token


class Any(token.Token):
    def match(self, word):
        print word
        return True

class StartsWithF(token.Token):
    def match(self, word):
        print word
        return word[0] == 'f'

grammar = token.construct(Any() + StartsWithF())

print str(grammar) # == Any StartsWithF


L = token.LiteralType

grammar = token.construct(
        [ token.IPv4Address | token.IPv6Address ] +
        [
            L('advertised-routes') |
            L('paths') + [ token.Regex ] |
            L('policy') + [ L('detail') ] |
            L('received') + L('prefix-filter') |
            L('routes')
        ])

print str(grammar) # ==  IPv4Type | IPv6Type ] [ advertised-routes | paths | [ RegexType ] | policy [ detail ] | received prefix-filter | routes ]
