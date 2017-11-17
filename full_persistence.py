# jamb, rusch 6.851 Fall 2017

from ordered_list import Versioner, VersionPtr

d = 3  # max number of outgoing pointers allowed for any object
p = 3  # max number of pointers allowed to any object


# Fully Persistent Pointer Machine
class FPPM():
    '''Serves as a parent object for FPNodes, each of which stores fields and modifications.
        Stores the OrderedFile that allows versioning.
        Queries return the root node at a given version.'''

    # constructor
    def __init__(self):
        self.versioner = Versioner()
        self.root = FPNode("root", self)  # TODO does this even make sense?

    # returns the root FPNode at the given VersionPtr
    def get_root(self, version):
        return version.get_root()


# TODOs:
# implement all the stuff with "pass"

class FPNode():
    '''A fully persistent DS node: stores fields, reverse pointers, mods.'''

    # initialize empty node with String name, FPPM parent
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent  # the FPPM that this node is in, for version tracking
        self.fields = {}
        # reverse_pointers is a list that stores (node, field name) where this node is referenced
        self.fields[("__REVERSE_PTRS__")] = []
        self.mods = []  # mod is a tuple of (version, field, value)
        # is_active becomes false when it overflows and splits into two nodes
        # and should no longer have things pointing into or modifying it
        self.is_active = True

    # print for debugging
    def formatted(self):
        pass

    # retrieve the value of the field at the given VersionPtr
    # returns None if it's not in the fields or mods
    # if version is older than anything in this node, throws an error
    def get_field(self, name, version):
        pass

    # modify a field value (add a mod if not full, split node if it is) right after the given version
    # returns the VersionPtr for the new version created by this modification
    def set_field(self, name, value, version):
        pass

    # suggested private methods to copy over from partial persistence:
    # _get_revptrs
    # _add_revptr
    # _remove_revptr
    # some sort of copy constructor like _from_node except we need to split into two
