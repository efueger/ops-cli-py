import option

# Sest command
# show bgp all neighbors
#  [ip-address | ipv6-address]
#  [advertised-routes | dampened-routes | flap-statistics | paths [reg-exp] |
#   policy [detail] | received prefix-filter | received-routes | routes]


L = option.LiteralType

print option.IPv4 | option.IPv6
options = (
        [option.IPv4 | option.IPv6] +
        [
            L('advertised-routes') |
            L('dampened-routes') |
            L('flap-statistics') |
            L('paths') + [option.Regex] |
            L('policy') + [L('detail')] |
            L('received') + L('prefix-filter') |
            L('received-routes') |
            L('routes')
        ])

print options
