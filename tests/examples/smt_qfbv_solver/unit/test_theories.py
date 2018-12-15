import unittest
import examples.smt_qfbv_solver.theories as theories
import examples.smt_qfbv_solver.sorts as sorts


class TestCoreSyntacticFunctionScopeFactory(unittest.TestCase):

    @staticmethod
    def __test_has_comparison_fn(name):
        under_test = theories.CoreSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)

        signature, name = scope.get_signature(name)
        assert name == name
        assert signature.get_num_parameters() == 0
        assert signature.get_arity() == 2

        bv_sort = sort_ctx.get_bv_sort(2)
        assert signature.get_range_sort([bv_sort, bv_sort]) is sort_ctx.get_bool_sort()

    @staticmethod
    def __test_comparison_fn_is_not_applicable_to_unequally_sorted_terms(name):
        under_test = theories.CoreSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, _ = scope.get_signature(name)
        assert signature.get_range_sort([sort_ctx.get_bv_sort(2), sort_ctx.get_bv_sort(1)]) is None
        assert signature.get_range_sort([sort_ctx.get_int_sort(), sort_ctx.get_bv_sort(1)]) is None
        assert signature.get_range_sort([sort_ctx.get_int_sort(), sort_ctx.get_bool_sort()]) is None

    def test_has_eq_fn(self):
        self.__test_has_comparison_fn("=")

    def test_eq_fn_is_not_applicable_to_unequally_sorted_terms(self):
        self.__test_comparison_fn_is_not_applicable_to_unequally_sorted_terms("=")

    def test_has_distinct_fn(self):
        self.__test_has_comparison_fn("distinct")

    def test_distinct_fn_is_not_applicable_to_unequally_sorted_terms(self):
        self.__test_comparison_fn_is_not_applicable_to_unequally_sorted_terms("distinct")

    def test_has_not_fn(self):
        under_test = theories.CoreSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)

        signature, name = scope.get_signature("not")
        assert name == "not"
        assert signature.get_num_parameters() == 0
        assert signature.get_arity() == 1

        assert signature.get_range_sort([sort_ctx.get_bool_sort()]) is sort_ctx.get_bool_sort()

    def test_not_fn_is_not_applicable_to_unequally_sorted_terms(self):
        under_test = theories.CoreSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, _ = scope.get_signature("not")
        assert signature.get_range_sort([sort_ctx.get_bv_sort(2)]) is None
        assert signature.get_range_sort([sort_ctx.get_int_sort()]) is None

    @staticmethod
    def __test_has_binary_boolean_fn(name: str):
        under_test = theories.CoreSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)

        signature, name = scope.get_signature(name)
        assert name == name
        assert signature.get_num_parameters() == 0
        assert signature.get_arity() == 2

        dom_sorts = [sort_ctx.get_bool_sort()]*2
        assert signature.get_range_sort(dom_sorts) is sort_ctx.get_bool_sort()

    @staticmethod
    def __test_binary_boolean_fn_is_only_applicable_to_boolean_sorted_terms(name: str):
        under_test = theories.CoreSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, _ = scope.get_signature(name)
        assert signature.get_range_sort([sort_ctx.get_bv_sort(2), sort_ctx.get_bv_sort(2)]) is None
        assert signature.get_range_sort([sort_ctx.get_int_sort(), sort_ctx.get_bool_sort()]) is None

    def test_has_implies_fn(self):
        self.__test_has_binary_boolean_fn("=>")

    def test_implies_fn_is_only_applicable_to_boolean_sorted_terms(self):
        self.__test_binary_boolean_fn_is_only_applicable_to_boolean_sorted_terms("=>")

    def test_has_and_fn(self):
        self.__test_has_binary_boolean_fn("and")

    def test_and_fn_is_only_applicable_to_boolean_sorted_terms(self):
        self.__test_binary_boolean_fn_is_only_applicable_to_boolean_sorted_terms("and")

    def test_has_or_fn(self):
        self.__test_has_binary_boolean_fn("or")

    def test_or_fn_is_only_applicable_to_boolean_sorted_terms(self):
        self.__test_binary_boolean_fn_is_only_applicable_to_boolean_sorted_terms("or")

    def test_has_xor_fn(self):
        self.__test_has_binary_boolean_fn("xor")

    def test_xor_fn_is_only_applicable_to_boolean_sorted_terms(self):
        self.__test_binary_boolean_fn_is_only_applicable_to_boolean_sorted_terms("xor")

    def test_has_boolean_constants(self):
        under_test = theories.CoreSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)

        signature, name = scope.get_signature("true")
        assert name == "true"
        assert signature.get_arity() == 0
        assert signature.get_num_parameters() == 0
        assert signature.get_range_sort([]) is sort_ctx.get_bool_sort()

        signature, name = scope.get_signature("false")
        assert name == "false"
        assert signature.get_arity() == 0
        assert signature.get_num_parameters() == 0
        assert signature.get_range_sort([]) is sort_ctx.get_bool_sort()