"""
Contexts hold state and knows about valid actions to take inside the context.

A context can be thought of as a box with some optional attributes attatched
to it. For example you might want to have a command 'vlan 10' to enter a
state where every command would affect VLAN 10. Creating a VLAN context for
this with a VLAN ID attribute is the right way to go.

Contexts have only one method that you usually need to care about: new.
New is used to attach attributes when binding a context. Override it
to assign attributes for later use.

# Context trees
A context tree contains a reference to the active context, but also every
valid action that can be taken inside that context.

There are two types of contexts trees:
Unbound (ContextTree) and Bound (BoundContextTree)

Limitations:
- When a ContextTree is bound it cannot be unbound again.
- You can only perform actions on bound context tree.
- A bound context tree does not allow action registration or context
  family switching (see below)

# Creating and bindning a Context tree

c = context.ContextTree(context.Context)

Here we created 'c', a context tree that by default uses
the context.Context context type for the root context that
everything inherits from.

If we want to change a context to another type of context
we can do so by assigning it a Context subclass type:

class MyConfigContext(context.Context):
  pass
c.config = MyConfigContext

We can also attatch actions by derriving ContextBoundObject:

class Action(context.ContextBoundObject):
  def __call__(self, user):
    # We can access the context attributes via self.context
    print user, 'is doing stuff inside context'
c.config.action = Action

To call action we first need to bind the context:
ctxt = c.config()
This will instansiate MyConfigContext. If we had any arguments to 'new'
we would pass them here, like: c.config(thing=1)

We can now call action:
ctxt.action('Chuck Norris')
=> "Chuck Norris is doing stuff inside context

# Note on border actions
A border action is an action that is also switching context.
Example are 'configure', and 'vlan' commands.

They are registeres like this:
c.configure = MyConfigureContext
c.configure = MyConfigureAction

This looks odd at first glance, but what the first line is doing is
assigning the context family to the c.configure subtree.
The second line is then bindning an action to that specific node node.

If this becomes too confusing for people we might end up changing it.

# Iterating over Context trees

Iterating over an unbound context tree gives you the currently
registered branches.

Example:
c.configure = Foo
c.reload = Bar
print list(c) => ['configure', 'reload']

Iterating over a bound context tree however will give you all
bound actions inside the same context family (i.e. all allowed
actions)

Example:
c.configure = Foo
c.configure.hostname = Bar
c.reload = Xyz
print list(c()) => [(['configure'], Foo), (['reload'], Xyz)]
print list(c.configure()) => [(['hostname'], Bar)]
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
        self.new(*args, **kwargs)

    def __str__(self):
        return self.prompt

    def new(self, *args, **kwargs):
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
