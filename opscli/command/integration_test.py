import command
import context
import match
import parse
import token


class AnyToken(token.Token):
    def match(self, unused_word):
        return True


class VlanToken(token.Token):
    def match(self, word):
        try:
            int(word)
            return True
        except ValueError:
            return False


class VlanContext(context.Context):
    def __init__(self, vlan):
        self.vlan = vlan

class VlanConfigure(command.Utility):

    options = token.construct(VlanToken())

    def command(self, vlan_id):
        return root.vlan(vlan_id)

class Shutdown(command.Feature):
    def activate(self):
        print 'Shutting down VLAN', self.context.vlan

    def deactivate(self):
        print 'Starting VLAN', self.context.vlan


class Description(command.Feature):

    options = token.construct(AnyToken())

    def activate(self, description):
        print 'Setting description to', description

    def deactivate(self):
        print 'Removing description'


root = context.ContextTree(context.Context)

root.vlan = VlanContext
root.vlan = VlanConfigure
root.vlan.shutdown = Shutdown
root.vlan.description = Description


# Test it
# This is a very simple implementation of an CLI to test how all
# pieces fit together.
def execute(ctxt, command):
    # Step 0) Construct match tree
    # This is always the same as long as we don't load new commands or
    # modify the options to a command class.
    # This will usually be calculated on startup and then never again.
    commands = list(ctxt)
    full_tree = list()
    for words, obj in commands:
        for option in obj.options:
            full_tree.append(
                    match.MatchGroup(words, option, obj))

    # Step 1) Parse command
    parse_result = parse.parse(command)
    first_command = parse_result.commands[0]

    # Step 2) Match and bind
    match_result = next(match.match(first_command, full_tree))
    bound_command = match_result.value.bind(**match_result.modifiers)
    # Remove options that the receiving function will not handle
    options = match_result.secondary[:bound_command.argc]

    # Step 3) Execute
    try:
        ret = bound_command(*options)
    except TypeError as e:
        print 'Tried calling', bound_command, 'but got:', str(e)
        return ctxt

    # Step 4) Handle result
    if ret is None:
        pass
    elif isinstance(ret, context.BoundContextTree):
        ctxt = ret
    else:
        print ret
    return ctxt


ctxt = root()
ctxt = execute(ctxt, 'vlan 1')          # vlan.command(1)
execute(ctxt, 'no shutdown')            # shutdown.dectivate()
execute(ctxt, 'desc "Hello World"')     # description.activate('Hello World')
execute(ctxt, 'no desc')                # description.deactivate()
execute(ctxt, 's')                      # shutdown.activate()
