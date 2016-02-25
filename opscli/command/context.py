"""
TODO(bluecmd): Talk about setting up contexts
TODO(bluecmd): Talk about binding and calling contexts
TODO(bluecmd): Talk about iteration and border objects
"""
from collections import defaultdict


class Context(object):
    """Context is a state in the command tree.

    Contextes by default adopt all attributes of their parents.
    """

    prompt = ''

    def __init__(self, parent, *args, **kwargs):
        for key, value in parent.__dict__.iteritems():
            setattr(self, key, value)
        self.parent = parent
        self.new(*args, **kwargs)

    def __str__(self):
        return self.prompt

    def new(self, *args, **kwargs):
        pass

    def exit(self):
        return self.parent


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
        """Bind a context to allow command execution."""
        context = self._get_context()(self.context, *args, **kwargs)
        return BoundContextTree(self, context)

    def __iter__(self):
        """Unbound contexts allows enumeration of branches."""
        return iter(self._branches)

    def _is_border_branch(self, branch):
        return self._branches[branch]._is_border_object()

    def _is_border_object(self):
        if self._context == None:
            return False
        return self._parent._get_context() != self._context


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

    def __str__(self):
        return str(self._context)

    def __iter__(self):
        """Bound context iterates over the bound objects within the context."""
        if self._tree._bind:
            # If we are a border object, we belong to the parent context
            if not self._tree._is_border_object():
                yield ([], self.New())
        for branch in self._tree:
            child = getattr(self, branch)
            # Check that we're not trying to cross a context boundry
            if self._tree._is_border_branch(branch):
                # Allow border objects
                if child._tree._bind:
                    yield ([branch], child.New())
                continue
            for combination, obj in child:
                yield ([branch] + combination, obj)

    def New(self):
        return self._tree._bind(self)

    def Call(self, *args, **kwargs):
        return self.New()(*args, **kwargs)
