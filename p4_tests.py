import unittest
import random
from partial_persistence import Node
from partial_persistence import PartiallyPersistentPointerPackage as PPPP

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



    """

    def test_init_and_str(self):
        n0 = Node("n0", self.P4)
        self.assertEqual(str(n0), "n0")
        self.assertEqual(self.P4.get_nodes(), [n0])
        self.assertEqual(n0.parent, self.P4)
        self.assertEqual(n0.fields, {"__REVERSE_PTRS__": []})
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


    # TODO: field that points to other node object; overflow nodes with and without mods; multi overflows
    def test_get_set_overflow(self):
        pass

    def test_get_set_overflow_multiple(self):
        pass

    def test_get_set_node_fields(self):
        # set, unset, check all the pointer chasing
        pass

    def test_get_set_node_fields_with_overflow(self):
        pass


if __name__ == '__main__':
    test_suite = TestPartialPersistence
    unittest.main()
