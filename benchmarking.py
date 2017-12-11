import cProfile
import unittest
import time
import random
from math import log
from collections import defaultdict
from fpbst import FPBST
from full_persistence import FPPM
from full_persistence import FPNode


# Linked list

# 4 depth binary history for each node


def timeit(f):
    def wrapper(*args, **kwargs):
        t1 = time.process_time()
        ret = f(*args, **kwargs)
        t2 = time.process_time()
        return ret, t2 - t1
    return wrapper

def asymptotic(xs, ns):
    xs = [str(x / xs[0] / n) for x, n in zip(xs, ns)]
    return '\n'.join(xs)

@timeit
def create_linked_list(n):
    # Initialize Fully Persitent Pointer Machine
    fppm = FPPM()
    root = fppm.get_root(fppm.first_version)

    node = root
    next_node = FPNode("n{}".format(0), fppm, fppm.first_version)
    v = root.set_field("p0", next_node, fppm.first_version)
    root = fppm.get_root(fppm.first_version)
    root.good_v = v
    node = root.get_field("p0", v)
    prev_node = root

    for i in range(1, n):
        next_node = FPNode("n{}".format(i), fppm, fppm.first_version)
        v = node.set_field("p0", next_node, fppm.first_version)
        node.good_v = v
        node = prev_node.get_field("p0", prev_node.good_v)
        prev_node = node
        node = node.get_field("p0", v)

    return root

@timeit
def linear_value_history_sweep_write(root, n):
    versions = defaultdict(list)

    node = root
    n_i = 0
    while node:
        version = node.good_v
        for i in range(n):
            version = node.set_field("v0", i, version)
            versions[n_i].append(version)
        node = node.get_field("p0", version)
        n_i += 1

    return versions

@timeit
def linear_value_history_sweep_read(root, versions):
    node = root
    for n_i in range(len(versions)):
        node_versions = versions[n_i]
        for i, version in enumerate(node_versions):
            val = node.get_field("v0", version)
            #assert(val == i)

@timeit
def earliest_history_sweep_write(root, n):
    versions = defaultdict(list)

    node = root
    n_i = 0
    while node:
        for i in range(n):
            version = node.set_field("v0", i, node.earliest_version)
            versions[n_i].append(version)
        node = node.get_field("p0", version)
        n_i += 1

    return versions

@timeit
def earliest_history_sweep_read(root, versions):
    node = root
    for n_i in range(len(versions)):
        node_versions = versions[n_i]
        for i, version in enumerate(node_versions):
            val = node.get_field("v0", version)
            #assert(val == i)

@timeit
def branching_history_sweep_write(root, n):
    versions = defaultdict(list)

    def recurse(node, v, n, n_i):
        if n <= 1:
            return None

        left_v = node.set_field("v0", n, v)
        right_v = node.set_field("v0", n, v)
        versions[n_i].append(left_v)
        versions[n_i].append(right_v)
        recurse(node, left_v, n-1, n_i)
        recurse(node, right_v, n-1, n_i)

    node = root
    n_i = 0
    while node:
        recurse(node, node.earliest_version, int(log(n, 2)), n_i)
        node = node.get_field("p0", node.earliest_version)
        n_i += 1

    return versions

@timeit
def branching_history_sweep_read(root, versions):
    node = root
    for n_i in range(len(versions)):
        node_versions = versions[n_i]
        for i, version in enumerate(node_versions):
            val = node.get_field("v0", version)
            #assert(val == i)

@timeit
def random_history_sweep_write(root, n):
    all_versions = defaultdict(list)

    node = root
    n_i = 0
    while node:
        versions = [node.earliest_version]
        for i in range(n):
            version = random.choice(versions)
            new_version = node.set_field("v0", i, version)
            versions.append(new_version)
            all_versions[n_i].append(new_version)
        node = node.get_field("p0", version)
        n_i += 1

    return all_versions

@timeit
def random_history_sweep_read(root, versions):
    node = root
    for n_i in range(len(versions)):
        node_versions = versions[n_i]
        for i, version in enumerate(node_versions):
            val = node.get_field("v0", version)
            #assert(val == i)

LINKED_SIZE = 1024
def linked_list():
    ns1 = [2**n for n in range(8)]
    ns2 = [2**n for n in range(8)]

    list_creation_ts = [create_linked_list(n)[1] for n in ns1]

    linear_ts = []
    linear_ts_read = []
    for n in ns2:
        root, _ = create_linked_list(int(LINKED_SIZE))
        versions, t = linear_value_history_sweep_write(root, n)
        linear_ts.append(t)
        linear_ts_read.append(linear_value_history_sweep_read(root, versions)[1])

    earliest_ts = []
    earliest_ts_read = []
    for n in ns2:
        root, _ = create_linked_list(int(LINKED_SIZE))
        versions, t = earliest_history_sweep_write(root, n)
        earliest_ts.append(t)
        earliest_ts_read.append(earliest_history_sweep_read(root, versions)[1])

    branching_ts = []
    branching_ts_read = []
    for n in ns2:
        root, _ = create_linked_list(int(LINKED_SIZE))
        versions, t = branching_history_sweep_write(root, n)
        branching_ts.append(t)
        branching_ts_read.append(branching_history_sweep_read(root, versions)[1])

    random_ts = []
    random_ts_read = []
    for n in ns2:
        root, _ = create_linked_list(int(LINKED_SIZE))
        versions, t = random_history_sweep_write(root, n)
        random_ts.append(t)
        random_ts_read.append(random_history_sweep_read(root, versions)[1])

    print("========CREATION TIMES================")
    print("T0 = {}".format(list_creation_ts[0]))
    print(asymptotic(list_creation_ts, ns1))
    print()
    print()
    print("========LINEAR HISTORY CREATION=======")
    print("T0 = {}".format(linear_ts[0]))
    print(asymptotic(linear_ts, ns2))
    print()
    print("========LINEAR HISTORY READ=======")
    print("T0 = {}".format(linear_ts_read[0]))
    print(asymptotic(linear_ts_read, ns2))
    print()
    print("========EARLIEST HISTORY CREATION========")
    print("T0 = {}".format(earliest_ts[0]))
    print(asymptotic(earliest_ts, ns2))
    print()
    print("========EARLIEST HISTORY READ========")
    print("T0 = {}".format(earliest_ts_read[0]))
    print(asymptotic(earliest_ts_read, ns2))
    print()
    print("========BRANCHING HISTORY CREATION========")
    print("T0 = {}".format(branching_ts[0]))
    print(asymptotic(branching_ts, ns2))
    print()
    print("========BRANCHING HISTORY READ========")
    print("T0 = {}".format(branching_ts_read[0]))
    print(asymptotic(branching_ts_read, ns2))
    print()
    print("========RANDOM HISTORY CREATION========")
    print("T0 = {}".format(random_ts[0]))
    print(asymptotic(random_ts, ns2))
    print()
    print("========RANDOM HISTORY READ========")
    print("T0 = {}".format(random_ts_read[0]))
    print(asymptotic(random_ts_read, ns2))
    print()

######################
### TREE STUFF #######
######################

# Global accumulator for somer assertion testing

@timeit
def create_tree(n):
    # Initialize Fully Persitent Pointer Machine
    fppm = FPPM()

    # Setup node0 and node1
    root = FPNode("root", fppm, fppm.first_version)
    def recurse(node, name, n):
        if n <= 1:
            return None

        left_n = FPNode(name + "L", fppm, node.earliest_version)
        right_n = FPNode(name + "R", fppm, node.earliest_version)
        v = node.set_field("left", left_n, node.earliest_version)
        v = node.set_field("right", right_n, v)
        recurse(node, name + "L", n-1)
        recurse(node, name + "R", n-1)
        return v

    v = recurse(root, "node", int(log(n, 2)))
    root.good_version = v
    return root, v

@timeit
def linear_value_history_tree_write(root, n):

    def edit_recurse(node, versions):
        if not node:
            return

        version = node.good_version
        for i in range(n):
            version = node.set_field("v0", i, version)
            versions[node.name].append(version)

        version = node.earliest_version
        edit_recurse(node.get_field("left", version), versions)
        edit_recurse(node.get_field("right", version), versions)

    versions = defaultdict(list)
    edit_recurse(root, versions)
    return versions

@timeit
def linear_value_history_tree_read(root, versions):

    def read_recurse(node, versions):
        if not node:
            return

        for i, version in enumerate(versions[node.name]):
            val = node.get_field("v0", version)

        version = node.earliest_version
        read_recurse(node.get_field("left", version), versions)
        read_recurse(node.get_field("right", version), versions)

    read_recurse(root, versions)

@timeit
def earliest_history_tree_write(root, n):

    def edit_recurse(node, versions):
        if not node:
            return

        version = node.earliest_version
        for i in range(n):
            version = node.set_field("v0", i, version)
            versions[node.name].append(version)

        edit_recurse(node.get_field("left", version), versions)
        edit_recurse(node.get_field("right", version), versions)

        version = node.earliest_version
    versions = defaultdict(list)
    edit_recurse(root, versions)
    return versions

@timeit
def earliest_history_tree_read(root, versions):

    def read_recurse(node, versions):
        if not node:
            return

        for i, version in enumerate(versions[node.name]):
            val = node.get_field("v0", version)

        read_recurse(node.get_field("left", version), versions)
        read_recurse(node.get_field("right", version), versions)

    read_recurse(root, versions)

@timeit
def branching_history_tree_write(root, nt):
    def edit_recurse(node, versions):
        if not node:
            return

        edit_recurse_ver(node, node.earliest_version, int(log(nt, 2)), versions)

        version = node.earliest_version
        edit_recurse(node.get_field("left", version), versions)
        edit_recurse(node.get_field("right", version), versions)

    def edit_recurse_ver(node, v, n, versions):
        if n <= 1:
            return None

        left_v = node.set_field("v0", n, v)
        right_v = node.set_field("v0", n, v)
        versions[node.name].append(left_v)
        versions[node.name].append(right_v)
        edit_recurse_ver(node, left_v, n-1, versions)
        edit_recurse_ver(node, right_v, n-1, versions)

    versions = defaultdict(list)
    edit_recurse(root, versions)
    return versions

@timeit
def branching_history_tree_read(root, versions):

    def read_recurse(node, versions):
        if not node:
            return

        for i, version in enumerate(versions[node.name]):
            val = node.get_field("v0", version)

        version = node.earliest_version
        read_recurse(node.get_field("left", version), versions)
        read_recurse(node.get_field("right", version), versions)

    read_recurse(root, versions)

@timeit
def random_history_tree_write(root, n):
    def edit_recurse(node, all_versions):
        if not node:
            return

        versions = [node.earliest_version]
        for i in range(n):
            version = random.choice(versions)
            versions.append(node.set_field("v0", i, version))
        all_versions[node.name] = versions

        version = node.earliest_version
        edit_recurse(node.get_field("left", version), all_versions)
        edit_recurse(node.get_field("right", version), all_versions)

    versions = defaultdict(list)
    edit_recurse(root, versions)
    return versions

@timeit
def random_history_tree_read(root, versions):
    def read_recurse(node, versions):
        if not node:
            return

        for i, version in enumerate(versions[node.name]):
            val = node.get_field("v0", version)

        version = node.earliest_version
        read_recurse(node.get_field("left", version), versions)
        read_recurse(node.get_field("right", version), versions)

    read_recurse(root, versions)

def tree():
    ns1 = [2**n for n in range(8)]

    list_creation_ts = [create_tree(n)[1] for n in ns1]

    ns2 = [2**n for n in range(8)]

    TREE_SIZES = 1024
    linear_ts_write = []
    linear_ts_read = []
    for n in ns2:
        root, _ = create_tree(int(TREE_SIZES))
        root, _ = root
        versions, t = linear_value_history_tree_write(root, n)
        linear_ts_write.append(t)
        linear_ts_read.append(linear_value_history_tree_read(root, versions)[1])

    earliest_ts_write = []
    earliest_ts_read = []
    for n in ns2:
        root, _ = create_tree(int(TREE_SIZES))
        root, _ = root
        versions, t = earliest_history_tree_write(root, n)
        earliest_ts_write.append(t)
        earliest_ts_read.append(earliest_history_tree_read(root, versions)[1])

    branching_ts_write = []
    branching_ts_read = []
    for n in ns2:
        root, _ = create_tree(int(TREE_SIZES))
        root, _ = root
        versions, t = branching_history_tree_write(root, n)
        print(len(versions), n)
        branching_ts_write.append(t)
        branching_ts_read.append(branching_history_tree_read(root, versions)[1])

    random_ts_write = []
    random_ts_read = []
    for n in ns2:
        root, _ = create_tree(int(TREE_SIZES))
        root, _ = root
        versions, t = random_history_tree_write(root, n)
        print(len(versions), n)
        random_ts_write.append(t)
        random_ts_read.append(random_history_tree_read(root, versions)[1])


    print("========CREATION TIMES================")
    print(asymptotic(list_creation_ts,
          [n - 1 if n % 2 == 0 else n for n in ns1])
         )
    print()
    print("========LINEAR HISTORY CREATION=======")
    print(asymptotic(linear_ts_write, ns2))
    print()
    print("========LINEAR HISTORY READ=======")
    print(asymptotic(linear_ts_read, ns2))
    print()
    print("========EARLIEST HISTORY CREATION========")
    print(asymptotic(earliest_ts_write, ns2))
    print()
    print("========EARLIEST HISTORY READ========")
    print(asymptotic(earliest_ts_read, ns2))
    print()
    print("========BRANCHING HISTORY CREATION========")
    print(asymptotic(branching_ts_write, ns2))
    print()
    print("========BRANCHING HISTORY READ========")
    print(asymptotic(branching_ts_read, ns2))
    print()
    print("========RANDOM HISTORY CREATION========")
    print(asymptotic(random_ts_write, ns2))
    print()
    print("========RANDOM HISTORY READ========")
    print(asymptotic(random_ts_read, ns2))
    print()

# BSTS

@timeit
def random_large_bst(n):
    tree = FPBST()
    v0 = tree.earliest_version
    versions = [v0]
    ivs = []
    for _ in range(n):
        i = random.randint(0, n)
        v = random.choice(versions)
        v = tree.insert(i, v)
        ivs.append((i, v))

    random.shuffle(ivs)

    for i, v in ivs:
        tree.find(i, v)

def bst():
    ns2 = [2**n for n in range(8)]
    random_ts = []
    for n in ns2:
        random_ts.append(random_large_bst(n)[1])

    print(asymptotic(random_ts, ns2))


if __name__ == '__main__':
    print("==========================")
    print("==========LIST===========")
    print("==========================")
    print()
    linked_list()
    print("==========================")
    print("===========TREE===========")
    print("==========================")
    print()
    tree()
    print("==========================")
    print("============BST===========")
    print("==========================")
    print()
    bst()
