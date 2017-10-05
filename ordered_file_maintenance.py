# jamb, rusch, nchanda2 

arr = []

def insert(arr, pos):
	pass

# return the number of items between i and j-1 in the array
# also, while scanning, rewrite all elements from i to j-1 to be on the left side of the interval
def _scan(arr, i, j):
	pass

# given the level up the tree we're at, we have 2^level * log(n) things in a block
# returns how many blocks there are in the tree at that level
def _num_blocks(arr, level):
	# ceiling function of n/2^level*logn
	return int((n-1)/(2**level * math.log(n, 2)))+1

# given the elements from i to j-1 are all on the left side of the interval, and there are count of them,
# rewrite the elements to be evenly spread across the interval and return nothing
def _even_spread(arr, i, j, count):
	pass

