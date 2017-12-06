# jamb, rusch 6.851 Fall 2017

# TODOs:
# stuff below
# change bucket_list to OFM not list

import math
from ordered_file_maintenance import OrderedFile

W = 16  # machine word size, TODO swap to 64
B = 4 # for printing only

def binary_string(index):
    ret = ""
    for _ in range(W+B):
        ret = str(index % 2) + ret
        index = index // 2
    return ret


class VersionPtr():
    '''Version object to be stored in an OrderedList, be compared,
        and also point to the root node of its version in a FPPM.'''

    # constructor
    def __init__(self, index, root, bucket):
        self.index = index
        self.root = root
        root.add_version_pointer(self)
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
        return "<VersionPtr at index %s--%s>" % (self.bucket.index, self.index)

    def __repr__(self):
        return "<VP %s>" % binary_string(self.get_index())


class Versioner():
    '''Versioning object that stores an OrderedList and a list of VersionPtrs into it
        to maintain via a callback function.'''

    # constructor
    def __init__(self, mock=False):
        self.list = None
        if mock:
            self.list = OrderedListComparison(self.callback, self)
        else:
            self.list = OrderedList(self.callback, self)
        self.ptrs_to_update = {}  # map from index to Bucket; note only one Bucket should ever be created to that index

    # OrderedList should call this whenever it moves the bucket at position index to new_index
    # returns nothing
    def callback(self, index, new_index):
        if index == new_index:
            # don't need to do anything
            return
        bucket = self.ptrs_to_update.get(index)
        if bucket:
            assert bucket.index == index
            bucket.set_index(new_index)
            assert self.ptrs_to_update.get(new_index) is None
            self.ptrs_to_update[new_index] = self.ptrs_to_update.pop(index)
        return

    # add a bucket to keep track of in callbacks
    def track_bucket(self, bucket):
        index = bucket.index
        assert self.ptrs_to_update.get(index) is None, "index=%s, ptr=%s, bucket_list=%s" % (index, str(self.ptrs_to_update.get(index)), self.list.bucket_list)
        self.ptrs_to_update[index] = bucket
        #print("Tracking bucket: %s=%s" % (index, bucket))
        #print(self.ptrs_to_update)

    # insert a new VersionPtr into the OrderedList after the given VersionPtr and return it
    def insert_after(self, version):
        return self.list.insert_after(version)

    # insert something when currently empty
    def insert_first(self, root):
        ver_ptr = self.list.insert_first(root)
        self.track_bucket(ver_ptr.bucket)
        return ver_ptr


class OrderedListComparison(list):
    '''MOCK EXAMPLE of ordered-file-maintenance-based data structure, not O(1)'''

    # constructor
    def __init__(self, callback, versioner):
        super(OrderedListComparison, self).__init__([None, None])
        self.callback = callback  # call on (index, new_index) any time we move a BottomBucket from index to new_index
        self.bucket_list = []
        self.count = 0
        self.versioner = versioner

    # insert a new VersionPtr into the list after the given VersionPtr and return it
    # TODO how do we know what root to insert? should probably change at some point
    def insert_after(self, version):
        self.count += 1
        bucket_count = None
        while (bucket_count is None):
            bucket_count = version.bucket.insert_count()
        index = version.index + (1 << (W - bucket_count))
        #print("INSERT after version %s: new version %s" % (version.index, index))
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
        return ver_ptr

    # add a new bucket to the bucket_list after the specified position
    # adjust indices of all later buckets accordingly
    def insert_bucket_after(self, bucket_index, new_bucket):
        self.bucket_list.insert(bucket_index+1, new_bucket)
        for i in range(len(self.bucket_list)-1, bucket_index+1, -1):
            self.callback(self.bucket_list[i].index, self.bucket_list[i].index+1)

    # return the total number of version pointers in self
    def get_count(self):
        return self.count


class OrderedList():
    '''The real one, with OFM.'''
        # constructor
    def __init__(self, callback, versioner):
        # should call callback on (index, new_index) any time we move a BottomBucket from index to new_index
        self.bucket_list = OrderedFile(callback)
        self.count = 0
        self.versioner = versioner

    # insert a new VersionPtr into the list after the given VersionPtr and return it
    # TODO how do we know what root to insert? should probably change at some point
    def insert_after(self, version):
        self.count += 1
        bucket_count = None
        while (bucket_count is None):
            bucket_count = version.bucket.insert_count()
        index = version.index + (1 << (W - bucket_count))
        #print("INSERT after version %s: new version %s" % (version.index, index))
        new_ptr = VersionPtr(index, version.get_root(), version.bucket)
        new_ptr.next_in_bucket = version.next_in_bucket
        version.next_in_bucket = new_ptr
        return new_ptr

    # same as insert_after except there's nothing in the list so it can't be after something
    # pass in the root of the DS we're making an OL on
    def insert_first(self, root):
        ##assert len(self.bucket_list) == 0  # this probably isn't true for OFM
        ver_ptr = VersionPtr(0, root, None)
        new_bucket = BottomBucket(index=0, parent=self, first_elt=ver_ptr)
        ver_ptr.bucket = new_bucket
        self.bucket_list.insert(new_bucket, 0)
        self.count += 1
        return ver_ptr

    # add a new bucket to the bucket_list after the specified position
    def insert_bucket_after(self, bucket_index, new_bucket):
        self.bucket_list.insert(new_bucket, bucket_index)

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
        if (self.count >= W):
            self.split()
            return None
        return self.count

    # split into two bottom buckets by scanning and moving the second half, insert the second after the first in the parent
    def split(self):
        #print("SPLITTING; self.count=%s" % self.count)
        ver_ptr = self.first_ptr
        last_first_half = None
        for i in range(self.count//2):
            #print("First loop {}".format(i))
            last_first_half = ver_ptr
            ver_ptr = ver_ptr.next_in_bucket
        last_first_half.next_in_bucket = None
        new_bucket = BottomBucket(self.index+1, self.parent, ver_ptr)
        prev_ptr = last_first_half
        while ver_ptr:    ##for i in range(self.count//2, self.count):
            ver_ptr.bucket = new_bucket
            bucket_count = new_bucket.insert_count()
            ver_ptr.index = (prev_ptr.index if prev_ptr != last_first_half else 0) + (1 << (W - bucket_count))
            prev_ptr = ver_ptr
            ver_ptr = ver_ptr.next_in_bucket
        self.count = self.count//2
        self.parent.insert_bucket_after(self.index, new_bucket)
        ##self.parent.versioner.track_bucket(new_bucket)

    def set_index(self, index):
        self.index = index

    def __str__(self):
        return "BUCKET %s: %s elements" % (self.index, self.count)

    def __repr__(self):
        return "BUCKET %s: %s elements" % (self.index, self.count)




