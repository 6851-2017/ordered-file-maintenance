import unittest
import random
from ordered_file_maintenance import OrderedFile

class TestOrderedMaintenace(unittest.TestCase):

    def setUp(self):
        self.arr = OrderedFile()

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
    unittest.main()
