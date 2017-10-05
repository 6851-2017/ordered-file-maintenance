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
	pass

# given the level up the tree we're at, we have 2^level * log(n) things in a block
# returns how many blocks there are in the tree at that level
def _num_blocks(arr, level):
	# ceiling function of n/2^level*logn
	n = len(arr)
	return int((n-1)/(2**level * math.log(n, 2)))+1

# rewrites all elements from i to j-1 to be evenly spread across the interval and return nothing
def _rewrite(arr, i, j):
	# call _collapse and _even_spread
	pass

# rewrites all elements from i to j-1 to be on the left side of the interval,
# and returns a count of how many elements it found
def _collapse(arr, i, j):
	pass

# given the elements from i to j-1 are all on the left side of the interval, and there are n of them,
# rewrite the elements to be evenly spread across the interval and return nothing
def _even_spread(arr, i, j, n):
    block_size = j - i
    interval = block_size / n

    start = j % interval
    for start, end in enumerate(range(i, j, interval))[::-1]:
        arr[end], arr[start] = arr[start], None
