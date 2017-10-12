import unittest
import random
from ordered_file_maintenance import OrderedFile

class TestOrderedMaintenace(unittest.TestCase):

    def setUp(self):
        self.arr = OrderedFile()

    def test_collapse(self):
        self.arr += [1,2, None, 3, None, 4]
        print(self.arr)
        self.arr._collapse(0, 8)
        print(self.arr)
        assert(self.arr == [1, 2, 3, 4, None, None, None, None])

    def test_collapse_partial_range1(self):
        self.arr += [1,2, None, 3, None, 4,6,7]
        self.arr._collapse(0, 5)
        assert(self.arr == [1, 2, None, None, None, 3, None, 4, 6, 7])

    def test_collapse_partial_range2(self):
        self.arr += [1,2, None, 3, None, 4,6,7]
        self.arr._collapse(5, 10)
        assert(self.arr == [None, None, 1, 2, None, 3, 4, 6, 7, None])

    def test_collapse_only_nones(self):
        self.arr += [1,2, None, 3, None, 4]
        self.arr._collapse(0, 1)
        assert(self.arr == [None, None, 1, 2, None, 3, None, 4])

    def test_collapse_insert_at_empty_slot(self):
        self.arr += [1,2, None, 3, None, 4,6,7]
        self.arr._collapse(1, 7, elem=100, pos=4)
        assert(self.arr == [None, 1, 2, 100, 3, None, None, 4, 6, 7])

    def test_collapse_insert_at_used_slot(self):
        self.arr += [1,2, None, 3, None, 4,6,7]
        self.arr._collapse(5, 10, elem=100, pos=8)
        assert(self.arr == [None, None, 1, 2, None, 3, 4, 100, 6, 7])

    def test_insert_into_empy_arr(self):
        self.arr.insert(1, 0)
        assert(self.arr.read(0) == 1)

    def test_insert_many(self):
        for i in range(int(1e4)):
            self.arr.insert(i, i)

        for i in range(int(1e4)):
            assert(self.arr.read(i) == i)

    def test_insert_interleave(self):
        for i in range(0, int(1e3), 2):
            self.arr.insert(i, i)
        for i in range(1, int(1e3), 2):
            self.arr.insert(i, i)
        for i in range(int(1e3)):
            assert(self.arr.read(i) == i)

    def test_insert_backwards(self):
        for i in range(int(1e3), 0, -1):
            self.arr.insert(i, i)
        for i in range(int(1e3)):
            assert(self.arr.read(i) == i)

    def test_insert_backwards_interleaved(self):
        for i in range(int(1e3), 1, -2):
            self.arr.insert(i, i)
        for i in range(int(1e3) - 1, 0, -2):
            self.arr.insert(i, i)
        for i in range(int(1e3)):
            assert(self.arr.read(i) == i)

    def test_insert_shuffled(self):
        order = range(int(1e3))
        random.shuffle(order)
        for i in order:
            self.arr.insert(i, i)
        for i in range(int(1e3)):
            assert(self.arr.read(i) == i)

if __name__ == '__main__':
    test_suite = TestOrderedMaintenace
    unittest.main()
