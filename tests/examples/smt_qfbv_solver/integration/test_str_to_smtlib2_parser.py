# Integration tests for the S-Expression and SMTLib2 parsers

import unittest
from examples.smt_qfbv_solver.sexp_parser import lex_sexp, parse_sexp
from examples.smt_qfbv_solver.smtlib2_parser import parse_smtlib2_problem
import examples.smt_qfbv_solver.ast as ast


class TestSExprParserAndSMTLib2ParserIntegration(unittest.TestCase):
    def test_parse_empty_problem(self):
        result = parse_smtlib2_problem(parse_sexp(lex_sexp("")))
        assert len(result) == 0

    def test_parse_single_expr(self):
        result = parse_smtlib2_problem(parse_sexp(lex_sexp("(set-logic QF_BV)")))
        assert len(result) == 1
        assert result[0].tree_to_string() == "SetLogicCommandASTNode Logic: QF_BV"

    def test_parse_single_expr(self):
        result = parse_smtlib2_problem(parse_sexp(lex_sexp("(set-logic QF_BV)")))
        assert len(result) == 1
        assert result[0].tree_to_string() == "SetLogicCommandASTNode Logic: QF_BV"

    @staticmethod
    def __test_parse(smtlib_problem: str, expected_ast: str):
        result = parse_smtlib2_problem(parse_sexp(lex_sexp(smtlib_problem)))

        result_ast = ""
        for x in result:
            assert isinstance(x, ast.ASTNode)
            result_ast += "\n" + x.tree_to_string(12)

        assert expected_ast == result_ast, "Problem instance:\n" + smtlib_problem\
            + "\nExpected AST:\n" + expected_ast + "\nActual AST:\n" + result_ast

    def test_parse_assert_simple(self):
        problem = """(declare-const x (_ BitVec 20))
                     (declare-const y (_ BitVec 20))
                     (declare-fun _eq ((_ BitVec 20) (_ BitVec 20)) Bool)
                     (declare-fun _not ((_ BitVec 20)) (_ BitVec 20))
                     (assert (_eq (_not x) y))
                     (check-sat)"""

        expected_result_ast = """
            DeclareFunCommandASTNode FunctionName: x DomainSorts: [] RangeSort: (_ BitVec 20)
            DeclareFunCommandASTNode FunctionName: y DomainSorts: [] RangeSort: (_ BitVec 20)
            DeclareFunCommandASTNode FunctionName: _eq DomainSorts: ['(_ BitVec 20)', '(_ BitVec 20)'] RangeSort: Bool
            DeclareFunCommandASTNode FunctionName: _not DomainSorts: ['(_ BitVec 20)'] RangeSort: (_ BitVec 20)
            AssertCommandASTNode
              FunctionApplicationASTNode Function: _eq Sort: Bool
                FunctionApplicationASTNode Function: _not Sort: (_ BitVec 20)
                  FunctionApplicationASTNode Function: x Sort: (_ BitVec 20)
                FunctionApplicationASTNode Function: y Sort: (_ BitVec 20)
            CheckSATCommandASTNode"""

        self.__test_parse(problem, expected_result_ast)
