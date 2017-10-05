import unittest
from ordered_file_maintenance import *

class TestOrderedMaintenace(unittest.TestCase):

    def test_insert_into_empy_arr(self):
        arr = []
        insert(1, arr, 0)
        assert(read(arr, 0) == 1)

    def test_insert_into_empy_arr(self):
        pass


if __name__ == '__main__':
    unittest.main()
