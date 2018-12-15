import unittest
import examples.smt_qfbv_solver.theories as theories
import examples.smt_qfbv_solver.sorts as sorts
import examples.smt_qfbv_solver.syntactic_scope as synscope


class TestCoreSyntacticFunctionScopeFactory(unittest.TestCase):

    @staticmethod
    def __test_has_comparison_fn(name):
        under_test = theories.CoreSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)

        signature, lookup_name = scope.get_signature(name)
        assert lookup_name == name
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

        signature, lookup_name = scope.get_signature(name)
        assert lookup_name == name
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


class TestFixedSizeBVSyntacticFunctionScopeFactory(unittest.TestCase):
    def test_has_concat_fn(self):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, lookup_name = scope.get_signature("concat")

        assert lookup_name == "concat"
        assert signature.get_num_parameters() == 0
        assert signature.get_arity() == 2

        bv_sort_a = sort_ctx.get_bv_sort(2)
        bv_sort_b = sort_ctx.get_bv_sort(4)
        assert signature.get_range_sort([bv_sort_a, bv_sort_b]) is sort_ctx.get_bv_sort(6)

    def test_concat_fn_is_only_applicable_to_bv_sorted_terms(self):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, _ = scope.get_signature("concat")

        assert signature.get_range_sort([sort_ctx.get_bv_sort(0), sort_ctx.get_bool_sort()]) is None
        assert signature.get_range_sort([sort_ctx.get_int_sort(), sort_ctx.get_bool_sort()]) is None

    def test_has_extract_fn(self):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        mangled_name = synscope.SyntacticFunctionScope.mangle_parametrized_function_name("extract")
        signature, lookup_name = scope.get_signature(mangled_name)

        assert lookup_name == mangled_name
        assert signature.get_num_parameters() == 2
        assert signature.get_arity() == 1

        bv_sort = sort_ctx.get_bv_sort(10)
        assert signature.get_range_sort([3, 1, bv_sort]) is sort_ctx.get_bv_sort(3)
        assert signature.get_range_sort([0, 0, bv_sort]) is sort_ctx.get_bv_sort(1)
        assert signature.get_range_sort([9, 9, bv_sort]) is sort_ctx.get_bv_sort(1)

    def test_extract_fn_is_only_applicable_to_legally_sorted_terms(self):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        mangled_name = synscope.SyntacticFunctionScope.mangle_parametrized_function_name("extract")
        signature, _ = scope.get_signature(mangled_name)

        assert signature.get_range_sort([3, 1, sort_ctx.get_int_sort()]) is None
        assert signature.get_range_sort([3, 1, sort_ctx.get_bool_sort()]) is None
        assert signature.get_range_sort([4, 4, sort_ctx.get_bv_sort(1)]) is None

    @staticmethod
    def __test_has_neg_fn(name):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, lookup_name = scope.get_signature(name)

        assert lookup_name == name
        assert signature.get_num_parameters() == 0
        assert signature.get_arity() == 1

        bv_sort = sort_ctx.get_bv_sort(3)
        assert signature.get_range_sort([bv_sort]) is bv_sort

    @staticmethod
    def __test_neg_fn_is_only_applicable_to_bv_sorted_terms(name):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, _ = scope.get_signature(name)

        assert signature.get_range_sort([sort_ctx.get_int_sort()]) is None
        assert signature.get_range_sort([sort_ctx.get_bool_sort()]) is None

    def test_has_bvneg_fn(self):
        self.__test_has_neg_fn("bvneg")

    def test_bvneg_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_neg_fn_is_only_applicable_to_bv_sorted_terms("bvneg")

    def test_has_bvnot_fn(self):
        self.__test_has_neg_fn("bvnot")

    def test_bvnot_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_neg_fn_is_only_applicable_to_bv_sorted_terms("bvnot")

    @staticmethod
    def __test_has_binary_fn(name):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, lookup_name = scope.get_signature(name)

        assert lookup_name == name
        assert signature.get_num_parameters() == 0
        assert signature.get_arity() == 2

        bv_sort = sort_ctx.get_bv_sort(3)
        assert signature.get_range_sort([bv_sort, bv_sort]) is bv_sort

    @staticmethod
    def __test_binary_fn_is_only_applicable_to_bv_sorted_terms(name):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, _ = scope.get_signature(name)

        assert signature.get_range_sort([sort_ctx.get_int_sort(), sort_ctx.get_int_sort()]) is None
        assert signature.get_range_sort([sort_ctx.get_bool_sort(), sort_ctx.get_int_sort()]) is None

    def test_has_bvand_fn(self):
        self.__test_has_binary_fn("bvand")

    def test_bvand_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_binary_fn_is_only_applicable_to_bv_sorted_terms("bvand")
        
    def test_has_bvor_fn(self):
        self.__test_has_binary_fn("bvor")

    def test_bvor_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_binary_fn_is_only_applicable_to_bv_sorted_terms("bvor")
        
    def test_has_bvadd_fn(self):
        self.__test_has_binary_fn("bvadd")

    def test_bvadd_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_binary_fn_is_only_applicable_to_bv_sorted_terms("bvadd")
        
    def test_has_bvmul_fn(self):
        self.__test_has_binary_fn("bvmul")

    def test_bvmul_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_binary_fn_is_only_applicable_to_bv_sorted_terms("bvmul")
        
    def test_has_bvudiv_fn(self):
        self.__test_has_binary_fn("bvudiv")

    def test_bvudiv_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_binary_fn_is_only_applicable_to_bv_sorted_terms("bvudiv")
        
    def test_has_bvurem_fn(self):
        self.__test_has_binary_fn("bvurem")

    def test_bvurem_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_binary_fn_is_only_applicable_to_bv_sorted_terms("bvurem")
        
    def test_has_bvshl_fn(self):
        self.__test_has_binary_fn("bvshl")

    def test_bvshl_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_binary_fn_is_only_applicable_to_bv_sorted_terms("bvshl")

    def test_has_bvlshr_fn(self):
        self.__test_has_binary_fn("bvlshr")

    def test_bvlshr_fn_is_only_applicable_to_bv_sorted_terms(self):
        self.__test_binary_fn_is_only_applicable_to_bv_sorted_terms("bvlshr")

    def test_has_bvult_fn(self):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, lookup_name = scope.get_signature("bvult")

        assert lookup_name == "bvult"
        assert signature.get_num_parameters() == 0
        assert signature.get_arity() == 2

        bv_sort_a = sort_ctx.get_bv_sort(4)
        bv_sort_b = sort_ctx.get_bv_sort(4)
        assert signature.get_range_sort([bv_sort_a, bv_sort_b]) is sort_ctx.get_bool_sort()

    def test_bvult_fn_is_only_applicable_to_bv_sorted_terms(self):
        under_test = theories.FixedSizeBVSyntacticFunctionScopeFactory()
        sort_ctx = sorts.SortContext()
        scope = under_test.create_syntactic_scope(sort_ctx)
        signature, _ = scope.get_signature("bvult")

        assert signature.get_range_sort([sort_ctx.get_bv_sort(1), sort_ctx.get_bool_sort()]) is None
        assert signature.get_range_sort([sort_ctx.get_bv_sort(1), sort_ctx.get_bv_sort(2)]) is None
        assert signature.get_range_sort([sort_ctx.get_bool_sort(), sort_ctx.get_bool_sort()]) is None
