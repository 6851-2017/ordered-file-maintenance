# jamb, rusch 6.851 fall 2017

from full_persistence import FPPM
from full persistence import FPNode


class FPBST():
    '''Fully persistent binary search tree.'''

    class BSTNode():
        def __init__(self, val, parent, version):
            if parent is None:
                self.fppm = FPPM()
                self.node = self.fppm.get_root(self.fppm.first_version)
            else:
                self.fppm = parent.fppm
                self.node = FPNode("", fppm, version)
            self.node.set_field("parent", parent)
            self.node.set_field("val", val)
            self.node.set_field("left", None)
            self.node.set_field("right", None)
            self.earliest_version = self.node.earliest_version

        def set_right(self, right, version):
            return self.node.set_field("right", right, version)

        def set_left(self, left, version):
            return self.node.set_field("left", left, version)

        def set_parent(self, parent, version):
            return self.node.set_field("parent", parent, version)

        def get_right(self, version):
            return self.node.get_field("right", version)

        def get_left(self, version):
            return self.node.get_field("left", version)

        def get_parent(self, version):
            return self.node.get_field("parent", version)

        def get_value(self, version):
            return self.node.get_field("val", version)

        
    def __init__(self, val, comparator=lambda x, y: x<y):
        self.root = BSTNode("ROOT", None, None)  # ROOT node, tree actually starts at its right child
        self.comparator = comparator

    # return a new version with the value inserted
    def insert(self, val, version):
        parent = self.root
        node = parent.get_right()
        is_right_child = True
        while (node is not None):
            parent = node
            if comparator(val, node.get_value()):
                is_right_child = True
                node = node.get_right()
            else:
                is_right_child = False
                node = node.get_left()
        new_node = BSTNode(val, parent, version)
        if is_right_child:
            new_version = parent.set_right(new_node, version)
        else:
            new_version = parent.set_left(new_node, version)
        return new_version
            

    # return a new version with the value deleted (if it existed)
    def delete(self, val, version):
        parent = self.root
        node = parent.get_right()
        is_right_child = True
        
        while (node is not None):
            if node.get_value() == val:
                # TODO this is the part where it should return a thing
                # BST deletion is hard
                    
            parent = node
            if comparator(val, node.get_value()):
                is_right_child = True
                node = node.get_right()
            else:
                is_right_child = False
                node = node.get_left()
        return version
            

    # return the node of the value
    def find(self, val, version):
        node = self.root.get_right()
        while (node is not None):
            if node.get_value == val:
                return node
            if comparator(val, node.get_value()):
                node = node.get_right()
            else:
                node = node.get_left()
        return None
