# jamb, rusch, nchinda2, luh


import math




# represent a file with this behind-the-scenes thing that keeps elements O(1) apart and takes only O(log^2(n)) updates
class OrderedFile(list):

    def __init__(self):
        super(OrderedFile, self).__init__([None, None])

    # report what value is present at a given index pos
    def read(arr, pos):
        if arr[pos] is None:
            raise ValueError("Attempted to read at position where there is no value.")
        return arr[pos]

    # given a position, scan forward O(1) to find the next non-empty element (not-including-this-one);
    # should be sort of like an iterator into the file being represented
    def get_next(arr, pos):
        pos = pos + 1
        while (pos < len(arr) and arr[pos] is None):
            pos = pos + 1
        if pos == len(arr):
            return None
        return pos

    # given a position, scan backward O(1) to find the previous non-empty element (not-including-this-one);
    # should be sort of like a reverse iterator into the file being represented
    def get_previous(arr, pos):
        pos = pos - 1
        while (pos >= 0 and arr[pos] is None):
            pos = pos - 1
        if pos < 0:
            return None
        return pos

    # add the element elem to the array after position pos, rewriting as needed to make space
    # return nothing; modify the array in place
    # TODO Add middle log level
    def insert(arr, elem, pos):
        if pos > len(arr):
            raise ValueError("attempted inserting past the end of the array")

        level = 0  # what level we're looking at within the tree, going from bottom up
        while (True):
            height = int(math.log(len(arr)-1, 2))+1  # height of tree, ceiling functioned
            #print(level, height)
            # check for being at a level such that we need to allocate more space in the array
            if level > height:
                arr += [None] * 2**height
                height += 1

            num_blocks = arr._num_blocks(level)
            # blocklen = len(arr)/num_blocks; blocknum = int(pos/blocklen); start, end = block_index*blocklen, (block_index+1)*blocklen
            block_index = int(pos * num_blocks / len(arr))
            start = int(block_index * len(arr) / num_blocks)
            end = int((block_index + 1) * len(arr) / num_blocks)
            block_element_count = arr._scan(start, end) + 1  # +1 because we'll insert one
            block_max_elements = end - start
            block_density = block_element_count / block_max_elements

            depth = height - level
            #max_density = 3/4 + 1/4*depth/height
            #min_density = 1/2 - 1/4*depth/height
            t = 1.5
            max_density = t**(depth - height - 1)
            min_density = t**(depth - height)
            #print(block_density, min_density, max_density)

            if block_density <= max_density:
                # yay! we can stop at this level
                ##print("\ni=%s, j=%s" % (start, end))
                ##print("Arr=", arr)
                ##print("\t adding ", elem)
                count = arr._collapse(start, end, elem, pos)
                ##print("Collapsed Arr=", arr)
                ##print("\t count ", count)
                arr._even_spread(start, end, count)
                ##print("Spread Arr=", arr)
                return

            # in this case, this level isn't good enough and we need to iterate and rewrite at a higher level
            level += 1

    # return the number of items between i and j-1 in the array
    # also, while scanning, rewrite all elements from i to j-1 to be on the left side of the interval
    def _scan(arr, i, j):
        return len([x for x in arr[i:j] if x is not None])

    # given the level up the tree we're at, we have 2^level * log(n) things in a block
    # returns how many blocks there are in the tree at that level
    def _num_blocks(arr, level):
        # ceiling function of n/2^level*logn
        n = len(arr)
        #print("n=%s" % n)
        return int((n-1)/(2**level * math.log(n, 2)))+1

    # collapse the interval from i to j, clumping elements to the left of it
    # if j > len(arr), just go to end of array
    # meanwhile insert (or delete if deleting) elem after (at) pos
    # TODO deleting doesn't work
    # return the count of elements collapsed
    def _collapse(arr, i, j, elem, pos, deleting=False):
        next_pos=i
        temp_i_val = None
        temp_i_plus_one = arr[i]
        arr[i] = None
        for index in range(i,j):
            # get the value for the next round, since we might overwrite it this round
            assert next_pos <= index+1
            temp_i_val = temp_i_plus_one
            if index + 1 < j:
                temp_i_plus_one = arr[index+1]
                arr[index+1] = None

            # now look at this round's stored value and collapse it
            if temp_i_val is not None:
                arr[next_pos] = temp_i_val
                ##arr.callback(index, next_pos)
                temp_i_val.set_index(next_pos)
                next_pos += 1
            if index == pos:
                arr[next_pos] = elem
                next_pos += 1
        count = next_pos - i
        assert count <= j-i
        return count

    # rewrites all elements from i to j-1 to be evenly spread across the interval and return nothing
    # also inserts elem at the specified position while it's rewriting
    # TODO make this more in-place
    def _even_spread(arr, i, j, count):
        newIndices = [i + (k*(j-i))//count for k in range(count)]
        ##print("Indices=", newIndices)
        for it in range(count-1, -1, -1):
            elem = arr[i+it]
            index = newIndices[it]  # i + (it*(j-i))//count
            arr[i+it] = None
            arr[index] = elem
            ##print("\t it=%s i+it=%s index=%s elem=%s" % (it, i+it, index, elem))
            ##arr.callback(i+it, index)
            elem.set_index(index)
        return

    # FORMATTERS

    # (1  (2  )2  (3  )3  )1
    def parenth_version_format(arr):
        ret = ""
        for bucket in arr:
            if bucket is not None:
                ret += bucket.parenth_format()
        return ret




