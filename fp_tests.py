import unittest
from full_persistence import FPPM
from full_persistence import FPNode

class TestFullPersistence(unittest.TestCase):

    def test_init(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, 0)


    def test_linked_list(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, 0)
        node1 = FPNode("n1", ffpm, 0)
        v1 = node0.set_field("p0", node1, 0)
        n1 = node0.get_field("p0", 0)
        assert(node1 == n1)
        node1.set_field("p0", node1, 0)
        n1 = node0.get_field("p0", 0)
        assert(node1 == n1)

if __name__ == '__main__':
    unittest.main()
