import abc
import context

class Command(context.ContextBoundObject):

    __metaclass__ = abc.ABCMeta

    class Bound(object):

        def __init__(self, command, options, is_negated=False):
            self.command = command
            self.options = options
            self.is_negated = is_negated

        def __call__(self):
            return self.command.execute(self.options, self.is_negated)

    def __call__(self, *args, **kwargs):
        return Command.Bound(self, args, **kwargs)()

    @abc.abstractmethod
    def execute(self, options, is_negated):
        pass



class Feature(Command):
    """Feature commands are for features that can be activated/deactivated.

    Example is "debug". The "debug" command belongs to a feature context
    since it can be activated ("debug foo") and deactivated ("no debug foo").
    """

    def execute(self, options, is_negated):
        if is_negated:
            self.deactivate(*options)
        else:
            self.activate(*options)

    def isActivated(self):
        pass

    def activate(self):
        pass

    def deactivate(self):
        pass



class Utility(Command):
    """Utility commands are for simple commands that only produce output."""

    def execute(self, options, unused_is_negated):
        return self.command(*options)

    def command(self):
        pass

