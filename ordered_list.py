# jamb, rusch 6.851 Fall 2017

# TODOs: implement all the stuff with "pass"



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

    # insert a new VersionPtr into the list after the given VersionPtr and return it
    def insert_after(self, version):
        pass


class VersionPtr():
    '''Version object to be stored in an OrderedList, be compared,
        and also point to the root node of its version in a FPPM.'''

    # constructor
    def __init__(self, index, root):
        self.index = index
        self.root = root

    # overload > operator
    def __gt__(self, other):
        return self.index > other.index

    #overload < operator
    def __lt__(self, other):
        return self.index < other.index

    # get root
    def get_root(self):
        return self.root

    # string format
    def __str__(self):
        return "<VersionPtr at index %s>" % index



