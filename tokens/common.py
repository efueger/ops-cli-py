
import re

from opscli.command.token import Token


class IPv4Type(Token):
    """Matches any IPv4 address."""

    def match(self, word):
        return True

    def transform(self, word):
        # TODO(bluecmd): Use some kind of IP library here
        return word


class IPv6Type(Token):
    """Matches any IPv6 address."""

    def match(self, word):
        return True

    def transform(self, word):
        # TODO(bluecmd): Use some kind of IP library here
        return word


class RegexType(Token):
    """Matches any valid Regexp syntax."""

    def match(self, word):
        return True


    def transform(self, word):
        return re.compile(word)


# Quick access to common used types
IPv4Address = IPv4Type()
IPv6Address = IPv6Type()
Regex = RegexType()
