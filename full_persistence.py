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

    # returns the root FPNode at the given VersionPtr
    def get_root(self, version):
        return version.get_root()


class Mod():
    def __init__(self, do_version, undo_version, node, field, value, old_value):
        self.do_version = do_version
        self.undo_version = undo_version
        self.node = node
        self.field = field
        self.value = value
        self.old_value = old_value

    def set_value(self, value):
        self.value = value

    def update_node(self, old_node, new_node, version):
        pass  # TODO implement, crap how???


class REVPTR():
    def __init__(self, mod):
        self.mod = mod


class DO():
    def __init__(self, mod):
        self.mod = mod

    def get_version(self):
        return self.mod.do_version

    def get_value(self):
        return self.mod.value

    def get_field(self):
        return self.mod.field


class UNDO():
    def __init__(self, mod):
        self.mod = mod

    def get_version(self):
        return self.mod.undo_version

    def get_value(self):
        return self.mod.old_value

    def get_field(self):
        return self.mod.field
        

class FPNode():
    '''A fully persistent DS node: stores fields, reverse pointers, mods.'''

    # initialize empty node with String name, FPPM parent
    def __init__(self, name, parent, version):
        self.name = name
        self.parent = parent  # the FPPM that this node is in, for version tracking
        self.earliest_version = version
        self.fields = {}
        self.reverse_pointers = []  # list of REVPTR objects
        self.changes = []  # list of DO and UNDO objects
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
        for rp in self.reverse_pointers:
            s += str(rp) + "\n"
        s += "MODS:\n"
        for change in sorted(self.changes, key=lambda x: x.get_version()):
            vers, undovers, f, val, oldval = change.mod.do_version, change.mod.undo_version, change.mod.field, change.mod.value, change.mod.old_value
            s += "\tVersion " + str(vers) + " until " + str(undovers) + ", field " + f + ", value " + str(val) + ", oldvalue " + str(oldval) + "\n"
        return s

    # retrieve the value of the field at the given VersionPtr
    # returns None if it's not in the fields or mods
    # if version is older than anything in this node, throws an error
    def get_field(self, field, version):
        if (version < self.earliest_version):
            raise Exception("Cannot get a field from a node at a version earlier than its earliest version.")
        if (self.child and not version < self.child.earliest_version):
            raise Exception("Should have called get_field on child instead.")
        self.changes = sorted(self.changes, key=lambda x: x.get_version())
        for change in self.changes[::-1]:
            if change.get_field() == field and change.get_version() <= version:
                return change.get_value()
        return self.fields.get(field)

    # modify a field value (add a mod if not full, split node if it is) right after the given version
    # returns the VersionPtr for the new version created by this modification
    # also puts the undo of this modification immediately after
    def set_field(self, field, value, version, version_name=""):
        # check for an overflow in progress
        if len(self.changes) >= 2*(d+p+1):
            if self.child is None:
                raise Exception("Node has overflowed but doesn't have children to move to.")
            if version >= self.child.earliest_version:
                return self.child._set_field_helper(field, value, version)
        if (version < self.earliest_version):
            raise Exception("Cannot set a field at a version (%s) earlier than a node's earliest version (%s)." % (version, self.earliest_version))

        # create versions for the DO / UNDO
        do_version = self.parent.versioner.insert_after(version)
        do_version.version_name = "(" + version_name
        undo_version = self.parent.versioner.insert_after(do_version)
        undo_version.version_name = version_name + ")"
        
        old_value = self.get_field(field, version)
        mod = Mod(do_version, undo_version, self, field, value, old_value)
        self.changes.append(DO(mod))
        self.changes.append(UNDO(mod))

        # overflow if needed
        if len(self.changes) >= 2*(d+p+1):
            self._overflow()

        # update reverse_pointers
        if type(old_value) is FPNode:
            pass  # TODO we should probably have some way to temporarily remove the revptr for it
                    # during the duration of the new value so we don't have too many revptrs.
                    # but I don't see how to do this, and this should work
        if type(value) is FPNode:
            value.reverse_pointers.append(REVPTR(mod))

        return do_version
    

    # PRIVATE METHODS

    # return a child object of the same type; overload in subclasses
    def _make_child(self, mid_version):
        return FPNode(self.name, self.parent, mid_version)

    # create two new nodes with the first and second half of mods, make them the children
    # then once they're set up, do a bunch of pointer chasing
    def _overflow(self):
        # amend old node to have children
        self.changes = sorted(self.changes, key=lambda x: x.get_version())
        mid_index = len(self.changes)//2
        mid_version = self.changes[mid_index].get_version()
        child = self._make_child(mid_version)
        child.child = self.child  # the thing that was formerly the child gets shifted down one in the linked-list-ish thing
        self.child = child

        # set values of child fields
        child.fields = self.fields.copy()
        child.changes = self.changes[mid_index:]
        self.changes = self.changes[:mid_index]
        for change in self.changes:  # mods in the older half applied to newer half
            child.fields[change.get_field()] = change.get_value()

        # update reverse pointers of self and child
        old_revptrs = []
        new_revptrs = []
        for rp in self.reverse_pointers:
            if rp.mod.do_version < mid_version:
                old_revptrs.append(rp)
            if rp.mod.undo_version >= mid_version:
                new_revptrs.append(rp)
        self.reverse_pointers = old_revptrs
        child.reverse_pointers = new_revptrs

        # go through revptrs and change their mods' node to be child and not self
        for revptr in child.reverse_pointers:
            revptr.mod.update_node(self, child, mid_version)
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
                version.root = self.child
        self.version_ptrs = old_ptrs
        self.child.version_ptrs = new_ptrs
        return
            
        

    


