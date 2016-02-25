import collections

from opscli.command import match
from opscli.command import parse
from opscli.command import token


# When modifiers such as 'no' have been parsed they are attached to the command
# using this structure
CommandStruct = collections.namedtuple(
        'CommandStruct', ('modifiers', 'command'))


class Error(Exception):
    """Base error class for this module."""
    pass


class CommandNotFoundError(Error):
    """The user tried to execute a command that doesn't exist."""
    pass


class CommandParsingError(Error):
    """The command line couldn't be parsed."""
    pass


class LineHelper(object):
    """Logic glue between CLI logic and Console implementation."""

    def qhelp(self, line):
        pass

    def complete(self, line):
        pass


class ContextLineHelper(LineHelper):

    def __init__(self, context, global_context):
        self.global_context = global_context
        self.set_context(context)

    def set_context(self, context):
        commands = list(context) + list(self.global_context)
        tree = match.Tree()
        for words, obj in commands:
            # TODO(bluecmd): Register legal modifiers for this command
            modifiers = {'is_negated': False}
            struct = CommandStruct(modifiers, obj)
            command_tokens = [token.LiteralType(x) for x in words]
            for option in obj.options:
                tree.add(match.MatchGroup(command_tokens, option, struct))
        self.tree = tree
        self.context = context

    @property
    def prompt(self):
        # TODO(bluecmd): Make nice prompt
        return str(self.context)

    def resolve_commands(self, line):
        # Step 1) Parse command
        parse_result = parse.parse(line)
        if not parse_result.success:
            raise CommandParsingError(parse_result.error)

        for command in parse_result.commands:
            # Step 2) Match and bind
            match_result = next(self.tree.match(command), None)
            if match_result is None:
                raise CommandNotFoundError(command)
            modifiers = match_result.value.modifiers
            bound_command = match_result.value.command.bind(**modifiers)
            # Remove options that the receiving function will not handle
            option_tokens = match_result.secondary[:bound_command.argc]

            # Step 3) Transform options
            # Remove primary (command) arguments
            option_words = command[len(match_result.primary):]
            options = [token(word) for word, token in zip(option_words, option_tokens)]

            yield bound_command, options

    def prefix_matched_candidates(self, line):
        """Calculates the prefix matched candidates.

        Examples for prefix candidate:
        If line = 'show bgp' and there is an 'show bgp neighbor' then
        'neighbor' is a prefix matched candidate.
        """
        if not line:
            # On empty line: show all commands in this context.
            return sorted(str(x) for x in self.tree), ''

        ends_with_white = line[-1].isspace()

        # We need to strip the input here because the command line is not yet
        # complete and may include trailing spaces that are not valid otherwise
        parse_result = parse.parse(line.strip())
        if not parse_result.success:
            raise CommandParsingError(parse_result.error)

        # Grab the last command, assume the user wants to know about that
        # TODO(bluecmd): We could try to figure out what command the user was
        # located at when typing '?' and give help about that option.
        command = parse_result.commands[-1]

        matches = list(self.tree.match(command, prefix=True))
        if not matches:
            raise CommandNotFoundError(' '.join(command))

        # Extract the part we care about
        candidates = []
        for match in matches:
            # Assemble the fully qualified command from the command and options
            # parts.
            qualified = match.primary + match.secondary

            # Remove the command we already have depending on where we are
            if ends_with_white:
                if len(qualified) == len(command):
                    # This means that the command is qualified as it is
                    candidate = ''
                else:
                    candidate = qualified[len(command)]
            else:
                candidate = qualified[len(command)-1]
            # De-duplicate
            if str(candidate) in candidates:
                continue
            candidates.append(str(candidate))
        return candidates, '' if ends_with_white else command[-1]

    def qhelp(self, line):
        """Called when ? is pressed. line is the text up to that point.
        Returns help items to be shown, as a list of (command, helptext)."""
        candidates, _ = self.prefix_matched_candidates(line)
        return candidates

    def complete(self, line):
        """Called when <TAB> is pressed. First time it will complete the word
        if possible. If not, pressed a second time it will display the possible
        alternatives."""
        candidates, current = self.prefix_matched_candidates(line)
        # Remove the already typed part of the candidates if there is only one
        if len(candidates) == 1:
            candidates[0] = candidates[0][len(current):]
        return candidates
