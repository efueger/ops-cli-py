import collections
import pyparsing as p

Segment = (
        p.QuotedString('\'', escChar='\\') |
        p.QuotedString('"', escChar='\\') |
        p.CharsNotIn(' |'))

# CommandEnd forbids trailing space
CommandEnd = p.ZeroOrMore(Segment + p.Suppress(p.White())) + Segment

# CommandPiped requires '|' at end, but ' |' is also fine
CommandPiped = p.OneOrMore(Segment + p.Suppress(p.ZeroOrMore(p.White()))) + p.Suppress(p.Literal('|'))

# A command consists of 'Command' or 'Command | Command'
Grammar = p.LineStart() + p.ZeroOrMore(p.Group(CommandPiped)) + p.Group(CommandEnd) + p.LineEnd()

ParseResult = collections.namedtuple(
    'ParseResult', ('success', 'error', 'commands'))


def parse(string):
    """Parse a given unicode string."""
    error = None
    commands = []
    try:
        commands = Grammar.parseString(string)
    except p.ParseException as e:
        error = e
    success = error is None
    return ParseResult(success, error, commands)


# This enables caching of match logic inside of p
p.ParserElement.enablePackrat()
