
import os
import sys

from pyrepl.reader import Reader
from pyrepl.unix_console import UnixConsole
from pyrepl.historical_reader import HistoricalReader
import pyrepl.commands

from opscli import linehelper


HISTORY_FILE = '~/.opscli_history'

# Number of lines to remember across sessions.
HISTORY_SIZE = 1000

class ExtendedHistoricalReader(HistoricalReader):

    def __init__(self, *args, **kwargs):
        super(ExtendedHistoricalReader, self).__init__(*args, **kwargs)
        self.fix_syntax_table()
        self.last_event = None

    def fix_syntax_table(self):
        """The default pyrepl syntax table only considers a-z as word
        boundaries, which affects keyboard navigation. Add a few more."""
        extra = '0123456789_-'
        for c in extra:
            self.syntax_table[unichr(ord(c))] = 1

    def after_command(self, cmd):
        # This has the callback names e.g. 'qhelp', 'complete' etc.
        self.last_event = cmd.event_name
        super(ExtendedHistoricalReader, self).after_command(cmd)

    def error(self, msg):
        """This gets messages from pyrepl's edit commands, nothing you
        want to see displayed. However they're the sort of thing that
        cause readline to send a beep."""
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
    """
    This class extends pyrepl's Reader to provide command modules.
    """
    def __init__(self, prompt, motd, helper):
        self.reader = ExtendedHistoricalReader(UnixConsole())
        self.reader.bind(r'?', 'qhelp')
        self.reader.bind(r'\t', 'complete')
        self.bind('interrupt', self.interrupt)
        self.bind('complete', self.complete)
        self.bind('qhelp', self.qhelp)
        self.prompt_base = prompt
        self.helper = helper

        self.output(motd)

        super(PyreplConsole, self).__init__()

    def interrupt(self, unused_line):
        raise KeyboardInterrupt

    def qhelp(self, line):
        try:
            items = self.helper.qhelp(line)
        except linehelper.CommandNotFoundError:
            self.print_inline('% Command not found')
            return

        self.output()
        for item in items:
            self.output(item if item else '<cr>')

        sys.stdout.write(self.reader.ps1 + line)
        sys.stdout.flush()

    def complete(self, line):
        if not line:
            return
        # Only show next words/arguments on second tab.
        show_more = self.reader.last_event == 'complete'
        try:
            items = self.helper.complete(line)
        except linehelper.CommandNotFoundError:
            self.print_inline('% Command not found')
            return
        if len(items) == 1:
            self.reader.insert(items[0] + ' ')
        else:
            if show_more:
                # Replace '' with '<cr>'
                items = [x if x else '<cr>' for x in items]
                self.print_inline(self.fmt_cols(items))
            else:
                self.reader.console.beep()

    def fmt_cols(self, data):
        """Arrange strings into columns depending on terminal width and the
        longest string."""
        return '    '.join(data)

    def bind(self, action, function):
        class command(pyrepl.commands.Command):
            def do(unused_other):
                line = ''.join(self.reader.buffer)
                function(line)
        self.reader.commands[action] = command

    def loop(self):
       with HistoryFile(self.reader):
            while True:
                try:
                    self.reader.ps1 = (
                            self.prompt_base + self.helper.prompt)
                    read = self.reader.readline().strip()
                    if read:
                        yield read
                except EOFError:
                    # ctrl-d quits the shell.
                    break
                except KeyboardInterrupt:
                    # ctrl-c throws away the current line and prompts again.
                    self.output('^C')

    def print_inline(self, text):
        """Write text on the next line, and reproduce the prompt and entered
        text without submitting it."""
        self.output()
        self.output(text)
        sys.stdout.write(self.reader.ps1)
        sys.stdout.write(''.join(self.reader.buffer))
        sys.stdout.flush()

    def output(self, *values):
        """Called when there is something to output returned by a command."""
        sys.stdout.write((' '.join(values) + '\n').replace('\n', '\r\n'))
        sys.stdout.flush()
