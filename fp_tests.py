import unittest
from full_persistence import FPPM
from full_persistence import FPNode

class TestFullPersistence(unittest.TestCase):

    def test_init(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, 0)


    def test_single_link(self):
        # Initialize Fully Persitent Pointer Machine
        ffpm = FPPM()

        # Setup node0 and node1
        node0 = FPNode("n0", ffpm, ffpm.first_version)
        ffpm.first_version.root = node0
        node1 = FPNode("n1", ffpm, ffpm.first_version)
        node2 = FPNode("n2", ffpm, ffpm.first_version)

        # Set node0 to point to node1 at the first version
        v1 = node0.set_field("p0", node1, ffpm.first_version)
        n1 = node0.get_field("p0", v1)
        assert(node1 == n1)

        # Set node0 to point to node1 at the first version again
        v2 = node1.set_field("p0", node1, v1)
        n2 = node0.get_field("p0", v2)
        assert(node1 == n2)

        # Set the value of node1 to 5
        v3 = node1.set_field("val0", 5, v2)
        val1 = node1.get_field("val0", v3)
        assert(val1 == 5)

        # Set the value of node1 now to 10
        v4 = node1.set_field("val0", 10, v3)
        val2 = node1.get_field("val0", v4)
        assert(val2 == 10)

        # Read the previous version
        val3 = node1.get_field("val0", v3)
        assert(val3 == 5)

        # Force an overflow
        for _ in range(20):
            _version = node0.set_field("val0", node2, v1)

        # Check that one of the previous sets still points to node1
        n3 = node0.get_field("p0", v1)
        assert(n3 == n1)

    """
    def test_cycle(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, ffpm.first_version)
        ffpm.first_version.root = node0
        node1 = FPNode("n1", ffpm, ffpm.first_version)
        v1 = node0.set_field("p0", node1, ffpm.first_version)
        n1 = node0.get_field("p0", ffpm.first_version)
    """


if __name__ == '__main__':
    unittest.main()
