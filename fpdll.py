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

    def __init__(self, comparator=lambda x, y: x<y):
        self.root = BSTNode("ROOT", None, None, None)  # ROOT node, list actually starts at its child
        self.comparator = comparator
        self.earliest_version = self.root.earliest_version
        self.first = self.root
        self.last = self.root

    def get_first(self):
        return self.first

    def get_last(self):
        return self.last

    # return a new version with the value inserted after the given DLLNode
    def insert_after(self, node, val, version):
        child = node.get_child(version)
        new_node = DLLNode(val, node, child, version)
        new_version = node.set_child(new_node, version)
        new_version = child.set_parent(new_node, new_version)
        return new_version

    # return a new version with the value inserted before the given DLLNode
    def insert_before(self, node, val, version):
        parent = node.get_parent(version)
        new_node = DLLNode(val, parent, node, version)
        new_version = parent.set_child(new_node, version)
        new_version = node.set_parent(new_node, new_version)
        return new_version

    # return a new version with the value deleted (if it existed)
    def delete(self, node, version):
        parent = node.get_parent(version)
        child = node.get_child(version)
        new_version = parent.set_child(child, version)
        new_version = child.set_parent(parent, new_version)
        return new_version
        
