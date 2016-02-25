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

#print str(grammar) # == Any StartsWithF
#print list(grammar) # == [[Any, StratsWithF]]

grammar = token.construct(Any() + StartsWithF() + [ Any() + [ StartsWithF() ] ])

print str(grammar) # == Any StartsWithF [ Any [ StartsWithF ] ]
print list(grammar) # == [[Any, StartsWithF], [Any, StartsWithF, Any], [Any, StartsWithF, Any, StartsWithF ]]
