import unittest
import random
from ordered_file_maintenance import *

class TestOrderedMaintenace(unittest.TestCase):

    def test_insert_into_empy_arr(self):
        arr = []
        insert(1, arr, 0)
        assert(read(arr, 0) == 1)

    def test_insert_many(self):
        arr = []
        for i in range(int(1e4)):
            insert(i, arr, i)

        for i in range(int(1e4)):
            assert(read(arr, i) == i)

    def test_insert_interleave(self):
        arr = []
        for i in range(0, int(1e3), 2):
            insert(i, arr, i)
        for i in range(1, int(1e3), 2):
            insert(i, arr, i)
        for i in range(int(1e3)):
            assert(read(arr, i) == i)

    def test_insert_backwards(self):
        arr = []
        for i in range(int(1e3), 0, -1):
            insert(i, arr, i)
        for i in range(int(1e3)):
            assert(read(arr, i) == i)

    def test_insert_backwards_interleaved(self):
        arr = []
        for i in range(int(1e3), 1, -2):
            insert(i, arr, i)
        for i in range(int(1e3) - 1, 0, -2):
            insert(i, arr, i)
        for i in range(int(1e3)):
            assert(read(arr, i) == i)

    def test_insert_shuffled(self):
        arr = []
        order = range(int(1e3))
        random.shuffle(order)
        for i in order:
            insert(i, arr, i)
        for i in range(int(1e3)):
            assert(read(arr, i) == i)

if __name__ == '__main__':
    unittest.main()
