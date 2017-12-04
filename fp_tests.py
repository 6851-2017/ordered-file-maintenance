import unittest
from full_persistence import FPPM
from full_persistence import FPNode

class TestFullPersistence(unittest.TestCase):

    def test_init(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, 0)


    def test_linked_list(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, ffpm.first_version)
        ffpm.first_version.root = node0
        node1 = FPNode("n1", ffpm, ffpm.first_version)
        v1 = node0.set_field("p0", node1, ffpm.first_version)
        n1 = node0.get_field("p0", v1)
        assert(node1 == n1)
        v2 = node1.set_field("p0", node1, v1)
        n1 = node0.get_field("p0", v2)
        assert(node1 == n1)

if __name__ == '__main__':
    unittest.main()
