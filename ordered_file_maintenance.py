# jamb, rusch, nchinda2, luh


import math

class OrderedFile(list):

    def __init__(self):
        super(OrderedFile, self).__init__([None, None])

    def read(arr, pos):
        x = 0
        i = 0
        while pos >= x:
            if arr[i] is not None:
                x += 1
            i += 1

            if i > len(arr):
                raise Exception("Index not present")

        return arr[i-1]

    # add the element elem to the array at position pos, rewriting as needed to make space
    # return nothing; modify the array in place
    def insert(arr, elem, pos):
        if pos > len(arr):
            raise ValueError("attempted inserting past the end of the array")

        level = 0  # what level we're looking at within the tree, going from bottom up
        while (True):
            height = int(math.log(len(arr)-1, 2))+1  # height of tree, ceiling functioned
            print(level, height)
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
            max_density = 3/4 + 1/4*depth/height
            min_density = 1/2 - 1/4*depth/height
            print(block_density, min_density, max_density)

            if block_density <= max_density:
                # yay! we can stop at this level
                interval = arr._collapse(start, end, elem, pos)
                arr._even_spread(start, end, interval)
                return

            # in this case, this level isn't good enough and we need to iterate and rewrite at a higher level
            level += 1

    # remove the element from the array at the given position
    # return nothing; modify the array in place
    def delete(arr, pos):
        if pos > len(arr):
            raise ValueError("attempted deleting past the end of the array")

        level = 0  # what level we're looking at within the tree, going from bottom up
        while (True):
            height = int(math.log(len(arr)-1, 2))+1  # height of tree, ceiling functioned
            print(level, height)
            # check for being at a level such that we need to reduce space in the array
            if level > height:
                interval = arr._collapse(0, len(arr), None, pos, True)
                arr._even_spread(0, len(arr)//2, interval)
                arr = arr[0:len(arr)//2]
                height -= 1
                return

            num_blocks = arr._num_blocks(level)
            # blocklen = len(arr)/num_blocks; blocknum = int(pos/blocklen); start, end = block_index*blocklen, (block_index+1)*blocklen
            block_index = int(pos * num_blocks / len(arr))
            start = int(block_index * len(arr) / num_blocks)
            end = int((block_index + 1) * len(arr) / num_blocks)
            block_element_count = arr._scan(start, end) - 1  # +1 because we'll delete one
            block_max_elements = end - start
            block_density = block_element_count / block_max_elements

            depth = height - level
            max_density = 3/4 + 1/4*depth/height
            min_density = 1/2 - 1/4*depth/height
            print(block_density, min_density, max_density)

            if block_density >= min_density:
                    # yay! we can stop at this level
                    interval = arr._collapse(start, end, None, pos, True)
                    arr._even_spread(start, end, interval)
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
            print("n=%s" % n)
            return int((n-1)/(2**level * math.log(n, 2)))+1

    def _collapse(arr, i, j, elem, pos, deleting=False):
        interval = (arr[i:pos]+arr[pos+1:j]) if deleting else (arr[i:pos] + [elem] + arr[pos:j])
        return interval

    # rewrites all elements from i to j-1 to be evenly spread across the interval and return nothing
    # also inserts elem at the specified position while it's rewriting
    def _even_spread(arr, i, j, interval):
        elems = [thing for thing in interval if thing is not None]
        count = len(elems)
        assert count <= j-i
        arr[i:j] = [None]*(j-i)
        newIndices = [i + (k*(j-i))//count for k in range(count)]
        for elem, index in zip(elems, newIndices):
            arr[index] = elem


    
