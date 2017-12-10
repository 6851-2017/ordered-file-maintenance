import unittest
from full_persistence import FPPM
from full_persistence import FPNode

# TODO
# test roots overflowing
# test multiple fields

# Hack to give each thing unique name
inc = 0
class TestFullPersistence(unittest.TestCase):

    def test_init(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, 0)


    def test_single_link(self):
        # Initialize Fully Persitent Pointer Machine
        ffpm = FPPM()

        # Setup node0 and node1
        node0 = FPNode("n0", ffpm, ffpm.first_version)
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
            _version = node0.set_field("p0", node2, v1)

        # Overflow from successive versions
        version = v1
        for _ in range(20):
            version = node0.set_field("p0", node2, version)

        # Check that one of the previous sets still points to node1
        n3 = node0.get_field("p0", v1)
        assert(n3 == n1)

        # Change something after an early version
        v5 = node0.set_field("p0", node1, v1)
        v6 = node0.set_field("val0", 5, v5)
        v7 = node0.set_field("p0", node1, v5)

        n4 = node0.get_field("p0", v5)

        self.assertEqual(n4, node1)

    def test_cycle(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, ffpm.first_version)
        node1 = FPNode("n1", ffpm, ffpm.first_version)
        node2 = FPNode("n2", ffpm, ffpm.first_version)

        # Create a cycle
        v1 = node0.set_field("p0", node1, ffpm.first_version)
        v2 = node1.set_field("p0", node0, ffpm.first_version)

        # Test that nodes along cycle are valid
        n1 = node0.get_field("p0", v1)
        n0 = n1.get_field("p0", v2)
        n1_2 = n0.get_field("p0", v1)
        self.assertEqual(n0, node0)
        self.assertEqual(n1_2, node1)

        # Insert node into cycle
        v3 = node0.set_field("p0", node2, v1)
        v4 = node2.set_field("p0", node1, ffpm.first_version)

    def test_tree(self):
        ffpm = FPPM()
        root = FPNode("root", ffpm, ffpm.first_version)

        def recurse(node, d):
            global inc
            inc += 1
            if d > 4:
                return None
            else:
                v = ffpm.first_version
                left = FPNode("left{}".format(inc), ffpm, v)
                v1 = node.set_field("left", left, v)
                recurse(left, d + 1)

                right = FPNode("right{}".format(inc), ffpm, v)
                v2 = node.set_field("right", right, v)
                recurse(right, d + 1)

        recurse(root, 0)

    def test_self_pointing_overflow(self):
        ffpm = FPPM()
        node0 = FPNode("n0", ffpm, ffpm.first_version)

        # Point to self three times to fill up mods slots
        v1 = node0.set_field("p0", node0, ffpm.first_version)
        v2 = node0.set_field("p1", node0, ffpm.first_version)
        v3 = node0.set_field("p2", node0, ffpm.first_version)

        n1 = node0.get_field("p0", v1)
        n2 = node0.get_field("p1", v2)
        n3 = node0.get_field("p2", v3)

        self.assertEqual(n1, node0)
        self.assertEqual(n2, node0)
        self.assertEqual(n3, node0)

        # One more change should overflow
        v4 = node0.set_field("p0", node0, v3)
        n4 = node0.get_field("p2", v3)

        self.assertEqual(n4, node0)

    def test_set_many_values(self):
        ffpm = FPPM()
        root = ffpm.get_root(ffpm.first_version)
        node0 = FPNode("n0", ffpm, ffpm.first_version)
        v0 = root.set_field("node", node0, ffpm.first_version, "v")
        #print(root.formatted())
        #print("v0=",v0)

        for i in range(30):
            n0 = ffpm.get_root(v0).get_field("node", v0)
            v1 = n0.set_field("val0", i, v0, "%s" % i)
            #print(n0.formatted())

        version = v0
        versions = []
        for i in range(30):
            n0 = ffpm.get_root(version).get_field("node", version)
            version = n0.set_field("val0", i, version, "%s" % i)
            #print(n0.formatted())
            versions.append((i, version))
#        print(ffpm.all_version_ptrs_ever)

        for i, version in versions:
            n0 = ffpm.get_root(version).get_field("node", version)
            val = n0.get_field("val0", version)
#            self.assertEqual(i, val)
            print(i, val)


    def test_set_not_as_many_values(self):
        ffpm = FPPM()
        root = ffpm.get_root(ffpm.first_version)
        node0 = FPNode("n0", ffpm, ffpm.first_version)
        v0 = root.set_field("node", node0, ffpm.first_version, "v")
        #print(root.formatted())
        #print("v0=",v0)

        for i in range(5):
            n0 = ffpm.get_root(v0).get_field("node", v0)
            v1 = n0.set_field("val0", 0, v0, "%s" % i)

        version = v0
        versions = []
        for i in range(5):
            n0 = ffpm.get_root(version).get_field("node", version)
            version = n0.set_field("val0", i, version, "%s" % i)
            versions.append((i, version))

        for i, version in versions:
            n0 = ffpm.get_root(version).get_field("node", version)
            val = n0.get_field("val0", version)
            self.assertEqual(i, val)
#            print(i, val)


    def test_above_with_only_root(self):
        ffpm = FPPM()
        root = ffpm.get_root(ffpm.first_version)
        v0 = root.set_field("val0", 0, ffpm.first_version, "val0")

        for i in range(30):
            n0 = ffpm.get_root(v0)
            v1 = n0.set_field("val0", i, v0, "%s" % i)

        version = v0
        versions = []
        for i in range(30):
            n0 = ffpm.get_root(version)
            version = n0.set_field("val0", i, version, "%s" % i)
            versions.append((i, version))
        for i, version in versions:
            n0 = ffpm.get_root(version)
            val = n0.get_field("val0", version)
            self.assertEqual(i, val)
#            print(i, val)

    def test_set_with_root(self):
        ffpm = FPPM()
        root = ffpm.get_root(ffpm.first_version)
        node0 = FPNode("n0", ffpm, ffpm.first_version)
        v0 = root.set_field("node", node0, ffpm.first_version, "v")
        v1 = root.set_field("val", 6, v0)
        self.assertEqual(ffpm.get_root(v1).get_field("node", v1), node0)
        v2 = node0.set_field("val", 7, v0)       
        self.assertEqual(ffpm.get_root(v2).get_field("node", v2).get_field("val", v2), 7)
        v3 = node0.set_field("val", 8, v0)
        self.assertEqual(ffpm.get_root(v3).get_field("node", v3).get_field("val", v3), 8)
        self.assertEqual(ffpm.get_root(v2).get_field("node", v2).get_field("val", v2), 7)



if __name__ == '__main__':
    unittest.main()
