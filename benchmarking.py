import unittest
import time
import random
from math import log
from full_persistence import FPPM
from full_persistence import FPNode


# Linked list

# 4 depth binary history for each node


def timeit(f):
    def wrapper(*args, **kwargs):
        t1 = time.process_time()
        ret = f(*args, **kwargs)
        t2 = time.process_time()
        return ret, (t2 - t1)
    return wrapper

def asymptotic(xs, ns):
    return [x / xs[0] / n for x, n in zip(xs, ns)]

@timeit
def create_linked_list(n):
    # Initialize Fully Persitent Pointer Machine
    fppm = FPPM()

    # Setup node0 and node1
    root = FPNode("root", fppm, fppm.first_version)

    prev_node = root
    for i in range(1, n):
        cur_node = FPNode("n{}".format(i), fppm, fppm.first_version)
        prev_node.set_field("p0", cur_node, fppm.first_version)
        prev_node = cur_node

    return root

@timeit
def linear_value_history_sweep(root, n):
    node = root
    while node:
        version = node.earliest_version
        for i in range(n):
            version = node.set_field("v0", i, version)
        node = node.get_field("p0", version)

@timeit
def earliest_history_sweep(root, n):
    node = root
    while node:
        for i in range(n):
            version = node.set_field("v0", i, node.earliest_version)
        node = node.get_field("p0", version)

@timeit
def branching_history_sweep(root, n):

    def recurse(node, v, n):
        if n <= 0:
            return None

        left_v = node.set_field("v0", n, v)
        right_v = node.set_field("v0", n, v)
        recurse(node, left_v, n-1)
        recurse(node, right_v, n-1)

    node = root
    while node:
        recurse(node, node.earliest_version, int(log(n, 2)))
        node = node.get_field("p0", node.earliest_version)


@timeit
def random_history_sweep(root, n):
    node = root
    while node:
        versions = [node.earliest_version]
        for i in range(n):
            version = random.choice(versions)
            versions.append(node.set_field("v0", i, version))
        node = node.get_field("p0", version)

def linked_list():
    ns1 = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

    list_creation_ts = [create_linked_list(n)[1] for n in ns1]

    ns2 = [1, 10, 100, 500, 1000]

    linear_ts = []
    for n in ns2:
        root, _ = create_linked_list(int(3e3))
        linear_ts.append(linear_value_history_sweep(root, n)[1])

    earliest_ts = []
    for n in ns2:
        root, _ = create_linked_list(int(3e3))
        earliest_ts.append(earliest_history_sweep(root, n)[1])

    branching_ts = []
    for n in ns2:
        root, _ = create_linked_list(int(3e3))
        branching_ts.append(branching_history_sweep(root, n)[1])

    random_ts = []
    for n in ns2:
        root, _ = create_linked_list(int(3e3))
        random_ts.append(random_history_sweep(root, n)[1])

    print("========CREATION TIMES================")
    print(asymptotic(list_creation_ts, ns1))
    print()
    print()
    print("========LINEAR HISTORY CREATION=======")
    print(asymptotic(linear_ts, ns2))
    print()
    print()
    print("========EARLIEST HISTORY CREATION========")
    print(asymptotic(earliest_ts, ns2))
    print()
    print()
    print("========BRANCHING HISTORY CREATION========")
    print(asymptotic(branching_ts, ns2))
    print()
    print()
    print("========RANDOM HISTORY CREATION========")
    print(asymptotic(random_ts, ns2))
    print()
    print()

######################
### TREE STUFF #######
######################

@timeit
def create_tree(n):
    # Initialize Fully Persitent Pointer Machine
    fppm = FPPM()

    # Setup node0 and node1
    root = FPNode("root", fppm, fppm.first_version)

    def recurse(node, name, n):
        if n <= 0:
            return None

        left_n = FPNode(name + "L", fppm, node.earliest_version)
        right_n = FPNode(name + "R", fppm, node.earliest_version)
        v = node.set_field("left", left_n, node.earliest_version)
        v = node.set_field("right", right_n, v)
        recurse(node, name + "L", n-1)
        recurse(node, name + "R", n-1)
        return v

    v = recurse(root, "node", int(log(n, 2)))
    return root, v

@timeit
def linear_value_history_tree(root, n):
    def recurse(node):
        if not node:
            return

        version = node.earliest_version
        for i in range(n):
            version = node.set_field("v0", i, version)

        version = node.earliest_version
        recurse(node.get_field("left", version))
        recurse(node.get_field("right", version))

    recurse(root)

@timeit
def earliest_history_tree(root, n):
    def recurse(node):
        if not node:
            return

        version = node.earliest_version
        for i in range(n):
            node.set_field("v0", i, version)

        recurse(node.get_field("left", version))
        recurse(node.get_field("right", version))

    recurse(root)

@timeit
def branching_history_tree(root, nt):
    def recurse(node):
        if not node:
            return

        recurse_ver(node, node.earliest_version, int(log(nt, 2)))

        version = node.earliest_version
        recurse(node.get_field("left", version))
        recurse(node.get_field("right", version))

    def recurse_ver(node, v, n):
        if n <= 0:
            return None

        left_v = node.set_field("v0", n, v)
        right_v = node.set_field("v0", n, v)
        recurse_ver(node, left_v, n-1)
        recurse_ver(node, right_v, n-1)

    recurse(root)

@timeit
def random_history_tree(root, n):
    def recurse(node):
        if not node:
            return

        versions = [node.earliest_version]
        for i in range(n):
            version = random.choice(versions)
            versions.append(node.set_field("v0", i, version))

        version = node.earliest_version
        recurse(node.get_field("left", version))
        recurse(node.get_field("right", version))

    recurse(root)

def tree():
    ns1 = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]

    list_creation_ts = [create_tree(n)[1] for n in ns1]

    ns2 = [1, 10, 100, 500, 1000]

    linear_ts = []
    for n in ns2:
        root, _ = create_tree(int(3e3))
        root, _ = root
        linear_ts.append(linear_value_history_tree(root, n)[1])

    earliest_ts = []
    for n in ns2:
        root, _ = create_tree(int(3e3))
        root, _ = root
        earliest_ts.append(earliest_history_tree(root, n)[1])

    branching_ts = []
    for n in ns2:
        root, _ = create_tree(int(3e3))
        root, _ = root
        branching_ts.append(branching_history_tree(root, n)[1])

    random_ts = []
    for n in ns2:
        root, _ = create_tree(int(3e3))
        root, _ = root
        random_ts.append(random_history_tree(root, n)[1])

    print("========CREATION TIMES================")
    print(asymptotic(list_creation_ts, ns1))
    print()
    print("========LINEAR HISTORY CREATION=======")
    print(asymptotic(linear_ts, ns2))
    print()
    print("========EARLIEST HISTORY CREATION========")
    print(asymptotic(earliest_ts, ns2))
    print()
    print("========BRANCHING HISTORY CREATION========")
    print(asymptotic(branching_ts, ns2))
    print()
    print("========RANDOM HISTORY CREATION========")
    print(asymptotic(random_ts, ns2))
    print()


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
