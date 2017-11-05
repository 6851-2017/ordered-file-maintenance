# jamb, rusch 6.851 Fall 2017


p = 5  # max number of pointers allowed to any object

class PartiallyPersistentPointerPackage():
    '''Has a list of Nodes, each of which is partially persistent and has
        bidirectional pointers with other Nodes.'''
    def __init__(self):
        self.nodes = []
        self.version = 0

    def add_node(node):
        self.nodes.append(node)


# TODOs:
# how do we handle lookups for things before the version of the current base node?
# do reverse_pointers ever get deleted if the thing no longer references this node?

class Node():
    '''A partially persistent DS node; stores fields, reverse pointers, mods.'''

    # initialize empty node
    def __init__(self, parent):
        self.parent = parent  # the PPPP that this node is in, for version tracking
        self.fields = {}  # map field name to value (value is probably a pointer)
        self.reverse_pointers = []  # reverse_pointer stores (node, field name) where this node is referenced
        self.mods = []  # mod is a tuple of (version, field, value)

    # copy constructor, but turns mods directly into changing fields and has empty mods
    # also goes through reverse pointers and sends them to itself
    def __init__(self, node, parent):
        self.parent = parent
        self.fields = node.fields.copy()
        for _, name, val in node.mods:
            assert name in self.fields.keys()
            self.fields[name] = val
        self.mods = []
        for from_node, field_name in node.reverse_pointers:
            assert field_name in from_node.fields.keys()
            from_node.fields[field_name] = self
        self.reverse_pointers = node.reverse_pointers

    # find the current version
    def get_version(self):
        return self.parent.version

    # update version by one
    def increment_version(self):
        self.parent.version += 1

    # modify a field value (add a mod if not full, create new node if it is)
    def set_field(self, name, value):
        self.increment_version()
        if len(self.mods) >= p:
            n = Node(self, parent)
        else:
            self.mods.append((self.get_version(), name, value))

    # add reverse pointer, check if there are more than p of them
    def add_reverse_pointer(self, from_node, field_name):
        self.reverse_pointers.append((from_node, field_name))
        assert len(self.reverse_pointers) <= p

    # retrieve the value of the field at the given version (by default, current)
    # returns None if it's not in the fields or mods
    def get_field(self, name, version=None):
        if version is None:
            version = self.get_version()
        for mod in self.mods[::-1]:
            if mod[1] == name and mod[0] <= version:
                return mod[2]
        return self.fields.get(name)
    
