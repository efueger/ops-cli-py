"""
Network-OS style command parsing.

This module takes a string of a command line and upon successful
parsing returns a list of commands, each split up by the different
command words.

Grammar:
  Words can be within quotes (' and "), at which point they
  are allowed to contain any reasonable character. Backslash (\)
  is the escape character.
  
  A command consists of at least one whitespace separated word(s).
  
  A command line consists of at least one command. If multiple
  commands they are to be seperated with '|'.

Example:
  exit
  show running-config
  show running-config | inc hostname
  motd "My Cool Switch!"
  
Usage:
  import parse
  result = parse.parse("show running-config")
  if result.success:
    print result.commands # Will print: [["show", "running-config"]]
  else:
    print result.error
"""
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
