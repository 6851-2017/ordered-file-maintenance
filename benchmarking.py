from bench_base import *

def test_suite():
    # list_creation_ts = [create_linked_list(n)[1] for n in ns1]

    print("Structure,Test,ReadWrite,P,D,T,struct_n,hist_n,t")
    ps = (3, 10, 20)
    ds = ps
    Ts = (1.1, 1.5, 2.0)
    struct_ns = [32]
    rounds = 3
    hist_ns = [2**n for n in range(8)]

    pool = Pool(64)
    args = []
    for p in ps:
        for d in ds:
            for T in Ts:
                for test in list_tests:
                    for struct_n in struct_ns:
                        for hist_n in hist_ns:
                            args.append((p, d, T, test,
                                        rounds, struct_n, hist_n))
    pool.map(list_f, args)

    for p in ps:
        for d in ds:
            for T in Ts:
                for test in tree_tests:
                    for struct_n in struct_ns:
                        for hist_n in hist_ns:
                            args.append((p, d, T, test,
                                        rounds, struct_n, hist_n))
    pool.map(tree_f, args)

list_tests = {'linear': (list_linear_write, list_linear_read),
              'branching': (list_branching_write, list_branching_read),
              'earliest': (list_earliest_write, list_earliest_read),
              'random': (list_random_write, list_random_read),
             }

tree_tests = {'linear': (linear_history_tree_write, linear_history_tree_read),
              'branching': (branching_history_tree_write, branching_history_tree_read),
              'earliest': (earliest_history_tree_write, earliest_history_tree_read),
              'random': (random_history_tree_write, random_history_tree_read),
             }

def list_f(args):
    (p, d, T, test, rounds, struct_n, hist_n) = args
    w_func, r_func = list_tests[test]
    tw = 0
    tr = 0
    for _ in range(rounds):
        (root, v), _ = create_linked_list(struct_n, T, p, d)
        (vs, t) = w_func(root, v, hist_n)
        tw += t

        (_, t) = r_func(root, vs)
        tr += t

    tw = tw / rounds
    tr = tr / rounds

    csv_line('list', test, 'write', p, d, T, struct_n, hist_n, tw)
    csv_line('list', test, 'read', p, d, T, struct_n, hist_n, tr)

def tree_f(args):
    (p, d, T, test, rounds, struct_n, hist_n) = args
    w_func, r_func = list_tests[test]
    tw = 0
    tr = 0
    for _ in range(rounds):
        (root, v), _ = create_tree(struct_n, T, p, d)
        (vs, t) = w_func(root, v, hist_n)
        tw += t

        (_, t) = r_func(root, vs)
        tr += t

    tw = tw / rounds
    tr = tr / rounds

    csv_line('tree', test, 'write', p, d, T, struct_n, hist_n, tw)
    csv_line('tree', test, 'read', p, d, T, struct_n, hist_n, tr)

if __name__ == '__main__':
    test_suite()

    """
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
    """
