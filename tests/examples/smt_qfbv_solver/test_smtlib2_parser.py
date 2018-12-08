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


class TestSyntacticFunctionScope(unittest.TestCase):
    def test_has_added_signature(self):
        sort_ctx = sorts.SortContext()
        sig = smt.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        under_test = smt.SyntacticFunctionScope(None)
        under_test.add_signature("foo", sig)
        assert(under_test.get_signature("foo") is sig)

    def test_queries_parent_scope(self):
        sort_ctx = sorts.SortContext()
        sig = smt.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        parent = smt.SyntacticFunctionScope(None)
        under_test = smt.SyntacticFunctionScope(parent)
        parent.add_signature("foo", sig)
        assert(under_test.get_signature("foo") is sig)

    def test_set_parent_scope(self):
        sort_ctx = sorts.SortContext()
        sig = smt.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        parent = smt.SyntacticFunctionScope(None)
        under_test = smt.SyntacticFunctionScope(None)
        under_test.set_parent(parent)
        parent.add_signature("foo", sig)
        assert(under_test.get_signature("foo") is sig)

    def test_refuses_to_add_when_unshadowable(self):
        sort_ctx = sorts.SortContext()
        sig = smt.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, False)
        parent = smt.SyntacticFunctionScope(None)
        parent.add_signature("foo", sig)

        under_test = smt.SyntacticFunctionScope(parent)
        with self.assertRaises(ValueError):
            under_test.add_signature("foo", sig)


def create_function_signature_fn(domain_sorts, range_sort):
    def __result(x):
        if list(x) == domain_sorts:
            return range_sort
        return None
    return __result


def create_constant_signature_fn(range_sort):
    def __result(_):
        return range_sort
    return __result


class TestParseSmtlib2Term(unittest.TestCase):
    def test_int_literal_is_term(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)
        result = smt.parse_smtlib2_term("100", sort_ctx, fun_scope)
        assert isinstance(result, ast.LiteralASTNode)
        assert isinstance(result.get_sort(), sorts.IntegerSort)
        assert result.get_literal() == 100

    def test_bv_literal_is_term(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)
        result = smt.parse_smtlib2_term("#b100", sort_ctx, fun_scope)
        assert isinstance(result, ast.LiteralASTNode)
        assert isinstance(result.get_sort(), sorts.BitvectorSort)
        assert result.get_literal() == 4

    def test_constant_is_term(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)
        constant_signature = smt.FunctionSignature(create_constant_signature_fn(sort_ctx.get_int_sort()), 0, True)
        fun_scope.add_signature("foonction", constant_signature)

        result = smt.parse_smtlib2_term("foonction", sort_ctx, fun_scope)
        assert isinstance(result, ast.FunctionApplicationASTNode)
        assert isinstance(result.get_sort(), sorts.IntegerSort)
        assert result.get_function_name() == "foonction"
        assert len(result.get_child_nodes()) == 0

    def test_constant_in_parens_is_term(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)
        constant_signature = smt.FunctionSignature(create_constant_signature_fn(sort_ctx.get_int_sort()), 0, True)
        fun_scope.add_signature("foonction", constant_signature)

        result = smt.parse_smtlib2_term(["foonction"], sort_ctx, fun_scope)
        assert isinstance(result, ast.FunctionApplicationASTNode)
        assert isinstance(result.get_sort(), sorts.IntegerSort)
        assert result.get_function_name() == "foonction"
        assert len(result.get_child_nodes()) == 0

    def test_function_expression_is_term(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        fun_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_bv_sort(3), sort_ctx.get_int_sort()],
                                                        range_sort=sort_ctx.get_int_sort())
        fun_scope.add_signature("foonction", smt.FunctionSignature(fun_signature_fn, 2, True))

        result = smt.parse_smtlib2_term(["foonction", "#b100", "30"], sort_ctx, fun_scope)
        assert isinstance(result, ast.FunctionApplicationASTNode)
        assert isinstance(result.get_sort(), sorts.IntegerSort)
        assert result.get_function_name() == "foonction"
        assert len(result.get_child_nodes()) == 2

        lhs_node = result.get_child_nodes()[0]
        assert isinstance(lhs_node, ast.LiteralASTNode)
        assert lhs_node.get_sort() == sort_ctx.get_bv_sort(3)
        assert lhs_node.get_literal() == 4

        rhs_node = result.get_child_nodes()[1]
        assert isinstance(rhs_node, ast.LiteralASTNode)
        assert rhs_node.get_sort() == sort_ctx.get_int_sort()
        assert rhs_node.get_literal() == 30

    def test_parse_nested_term(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        foonction_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_int_sort(),
                                                                            sort_ctx.get_bv_sort(3),
                                                                            sort_ctx.get_int_sort()],
                                                              range_sort=sort_ctx.get_int_sort())
        threebitbv_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_int_sort()],
                                                               range_sort=sort_ctx.get_bv_sort(3))
        integerthingy_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_int_sort()],
                                                                  range_sort=sort_ctx.get_int_sort())

        fun_scope.add_signature("foonction", smt.FunctionSignature(foonction_signature_fn, 3, True))
        fun_scope.add_signature("threebitbv", smt.FunctionSignature(threebitbv_signature_fn, 1, True))
        fun_scope.add_signature("integerthingy", smt.FunctionSignature(integerthingy_signature_fn, 1, True))

        result = smt.parse_smtlib2_term(["foonction", "100", ["threebitbv", "5"], ["integerthingy", "1024"]],
                                        sort_ctx, fun_scope)
        assert isinstance(result, ast.FunctionApplicationASTNode)
        expected_tree = """FunctionApplicationASTNode Function: foonction Sort: Int
  LiteralASTNode Literal: 100 Sort: Int
  FunctionApplicationASTNode Function: threebitbv Sort: (_ BitVec 3)
    LiteralASTNode Literal: 5 Sort: Int
  FunctionApplicationASTNode Function: integerthingy Sort: Int
    LiteralASTNode Literal: 1024 Sort: Int"""
        actual_tree = result.tree_to_string()
        assert actual_tree == expected_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_fails_for_function_application_with_bad_arity(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        fun_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_bv_sort(3), sort_ctx.get_int_sort()],
                                                        range_sort=sort_ctx.get_int_sort())
        fun_scope.add_signature("foonction", smt.FunctionSignature(fun_signature_fn, 2, True))

        with self.assertRaises(ValueError):
            smt.parse_smtlib2_term(["foonction", "#b100"], sort_ctx, fun_scope)

    def test_fails_for_function_application_with_bad_type(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        fun_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_bv_sort(3), sort_ctx.get_int_sort()],
                                                        range_sort=sort_ctx.get_int_sort())
        fun_scope.add_signature("foonction", smt.FunctionSignature(fun_signature_fn, 2, True))

        with self.assertRaises(ValueError):
            smt.parse_smtlib2_term(["foonction", "1", "2"], sort_ctx, fun_scope)

    def test_fails_for_constant_with_argument(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        fun_signature_fn = create_constant_signature_fn(range_sort=sort_ctx.get_int_sort())
        fun_scope.add_signature("fooconst", smt.FunctionSignature(fun_signature_fn, 2, True))

        with self.assertRaises(ValueError):
            smt.parse_smtlib2_term(["fooconst", "1"], sort_ctx, fun_scope)

    def test_fails_for_unary_function_used_as_constant(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        fun_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_bv_sort(3)],
                                                        range_sort=sort_ctx.get_int_sort())
        fun_scope.add_signature("foonction", smt.FunctionSignature(fun_signature_fn, 2, True))

        with self.assertRaises(ValueError):
            smt.parse_smtlib2_term("foonction", sort_ctx, fun_scope)