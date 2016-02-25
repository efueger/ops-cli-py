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

    class AnotherFakeContext(context.Context):
        pass

    class AnotherFakeObject(context.ContextBoundObject):
        def __call__(self):
            pass

    root = context.ContextTree(context.Context)
    root.some_context = FakeContext
    # Test both context and command object in one
    root.some_context.fake = FakeObject

    # Call test
    foo = root.some_context(thing=1)
    # Call FakeObject inside 'some_context'
    print foo.fake.Call(other='a') # == [1, 'a']

    bar = foo.fake(thing=2)
    # Call FakeObject inside 'some_context.fake'
    print bar.Call(other='a')  # == [2, 'b']


    # Iterator test

    # When iterating over bound contexts we should not see objects
    # belonging inside the other context, but should see border objects
    root.some_context.another_context = AnotherFakeContext
    root.some_context.another_context = FakeObject
    root.some_context.another_context.fake.object = AnotherFakeObject

    print list(root) # == ['some_context']

    print 'Root'
    print list(root()) # == []
    print 'SomeContext'
    print list(root.some_context(thing=1)) # == [['another_context'], ['fake']]
    print 'AnotherContext'
    print list(root.some_context(thing=1).another_context()) # == [['fake', 'object']]


print 'testSimpleContext'
testSimpleContext()
print 'testSpecialContext'
testSpecialContext()
print 'testNestedContexts'
testNestedContexts()
