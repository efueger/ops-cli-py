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

    def __iter__(self):
        for operand in self.operands:
            for combination in operand:
                yield combination


class Optional(Condition):
    """Optional token/condition defined by [ X ]."""

    def __init__(self, operand):
        super(Optional, self).__init__(operand)

    def __str__(self):
        return '[ ' + str(self.operands[0]) + ' ]'

    def __iter__(self):
        yield []
        for combination in self.operands[0]:
            yield combination


# This is logical AND
class InOrder(Condition):
    """Logical AND'd token/conditions defined by A + B."""

    def __str__(self):
        return ' '.join(str(x) for x in self.operands)

    def __iter__(self):
        for combination in self._combinations():
            yield combination

    def __add__(self, other):
        return InOrder(*list(self.operands) + [other])

    def _combinations(self, level=0):
        if level == len(self.operands):
            yield []
            return

        primary = self.operands[level]
        for primary_combination in primary:
            for combination in self._combinations(level + 1):
                yield primary_combination + combination


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

    def __iter__(self):
        yield [self]

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
