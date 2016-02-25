"""
TODO(bluecmd): Describe how the magic |, + and [] works.

"""
import abc


class Condition(object):
    def __init__(self, *operands):
        # Convert lists to Optional elements
        # This is a bit special because [ X ] + [ Y ] will be passed as
        # [ X Y ] to us because how Python handles lists. So we need to iterate
        # over lists and push them on operands
        self.operands = []
        for operand in operands:
            if isinstance(operand, list):
                for optional_operand in operand:
                    self.operands.append(Optional(optional_operand))
            else:
                self.operands.append(operand)

    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                ', '.join(repr(x) for x in self.operands) + ')')

    def __or__(self, other):
        assert isinstance(other, Token) or isinstance(other, Condition)
        return OneOf(self, other)


class OneOf(Condition):
    """Logical OR'd token/conditions defined by A | B."""

    def __or__(self, other):
        assert isinstance(other, Token) or isinstance(other, Condition)
        # Simplify the expression a bit by unrolling OneOf
        return OneOf(*(list(self.operands) + [other]))

    def __str__(self):
        return ' | '.join(str(x) for x in self.operands)


class Optional(Condition):
    """Optional token/condition defined by [ X ]."""

    def __init__(self, operand):
        super(Optional, self).__init__(operand)

    def __str__(self):
        return '[ ' + str(self.operands[0]) + ' ]'


# This is logical AND
class InOrder(Condition):
    """Logical AND'd token/conditions defined by A + B."""

    def __str__(self):
        return ' '.join(str(x) for x in self.operands)


class Token(object):
    """Abstract token base class."""

    __metaclass__ = abc.ABCMeta

    def __str__(self):
        return self.__class__.__name__

    def __or__(self, other):
        assert isinstance(other, Token) or isinstance(other, Condition)
        if isinstance(other, Token):
            return OneOf(self, other)
        return OneOf(self, *other.operands)

    def __add__(self, other):
        assert isinstance(other, Token) or isinstance(other, Condition) or isinstance(other, list)
        return InOrder(self, other)

    @abc.abstractmethod
    def match(self, word):
        pass


def construct(operand):
    # To make it simpler for the programmer to think correctly, we have this
    # simple constructor function.
    # It avoids nesting to InOrder() in eachother, really - that's about it.
    if isinstance(operand, Condition):
        return operand
    else:
        return InOrder(operand)


# TODO(bluecmd): Move these to a plugin driven directory
class LiteralType(Token):
    """Matches a given literal string."""

    def __init__(self, string):
        self.string = string

    def __str__(self):
        return self.string

    def match(self, word):
        return word == self.string


class IPv4Type(Token):
    """Matches any IPv4 address."""

    def match(self, word):
        return True


class IPv6Type(Token):
    """Matches any IPv6 address."""

    def match(self, word):
        return True


class RegexType(Token):
    """Matches any valid Regexp syntax."""

    def match(self, word):
        return True


class StringRegexType(Token):
    """Matches strings that match against given rexep."""

    def match(self, word):
        return True


# Quick access to common used types
IPv4Address = IPv4Type()
IPv6Address = IPv6Type()
Regex = RegexType()
