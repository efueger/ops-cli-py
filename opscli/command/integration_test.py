import collections
import command
import context
import match
import parse
import token


class AnyToken(token.Token):
    def match(self, unused_word):
        return True
    def transform(self, word):
        return word


class VlanToken(token.Token):
    def match(self, word):
        try:
            int(word)
            return True
        except ValueError:
            return False
    def transform(self, word):
        return int(word)


class VlanContext(context.Context):
    def new(self, vlan):
        self.vlan = vlan

class VlanConfigure(command.Utility):

    options = token.construct(VlanToken())

    def command(self, vlan_id):
        print repr(vlan_id)
        assert isinstance(vlan_id, int)
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


def create_match_tree(ctxt):
    CommandStruct = collections.namedtuple(
            'CommandStruct', ('modifiers', 'command'))
    commands = list(ctxt)
    tree = match.Tree()
    for words, obj in commands:
        # TODO(bluecmd): Register legal modifiers for this command
        modifiers = {'is_negated': False}
        struct = CommandStruct(modifiers, obj)
        command_tokens = [token.LiteralType(x) for x in words]
        for option in obj.options:
            tree.add(match.MatchGroup(command_tokens, option, struct))

    return tree

# Test it
# This is a very simple implementation of an CLI to test how all
# pieces fit together.
def execute(ctxt, words):
    # Step 0) Construct match tree for the current context
    full_tree = create_match_tree(ctxt)

    # Step 1) Parse command
    parse_result = parse.parse(words)
    command = parse_result.commands[0]

    # Step 2) Match and bind
    match_result = next(full_tree.match(command))
    modifiers = match_result.value.modifiers
    bound_command = match_result.value.command.bind(**modifiers)
    # Remove options that the receiving function will not handle
    option_tokens = match_result.secondary[:bound_command.argc]

    # Step 3) Transform options
    # Remove primary (command) arguments
    option_words = command[len(match_result.primary):]
    options = [token(word) for word, token in zip(option_words, option_tokens)]

    # Step 4) Execute
    try:
        ret = bound_command(*options)
    except TypeError as e:
        print 'Tried calling', bound_command, 'but got:', str(e)
        return ctxt

    # Step 5) Handle result
    if ret.value is not None:
        print ret
    return ret.context


ctxt = root()
ctxt = execute(ctxt, 'vlan 1')          # vlan.command(1)
#execute(ctxt, 'no shutdown')            # shutdown.dectivate()
execute(ctxt, 'desc "Hello World"')     # description.activate('Hello World')
#execute(ctxt, 'no desc')                # description.deactivate()
execute(ctxt, 's')                      # shutdown.activate()
