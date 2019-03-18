import unittest
import abc
from cscl.cardinality_constraint_encoders import *
from cscl_tests.testutils.trivial_sat_solver import TrivialSATSolver
from cscl_tests.testutils.logging_clause_consumer_decorator import LoggingClauseConsumerDecorator


def has_k_bits_trivial(i, k):
    """
    Determines whether i has exactly k bits set to one.

    :param i: A non-negative integer.
    :param k: A non-negative integer
    :return: True if i has exactly k bits set to one, False otherwise.
    """

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


class TestSubsetsOfSizeK(unittest.TestCase):
    def test_empty_list_has_empty_subset(self):
        subsets = subsets_of_size_k([], 0)
        self.assertEqual(subsets,  [[]], "Bad subsets: " + str(subsets))

    def test_empty_list_has_no_subsets_of_size_1(self):
        subsets = subsets_of_size_k([], 1)
        self.assertEqual(len(subsets), 0, "Bad subsets: " + str(subsets))

    def __subsets_of_size_k_test(self, collection, max_k):
        """
        Tests subsets_of_size_k() by comparing its result to subsets_of_size_k_trivial().

        The test is performed for the given list and k in range(0, max_k+1). If the
        results of the two implementations differ, an assertion fails.

        :param collection: A list.
        :param max_k: The maximum value of k, a non-negative integer.
        :return: None
        """
        for k in range(0, max_k + 1):
            subsets = subsets_of_size_k(list(collection), k)
            expected = subsets_of_size_k_trivial(list(collection), k)
            fail_msg = "Unexpected result: " + str(subsets) + "\n\nExpected: " + str(expected) \
                       + "\nPicked from: " + str(collection) + "\nwith k=" + str(k)
            self.assertEqual(len(subsets), len(expected), fail_msg)
            self.assertEqual(set(sorted_tuples(subsets)), set(sorted_tuples(expected)), fail_msg)

    def test_list_len_1(self):
        self.__subsets_of_size_k_test([2], 2)

    def test_list_len_2(self):
        self.__subsets_of_size_k_test([3, 2], 3)

    def test_list_len_4(self):
        self.__subsets_of_size_k_test([3, 2, 5, 6], 5)

    def test_list_len_6(self):
        self.__subsets_of_size_k_test([3, 2, 5, 6, -1, -2], 7)


class AbstractEncodeAtMostKConstraintTestCase(abc.ABC):

    def __init__(self):
        if not isinstance(self, unittest.TestCase):
            raise RuntimeError("This mixin may only be used with test cases, since it uses self.assert*")

    @abc.abstractmethod
    def get_encoder_fn(self):
        pass

    def test_constraining_no_lits_yields_empty_problem(self):
        lit_factory = TrivialSATSolver()
        encoder = self.get_encoder_fn()
        result = encoder(lit_factory, 2, [])
        # noinspection PyUnresolvedReferences
        self.assertEqual(result, [])

    def test_constraining_single_lit_with_k0_yields_unary_clause(self):
        lit_factory = TrivialSATSolver()
        encoder = self.get_encoder_fn()
        result = encoder(lit_factory, 0, [1])
        # noinspection PyUnresolvedReferences
        self.assertEqual(result, [[-1]], "Bad encoding: " + str(result))

    def test_constraining_single_lit_with_k1_yields_empty_problem(self):
        lit_factory = TrivialSATSolver()
        encoder = self.get_encoder_fn()
        result = encoder(lit_factory, 1, [1])
        # noinspection PyUnresolvedReferences
        self.assertEqual(result, [], "Bad encoding: " + str(result))

    def test_constraining_single_lit_with_k2_yields_empty_problem(self):
        lit_factory = TrivialSATSolver()
        encoder = self.get_encoder_fn()
        result = encoder(lit_factory, 2, [1])
        # noinspection PyUnresolvedReferences
        self.assertEqual(result, [], "Bad encoding: " + str(result))

    def __at_most_k_constraint_encoder_test(self, encoder, amnt_constrained_lits):
        """
        Tests the given at-most-k-constraint encoder for constraining amnt_constraint_lits literals.

        The encoder is tested for amnt_constraint_lits and for each k in range(0, amnt_constrained_lits+2),
        with all assignment combinations being tested. On failure, an assertion fails.

        :param encoder: The at-most-k-constraint encoder to be tested.
        :param amnt_constrained_lits: The amount of literals to be constrained for testing.
        :return: None
        """
        for k in range(0, amnt_constrained_lits + 2):
            checker = TrivialSATSolver()
            constrained_lits = []
            for i in range(0, amnt_constrained_lits):
                constrained_lits.append(checker.create_literal())

            constraint = encoder(checker, k, constrained_lits)
            logging_checker = LoggingClauseConsumerDecorator(checker)
            for clause in constraint:
                logging_checker.consume_clause(clause)

            def check_constraint_for_l_lits_set_true(l, expected_satisfiable):
                all_assumptions = subsets_of_size_k_trivial(constrained_lits, l)
                for assumptions in all_assumptions:
                    # noinspection PyUnresolvedReferences
                    self.assertEqual(checker.solve(assumptions), expected_satisfiable,
                                     "Failed for k=" + str(k) + ", assumptions=" + str(assumptions)
                                     + "\nBad constraint:\n" +
                                     logging_checker.to_string())

            for x in range(0, k + 1):
                check_constraint_for_l_lits_set_true(x, True)

            for x in range(k + 1, amnt_constrained_lits + 1):
                check_constraint_for_l_lits_set_true(x, False)

    def test_constraining_2lits(self):
        self.__at_most_k_constraint_encoder_test(self.get_encoder_fn(), 2)

    def test_constraining_3lits(self):
        self.__at_most_k_constraint_encoder_test(self.get_encoder_fn(), 3)

    def test_constraining_5lits(self):
        self.__at_most_k_constraint_encoder_test(self.get_encoder_fn(), 5)


class TestEncodeAtMostKConstraintBinomial(unittest.TestCase, AbstractEncodeAtMostKConstraintTestCase):
    def get_encoder_fn(self):
        return encode_at_most_k_constraint_binomial


class TestEncodeAtMostKConstraintLTSeq(unittest.TestCase, AbstractEncodeAtMostKConstraintTestCase):
    def get_encoder_fn(self):
        return encode_at_most_k_constraint_ltseq


class TestEncodeAtMostKConstraintCommander(unittest.TestCase, AbstractEncodeAtMostKConstraintTestCase):
    def get_encoder_fn(self):
        return encode_at_most_k_constraint_commander


class TestChunks(unittest.TestCase):
    def test_raises_for_negative_chunk_size(self):
        with self.assertRaises(ValueError):
            list(chunks([1], -1))

    def test_raises_for_zero_chunk_size(self):
        with self.assertRaises(ValueError):
            list(chunks([1], 0))

    def test_returns_empty_list(self):
        result = list(chunks([], 2))
        self.assertEqual(result, [], "Unexpected result " + str(result))

    def test_chunks_single_element_list_with_chunk_size_1(self):
        result = list(chunks([1], 1))
        self.assertEqual(result, [[1]], "Unexpected result " + str(result))

    def test_chunks_list_with_list_len_smaller_than_chunk_size(self):
        result = list(chunks([1, 2, 3, 4, 5], 10))
        self.assertEqual(result, [[1, 2, 3, 4, 5]], "Unexpected result " + str(result))

    def test_chunks_list_with_list_len_not_divisible_by_chunk_size(self):
        result = list(chunks([1, 2, 3, 4, 5], 3))
        self.assertEqual(result, [[1, 2, 3], [4, 5]], "Unexpected result " + str(result))

    def test_chunks_list_with_list_len_divisible_by_chunk_size(self):
        result = list(chunks([1, 2, 3, 4, 5, 6], 3))
        self.assertEqual(result, [[1, 2, 3], [4, 5, 6]], "Unexpected result " + str(result))
