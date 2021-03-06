# jamb, rusch 6.851 Fall 2017

from ordered_list import OrderedList, OrderedListComparison, VersionPtr

d = 3  # max number of outgoing pointers allowed for any object
p = 3  # max number of pointers allowed to any object


# Fully Persistent Pointer Machine
class FPPM():
    '''Serves as a parent object for FPNodes, each of which stores fields and modifications.
        Stores the OrderedFile that allows versioning.
        Queries return the root node at a given version.'''

    # constructor
    def __init__(self):
        self.versioner = OrderedList()
        root = FPRoot(self, None)
        self.first_version = self.versioner.insert_first(root)
        root.earliest_version = self.first_version
        self.all_version_ptrs_ever = [self.first_version]  # TODO delete this thing, just for testing

    # returns the root FPNode at the given VersionPtr
    def get_root(self, version):
        return version.get_root()


# TODOs:
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
        self.reverse_pointer_mods = []  # list of tuples (node, field_name, version, is_adding) for revptr mods
        self.reverse_pointers = []  # list of tuples (node, field_name, version)
        self.mods = []  # mod is a tuple of (version, field, value)
        self.child = None  # when overflows, has a child for the thing after it

    # print for debugging
    def formatted(self):
        s = "\n" + str(self) + "\n"
        s += "PARENT: " + str(self.parent) + "\n"
        s += "CHILD: " + str(self.child) + "\n"
        s += "EARLIEST VERSION: " + str(self.earliest_version) + "\n"
        s += "FIELDS:\n"
        for f in self.fields.keys():
            s += "\t" + f + ": " + str(self.fields.get(f, self.earliest_version)) +"\n"
        s += "REVERSE POINTERS:\n"
        for (node, f, vers) in self.reverse_pointers:
            s += "    Version: " + str(vers) + ", node: " + str(node) + ", field " + f + "\n"
        for (node, f, vers, adding) in self.reverse_pointer_mods:
            s += "  " + "+" if adding else "-" + " Version: " + str(vers) + ", node: " + str(node) + ", field " + f + "\n"
        s += "MODS:\n"
        for (vers, f, val) in sorted(self.mods, key=lambda x: x[0]):
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
##        if (self.child and not version < self.child.earliest_version):
##            return self.child.get_field(name, version)
        self.mods = sorted(self.mods, key=lambda x: x[0])
        for mod in self.mods[::-1]:
            if mod[1] == name and not mod[0] > version:
                return mod[2]
        return self.fields.get(name)

    # modify a field value (add a mod if not full, split node if it is) right after the given version
    # returns the VersionPtr for the new version created by this modification
    # also puts the undo of this modification immediately after
    def set_field(self, name, value, version, version_name=""):
        if (version < self.earliest_version):
            raise Exception("Cannot set a field at a version (%s) earlier than a node's earliest version (%s)." % (version, self.earliest_version))
        old_value = self.get_field(name, version)
        done_version = self._set_field_helper(name, value, version)
        done_version.version_name = "(" + version_name
        undone_version = self._set_field_helper(name, old_value, done_version)
        undone_version.version_name = version_name + ")"
        self.parent.all_version_ptrs_ever.append(done_version)
        self.parent.all_version_ptrs_ever.append(undone_version)
        return done_version

    # PRIVATE METHODS

    # modify a field value (add a mod if not full, split node if it is) right after the given version
    # returns the VersionPtr for the new version created by this modification
    def _set_field_helper(self, name, value, version):
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
            old_value._remove_reverse_pointer(self, name, new_version)
        if type(value) is FPNode:
            value._add_reverse_pointer(self, name, new_version)

        return new_version

    # return a child object of the same type; overload in subclasses
    def _make_child(self, mid_version):
        return FPNode(self.name, self.parent, mid_version)

    # create two new nodes with the first and second half of mods, make them the children
    # then once they're set up, do a bunch of pointer chasing
    def _overflow(self):
        # amend old node to have children
        self.mods = sorted(self.mods, key=lambda x: x[0])
        mid_version = self.mods[len(self.mods)//2][0]
        rightchild = self._make_child(mid_version)
        rightchild.child = self.child
        self.child = rightchild

        # set values of child fields
        rightchild.fields = self.fields.copy()
        rightchild.mods = self.mods[len(self.mods)//2:]
        self.mods = self.mods[:len(self.mods)//2]
        for _, name, val in self.mods:  # mods in the older half applied to newer half
            rightchild.fields[name] = val

        # update reverse pointer stuff
        rightchild.reverse_pointers = self.reverse_pointers
        keep_revptr_adds = []
        for node, field, version in self.reverse_pointer_adds:
            if version < mid_version:
                rightchild.reverse_pointers.append((node, field, version))
                keep_revptr_adds.append((node, field, version))
            else:
                rightchild.reverse_pointer_adds.append((node, field, version))
        keep_revptr_deletes = []
        for delnode, delfield, delversion in self.reverse_pointer_deletes:
            if version < mid_version:
                rightchild.reverse_pointers = list(filter(rightchild.reverse_pointers, lambda (node, field, version): not (delnode == node and delfield == field and delversion > version)))
                keep_revptr_deletes.append((delnode, delfield, delversion))
            else:
                rightchild.reverse_pointer_deletes.append((delnode, delfield, delversion))
        self.reverse_pointer_adds = keep_revptr_adds
        self.reverse_pointer_deletes = keep_revptr_deletes

        # pointer chasing time!
        # go through every initial-field and mod, change revptrs
        for version, field_name, val in rightchild.mods:
            # directly change revptrs for mods
            if type(val) is FPNode or type(val) is FPRoot:
                val._update_reverse_pointers(self, rightchild, field_name, version)
        for field_name in rightchild.fields.keys():
            # use mods to add revptrs for newly created additional fields pointing into it from new child
            val = rightchild.fields[field_name]
            if type(val) is FPNode or type(val) is FPRoot:
                val._add_reverse_pointer(rightchild, field_name, mid_version)

        # then go through all the revptrs and update their things' forward pointers
        for from_node, field_name, version in rightchild.reverse_pointers:
            # use mods to add forward pointers after mid_version to rightchild instead of left child
            if (mid_version < from_node.earliest_version and from_node.fields[field_name] == self):
                # it should effectively point to rightchild all along
                from_node.fields[field_name] = rightchild
            else:
                from_node.set_field(field_name, rightchild, mid_version)
                
        for from_node, field_name, version, adding in rightchild.reverse_pointer_mods:
            if adding:
                from_node._update_forward_pointers(self, rightchild, field_name, version)
            # don't actually have to do anything for deletion I think?
        return


    # comparison function on mods (determine which is earlier version)
    def _compare_mods(self, mod1, mod2):
        return mod1[0] < mod2[0]

    # return a list of reverse pointers
    def _get_revptrs(self, version):
        revptrs = self.reverse_pointers
        self.reverse_pointer_mods = sorted(self.reverse_pointer_mods, key=lambda x: x[2])
        for (node, field, vers, adding) in self.reverse_pointer_mods:
            if vers > version:
                break
            if adding:
                revptrs.append((node, field, vers))
            else:
                revptrs = list(filter(revptrs, lambda (n, f, v): not (node == n and field == f)))
        revptrs = list(map(revptrs, lambda x: (x[0], x[1])))
        return revptrs

    # add reverse pointer, check if there are more than p of them
    def _add_reverse_pointer(self, from_node, field_name, version):
        self.reverse_pointer_mods.append((from_node, field_name, version, True))
        # assert len(revptrs) <= p  # removed for testing, TODO add back, also add something about not too many mods on revptrs
        return

    # remove reverse pointer
    def _remove_reverse_pointer(self, from_node, field_name, version):
        self.reverse_pointer_mods.append((from_node, field_name, version, False))
        return

    # manually replace pointers to go to newly created nodes and not reference the obsoletified ones
    def _update_reverse_pointers(self, old_node, new_node, field_name, version):
        revptrs_list = self._get_revptrs(version)
        
        for i in range(len(revptrs_list)):
            (node, name) = revptrs_list[i]
            if node == old_node:
                revptrs_list[i] = (new_node, name)
        return

    # manually replace pointers to go to newly created nodes and not reference the obsoletified ones
    def _update_forward_pointers(self, old_node, new_node, field_name, version):
        if version <= self.earliest_version and self.fields[field_name] == old_node:
            self.fields[field_name] = new_node
        self.mods = sorted(self.mods, key=lambda x: x[0])
        for i in range(len(self.mods)):
            vers, name, val = self.mods[i]
            if version == vers and field_name == name and val == old_node:
                self.mods[i] = vers, name, new_node
        return


class FPRoot(FPNode):
    def __init__(self, parent, version):
        super(FPRoot, self).__init__("__ROOT__", parent, version)
        self.version_ptrs = []

    def _make_child(self, mid_version):
        return FPRoot(self.parent, mid_version)

    def add_version_pointer(self, version):
        self.version_ptrs.append(version)

    def _overflow(self):
        super(FPRoot, self)._overflow()
        old_ptrs = []
        new_ptrs = []
        for version in self.version_ptrs:
            if version < self.child.earliest_version:
                old_ptrs.append(version)
            else:
                new_ptrs.append(version)
                version.root = self.child  # TODO verify that this is always an FPRoot object?
        self.version_ptrs = old_ptrs
        self.child.version_ptrs = new_ptrs
        return
            
        

    


