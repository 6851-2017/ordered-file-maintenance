# jamb, rusch 6.851 Fall 2017

# TODOs:
# stuff below
# change bucket_list to OFM not list
# do we need callbacks anywhere?

import math

W = 64  # machine word size


class VersionPtr():
    '''Version object to be stored in an OrderedList, be compared,
        and also point to the root node of its version in a FPPM.'''

    # constructor
    def __init__(self, index, root, bucket):
        self.index = index
        self.root = root
        self.bucket = bucket
        self.next_in_bucket = None

    # overload > operator
    def __gt__(self, other):
        return self.get_index() > other.get_index()

    #overload < operator
    def __lt__(self, other):
        return self.get_index() < other.get_index()

    # get concatenated bucket and within-bucket index
    def get_index(self):
        return (self.bucket.index << (W+1)) + self.index

    # get root
    def get_root(self):
        return self.root

    # string format
    def __str__(self):
        return "<VersionPtr at index %s>" % self.index


class Versioner():
    '''Versioning object that stores an OrderedList and a list of VersionPtrs into it
        to maintain via a callback function.'''

    # constructor
    def __init__(self):
        self.list = OrderedList(self.callback)
        self.ptrs_to_update = {}  # map from index to VersionPtr; note only one VersionPtr should ever be created to that index

    # OrderedList should call this whenever it moves the bucket at position index to new_index
    # returns nothing
    def callback(self, index, new_index):
        version = self.ptrs_to_update.get(index)
        if (version):
            assert(version.index == index)
            version.index = new_index
        return

    # insert a new VersionPtr into the OrderedList after the given VersionPtr,
    # return it, and add it to the list of VersionPtrs to update
    def insert_after(self, version):
        new_version = self.list.insert_after(version)
        if new_version:
            self.ptrs_to_update[new_version.index] = new_version
        return new_version

    def insert_first(self, root):
        return self.list.insert_first(root)


class OrderedList(list):
    '''Ordered-file-maintenance-based O(1) data structure'''

    # constructor
    def __init__(self, callback):
        super(OrderedList, self).__init__([None, None])
        self.callback = callback  # call on (index, new_index) any time we move a BottomBucket from index to new_index
        self.bucket_list = []  # TODO make this an O(log n) OrderedFileMaintenance thingy instead of a regular list
        self.count = 0

    # insert a new VersionPtr into the list after the given VersionPtr and return it
    # TODO how do we know what root to insert? should probably change at some point
    def insert_after(self, version):
        self.count += 1
        bucket_count = None
        while (bucket_count is None):
            bucket_count = version.bucket.insert_count()
        index = version.index + (1 << (W - bucket_count))
        new_ptr = VersionPtr(index, version.get_root(), version.bucket)
        new_ptr.next_in_bucket = version.next_in_bucket
        version.next_in_bucket = new_ptr
        return new_ptr

    # same as insert_after except there's nothing in the list so it can't be after something
    # pass in the root of the DS we're making an OL on
    def insert_first(self, root):
        assert len(self.bucket_list) == 0
        ver_ptr = VersionPtr(0, root, None)
        new_bucket = BottomBucket(index=0, parent=self, first_elt=ver_ptr)
        ver_ptr.bucket = new_bucket
        self.bucket_list = [new_bucket]
        self.count += 1
        print("Here", new_bucket)
        return ver_ptr

    # add a new bucket to the bucket_list after the specified position
    # adjust indices of all later buckets accordingly
    def insert_bucket_after(self, bucket_index, new_bucket):
        self.bucket_list.insert(bucket_index+1, new_bucket)
        for i in range(bucket_index+2, len(bucket_list)):
            self.bucket_list[i].index += 1

    # return the total number of version pointers in self
    def get_count(self):
        return self.count



class BottomBucket():
    '''Bucket item to store O(log n) things within an ordered list, and keep track
        of its own index in the upper structure and the number of things in it.'''

    # constructor; index is position within OrderedList parent; first_elt is first VersionPtr inserted
    def __init__(self, index, parent, first_elt):
        self.index = index
        self.count = 1
        self.parent = parent
        self.first_ptr = first_elt

    # increment and return the count so we know what number thing we are inserting
    # if too full, do a split and return None, user must redo since the version may have shifted buckets
    def insert_count(self):
        self.count += 1
        if (self.count > W):
            self.split()
            return None
        return self.count

    # split into two bottom buckets by scanning and moving the second half, insert the second after the first in the parent
    def split(self):
        ver_ptr = self.first_ptr
        last_first_half = None
        for i in range(self.count//2):
            print("First loop {}".format(i))
            last_first_half = ver_ptr
            ver_ptr = ver_ptr.next_in_bucket
        last_first_half.next_in_bucket = None
        new_bucket = BottomBucket(self.index+1, self.parent, ver_ptr)
        prev_ptr = last_first_half
        for i in range(self.count//2, self.count):
            print("Second loop {}".format(i))
            ver_ptr.bucket = new_bucket
            bucket_count = self.insert_count()
            ver_ptr.index = (prev_ptr.index if prev_ptr != last_first_half else 0) + (1 << (W - bucket_count))
            prev_ptr = ver_ptr
            ver_ptr = ver_ptr.next_in_bucket
        self.count = self.count//2
        self.parent.insert_bucket_after(self.index, new_bucket)




