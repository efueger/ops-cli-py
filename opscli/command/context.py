from collections import defaultdict


class Context(object):
    pass


class ContextBoundObject(object):
    def __init__(self, context):
        self.context = context

    def __call__(self, *args, **kwargs):
        pass


class ContextTree(object):
    """Meta class to handle context and command trees.

    Setting attributes:

    1) tree.a = Context
    This sets the default context from this place in the tree to SomeContext.

    2) tree.a = ContextBoundObject
    This sets the constructor for tree.a to construct a ContextBoundObject
    when called.

    Retriving attributes:

    Calling:
        This binds the context tree. TODO: describe more.

    Iterating:

    """

    def __init__(self, context=None, parent=None):
        self._context = context
        self._branches = defaultdict(lambda: ContextTree(parent=self))
        self._bind = None
        self._parent = parent

    def __getattr__(self, name):
        if name.startswith('_'):
            return super(ContextTree, self).__getattr__(name)
        return self._branches[name]

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(ContextTree, self).__setattr__(name, value)
            return

        if issubclass(value, Context):
            self._branches[name]._context = value
        else:
            self._branches[name]._bind = value

    def _get_context(self):
        return (self._context if self._context is not None
                else self._parent._get_context())

    def __call__(self, *args, **kwargs):
        context = self._get_context()(*args, **kwargs)
        return BoundContextTree(self, context)


class BoundContextTree(object):

    def __init__(self, tree, context):
        self._tree = tree
        self._context = context

    def __getattr__(self, name):
        return BoundContextTree(getattr(self._tree, name), self._context)

    def __setattr__(self, name, value):
        # Bound context trees are immutable
        assert name.startswith('_')
        super(BoundContextTree, self).__setattr__(name, value)

    def __call__(self, *args, **kwargs):
        return self._tree(*args, **kwargs)

    def New(self):
        return self._tree._bind(self._context)

    def Call(self, *args, **kwargs):
        return self.New()(*args, **kwargs)
