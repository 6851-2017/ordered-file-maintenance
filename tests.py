import unittest
import random
from ordered_file_maintenance import OrderedFile

class TestOrderedMaintenance(unittest.TestCase):

    def setUp(self):
        self.arr = OrderedFile()

    def test_collapse(self):
        self.arr += [1,2, None, None, None, 4]
        collapsed = self.arr._collapse(0, 8, 3, 4)
        self.assertEqual(collapsed, [1, 2, 3, 4, None, None, None, None])

    def test_collapse_partial_range(self):
        print(self.arr)
        self.arr += [1,2, None, None, None, 4,6,7]
        print(self.arr)
        collapsed = self.arr._collapse(0, 5, 3, 4)
        print(self.arr)
        assert(collapsed == [1, 2, 3, 4, None, None, None, None])

    def test_collapse_partial_range(self):
        self.arr += [1,2, None, None, None, 4]
        print(self.arr)
        self.arr._collapse(0, 8, 3, 3)
        print(self.arr)
        assert(self.arr.read(0) == 1)

    def test_insert_into_empty_arr(self):
        self.arr.insert(1, 0)
        assert(self.arr.read(0) == 1)

    def test_insert_many(self):
        for i in range(int(1e4)):
            self.arr.insert(i, i)

        for i in range(int(1e4)):
            assert(self.arr.read(i) == i)

    def test_insert_interleave(self):
        self.arr += [None]*int(1e3)
        for i in range(0, int(1e3), 2):
            self.arr.insert(i, i)
        for i in range(1, int(1e3), 2):
            self.arr.insert(i, i)
        for i in range(int(1e3)):
            assert(self.arr.read(i) == i)

    def test_insert_backwards(self):
        self.arr += [None]*int(1e3)
        for i in range(int(1e3), 0, -1):
            self.arr.insert(i, i)
        for i in range(int(1e3)):
            assert(self.arr.read(i) == i)

    def test_insert_backwards_interleaved(self):
        self.arr += [None]*int(1e3)
        for i in range(int(1e3), 1, -2):
            self.arr.insert(i, i)
        for i in range(int(1e3) - 1, 0, -2):
            self.arr.insert(i, i)
        for i in range(int(1e3)):
            assert(self.arr.read(i) == i)

    def test_insert_shuffled(self):
        self.arr += [None]*int(1e3)
        order = list(range(int(1e3)))
        random.shuffle(order)
        for i in order:
            self.arr.insert(i, i)
        for i in range(int(1e3)):
            assert(self.arr.read(i) == i)

if __name__ == '__main__':
    test_suite = TestOrderedMaintenance
    unittest.main()
