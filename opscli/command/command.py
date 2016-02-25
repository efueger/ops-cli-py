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
