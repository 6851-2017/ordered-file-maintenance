# jamb, rusch, nchanda2

arr = []

# add the element elem to array arr at position pos, rewriting as needed to make space
# return nothing; modify input array in place
def insert(elem, arr, pos):
	if pos > len(arr):
		raise ValueError("attempted inserting past the end of the array")
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
def _rewrite(arr, i, j):
    count = _collapse(arr, i, j)
    print(arr)
    _even_spread(arr, i, j, count)

# rewrites all elements from i to j-1 to be on the left side of the interval,
# and returns a count of how many elements it found
def _collapse(arr, i, j):
    openSlots = []
    count = 0
    for i in range(i, j):
        x = arr[i]
        if x is None:
            openSlots.append(i)
        else:
            count += 1
            if len(openSlots) != 0:
                newPos = openSlots.pop(0)
                arr[newPos] = x
                arr[i] = None
                openSlots.append(i)
    return count

# given the elements from i to j-1 are all on the left side of the interval, and there are count of them,
# rewrite the elements to be evenly spread across the interval and return nothing
def _even_spread(arr, i, j, count):
    print(count)
    spacing = int((j-i)/count)
    print(spacing)
    elementIndex = i+count
    for pos in range(len(arr)-1, 0, -1):
        if pos % spacing == 0:
            arr[pos] = None
        else:
            elementIndex -=1
            arr[pos] = arr[elementIndex]


# arr = [None]*15
# arr[1] = 5
# arr[1] = 1
# arr[2] = 5
# arr[7] = 5
# arr[14] = 8
# _rewrite(arr, 0, 8)
#
# print(arr)