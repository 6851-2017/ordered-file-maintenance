import cProfile
import unittest
import time
import random
from math import log
from collections import defaultdict
from fpbst import FPBST
from full_persistence import FPPM
from full_persistence import FPNode
from multiprocessing import Pool


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
    xs = ["{}\t{}".format(n, x) for x, n in zip(xs, ns)]
    return '\n'.join(xs)

def csv_line(struct, test, rw, p, d, T, struct_n, hist_n, t):
    print("{},{},{},{},{},{},{},{},{}".format(
            struct,
            test,
            rw,
            p,
            d,
            T,
            struct_n,
            hist_n,
            t,
    ))

@timeit
def create_linked_list(n, T, p, d):
    # Initialize Fully Persitent Pointer Machine
    fppm = FPPM(d=d, p=p, T=T)
    node = fppm.get_root(fppm.first_version)
    v = fppm.first_version
    for i in range(1, n):
        next_node = FPNode("n{}".format(i), fppm, v)
        v = node.set_field("p0", next_node, v)
        node = node.get_field("p0", v)

    return fppm.get_root(v), v

@timeit
def list_linear_write(root, v, n):
    versions = defaultdict(list)

    node = root
    n_i = 0
    while node:
        version = v
        for i in range(n):
            version = node.set_field("v0", i, version)
            versions[n_i].append(version)
        node = node.get_field("p0", version)
        n_i += 1

    return versions

@timeit
def list_linear_read(root, versions):
    node = root
    for n_i in range(len(versions)):
        node_versions = versions[n_i]
        for i, version in enumerate(node_versions):
            val = node.get_field("v0", version)
            #assert(val == i)

@timeit
def list_earliest_write(root, v, n):
    versions = defaultdict(list)

    node = root
    n_i = 0
    while node:
        for i in range(n):
            version = node.set_field("v0", i, v)
            versions[n_i].append(version)
        node = node.get_field("p0", version)
        n_i += 1

    return versions

@timeit
def list_earliest_read(root, versions):
    node = root
    for n_i in range(len(versions)):
        node_versions = versions[n_i]
        for i, version in enumerate(node_versions):
            val = node.get_field("v0", version)
            #assert(val == i)

@timeit
def list_branching_write(root, v, n):
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
        recurse(node, v, int(log(n, 2)), n_i)
        node = node.get_field("p0", v)
        n_i += 1

    return versions

@timeit
def list_branching_read(root, versions):
    node = root
    for n_i in range(len(versions)):
        node_versions = versions[n_i]
        for i, version in enumerate(node_versions):
            val = node.get_field("v0", version)
            #assert(val == i)

@timeit
def list_random_write(root, v, n):
    all_versions = defaultdict(list)

    node = root
    n_i = 0
    while node:
        versions = [v]
        for i in range(n):
            version = random.choice(versions)
            new_version = node.set_field("v0", i, version)
            versions.append(new_version)
            all_versions[n_i].append(new_version)
        node = node.get_field("p0", version)
        n_i += 1

    return all_versions

@timeit
def list_random_read(root, versions):
    node = root
    for n_i in range(len(versions)):
        node_versions = versions[n_i]
        for i, version in enumerate(node_versions):
            val = node.get_field("v0", version)
            #assert(val == i)

LINKED_SIZE = 64
def linked_list():
    ns1 = [2**n for n in range(8)]
    ns2 = [2**n for n in range(8)]

    list_creation_ts = [create_linked_list(n)[1] for n in ns1]

    linear_ts = []
    linear_ts_read = []
    for n in ns2:
        print(n)
        (root, v), _ = create_linked_list(int(LINKED_SIZE))
        versions, t = linear_value_history_sweep_write(root, v, n)
        linear_ts.append(t)
        linear_ts_read.append(linear_value_history_sweep_read(root, versions)[1])

    earliest_ts = []
    earliest_ts_read = []
    for n in ns2:
        (root, v), _ = create_linked_list(int(LINKED_SIZE))
        versions, t = earliest_history_sweep_write(root, v, n)
        earliest_ts.append(t)
        earliest_ts_read.append(earliest_history_sweep_read(root, versions)[1])

    branching_ts = []
    branching_ts_read = []
    for n in ns2:
        (root, v), _ = create_linked_list(int(LINKED_SIZE))
        versions, t = branching_history_sweep_write(root, v, n)
        branching_ts.append(t)
        branching_ts_read.append(branching_history_sweep_read(root, versions)[1])

    random_ts = []
    random_ts_read = []
    for n in ns2:
        (root, v), _ = create_linked_list(int(LINKED_SIZE))
        versions, t = random_history_sweep_write(root, v, n)
        random_ts.append(t)
        random_ts_read.append(random_history_sweep_read(root, versions)[1])

    print("========CREATION TIMES================")
    print("T0 = {}".format(list_creation_ts[0]))
    print(asymptotic(list_creation_ts, ns1))
    print()
    print()
    print("For linked list of size {}".format(LINKED_SIZE))
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
def create_tree(n, p, d, T):
    # Initialize Fully Persitent Pointer Machine
    fppm = FPPM(p=p, d=d, T=T)

    # Setup node0 and node1
    root = FPNode("root", fppm, fppm.first_version)
    def recurse(node, name, v, n):
        if n <= 1 or node is None:
            return v

        left_n = FPNode(name + "L", fppm, v)
        right_n = FPNode(name + "R", fppm, v)
        v = node.set_field("left", left_n, v)
        v = node.set_field("right", right_n, v)
        v = recurse(left_n, name + "L", v, n-1)
        v = recurse(right_n, name + "R", v, n-1)
        return v

    v = fppm.first_version
    v = recurse(root, "node", v, int(log(n, 2)))
    return root, v

@timeit
def linear_history_tree_write(root, v, n):

    def edit_recurse(node, versions):
        if not node:
            return

        version = v
        for i in range(n):
            version = node.set_field("v0", i, version)
            versions[node.name].append(version)

        edit_recurse(node.get_field("left", v), versions)
        edit_recurse(node.get_field("right", v), versions)

    versions = defaultdict(list)
    edit_recurse(root, versions)
    return versions

@timeit
def linear_history_tree_read(root, v, versions):

    def read_recurse(node, versions):
        if not node:
            return

        for i, version in enumerate(versions[node.name]):
            val = node.get_field("v0", version)

        read_recurse(node.get_field("left", v), versions)
        read_recurse(node.get_field("right", v), versions)

    read_recurse(root, versions)

@timeit
def earliest_history_tree_write(root, v, n):

    def edit_recurse(node, versions):
        if not node:
            return

        version = v
        for i in range(n):
            new_version = node.set_field("v0", i, version)
            versions[node.name].append(new_version)

        edit_recurse(node.get_field("left", v), versions)
        edit_recurse(node.get_field("right", v), versions)

    versions = defaultdict(list)
    edit_recurse(root, versions)
    return versions

@timeit
def earliest_history_tree_read(root, v, versions):

    def read_recurse(node, versions):
        if not node:
            return

        for i, version in enumerate(versions[node.name]):
            val = node.get_field("v0", version)

        read_recurse(node.get_field("left", v), versions)
        read_recurse(node.get_field("right", v), versions)

    read_recurse(root, versions)

@timeit
def branching_history_tree_write(root, v, nt):
    def edit_recurse(node, versions):
        if not node:
            return

        edit_recurse_ver(node, v, int(log(nt, 2)), versions)

        version = v
        edit_recurse(node.get_field("left", version), versions)
        edit_recurse(node.get_field("right", version), versions)

    def edit_recurse_ver(node, v2, n, versions):
        if n <= 1:
            return None

        left_v = node.set_field("v0", n, v2)
        right_v = node.set_field("v0", n, v2)
        versions[node.name].append(left_v)
        versions[node.name].append(right_v)
        edit_recurse_ver(node, left_v, n-1, versions)
        edit_recurse_ver(node, right_v, n-1, versions)

    versions = defaultdict(list)
    edit_recurse(root, versions)
    return versions

@timeit
def branching_history_tree_read(root, v, versions):

    def read_recurse(node, versions):
        if not node:
            return

        for i, version in enumerate(versions[node.name]):
            val = node.get_field("v0", version)

        read_recurse(node.get_field("left", v), versions)
        read_recurse(node.get_field("right", v), versions)

    read_recurse(root, versions)

@timeit
def random_history_tree_write(root, v, n):
    def edit_recurse(node, all_versions):
        if not node:
            return

        versions = [v]
        for i in range(n):
            version = random.choice(versions)
            versions.append(node.set_field("v0", i, version))
        all_versions[node.name] = versions

        version = v
        edit_recurse(node.get_field("left", version), all_versions)
        edit_recurse(node.get_field("right", version), all_versions)

    versions = defaultdict(list)
    edit_recurse(root, versions)
    return versions

@timeit
def random_history_tree_read(root, v, versions):
    def read_recurse(node, versions):
        if not node:
            return

        for i, version in enumerate(versions[node.name]):
            val = node.get_field("v0", version)

        read_recurse(node.get_field("left", v), versions)
        read_recurse(node.get_field("right", v), versions)

    read_recurse(root, versions)

TREE_SIZES = 16
def tree():
    ns1 = [2**n for n in range(12)]

    list_creation_ts = [create_tree(n)[1] for n in ns1]

    ns2 = [2**n for n in range(12)]

    linear_ts_write = []
    linear_ts_read = []
    for n in ns2:
        (root, v), _ = create_tree(int(TREE_SIZES))
        versions, t = linear_value_history_tree_write(root, v, n)
        linear_ts_write.append(t)
        linear_ts_read.append(linear_value_history_tree_read(root, v, versions)[1])

    earliest_ts_write = []
    earliest_ts_read = []
    for n in ns2:
        (root, v), _ = create_tree(int(TREE_SIZES))
        versions, t = earliest_history_tree_write(root, v, n)
        earliest_ts_write.append(t)
        earliest_ts_read.append(earliest_history_tree_read(root, v, versions)[1])

    branching_ts_write = []
    branching_ts_read = []
    for n in ns2:
        (root, v), _ = create_tree(int(TREE_SIZES))
        versions, t = branching_history_tree_write(root, v, n)
        branching_ts_write.append(t)
        branching_ts_read.append(branching_history_tree_read(root, v, versions)[1])

    random_ts_write = []
    random_ts_read = []
    for n in ns2:
        (root, v), _ = create_tree(int(TREE_SIZES))
        versions, t = random_history_tree_write(root, v, n)
        random_ts_write.append(t)
        random_ts_read.append(random_history_tree_read(root, v, versions)[1])


    print("========CREATION TIMES================")
    print(asymptotic(list_creation_ts,
          [n - 1 if n % 2 == 0 else n for n in ns1])
         )
    print()
    print("For tree of size {}".format(TREE_SIZES))
    print()
    print("========LINEAR HISTORY CREATION=======")
    print("T0 = {}".format(linear_ts_write[0]))
    print(asymptotic(linear_ts_write, ns2))
    print()
    print("========LINEAR HISTORY READ=======")
    print("T0 = {}".format(linear_ts_read[0]))
    print(asymptotic(linear_ts_read, ns2))
    print()
    print("========EARLIEST HISTORY CREATION========")
    print("T0 = {}".format(branching_ts_write[0]))
    print(asymptotic(earliest_ts_write, ns2))
    print()
    print("========EARLIEST HISTORY READ========")
    print("T0 = {}".format(earliest_ts_read[0]))
    print(asymptotic(earliest_ts_read, ns2))
    print()
    print("========BRANCHING HISTORY CREATION========")
    print("T0 = {}".format(branching_ts_write[0]))
    print(asymptotic(branching_ts_write, ns2))
    print()
    print("========BRANCHING HISTORY READ========")
    print("T0 = {}".format(branching_ts_read[0]))
    print(asymptotic(branching_ts_read, ns2))
    print()
    print("========RANDOM HISTORY CREATION========")
    print("T0 = {}".format(random_ts_write[0]))
    print(asymptotic(random_ts_write, ns2))
    print()
    print("========RANDOM HISTORY READ========")
    print("T0 = {}".format(random_ts_read[0]))
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

