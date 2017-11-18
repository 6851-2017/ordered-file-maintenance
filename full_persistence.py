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
        
    # returns the root FPNode at the given VersionPtr
    def get_root(self, version):
        return version.get_root()


# TODOs:
# implement all the stuff with "pass"

class FPNode():
    '''A fully persistent DS node: stores fields, reverse pointers, mods.'''

    # initialize empty node with String name, FPPM parent
    def __init__(self, name, parent, version):
        self.name = name
        self.parent = parent  # the FPPM that this node is in, for version tracking
        self.earliest_version = version
        self.fields = {}
        # reverse_pointers is a list that stores (node, field name) where this node is referenced
        self.fields[("__REVERSE_PTRS__")] = []
        self.mods = []  # mod is a tuple of (version, field, value)
        # is_active becomes false when it overflows and splits into two nodes
        # and should no longer have things pointing into or modifying it
        self.is_active = True
        self.children = (None, None)  # when no longer active, has children for earlier and later halves of mods

    # print for debugging
    def formatted(self):
        s = "\n" + str(self) + "\n"
        s += "PARENT: " + str(self.parent) + "\n"
        s += "FIELDS:\n"
        for f in self.fields.keys():
            s += "\t" + f + ": " + str(self.fields.get(f)) +"\n"
        s += "MODS:\n"
        for (vers, f, val) in self.mods:
            if f == "__REVERSE_PTRS__":
                s += "\tVersion " + str(vers) + ", field " + f + ", value " + str([(str(x[0]), str(x[1])) for x in val]) + "\n"
            else:
                s += "\tVersion " + str(vers) + ", field " + f + ", value " + str(val) + "\n"
        return s

    # retrieve the value of the field at the given VersionPtr
    # returns None if it's not in the fields or mods
    # if version is older than anything in this node, throws an error
    def get_field(self, name, version):
        if (version < earliest_version):
            raise Exception("Cannot get a field from a node at a version earlier than its earliest version.")
        for mod in self.mods[::-1]:
            if mod[1] == name and not mod[0] > version:
                return mod[2]
        return self.fields.get(name)

    # modify a field value (add a mod if not full, split node if it is) right after the given version
    # returns the VersionPtr for the new version created by this modification
    def set_field(self, name, value, version):
        # check for an overflow in progress
        if len(self.mods) >= 2*(d+p+1) or not self.is_active:
            leftchild, rightchild = self.children
            if leftchild is None or rightchild is None:
                raise Exception("Node has overflowed but doesn't have children to move to.")
            if version < rightchild.earliest_version:
                return leftchild.set_field(name, value, version)
            else:
                return rightchild.set_field(name, value, version)

        # create the modification
        old_value = self.get_field(name)
        new_version = self.parent.versioner.insert_after(version) 
        self.mods.append(new_version, name, value)

        # overflow if needed
        if len(self.mods) >= 2*(d+p+1):
            self.is_active = False
            self._overflow()

        # update reverse pointers
        if type(old_value) is Node:
            old_value._remove_reverse_pointer(self, name)
        if type(value) is Node:
            value._add_reverse_pointer(self, name)

        return new_version

    # PRIVATE METHODS

    # create two new nodes with the first and second half of mods, make them the children
    # then once they're set up, do a bunch of pointer chasing
    def _overflow(self):
        pass
    
    # return a list of reverse pointers
    def _get_revptrs(self):
        return self.get_field("__REVERSE_PTRS__")

    # add reverse pointer, check if there are more than p of them
    def _add_reverse_pointer(self, from_node, field_name):
        revptrs = list(self._get_revptrs())
        revptrs.append((from_node, field_name))
        assert len(revptrs) <= p
        self.set_field("__REVERSE_PTRS__", revptrs, new_version=False)

    # remove reverse pointer
    def _remove_reverse_pointer(self, from_node, field_name):
        revptrs = list(self._get_revptrs())
        revptrs.remove((from_node, field_name))
        self.set_field("__REVERSE_PTRS__", revptrs, new_version=False)





