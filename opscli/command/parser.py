import pyparsing as p

Segment = (
        p.QuotedString('\'', escChar='\\') |
        p.QuotedString('"', escChar='\\') |
        p.CharsNotIn(' '))


class ParseResult(object):

    grammar = p.ZeroOrMore(Segment + p.Suppress(p.White())) + Segment

    def __init__(self, string):
        self.result = self._tryParse(string)
        self.success = self.result is not None

    def _tryParse(self, string):
        try:
            return self.grammar.parseString(string)
        except p.ParseException as e:
            self.error = e


def parse(string):
    """Parse a given unicode string."""
    return ParseResult(string)


# This enables caching of match logic inside of p
p.ParserElement.enablePackrat()
