import unittest
from cscl.cardinality_constraints_encoders import *


def has_k_bits_trivial(i, k):
    """
    Determines whether i has exactly k bits set to one.

    :param i: A non-negative integer.
    :param k: A non-negative integer
    :return: True if i has exactly k bits set to one, False otherwise.
    """
    assert(i >= 0)

    counter = 0
    while i > 0:
        if i & 1 != 0:
            counter += 1
        i = i >> 1

    return counter == k


def select_items_by_bits(lst, i):
    """
    Selects items from lst indexed by the bits in i.

    :param lst: A list.
    :param i: A non-negative integer whose most significant bit is at a position lesser than len(lst).
    :return: A list containing all lst[k] where (i & (1 << k)) == 1.
    """
    assert (i >= 0)

    result = []
    counter = 0
    while i > 0:
        if i & 1 != 0:
            result.append(lst[counter])
        i = i >> 1
        counter += 1

    return result


def subsets_of_size_k_trivial(lst, k):
    """
    Computes all subsets of size k in a simple fashion.

    :param lst: A list.
    :param k: A non-negative integer.
    :return: A list containing all size-k subsets of collection.
    """
    if k > len(lst):
        return []
    if k == 0:
        return [[]]
    if k == len(lst):
        return [lst]

    result = []
    for i in range(0, 2**len(lst)):
        if has_k_bits_trivial(i, k):
            result.append(select_items_by_bits(lst, i))

    return result


def sorted_tuples(sequence):
    """
    Transforms the given sequence of lists to a sequence of sorted tuples.

    :param sequence: A sequence (l1, ..., lN) of lists.
    :return: A sequence (s1, ..., sN) with sI being the sorted tuple containing the values of lI.
    """
    sorted_seq = map(sorted, sequence)
    return map(tuple, sorted_seq)


def subsets_of_size_k_test(collection, max_k):
    """
    Tests subsets_of_size_k() by comparing its result to subsets_of_size_k_trivial().

    The test is performed for the given list and k in range(0, max_k+1). If the
    results of the two implementations differ, an assertion fails.

    :param collection: A list.
    :param max_k: The maximum value of k, a non-negative integer.
    :return: None
    """
    print("Testing subsets_of_size_k for " + str(collection))
    for k in range(0, max_k+1):
        print("  ...and k=" + str(k))
        subsets = subsets_of_size_k(list(collection), k)
        expected = subsets_of_size_k_trivial(list(collection), k)
        fail_msg = "Unexpected result: " + str(subsets) + "\n\nExpected: " + str(expected)
        assert (len(subsets) == len(expected)), fail_msg
        assert (set(sorted_tuples(subsets)) == set(sorted_tuples(expected))), fail_msg


class TestSubsetsOfSizeK(unittest.TestCase):
    def test_empty_list_has_empty_subset(self):
        subsets = subsets_of_size_k([], 0)
        assert (subsets == [[]]), "Bad subsets: " + str(subsets)

    def test_empty_list_has_no_subsets_of_size_1(self):
        subsets = subsets_of_size_k([], 1)
        assert (len(subsets) == 0), "Bad subsets: " + str(subsets)

    def test_list_len_1(self):
        subsets_of_size_k_test([2], 2)

    def test_list_len_2(self):
        subsets_of_size_k_test([3, 2], 3)

    def test_list_len_2(self):
        subsets_of_size_k_test([3, 2], 4)

    def test_list_len_4(self):
        subsets_of_size_k_test([3, 2, 5, 6], 5)

    def test_list_len_6(self):
        subsets_of_size_k_test([3, 2, 5, 6, -1, -2], 7)
