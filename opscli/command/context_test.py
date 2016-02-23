import context

def testSimpleContext():
    root = context.ContextTree(context.Context)
    foo = root.some_context()
    bar = root.some_context()

    print foo
    print bar

def testSpecialContext():

    class FakeContext(context.Context):
        def __init__(self, thing):
            self.thing = thing

    class FakeObject(context.ContextBoundObject):
        def __call__(self, other):
            return self.context.thing, other


    root = context.ContextTree(context.Context)
    root.some_context = FakeContext
    root.some_context.fake.command = FakeObject
    print root.some_context.fake.command._context

    print 'Binding context'
    print root.some_context
    foo = root.some_context(thing=1)
    print foo
    bar = root.some_context(thing=2)

    print 'Executing bound command'
    print foo.fake.command
    print foo.fake.command.Call(other='a')

def testNestedContexts():
    class FakeContext(context.Context):
        def __init__(self, thing):
            self.thing = thing

    class FakeObject(context.ContextBoundObject):
        def __call__(self, other):
            return self.context.thing, other



    root = context.ContextTree(context.Context)
    root.some_context = FakeContext
    # Test both context and command object in one
    root.some_context.another_context = FakeObject

    foo = root.some_context(thing=1)
    # Call FakeObject inside 'foo'
    print foo.another_context.Call(other='a') # == [1, 'a']

    bar = foo.another_context(thing=2)
    # Call FakeObject inside 'bar'
    print bar.Call(other='a')  # == [2, 'b']


print 'testSimpleContext'
testSimpleContext()
print 'testSpecialContext'
testSpecialContext()
print 'testNestedContexts'
testNestedContexts()
