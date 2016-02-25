from opscli.command.token import Token


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
