
import os

from pyrepl.reader import Reader
from pyrepl.unix_console import UnixConsole
from pyrepl.historical_reader import HistoricalReader
import pyrepl.commands

from opscli import options
from opscli import output


HISTORY_FILE = '~/.opscli_history'

# Number of lines to remember across sessions.
HISTORY_SIZE = 1000


class ExtendedHistoricalReader(HistoricalReader):

    def __init__(self, *args, **kwargs):
        super(ExtendedHistoricalReader, self).__init__(*args, **kwargs)
        self.fix_syntax_table()
        self.last_event = None

    def fix_syntax_table(self):
        '''The default pyrepl syntax table only considers a-z as word
        boundaries, which affects keyboard navigation. Add a few more.'''
        extra = '0123456789_-'
        for c in extra:
            self.syntax_table[unichr(ord(c))] = 1

    def after_command(self, cmd):
        # This has the callback names e.g. 'qhelp', 'complete' etc.
        self.last_event = cmd.event_name
        super(ExtendedHistoricalReader, self).after_command(cmd)

    def error(self, msg):
        '''This gets messages from pyrepl's edit commands, nothing you
        want to see displayed. However they're the sort of thing that
        cause readline to send a beep.'''
        self.console.beep()


class HistoryFile(object):

    def __init__(self, reader):
        self.histfile = os.path.expanduser(HISTORY_FILE)
        self.reader = reader

    def __enter__(self):
        if os.path.exists(self.histfile):
            with open(self.histfile) as f:
                self.reader.history = f.read().split('\n')[:-1]

    def __exit__(self, unused_type, unused_value, unused_traceback):
        with open(self.histfile, 'w') as f:
            f.write('\n'.join(self.reader.history[-HISTORY_SIZE:]))
            f.write('\n')


class PyreplConsole(object):
    '''
    This class extends pyrepl's Reader to provide command modules.
    '''
    def __init__(self, prompt, context):
        self.reader = ExtendedHistoricalReader(UnixConsole())
        self.reader.bind(r'?', 'qhelp')
        self.reader.bind(r'\t', 'complete')
        self.context = context
        self.bind('interrupt', self.interrupt)
        self.bind('complete', self.complete)
        self.bind('qhelp', self.qhelp)
        self.prompt_base = prompt

        super(PyreplConsole, self).__init__()

    def interrupt(self, unused_line):
        raise KeyboardInterrupt

    def qhelp(self, unused_line):
        pass

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
        self.print_inline(self.fmt_cols(items))

    def fmt_cols(self, data):
        '''Arrange strings into columns depending on terminal width and the
        longest string.'''
        return '    '.join(data)

    def bind(self, action, function):
        class command(pyrepl.commands.Command):
            def do(unused_other):
                line = ''.join(self.reader.buffer)
                function(line)
        self.reader.commands[action] = command

    def set_context(self, context):
        self.context = context

    def loop(self):
       with HistoryFile(self.reader):
            while True:
                try:
                    self.reader.ps1 = (
                            self.prompt_base + self.context.make_prompt())
                    yield self.reader.readline()
                except EOFError:
                    # ctrl-d quits the shell.
                    break
                except KeyboardInterrupt:
                    # ctrl-c throws away the current line and prompts again.
                    cli_out('^C')

    def print_inline(self, text):
        '''Write text on the next line, and reproduce the prompt and entered
        text without submitting it.'''
        output.cli_wrt('\r\n')
        output.cli_wrt(text.replace('\n', '\r\n'))
        output.cli_wrt('\r\n')
        output.cli_wrt(self.reader.ps1)
        output.cli_wrt(''.join(self.reader.buffer))

    def show_help(self, words):
        if not words:
            output.cli_help(self.context.get_help_subtree())
            return
        matches = self.context.find_command(words)
        if len(matches) == 0:
            output.cli_err(CLI_ERR_NOHELP_UNK)
        elif len(matches) > 1:
            output.cli_err(CLI_ERR_AMBIGUOUS)
        else:
            output.cli_out(matches[0].__doc__)


