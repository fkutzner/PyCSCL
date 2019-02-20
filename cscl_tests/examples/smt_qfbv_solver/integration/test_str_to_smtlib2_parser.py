# Integration tests for the S-Expression and SMTLib2 parsers

import unittest
from cscl_examples.smt_qfbv_solver.sexp_parser import lex_sexp, parse_sexp
from cscl_examples.smt_qfbv_solver.smtlib2_parser import parse_smtlib2_problem
import cscl_examples.smt_qfbv_solver.ast as ast


class TestSExprParserAndSMTLib2ParserIntegration(unittest.TestCase):
    def test_parse_empty_problem(self):
        result = parse_smtlib2_problem(parse_sexp(lex_sexp("")))
        assert len(result) == 0

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

    def test_parse_sign_extend_problem(self):
        problem = """(set-logic QF_BV)
                     (set-info :smt-lib-version 2.0)
                     (set-info :category "check")
                     (set-info :status unsat)
                     (declare-fun x () (_ BitVec 2))
                     (assert (xor (bvslt ((_ sign_extend 1) x) (_ bv0 3)) (bvslt x (_ bv0 2))))
                     (check-sat)"""

        expected_result_ast = """
            SetLogicCommandASTNode Logic: QF_BV
            DeclareFunCommandASTNode FunctionName: x DomainSorts: [] RangeSort: (_ BitVec 2)
            AssertCommandASTNode
              FunctionApplicationASTNode Function: xor Sort: Bool
                FunctionApplicationASTNode Function: bvslt Sort: Bool
                  FunctionApplicationASTNode Function: 0!sign_extend Sort: (_ BitVec 3) Parameters: (1,)
                    FunctionApplicationASTNode Function: x Sort: (_ BitVec 2)
                  LiteralASTNode Literal: 0 Sort: (_ BitVec 3)
                FunctionApplicationASTNode Function: bvslt Sort: Bool
                  FunctionApplicationASTNode Function: x Sort: (_ BitVec 2)
                  LiteralASTNode Literal: 0 Sort: (_ BitVec 2)
            CheckSATCommandASTNode"""
        self.__test_parse(problem, expected_result_ast)

    def test_parse_nestedlet(self):
        problem = """(assert
                       (let ((x true))
                         (and
                           (let ((y false))
                             y)
                           x)))
                     (check-sat)"""
        expected_result_ast = """
            AssertCommandASTNode
              LetTermASTNode Symbols: ['x']
                FunctionApplicationASTNode Function: true Sort: Bool
                FunctionApplicationASTNode Function: and Sort: Bool
                  LetTermASTNode Symbols: ['y']
                    FunctionApplicationASTNode Function: false Sort: Bool
                    FunctionApplicationASTNode Function: y Sort: Bool
                  FunctionApplicationASTNode Function: x Sort: Bool
            CheckSATCommandASTNode"""
        self.__test_parse(problem, expected_result_ast)
