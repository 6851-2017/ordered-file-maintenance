# jamb, rusch, nchinda2

import math

class OrderedFile(list):

    def __init__(self):
        super(OrderedFile, self).__init__([None])


    def read(arr, pos):
        x = 0
        i = 0
        while pos < x:
            if arr[i]:
                x += 1
            i += 1

            if i > len(arr):
                raise Exception("Index not present")

        return arr[x]

    # add the element elem to the array at position pos, rewriting as needed to make space
    # return nothing; modify the array in place
    def insert(arr, elem, pos):
            if pos > len(arr):
                raise ValueError("attempted inserting past the end of the array")

            level = 0  # what level we're looking at within the tree, going from bottom up
            height = int(math.log(len(arr)-1, 2))+1  # height of tree, ceiling functioned

            while (True):
                # check for being at a level such that we need to allocate more space in the array
                if level > height:
                        arr += [None] * 2**height

                num_blocks = _num_blocks(arr, level)
                # blocklen = len(arr)/num_blocks; blocknum = int(pos/blocklen); start, end = block_index*blocklen, (block_index+1)*blocklen
                block_index = int(pos * num_blocks / len(arr))
                start = int(block_index * len(arr) / num_blocks)
                end = int((block_index + 1) * len(arr) / num_blocks)
                block_element_count = _scan(arr, start, end)
                block_max_elements = end - start
                block_density = block_element_count / block_max_elements

                depth = height - level
                max_density = 3/4 + 1/4*depth/height
                min_density = 1/2 - 1/4*depth/height

                if block_density >= min_density and block_density <= max_density:
                        # yay! we can stop at this level
                        _rewrite(arr, start, end, elem)
                        return

                # in this case, this level isn't good enough and we need to iterate and rewrite at a higher level
                level += 1

    # remove the element from the array at the given position
    # return nothing; modify the array in place
    def delete(arr, pos):
        pass

    # return the number of items between i and j-1 in the array
    # also, while scanning, rewrite all elements from i to j-1 to be on the left side of the interval
    def _scan(arr, i, j):
            return len([x for x in arr[i:j] if x is not None])

    # given the level up the tree we're at, we have 2^level * log(n) things in a block
    # returns how many blocks there are in the tree at that level
    def _num_blocks(arr, level):
            # ceiling function of n/2^level*logn
            n = len(arr)
            return int((n-1)/(2**level * math.log(n, 2)))+1

    # rewrites all elements from i to j-1 to be evenly spread across the interval and return nothing
    # also inserts elem at the specified position while it's rewriting
    def _rewrite(arr, i, j):
        count = self._collapse(arr, i, j)
        self._even_spread(arr, i, j, count)

    # rewrites all elements from i to j-1 to be on the left side of the interval,
    # and returns a count of how many elements it found
    def _collapse(arr, i, j):
        openSlots = []
        count = 0
        for index in range(i, j):
            x = arr[index]
            if x is None:
                openSlots.append(index)
            else:
                count += 1
                if len(openSlots) != 0:
                    newPos = openSlots.pop(0)
                    arr[newPos] = x
                    arr[index] = None
                    openSlots.append(index)
        return count

    # given the elements from i to j-1 are all on the left side of the interval, and there are n of them,
    # rewrite the elements to be evenly spread across the interval and return nothing
    def _even_spread(arr, i, j, count):
        spacing = int((j-i)/count)
        elementIndex = i+count
        for pos in range(j-1, i-1, -1):
            if pos % spacing == 0:
                elementIndex -=1
                arr[pos] = arr[elementIndex]
            else:
                arr[pos] = None

