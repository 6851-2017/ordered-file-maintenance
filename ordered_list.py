# jamb, rusch 6.851 Fall 2017

# TODOs:
# implement all the stuff with "pass"
# change bucket_list to OFM not list
# implement VersionPtr.get_index()



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
        return (version.bucket.index << int(math.log2(self.count)+1)) + self.index

    # get root
    def get_root(self):
        return self.root

    # string format
    def __str__(self):
        return "<VersionPtr at index %s>" % index
    

class Versioner():
    '''Versioning object that stores an OrderedList and a list of VersionPtrs into it
        to maintain via a callback function.'''

    # constructor
    def __init__(self):
        self.list = OrderedList(self.callback)
        self.ptrs_to_update = {}  # map from index to VersionPtr; note only one VersionPtr should ever be created to that index

    # OrderedList should call this whenever it moves the element at position index to new_index
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


class OrderedList(list):
    '''Ordered-file-maintenance-based O(1) data structure'''

    # constructor
    def __init__(self, callback):
        super(OrderedList, self).__init__([None, None])
        self.callback = callback  # call on (index, new_index) any time we move a VersionPtr from index to new_index
        self.bucket_list = []  # TODO make this an O(log n) OrderedFileMaintenance thingy instead of a regular list
        self.count = 0

    # insert a new VersionPtr into the list after the given VersionPtr and return it
    # TODO how do we ever insert the first thing?
    # TODO how do we know what root to insert? should probably change at some point
    def insert_after(self, version):
        self.count += 1
        bucket_count = None
        while (bucket_count is None):
            bucket_count = version.bucket.insert_count()
        index = version.index + (1 << int(math.log2(self.count)))  # TODO if count's log increases between inserts this is BAD
        new_ptr = VersionPtr(index, version.get_root(), version.bucket)
        new_ptr.next_in_bucket = version.next_in_bucket
        version.next_in_bucket = new_ptr
        return new_ptr

    # return the total number of version pointers in self
    def get_count():
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
        if (self.count > math.log2(parent.get_count())):
            self.split()
            return None
        return self.count

    # split into two bottom buckets, insert the second after the first in the parent
    def split(self):
        pass



