import unittest
import cscl_examples.smt_qfbv_solver.sorts as sorts


class TestSortContext(unittest.TestCase):
    def test_has_integer_sort(self):
        under_test = sorts.SortContext()
        int_sort = under_test.get_int_sort()
        assert isinstance(int_sort, sorts.IntegerSort)

    def test_is_integer_sort_unique(self):
        under_test = sorts.SortContext()
        int_sort_a = under_test.get_int_sort()
        int_sort_b = under_test.get_int_sort()
        assert int_sort_a is int_sort_b

    def test_has_binary_bv_sort(self):
        under_test = sorts.SortContext()
        bv_sort = under_test.get_bv_sort(2)
        assert isinstance(bv_sort, sorts.BitvectorSort)
        assert bv_sort.get_len() == 2

    def test_has_ternary_bv_sort(self):
        under_test = sorts.SortContext()
        bv_sort = under_test.get_bv_sort(3)
        assert isinstance(bv_sort, sorts.BitvectorSort)
        assert bv_sort.get_len() == 3

    def test_is_bv_sort_unique(self):
        under_test = sorts.SortContext()
        bv_sort_a = under_test.get_bv_sort(3)
        bv_sort_b = under_test.get_bv_sort(3)
        assert bv_sort_a is bv_sort_b

    def test_has_bool_sort(self):
        under_test = sorts.SortContext()
        bool_sort = under_test.get_bool_sort()
        assert isinstance(bool_sort, sorts.BooleanSort)

    def test_is_bool_sort_unique(self):
        under_test = sorts.SortContext()
        bool_sort_a = under_test.get_bool_sort()
        bool_sort_b = under_test.get_bool_sort()
        assert bool_sort_a is bool_sort_b
