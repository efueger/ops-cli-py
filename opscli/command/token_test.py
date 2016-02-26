from opscli.command import token


class Any(token.Token):
    def match(self, word):
        return True
    def transform(self, word):
        return word


class StartsWithF(token.Token):
    def match(self, word):
        return word[0] == 'f'
    def transform(self, word):
        return 'foobar'


grammar = token.construct(Any() + StartsWithF())

print str(grammar) # == Any StartsWithF
print list(grammar) # == [[Any, StratsWithF]]

grammar = token.construct(Any() + StartsWithF() + [ Any() + [ StartsWithF() ] ])

print str(grammar) # == Any StartsWithF [ Any [ StartsWithF ] ]
print list(grammar) # == [[Any, StartsWithF], [Any, StartsWithF, Any], [Any, StartsWithF, Any, StartsWithF ]]
