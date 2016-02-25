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

class CommandNotFoundError(Exception):
    """Raised if the user tries to execute a command that doesn't exist."""
    pass


class LineHelper(object):
    """Logic glue between CLI logic and Console implementation."""

    def qhelp(self, line):
        pass

    def complete(self, line, show_all):
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

    def find_command(self, words):
        # Step 1) Parse command
        parse_result = parse.parse(words)
        command = parse_result.commands[0]

        # Step 2) Match and bind
        match_result = next(self.tree.match(command), None)
        if match_result is None:
            raise CommandNotFoundError(words)
        modifiers = match_result.value.modifiers
        bound_command = match_result.value.command.bind(**modifiers)
        # Remove options that the receiving function will not handle
        option_tokens = match_result.secondary[:bound_command.argc]

        # Step 3) Transform options
        # Remove primary (command) arguments
        option_words = command[len(match_result.primary):]
        options = [token(word) for word, token in zip(option_words, option_tokens)]

        return bound_command, options


    def qhelp_items(self, line):
        '''Called when ? is pressed. line is the text up to that point.
        Returns help items to be shown, as a list of (command, helptext).'''
        items = []
        words = line.split()
        if not words:
            # On empty line: show all commands in this context.
            return sorted(self.context.get_help_subtree())

        matches = self.context.find_command(words)
        if not matches:
            raise Exception(CLI_ERR_NOMATCH)
        if line[-1].isspace():
            # Last character is a space, so whatever comes before has
            # to match a command unambiguously if we are to continue.
            if len(matches) != 1:
                raise Exception(CLI_ERR_AMBIGUOUS)

            cmd_complete = False
            # TODO(bluecmd): This cuts all the way through the abstraction
            # Let's move get_help_subtree to cmdobj and use it here
            cmdobj = matches[0]
            for key in cmdobj.branch:
                items.append(self.context.helpline(cmdobj.branch[key], words))
            if hasattr(cmdobj, 'options'):
                opt_words = words[len(cmdobj.command):]
                if not opt_words and flags.F_NO_OPTS_OK in cmdobj.flags:
                    # Didn't use any options, but that's ok.
                    cmd_complete = True
                elif len(opt_words) == len(cmdobj.options):
                    # Used all options, definitely a complete command.
                    cmd_complete = True
                elif opt_words:
                    # Only some options were used, check if we missed
                    # any required ones.
                    try:
                        opt_tokens = tokenize_options(opt_words,
                                                      cmdobj.options)
                        check_required_options(opt_tokens, cmdobj.options)
                        # Didn't bomb out, so all is well.
                        cmd_complete = True
                    except:
                        pass
                items.extend(options.help_options(cmdobj, words))
            else:
                # Command has no options.
                cmd_complete = True
            if cmd_complete and hasattr(cmdobj, 'run'):
                items.insert(0, stringhelp.Str_help(('<cr>', cmdobj.__doc__)))
        else:
            # Possibly incomplete match, not ending in space.
            for cmdobj in matches:
                if len(words) <= len(cmdobj.command):
                    # It's part of the command
                    # TODO(bluecmd): This cuts all the way through the abstraction
                    # Let's move get_help_subtree to cmdobj and use it here
                    items.append(self.context.helpline(cmdobj, words[:-1]))
                else:
                    # Must be an option.
                    items.extend(options.complete_options(cmdobj, words))
        return sorted(items)

    def complete(self, line):
        if not line:
            return
        words = line.split()
        matches = self.context.find_command(words)
        if not matches:
            return

        items = []
        if line[-1].isspace():
            # Showing next possible words or arguments.
            if len(matches) != 1:
                # The line doesn't add up to an unambiguous command.
                return

            if self.reader.last_event != 'complete':
                # Only show next words/arguments on second tab.
                return

            cmdobj = matches[0]
            # Strip matched command words.
            words = words[len(cmdobj.command):]

            if cmdobj.branch.keys():
                # We have some matching words, need to list the rest.
                items = cmdobj.branch.keys()
            else:
                # No more commands branch off of this one. Maybe it
                # has some options?
                items = options.help_options(cmdobj, words)
        else:
            # Completing a word.
            if len(matches) == 1:
                # Found exactly one completion.
                if len(words) <= len(matches[0].command):
                    # It's part of the command
                    cmpl_word = matches[0].command[len(words) - 1]
                else:
                    # Must be an option.
                    cmpl_word = None
                    cmpls = options.complete_options(matches[0], words)
                    if len(cmpls) == 1:
                        # Just one option matched.
                        cmpl_word = cmpls[0]
                    elif len(cmpls) > 1:
                        # More than one match. Ignore the first completion
                        # attempt, and list all possible completions on every
                        # tab afterwards.
                        if self.last_event == 'complete':
                            for cmdobj in matches:
                                items.append(' '.join(cmpls))
                if cmpl_word:
                    cmpl = cmpl_word[len(words[-1]):]
                    self.reader.insert(cmpl + ' ')
            else:
                # More than one match. Ignore the first completion attempt,
                # and list all possible completions on every tab afterwards.
                if self.reader.last_event == 'complete':
                    for cmdobj in matches:
                        items.append(' '.join(cmdobj.command))
        if not items:
            return


