# jamb, rusch 6.851 fall 2017

from full_persistence import FPPM, FPNode


class BSTNode():
    def __init__(self, val, parent, version):
        if parent is None:
            self.fppm = FPPM()
            self.node = self.fppm.get_root(self.fppm.first_version)
        else:
            self.fppm = parent.fppm
            self.node = FPNode("", self.fppm, version)
        self.node.fields["parent"] = parent
        self.node.fields["val"] = val
        self.node.fields["left"] = None
        self.node.fields["right"] = None
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



class FPBST():
    '''Fully persistent binary search tree.'''

    def __init__(self, comparator=lambda x, y: x<y):
        self.root = BSTNode("ROOT", None, None)  # ROOT node, tree actually starts at its right child
        self.comparator = comparator
        self.earliest_version = self.root.earliest_version

    # return a new version with the value inserted
    def insert(self, val, version):
        parent = self.root
        node = parent.get_right(version)
        is_right_child = True
        while (node is not None):
            parent = node
            if self.comparator(val, node.get_value(version)):
                is_right_child = True
                node = node.get_right(version)
            else:
                is_right_child = False
                node = node.get_left(version)
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
            if node.get_value(version) == val:
                # TODO this is the part where it should return a thing
                # BST deletion is hard
                pass
            parent = node
            if self.comparator(val, node.get_value(version)):
                is_right_child = True
                node = node.get_right(version)
            else:
                is_right_child = False
                node = node.get_left(version)
        return version
            

    # return the node of the value
    def find(self, val, version):
        node = self.root.get_right(version)
        while (node is not None):
            if node.get_value(version) == val:
                return node
            if self.comparator(val, node.get_value(version)):
                node = node.get_right(version)
            else:
                node = node.get_left(version)
        return None

    def format(self, version):
        return self._format_helper(self.root, version, 0)

    def _format_helper(self, node, version, indent):
        s = "\t"*indent + str(node.get_value(version)) + "\n"
        l, r = node.get_left(version), node.get_right(version)
        if l is not None:
            s += self._format_helper(l, version, indent+1) + "\n"
        if r is not None:
            s += self._format_helper(r, version, indent+1) + "\n"
        return s
        


tree = FPBST()
v = tree.earliest_version
v = tree.insert(3, v)
v = tree.insert(5, v)
v2 = tree.insert(6, v)
v2 = tree.insert(2, v2)
##print(tree.format(v))
##print(tree.format(v2))
##print(tree.find(3, v2))
