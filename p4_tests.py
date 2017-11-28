import unittest
import random
from partial_persistence import Node
from partial_persistence import PartiallyPersistentPointerPackage as PPPP
from partial_persistence import p

class TestPartialPersistence(unittest.TestCase):

    def setUp(self):
        self.P4 = PPPP()

    """
TO TEST:
init / __str__
    node starts empty
    parent gets node
    named correctly (using __str__)
formatted
    prints reasonable things in a couple cases? (didn't implement this b/c annoying)
get_field
    current version, old version, too-old version
    get from starter node with no mods, starter node with mods,
        node freshly copied, node copied and with mods, node copied > 1 time
set_field
    value = None, integer, boolean, string, other node object
    set on starter node with no mods, starter node with mods,
        node freshly copied, node copied and with mods, node copied > 1 time
    set to point at itself
    """

    def test_init_and_str(self):
        n0 = Node("n0", self.P4)
        self.assertEqual(str(n0), "n0")
        self.assertEqual(self.P4.get_nodes(), [n0])
        self.assertEqual(n0.parent, self.P4)
        self.assertEqual(n0.mods, [])
        self.assertEqual(n0.is_active, True)

    def test_get_set_field_current(self):
        n0 = Node("n0", self.P4)
        n0 = n0.set_field("val", 5)
        self.assertEqual(n0.get_field("val"), 5)

    def test_get_set_field_past(self):
        n0 = Node("n0", self.P4)
        n0 = n0.set_field("val", 5)
        vers = self.P4.version
        n0 = n0.set_field("val", "five")
        self.assertEqual(n0.get_field("val"), "five")
        self.assertEqual(n0.get_field("val", vers), 5)

    def test_get_set_field_nonexistent(self):
        n0 = Node("n0", self.P4)
        n0 = n0.set_field("val", True)
        self.assertEqual(n0.get_field("val", 0), None)
        self.assertEqual(n0.get_field("value"), None)
        self.assertEqual(n0.get_field("val"), True)

    def test_get_set_overflow(self):
        # overflow nodes with and without mods
        n0 = Node("n0", self.P4)
        n0 = n0.set_field("val", -1)
        n0 = n0.set_field("truth", True)
        for i in range(2*p-2):
            n0 = n0.set_field("val", i)
        self.assertEqual(n0.get_field("val"), 2*p-3)
        for i in range(2*p-2, 2*p):
            n0 = n0.set_field("val", i)
        self.assertEqual(n0.get_field("val"), 2*p-1)
        self.assertEqual(len(n0.mods), 2)
        self.assertEqual(n0.get_field("val", 0), 2*p-3)

    def test_get_set_overflow_multiple(self):
        n0 = Node("n0", self.P4)
        for i in range(4*p+1):
            n0 = n0.set_field("val", i)
        self.assertEqual(n0.get_field("val"), 4*p)
        self.assertEqual(len(n0.mods), 1)

    def test_get_set_node_fields(self):
        # set, unset, check all the pointer chasing
        n0 = Node("n0", self.P4)
        n1 = Node("n1", self.P4)
        n2 = Node("n2", self.P4)
        n0 = n0.set_field("val", -1)
        n0 = n0.set_field("ptr0", n1)
        n1 = n1.set_field("ptr1", n2)
        n2 = n2.set_field("ptr2", n1)
        self.assertEqual(n1.get_field("ptr1"), n2)
        self.assertEqual(n0._get_revptrs(), [])
        self.assertEqual(n1._get_revptrs(), [(n0, "ptr0"), (n2, "ptr2")])
        self.assertEqual(n2._get_revptrs(), [(n1, "ptr1")])

    def test_get_set_node_fields_with_overflow(self):
        n0 = Node("n0", self.P4)
        n1 = Node("n1", self.P4)
        n2 = Node("n2", self.P4)
        for i in range(2*p+1):
            n0 = n0.set_field("val", i)
        n0 = n0.set_field("ptr0", n1)
        n1 = n1.set_field("ptr1", n2)
        n2 = n2.set_field("ptr2", n1)
        self.assertEqual(n1.get_field("ptr1"), n2)
        self.assertEqual(n0._get_revptrs(), [])
        self.assertEqual(n1._get_revptrs(), [(n0, "ptr0"), (n2, "ptr2")])
        self.assertEqual(n2._get_revptrs(), [(n1, "ptr1")])
        self.assertEqual(len(n0.mods), 2)

    def test_get_set_node_self_pointing(self):
        n0 = Node("n0", self.P4)
        n1 = Node("n1", self.P4)
        n0 = n0.set_field("ptr0", n0)
        self.assertEqual(n0.get_field("ptr0"), n0)
        n0 = n0.set_field("ptr1", n1)
        for i in range(2*p+1):
            n0 = n0.set_field("val", i)
        self.assertEqual(n0.get_field("ptr0"), n0)
        self.assertEqual(n0.get_field("ptr1"), n1)
        self.assertEqual(len(n0.mods), 4)

    def test_cycle_of_death(self):
        n0 = Node("n0", self.P4)
        n1 = Node("n1", self.P4)
        for i in range(p):
            n0 = n0.set_field("ptr"+str(i), n1)
            n1 = n1.set_field("ptr"+str(i), n0)
            print(n0.formatted())
        self.assertEqual(n0.get_field("ptr0"), n1)

if __name__ == '__main__':
    unittest.main()
