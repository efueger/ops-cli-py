from opscli.command import token
import common


L = common.LiteralType

grammar = token.construct(
        [ common.IPv4Address | common.IPv6Address ] +
        [
            L('advertised-routes') |
            L('paths') + [ common.Regex ] |
            L('policy') + [ L('detail') ] |
            L('received') + L('prefix-filter') |
            L('routes')
        ])

print str(grammar) # ==  IPv4Type | IPv6Type ] [ advertised-routes | paths | [ RegexType ] | policy [ detail ] | received prefix-filter | routes ]
print len(list(grammar)) # == 27
#for combination in grammar:
#    print [str(x) for x in combination]
