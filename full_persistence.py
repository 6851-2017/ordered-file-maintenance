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
        self.first_version = self.versioner.insert_first(self)

    # returns the root FPNode at the given VersionPtr
    def get_root(self, version):
        return version.get_root()


# TODOs:
# when we split it seems like we should make just one new and not both new for efficiency
# overflow is a mess and almost certainly has bugs / wrong logic somewhere
# omg we need a less inefficient way to store reverse pointers than a list of pairs that we rewrite with every change

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
        self.child = None  # when overflows, has a child for the thing after it

    # print for debugging
    def formatted(self):
        s = "\n" + str(self) + "\n"
        s += "PARENT: " + str(self.parent) + "\n"
        s += "FIELDS:\n"
        for f in self.fields.keys():
            s += "\t" + f + ": " + str(self.fields.get(f, self.earliest_version)) +"\n"
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
        if (version < self.earliest_version):
            raise Exception("Cannot get a field from a node at a version earlier than its earliest version.")
        for mod in self.mods[::-1]:
            if mod[1] == name and not mod[0] > version:
                return mod[2]
        return self.fields.get(name)

    # modify a field value (add a mod if not full, split node if it is) right after the given version
    # returns the VersionPtr for the new version created by this modification
    def set_field(self, name, value, version):
        # check for an overflow in progress
        if len(self.mods) >= 2*(d+p+1):
            if self.child is None:
                raise Exception("Node has overflowed but doesn't have children to move to.")
            if version >= self.child.earliest_version:
                return self.child.set_field(name, value, version)

        # create the modification
        old_value = self.get_field(name, version)
        new_version = self.parent.versioner.insert_after(version)
        self.mods.append((new_version, name, value))

        # overflow if needed
        if len(self.mods) >= 2*(d+p+1):
            self._overflow()

        # update reverse pointers
        if type(old_value) is FPNode:
            old_value._remove_reverse_pointer(self, name, version)
        if type(value) is FPNode:
            value._add_reverse_pointer(self, name, version)

        return new_version

    # PRIVATE METHODS

    # create two new nodes with the first and second half of mods, make them the children
    # then once they're set up, do a bunch of pointer chasing
    def _overflow(self):
        # amend old node to have children
        self.is_active = False
        self.mods = sorted(self.mods, key=lambda x: x[0])
        mid_mod = self.mods[len(self.mods)//2]
        mid_version = mid_mod[0]
        rightchild = FPNode(self.name+"R", self.parent, mid_version)
        self.child = rightchild

        # set values of child fields
        rightchild.fields = self.fields.copy()
        rightchild.mods = self.mods[len(self.mods)//2:]
        self.mods = self.mods[:len(self.mods)//2]
        for _, name, val in self.mods:  # mods in the older half applied to newer half
            rightchild.fields[name] = val

        # pointer chasing time!
        # go through every initial-field and mod, change revptrs
        for version, name, val in rightchild.mods:
            # directly change revptrs for mods
            if type(val) is FPNode:
                val._update_reverse_pointer(self, rightchild, name, version)
        for name in rightchild.fields.keys():
            # use mods to add revptrs for newly created additional fields pointing into it from new child
            val = rightchild.fields[name]
            if type(val) is FPNode:
                val._add_reverse_pointer(rightchild, name, mid_version)

        # then go through all the revptrs and update their things' forward pointers
        for from_node, field_name in self._get_revptrs(mid_version):
            # use mods to add forward pointers after mid_version to rightchild instead of left child
            from_node.set_field(field_name, rightchild, mid_version)
        for version, name, val in rightchild.mods:
            # directly change forward pointers corresponding to revptr modifications
            if name == "__REVERSE__PTRS__":
                possibly_just_added_node, field_name = val[-1] # we actually don't know if this modification was an addition or a deletion, so check if it equals this node
                if (possibly_just_added_node.get_field(field_name, version) == self):
                    possibly_just_added_node._update_forward_pointer(self, rightchild, field_name, version)
        return


    # comparison function on mods (determine which is earlier version)
    def _compare_mods(self, mod1, mod2):
        return mod1[0] < mod2[0]

    # return a list of reverse pointers
    def _get_revptrs(self, version):
        return self.get_field("__REVERSE_PTRS__", version)

    # add reverse pointer, check if there are more than p of them
    def _add_reverse_pointer(self, from_node, field_name, version):
        revptrs = list(self._get_revptrs(version))
        revptrs.append((from_node, field_name))
        assert len(revptrs) <= p
        self.set_field("__REVERSE_PTRS__", revptrs, version)

    # remove reverse pointer
    def _remove_reverse_pointer(self, from_node, field_name, version):
        revptrs = list(self._get_revptrs(version))
        revptrs.remove((from_node, field_name))
        self.set_field("__REVERSE_PTRS__", revptrs, version)

    # manually replace pointers to go to newly created nodes and not reference the obsoletified ones
    def _update_reverse_pointer(self, old_node, new_node, field_name, version):
        revptrs_list = self._get_revptrs(version)
        for i in range(len(revptrs_list)):
            (node, name) = revptrs_list[i]
            if node == old_node:
                revptrs_list[i] = (new_node, name)
        return

    # manually replace pointers to go to newly created nodes and not reference the obsoletified ones
    def _update_forward_pointer(self, old_node, new_node, field_name, version):
        if version == self.earliest_version and self.fields[field_name] == old_node:
            self.fields[field_name] = new_node
        for i in range(len(self.mods)):
            vers, name, val = self.mods[i]
            if version == vers and field_name == name and val == old_node:
                self.mods[i] = vers, name, new_node
        return





