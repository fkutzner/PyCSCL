import unittest
from typing import List
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


class TestParseSmtlib2Symbol(unittest.TestCase):

    def test_empty_string_is_not_symbol(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_symbol("")

    def test_string_with_whitespace_is_not_symbol(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_symbol("Foo Bar")

    def test_string_with_leading_digit_is_not_symbol(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_symbol("3x")

    def test_string_with_non_ascii_letter_is_not_symbol(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_symbol("🤖")

    def test_reserved_word_is_not_symbol(self):
        for x in ("let", "par", "_", "!", "as", "forall", "exists", "NUMERAL", "DECIMAL", "STRING",
                  "set-logic", "assert", "declare-fun", "declare-const", "define-fun", "define-const",
                  "check-sat", "push", "pop", "get-model", "get-unsat-core", "set-info", "get-info",
                  "declare-sort", "define-sort", "get-assertions", "get-proof", "get-value", "get-assignment",
                  "get-option", "set-option", "exit"):
            with self.assertRaises(ValueError):
                smt.parse_smtlib2_symbol(x)

    def test_alnum_string_is_symbol(self):
        assert smt.parse_smtlib2_symbol("abc01d") == "abc01d"

    def test_string_with_nonalnum_chards_is_symbol(self):
        assert smt.parse_smtlib2_symbol("a/b@_c%^") == "a/b@_c%^"


class TestSyntacticFunctionScope(unittest.TestCase):
    def test_has_added_signature(self):
        sort_ctx = sorts.SortContext()
        sig = smt.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        under_test = smt.SyntacticFunctionScope(None)
        under_test.add_signature("foo", sig)

        lookup_result = under_test.get_signature("foo")
        assert lookup_result is not None
        result_sig, result_name = lookup_result
        assert result_sig is sig
        assert result_name == "foo"

    def test_queries_parent_scope(self):
        sort_ctx = sorts.SortContext()
        sig = smt.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        parent = smt.SyntacticFunctionScope(None)
        under_test = smt.SyntacticFunctionScope(parent)
        parent.add_signature("foo", sig)

        lookup_result = under_test.get_signature("foo")
        assert lookup_result is not None
        result_sig, result_name = lookup_result
        assert result_sig is sig
        assert result_name == "foo"

    def test_set_parent_scope(self):
        sort_ctx = sorts.SortContext()
        sig = smt.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        parent = smt.SyntacticFunctionScope(None)
        under_test = smt.SyntacticFunctionScope(None)
        under_test.set_parent(parent)
        parent.add_signature("foo", sig)

        lookup_result = under_test.get_signature("foo")
        assert lookup_result is not None
        result_sig, result_name = lookup_result
        assert result_sig is sig
        assert result_name == "foo"

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

    def test_parse_let_term_with_no_defs(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        foonction_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_bv_sort(3)],
                                                              range_sort=sort_ctx.get_int_sort())
        fun_scope.add_signature("foonction", smt.FunctionSignature(foonction_signature_fn, 1, True))

        result = smt.parse_smtlib2_term(["let", [], ["foonction", "#b111"]], sort_ctx, fun_scope)
        expected_tree = """
            LetTermASTNode Symbols: []
              FunctionApplicationASTNode Function: foonction Sort: Int
                LiteralASTNode Literal: 7 Sort: (_ BitVec 3)"""
        actual_tree = "\n" + result.tree_to_string(12)
        assert expected_tree == actual_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_parse_let_term_with_single_def(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        foonction_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_bv_sort(3)],
                                                              range_sort=sort_ctx.get_int_sort())
        fun_scope.add_signature("foonction", smt.FunctionSignature(foonction_signature_fn, 1, True))

        result = smt.parse_smtlib2_term(["let",
                                         [["x", "#b111"]],
                                         ["foonction", "x"]], sort_ctx, fun_scope)
        expected_tree = """
            LetTermASTNode Symbols: ['x']
              LiteralASTNode Literal: 7 Sort: (_ BitVec 3)
              FunctionApplicationASTNode Function: foonction Sort: Int
                FunctionApplicationASTNode Function: x Sort: (_ BitVec 3)"""
        actual_tree = "\n" + result.tree_to_string(12)
        assert expected_tree == actual_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_parse_let_term_with_two_defs(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        foonction_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_bv_sort(3),
                                                                            sort_ctx.get_bv_sort(2)],
                                                              range_sort=sort_ctx.get_bv_sort(3))
        fun_scope.add_signature("foonction", smt.FunctionSignature(foonction_signature_fn, 2, True))

        result = smt.parse_smtlib2_term(["let",
                                         [["x", "#b11"], ["y", ["foonction", "#b011", "#b10"]]],
                                         ["foonction", "y", "x"]], sort_ctx, fun_scope)
        expected_tree = """
            LetTermASTNode Symbols: ['x', 'y']
              LiteralASTNode Literal: 3 Sort: (_ BitVec 2)
              FunctionApplicationASTNode Function: foonction Sort: (_ BitVec 3)
                LiteralASTNode Literal: 3 Sort: (_ BitVec 3)
                LiteralASTNode Literal: 2 Sort: (_ BitVec 2)
              FunctionApplicationASTNode Function: foonction Sort: (_ BitVec 3)
                FunctionApplicationASTNode Function: y Sort: (_ BitVec 3)
                FunctionApplicationASTNode Function: x Sort: (_ BitVec 2)"""
        actual_tree = "\n" + result.tree_to_string(12)
        assert expected_tree == actual_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_fails_for_malformed_let_statement(self):
        sort_ctx = sorts.SortContext()
        fun_scope = smt.SyntacticFunctionScope(None)

        foonction_signature_fn = create_function_signature_fn(domain_sorts=[sort_ctx.get_bv_sort(3),
                                                                            sort_ctx.get_bv_sort(2)],
                                                              range_sort=sort_ctx.get_bv_sort(3))
        fun_scope.add_signature("foonction", smt.FunctionSignature(foonction_signature_fn, 2, True))

        with self.assertRaises(ValueError):
            smt.parse_smtlib2_term(["let", "#b1111"], sort_ctx, fun_scope)

        with self.assertRaises(ValueError):
            smt.parse_smtlib2_term(["let", [["foonction", "#b011", "#b10"]], "#b1111"], sort_ctx, fun_scope)

        with self.assertRaises(ValueError):
            smt.parse_smtlib2_term(["let", ["x", ["foonction", "#b011", "#b10"]], "#b1111"], sort_ctx, fun_scope)

        with self.assertRaises(ValueError):
            smt.parse_smtlib2_term(["let", [["3", ["foonction", "#b011", "#b10"]]], "#b1111"], sort_ctx, fun_scope)


class TestParseSmtlib2Problem(unittest.TestCase):
    def test_empty_problem(self):
        result = smt.parse_smtlib2_problem([])
        assert result == []

    def test_set_logic_cmd_qfbv(self):
        result = smt.parse_smtlib2_problem([["set-logic", "QF_BV"]])
        assert type(result) == list
        assert len(result) == 1
        expected_tree = "SetLogicCommandASTNode Logic: QF_BV"
        actual_tree = result[0].tree_to_string()
        assert actual_tree == expected_tree,  "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_set_logic_cmd_fails_for_bad_arity(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["set-logic", "QF_BV", "foo"]])
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["set-logic"]])

    def test_declare_fun_cmd_without_args_and_int_range(self):
        result = smt.parse_smtlib2_problem([["declare-fun", "foonction", [], "Int"]])
        assert type(result) == list
        assert len(result) == 1
        expected_tree = "DeclareFunCommandASTNode FunctionName: foonction DomainSorts: [] RangeSort: Int"
        actual_tree = result[0].tree_to_string()
        assert actual_tree == expected_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_declare_fun_cmd_without_args_and_bv_range(self):
        result = smt.parse_smtlib2_problem([["declare-fun", "foonction", [], ["_", "BitVec", "32"]]])
        assert type(result) == list
        assert len(result) == 1
        expected_tree = "DeclareFunCommandASTNode FunctionName: foonction DomainSorts: [] RangeSort: (_ BitVec 32)"
        actual_tree = result[0].tree_to_string()
        assert actual_tree == expected_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_declare_fun_cmd_with_args_and_bv_range(self):
        result = smt.parse_smtlib2_problem([["declare-fun", "foonction", ["Int", ["_", "BitVec", "32"]],
                                             ["_", "BitVec", "32"]]])
        assert type(result) == list
        assert len(result) == 1
        expected_tree = "DeclareFunCommandASTNode FunctionName: foonction DomainSorts: ['Int', '(_ BitVec 32)']" + \
                        " RangeSort: (_ BitVec 32)"
        actual_tree = result[0].tree_to_string()
        assert actual_tree == expected_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_declare_const_cmd_with_int_sort(self):
        result = smt.parse_smtlib2_problem([["declare-const", "fooconst", "Int"]])
        assert type(result) == list
        assert len(result) == 1
        expected_tree = "DeclareFunCommandASTNode FunctionName: fooconst DomainSorts: [] RangeSort: Int"
        actual_tree = result[0].tree_to_string()
        assert actual_tree == expected_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_declare_const_cmd_with_bv_sort(self):
        result = smt.parse_smtlib2_problem([["declare-const", "fooconst", ["_", "BitVec", "32"]]])
        assert type(result) == list
        assert len(result) == 1
        expected_tree = "DeclareFunCommandASTNode FunctionName: fooconst DomainSorts: [] RangeSort: (_ BitVec 32)"
        actual_tree = result[0].tree_to_string()
        assert actual_tree == expected_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    @staticmethod
    def assert_printed_ast_equal(ast_nodes: List[ast.ASTNode], expected_tree: str, indent: int):
        actual_tree = "\n"
        for x in ast_nodes:
            assert isinstance(x, ast.ASTNode)
            actual_tree += x.tree_to_string(indent) + "\n"
        actual_tree = actual_tree.rstrip()
        assert actual_tree == expected_tree, "Unexpected AST:\n" + actual_tree + "\nExpected:\n" + expected_tree

    def test_assert(self):
        result = smt.parse_smtlib2_problem([["declare-const", "x", "Bool"],
                                            ["declare-fun", "=", ["Bool", "Bool"], "Bool"],
                                            ["assert", ["=", "x", "x"]]])
        expected_tree = """
          DeclareFunCommandASTNode FunctionName: x DomainSorts: [] RangeSort: Bool
          DeclareFunCommandASTNode FunctionName: = DomainSorts: ['Bool', 'Bool'] RangeSort: Bool
          AssertCommandASTNode
            FunctionApplicationASTNode Function: = Sort: Bool
              FunctionApplicationASTNode Function: x Sort: Bool
              FunctionApplicationASTNode Function: x Sort: Bool"""
        self.assert_printed_ast_equal(result, expected_tree, 10)

    def test_define_fun_no_args_int_value(self):
        result = smt.parse_smtlib2_problem([["declare-fun", "op", ["Int", "Int"], "Int"],
                                            ["define-fun", "foo", list(), "Int", ["op", "1", "2"]]])
        expected_tree = """
          DeclareFunCommandASTNode FunctionName: op DomainSorts: ['Int', 'Int'] RangeSort: Int
          DefineFunCommandASTNode FunctionName: foo FormalParameters: [] RangeSort: Int
            FunctionApplicationASTNode Function: op Sort: Int
              LiteralASTNode Literal: 1 Sort: Int
              LiteralASTNode Literal: 2 Sort: Int"""
        self.assert_printed_ast_equal(result, expected_tree, 10)

    def test_define_fun_single_arg_int_value(self):
        result = smt.parse_smtlib2_problem([["declare-fun", "op", ["Int", "Int"], "Int"],
                                            ["define-fun", "foo", [["x", "Int"]], "Int", ["op", "x", "2"]]])
        expected_tree = """
          DeclareFunCommandASTNode FunctionName: op DomainSorts: ['Int', 'Int'] RangeSort: Int
          DefineFunCommandASTNode FunctionName: foo FormalParameters: ['(x, Int)'] RangeSort: Int
            FunctionApplicationASTNode Function: op Sort: Int
              FunctionApplicationASTNode Function: x Sort: Int
              LiteralASTNode Literal: 2 Sort: Int"""
        self.assert_printed_ast_equal(result, expected_tree, 10)

    def test_define_fun_multiple_arg_int_value(self):
        result = smt.parse_smtlib2_problem([["declare-fun", "op", ["Int", "Int"], "Int"],
                                            ["define-fun", "foo", [["x", "Int"], ["y", "Int"]],
                                             "Int", ["op", "x", "y"]]])
        expected_tree = """
          DeclareFunCommandASTNode FunctionName: op DomainSorts: ['Int', 'Int'] RangeSort: Int
          DefineFunCommandASTNode FunctionName: foo FormalParameters: ['(x, Int)', '(y, Int)'] RangeSort: Int
            FunctionApplicationASTNode Function: op Sort: Int
              FunctionApplicationASTNode Function: x Sort: Int
              FunctionApplicationASTNode Function: y Sort: Int"""
        self.assert_printed_ast_equal(result, expected_tree, 10)

    def test_define_fun_fails_for_missing_args(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["define-fun", "foo", "Int", "3"]])

    def test_define_fun_fails_for_bad_parameter_sort(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["define-fun", "foo", ["x", "BadType"], "Int", "3"]])

    def test_define_fun_fails_for_bad_range_sort(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["define-fun", "foo", [], "BadType", "3"]])

    def test_define_fun_fails_for_bad_term_sort(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["define-fun", "foo", [], ["_", "BitVec", "2"], "2"]])

    def test_define_fun_fails_for_missing_term(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["define-fun", "foo", [], ["_", "BitVec", "2"]]])

    def test_define_fun_fails_for_undefined_symbol_in_term(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["define-fun", "foo", [["x", "Int"], ["y", "Int"]],
                                        "Int", ["op", "x", "y"]]])

    def test_define_const_int_value(self):
        result = smt.parse_smtlib2_problem([["define-const", "foo", "Int", "3"]])
        expected_tree = """
          DefineFunCommandASTNode FunctionName: foo FormalParameters: [] RangeSort: Int
            LiteralASTNode Literal: 3 Sort: Int"""
        self.assert_printed_ast_equal(result, expected_tree, 10)

    def test_define_const_bv_value(self):
        result = smt.parse_smtlib2_problem([["define-const", "foo", ["_", "BitVec", "2"], "#b10"]])
        expected_tree = """
          DefineFunCommandASTNode FunctionName: foo FormalParameters: [] RangeSort: (_ BitVec 2)
            LiteralASTNode Literal: 2 Sort: (_ BitVec 2)"""
        self.assert_printed_ast_equal(result, expected_tree, 10)

    def test_define_const_fails_for_bad_term_sort(self):
        with self.assertRaises(ValueError):
            smt.parse_smtlib2_problem([["define-const", "foo", ["_", "BitVec", "2"], "1"]])
