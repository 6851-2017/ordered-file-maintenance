# jamb, rusch 2017


import unittest
import random
from ordered_file_maintenance import OrderedFile, FilePointer

class TestFilePointer(unittest.TestCase):

    def setUp(self):
        self.file = FilePointer()

    """
    TO TEST:
    read_at_finger
        one element, many elements
    increment_finger
        nothing after, one thing after, many things after
    decrement_finger
        nothing before, one thing before, many things before
    insert_after_finger
        finger at beginning, middle, end of array
    """

    def test_insert_to_empty(self):
        self.file.insert_after_finger(1)
        self.assertEqual(self.file.read_at_finger(), 1)

    def test_insert_more(self):
        for i in range(20):
            self.file.insert_after_finger(i)
            self.assertEqual(self.file.read_at_finger(), i)

    def test_incr_decr(self):
        for i in range(20):
            self.file.insert_after_finger(i)
            self.assertEqual(self.file.read_at_finger(), i)
        for i in range(20):
            self.assertEqual(self.file.read_at_finger(), 19-i)
            self.file.decrement_finger()
        self.file.decrement_finger()
        self.assertEqual(self.file.read_at_finger(), 0)
        for i in range(20):
            self.assertEqual(self.file.read_at_finger(), i)
            self.file.increment_finger()
        self.file.increment_finger()
        self.assertEqual(self.file.read_at_finger(), 19)

    def test_different_order(self):
        self.file.insert_after_finger(-1)
        for i in range(20):
            self.file.insert_after_finger(i)
            self.file.decrement_finger()
        for i in range(20):
            self.file.increment_finger()
            self.assertEqual(self.file.read_at_finger(), 19-i)


if __name__ == '__main__':
    test_suite = TestFilePointer
    unittest.main()
