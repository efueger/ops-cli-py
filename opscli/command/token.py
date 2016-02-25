"""
Tokens are optimistically and lazy matched word types that have two
purposes: filter non-matching objects and transform matching ones.

Optimistic and lazy means that the string "he" matches the literal
token "hello". When transformed through the token "he" becomes "hello".

Examples of tokens are: words, numbers, ip-addresses.

Token transformation is a concept of taking the string representation
and constructing a more suitable data structure from it.

A simple example is a number token. It would be defined as:
class NumberType(token.Token):
  def match(self, word):
    return is_numeric(word)
  def transform(self, word):
    return int(word)
    
# Transforming tokens

Transforming is easiest done by treating a token instance as a functor:
number = NumberType()
number('10') => 10

# Conditions: Combining tokens
Combining two tokens creates a Condition.

The operators suppoerted are: | (OR),  + (PLUS) and [] (BRACKETS).
A OR B (A | B) is used to specifiy that the condition should
pass for both A tokens and B tokens.

Example: LiteralType("foo") | LiteralType("bar")
This would match everything "foo" and "bar".

A AND B (A + B) is used to specify that the A and B must
follow eachother.

Example: LiteralType("foo") + LiteralType("bar")
This will only match if "foo" is followed by "bar".

A BRACKET ( [ A ] ) means optional argument.

Example: LiteralType("foo") + [ LiteralType("bar") ]
This will match "foo" and also "foo", "bar".

# Using combinations
Combinations are used through iterating over them.
The iteration process will generate every legal combination
of the tokens in way that it's easy to match an array of words
against.

Example:

combinations = list(LiteralType("foo") + [ LiteralType("bar") ])
combinations[0] => [LiteralType("foo")]
combinations[0] => [LiteralType("foo"), LiteralType("bar")]
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
    """Abstract token base class.

    Tokens are optimistically and lazy matched. If the given word *so far*
    matches the word, then that's a match.

    Final validation is done in the transform() function before returning the
    structured value.
    """

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

    def __call__(self, word):
        return self.transform(word)

    def __ne__(self, word):
        return not self.__eq__(word)

    def __eq__(self, word):
        return self.match(word)

    @abc.abstractmethod
    def match(self, word):
        pass

    @abc.abstractmethod
    def transform(self, word):
        """Parse the word to structured data."""
        pass


class LiteralType(Token):
    """Matches a given literal string."""

    def __init__(self, string):
        self.string = string

    def __str__(self):
        return self.string

    def transform(self, word):
        return self.string

    def match(self, word):
        return self.string.upper().startswith(word.upper())


def construct(operand):
    # To make it simpler for the programmer to think correctly, we have this
    # simple constructor function.
    # It avoids nesting to InOrder() in eachother, really - that's about it.
    if isinstance(operand, Condition):
        return operand
    else:
        return InOrder(operand)
