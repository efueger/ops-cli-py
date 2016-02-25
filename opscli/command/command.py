"""
A command class represent an action that can be taken in the CLI.

There are two general types of commands:
- Utility
- Feature

Utility commands do something when you type the command.
Example: reload, clear, show ip route, configure, exit

Feature commands are things that can be modified, turned on, or turned off.
Example: hostname, ip routing, description

A basic utility command looks like this:

class MyCommand(command.Utility):
    '''Prints a message in the console'''
    
    def command(self):
        return 'Executing my command'

While a basic feature looks like:

class MyFeature(command.Feature):
    '''Turns the awesome feature on.'''
    
    def activate(self):
        print 'Executing FakeCommand'

Commands also have two optional fields:
- options
- prefixes (TODO)

# Options
Options takes a set of objects that will be compared to
the user given command line to make sure it validates and
to provide completition services. It's important to note
that this field needs iterate combinatorially - so
looping over it will produce all legal combinations.

For more info: Usually this field is set to token.InOrder (see token.py)

# Prefixes and Routing
Every command has a route() function that uses so called modifiers to
route the command to the correct function.

Example: Putting 'no' in prefixes will register the same command
twice - once without prefix, and once prefixed with 'no'.

This 'no' prefix can then be interpreted as a modifier. Usually
'no' results in setting 'is_negated' to True. This causes route()
to return deactivate() instead of the normal activate() on Feature
commands.

# Calling a command
When you have a command object you call it by first binding the modifiers
to it. This causes the routing to establish which function to call.
You then use the result of bind as a function call with the options
the function is expecting.

Example:
Assume we have Utility command with the following command function:
class MyCommand(command.Utility):
  def command(self, password):
    pass

We would call it like this:
MyCommand().bind(is_negated=False)("secret_password")
The reason for this syntax is that you can save the bound function
and call it later when the options are available. This is useful
for command parsing.

If you want to, you can also use a shortcut notation:
MyCommand()("secret_password", is_negated=False)
"""
import abc
import collections
import context


CommandResult = collections.namedtuple('CommandResult', ('context', 'value'))


class Command(context.ContextBoundObject):

    __metaclass__ = abc.ABCMeta

    # Default to no arguments required
    options = (list(), )

    class Bound(object):

        def __init__(self, command, **kwargs):
            self.command = command
            self.func = command.route(**kwargs)
            self.argc = self.func.func_code.co_argcount

        def __call__(self, *options):
            # Command functions return either text to print or switches
            # context. Find out what it wanted to do.
            ret = self.func(*options)
            ctxt = self.command.context
            value = None
            if isinstance(ret, context.BoundContextTree):
                ctxt = ret
            else:
                value = ret
            return CommandResult(ctxt, value)

        def __str__(self):
            return '%s.%s' % (self.func.im_class.__name__, self.func.__name__)

    def bind(self, **kwargs):
        return Command.Bound(self, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.bind(**kwargs)(*args)

    @abc.abstractmethod
    def route(self, **kwargs):
        pass


class Feature(Command):
    """Feature commands are for features that can be activated/deactivated.

    Example is "debug". The "debug" command belongs to a feature context
    since it can be activated ("debug foo") and deactivated ("no debug foo").
    """

    def route(self, is_negated):
        if is_negated:
            return self.deactivate
        else:
            return self.activate

    def isActivated(self):
        pass

    @abc.abstractmethod
    def activate(self):
        pass

    @abc.abstractmethod
    def deactivate(self):
        pass


class Utility(Command):
    """Utility commands are for simple commands that only produce output."""

    def route(self, **kwargs):
        return self.command

    @abc.abstractmethod
    def command(self):
        pass
