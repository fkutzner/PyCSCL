import unittest
import examples.smt_qfbv_solver.smtlib2_parser as smt
import examples.smt_qfbv_solver.sorts as sorts
import examples.smt_qfbv_solver.ast as ast


class TestParseSmtlib2Literal(unittest.TestCase):
    def test_fails_for_empty_string(self):
        sort_ctx = sorts.SortContext()
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_literal("", sort_ctx)

    def test_fails_for_fp_lit(self):
        sort_ctx = sorts.SortContext()
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_literal("1.0", sort_ctx)

    def test_parses_int0(self):
        sort_ctx = sorts.SortContext()
        result = smt.parse_smtlib2_literal("0", sort_ctx)
        assert result.get_literal() is 0, "Unexpected result " + str(result)
        assert isinstance(result.get_sort(), sorts.IntegerSort)

    def test_parses_int12(self):
        sort_ctx = sorts.SortContext()
        result = smt.parse_smtlib2_literal("12", sort_ctx)
        assert result.get_literal() is 12, "Unexpected result " + str(result)
        assert isinstance(result.get_sort(), sorts.IntegerSort)

    def test_fails_for_int_with_extra_leading_0(self):
        sort_ctx = sorts.SortContext()
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_literal("001", sort_ctx)

    def test_parses_bv0(self):
        sort_ctx = sorts.SortContext()
        result = smt.parse_smtlib2_literal("#b0", sort_ctx)
        assert result.get_literal() is 0, "Unexpected result " + str(result)
        assert isinstance(result.get_sort(), sorts.BitvectorSort)
        assert result.get_sort().get_len() == 1

    def test_parses_bv2(self):
        sort_ctx = sorts.SortContext()
        result = smt.parse_smtlib2_literal("#b10", sort_ctx)
        assert result.get_literal() is 2, "Unexpected result " + str(result)
        assert isinstance(result.get_sort(), sorts.BitvectorSort)
        assert result.get_sort().get_len() == 2

    def test_parses_bv21_with_leading_zeroes(self):
        sort_ctx = sorts.SortContext()
        result = smt.parse_smtlib2_literal("#b10101", sort_ctx)
        assert result.get_literal() is 21, "Unexpected result " + str(result)
        assert isinstance(result.get_sort(), sorts.BitvectorSort)
        assert result.get_sort().get_len() == 5


class TestParseSmtlib2Sort(unittest.TestCase):
    def test_parses_int_sort(self):
        sort_ctx = sorts.SortContext()
        result = smt.parse_smtlib2_sort("Int", sort_ctx)
        assert isinstance(result, sorts.IntegerSort)

    def test_parses_bv1_sort(self):
        sort_ctx = sorts.SortContext()
        result = smt.parse_smtlib2_sort(["_", "BitVec", "1"], sort_ctx)
        assert isinstance(result, sorts.BitvectorSort)
        assert result.get_len() == 1

    def test_parses_bv13_sort(self):
        sort_ctx = sorts.SortContext()
        result = smt.parse_smtlib2_sort(["_", "BitVec", "13"], sort_ctx)
        assert isinstance(result, sorts.BitvectorSort)
        assert result.get_len() == 13

    def test_refuses_malformed_bv_sort(self):
        sort_ctx = sorts.SortContext()
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_sort(["_", "BitVec"], sort_ctx)
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_sort(["_", "BitVec", "a"], sort_ctx)
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_sort(["_", "BitVec", "-1"], sort_ctx)

    def test_refuses_unknown_sort(self):
        sort_ctx = sorts.SortContext()
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_sort("Foo", sort_ctx)
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_sort(["_", "Foo"], sort_ctx)
