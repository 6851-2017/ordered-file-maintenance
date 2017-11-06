# jamb, rusch 6.851 Fall 2017


p = 3  # max number of pointers allowed to any object

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

class Node():
    '''A partially persistent DS node; stores fields, reverse pointers, mods.'''

    # initialize empty node
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent  # the PPPP that this node is in, for version tracking
        self.fields = {}  # map field name to value (value is probably a pointer)
        # reverse_pointers is a list that stores (node, field name) where this node is referenced
        self.fields[("__REVERSE_PTRS__")] = []
        self.mods = []  # mod is a tuple of (version, field, value)

    def __str__(self):
        return self.name

    def formatted(self):
        s = str(self) + "\n"
        s += "PARENT: " + str(self.parent) + "\n"
        s += "FIELDS:\n"
        for f in self.fields.keys():
            s += "\t" + f + ": " + str(self.fields.get(f)) +"\n"
##        s += "REVERSE POINTERS:\n"
##        for (n, f) in self.get_revptrs():
##            s += "\t" + "node " + str(n) + ", field " + f +"\n"
        s += "MODS:\n"
        for (vers, f, val) in self.mods:
            s += "\tVersion " + str(vers) + ", field " + f + ", value " + str(val) + "\n"
        return s

    # copy constructor, but turns mods directly into changing fields and has empty mods
    # also goes through reverse pointers and sends them to itself
    @classmethod
    def from_node(cls, node):
        print("CALLED FROM_NODE")
        new_node = cls(node.name, node.parent)
        new_node.fields = node.fields.copy()
        for _, name, val in node.mods:
            new_node.fields[name] = val
            if type(val) is Node:
                val.remove_reverse_pointer((node, name))
                val.add_reverse_pointer((new_node, name))
        for from_node, field_name in node.get_revptrs():
            from_node.set_field(field_name, new_node)
        return new_node

    # find the current version
    def get_version(self):
        return self.parent.version

    # update version by one
    def increment_version(self):
        self.parent.version += 1

    # modify a field value (add a mod if not full, create new node if it is)
    def set_field(self, name, value):
        self.increment_version()
        old_value = self.get_field(name)
        self.mods.append((self.get_version(), name, value))
        # fix reverse pointers
        if type(value) is Node:
            value.add_reverse_pointer(self, name)
        if type(old_value) is Node:
            old_value.remove_reverse_pointer(self, name)
        if len(self.mods) >= 2*p:
            n = Node.from_node(self)

    def get_revptrs(self):
        return self.get_field("__REVERSE_PTRS__")

    # add reverse pointer, check if there are more than p of them
    def add_reverse_pointer(self, from_node, field_name):
        revptrs = list(self.get_revptrs())
        revptrs.append((from_node, field_name))
        assert len(revptrs) <= p
        self.set_field("__REVERSE_PTRS__", revptrs)

    # remove reverse pointer
    def remove_reverse_pointer(self, from_node, field_name):
        revptrs = list(self.get_revptrs())
        revptrs.remove((from_node, field_name))
        self.set_field("__REVERSE_PTRS__", revptrs)

    # retrieve the value of the field at the given version (by default, current)
    # returns None if it's not in the fields or mods
    def get_field(self, name, version=None):
        if version is None:
            version = self.get_version()
        for mod in self.mods[::-1]:
            if mod[1] == name and mod[0] <= version:
                return mod[2]
        return self.fields.get(name)


# TESTING
P4 = PartiallyPersistentPointerPackage()
n0 = Node("n0", P4)
n1 = Node("n1", P4)
n2 = Node("n2", P4)
n3 = Node("n3", P4)
n4 = Node("n4", P4)
n0.set_field("ptr", 5)
n0.set_field("val", 5)
n0.set_field("ptr", n1)
n0.set_field("foo", "bar")
n2.set_field("ptr", n1)
print(n1.formatted())  # should have 2 back pointers
n2.set_field("ptr", n0)
n0.set_field("ptr", n2)
n0.set_field("foo", "foobar")
print(n1.formatted())  # now should have 0 back pointers
print(n2.get_field("ptr").formatted())  # should be a new n0 thing, not the original one
