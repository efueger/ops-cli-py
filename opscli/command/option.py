
class Condition(object):
    def __init__(self, *operands):
        # List operand = optional
        self.operands = operands

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                ', '.join(repr(x) for x in self.operands) + ')')

class Or(Condition):

    def __or__(self, other):
        assert isinstance(other, Token) or isinstance(other, Condition)
        return Or(*(list(self.operands) + [other]))


class And(Condition):
    pass


class Token(object):
    def __or__(self, other):
        assert isinstance(other, Token)
        return Or(self, other)

    def __add__(self, other):
        assert isinstance(other, Token) or isinstance(other, list)
        return And(self, other)

class LiteralType(Token):
    def __init__(self, string):
        self.string = string

class IPv4Type(Token):
    pass

class IPv6Type(Token):
    pass

class RegexType(Token):
    pass

IPv4 = IPv4Type()
IPv6 = IPv6Type()
Regex = RegexType()
