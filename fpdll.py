# jamb, rusch 6.851 fall 2017

from full_persistence import FPPM, FPNode, Field


class DLLNode():
    def __init__(self, val, parent, child, version):
        if parent is None:
            self.fppm = FPPM()
            self.node = self.fppm.get_root(self.fppm.first_version)
        else:
            self.fppm = parent.fppm
            self.node = FPNode("", self.fppm, version)
        self.node.fields["parent"] = Field(self.node, parent)
        self.node.fields["val"] = Field(self.node, val)
        self.node.fields["child"] = Field(self.node, child)
        self.earliest_version = self.node.earliest_version

    def set_child(self, right, version):
        return self.node.set_field("child", right, version)

    def set_parent(self, parent, version):
        return self.node.set_field("parent", parent, version)

    def get_child(self, version):
        return self.node.get_field("child", version)

    def get_parent(self, version):
        return self.node.get_field("parent", version)

    def get_value(self, version):
        return self.node.get_field("val", version)



class FPDLL():
    '''Fully persistent doubly linked list.'''

    def __init__(self, first_val, comparator=lambda x, y: x<y):
        first_node = DLLNode(first_val, None, None, None) # have to start with something
        self.comparator = comparator
        self.earliest_version = first_node.earliest_version
        self.first = first_node
        self.last = first_node

    def get_first(self):
        return self.first

    # return a new version with the value inserted after the given DLLNode
    def insert_after(self, node, val, version):
        child = node.get_child(version)
        new_node = DLLNode(val, node, child, version)
        new_version = node.set_child(new_node, version)
        new_version = child.set_parent(new_node, new_version) if child else new_version
        return new_version

    # return a new version with the value inserted before the given DLLNode
    def insert_before(self, node, val, version):
        parent = node.get_parent(version)
        new_node = DLLNode(val, parent, node, version)
        new_version = parent.set_child(new_node, version) if parent else version
        new_version = node.set_parent(new_node, new_version)
        return new_version

    # return a new version with the given node deleted
    def delete(self, node, version):
        parent = node.get_parent(version)
        child = node.get_child(version)
        new_version = parent.set_child(child, version) if parent else version
        new_version = child.set_parent(parent, new_version) if child else new_version
        return new_version

    def format(self, version):
        s = "DLL"
        node = self.first
        while (node is not None):
            s += " - " + str(node.get_value(version))
            node = node.get_child(version)
        return s


dll = FPDLL(3)
node = dll.get_first()
vers = dll.earliest_version
vers = dll.insert_after(node, 4, vers)
node = dll.get_first().get_child(vers)
vers = dll.insert_after(node, 5, vers)
print(dll.format(vers))

        
