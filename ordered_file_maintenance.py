# jamb, rusch, nchinda2

import math


class OrderedFile(list):

    # add the element elem to the array at position pos, rewriting as needed to make space
    # return nothing; modify the array in place
    def insert(arr, elem, pos):
            if pos > len(arr):
                    raise ValueError("attempted inserting past the end of the array")
            
            level = 0  # what level we're looking at within the tree, going from bottom up
            height = int(math.log(len(arr-1), 2))+1  # height of tree, ceiling functioned

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
            pass

    # given the level up the tree we're at, we have 2^level * log(n) things in a block
    # returns how many blocks there are in the tree at that level
    def _num_blocks(arr, level):
            # ceiling function of n/2^level*logn
            n = len(arr)
            return int((n-1)/(2**level * math.log(n, 2)))+1

    # rewrites all elements from i to j-1 to be evenly spread across the interval and return nothing
    # also inserts elem at the specified position while it's rewriting
    def _rewrite(arr, i, j, elem=None):
            # call _collapse and _even_spread
            pass

    # rewrites all elements from i to j-1 to be on the left side of the interval,
    # and returns a count of how many elements it found
    def _collapse(arr, i, j):
	    found = [elem for elem in arr[i:j] if elem is not None]
	    rewritten = found + [None]*(j-i-len(found))
	    arr[i:j] = rewritten
	    return len(found)

    # given the elements from i to j-1 are all on the left side of the interval, and there are n of them,
    # rewrite the elements to be evenly spread across the interval and return nothing
    def _even_spread(arr, i, j, n):
        block_size = j - i
        interval = block_size / n

        start = j % interval
        for start, end in enumerate(range(i, j, interval))[::-1]:
            arr[end], arr[start] = arr[start], None
