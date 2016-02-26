from opscli.command import context
from opscli.command import command


class FakeCommand(command.Utility):
    def command(self):
        print 'Executing FakeCommand'


root = context.ContextTree(context.Context)
root.fake = FakeCommand
root.fake().Call()


## More complex example

class VlanContext(context.Context):
    def new(self, vlan):
        self.vlan = vlan

class VlanConfigure(command.Utility):
    def command(self, vlan_id):
        return root.vlan(vlan_id)

class Shutdown(command.Feature):
    def activate(self):
        print 'Shutting down VLAN', self.context.vlan

    def deactivate(self):
        print 'Starting VLAN', self.context.vlan


class Description(command.Feature):
    def activate(self, description):
        print 'Setting description to', description

    def deactivate(self):
        print 'Removing description'


root.vlan = VlanContext
root.vlan = VlanConfigure
root.vlan.shutdown = Shutdown
root.vlan.description = Description

# Test it
context = root().vlan.Call(1).context
context.shutdown.Call(is_negated=True)
context.description.Call('Hello', is_negated=False)
context.description.Call(is_negated=True)
context.shutdown.Call(is_negated=False)
