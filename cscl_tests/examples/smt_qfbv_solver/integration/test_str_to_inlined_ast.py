# Integration tests for the SMTLib2 parser and the FunctionDefinitionInliner transformation

import unittest
from cscl_examples.smt_qfbv_solver.sexp_parser import lex_sexp, parse_sexp
from cscl_examples.smt_qfbv_solver.smtlib2_parser import parse_smtlib2_problem
import cscl_examples.smt_qfbv_solver.ast as ast
import cscl_examples.smt_qfbv_solver.ast_transformers as ast_trafo


class TestSMTLib2ParserAndFunctionDefinitionInlinerIntegration(unittest.TestCase):
    def test_parse_empty_problem(self):
        result = parse_smtlib2_problem(parse_sexp(lex_sexp("")))
        assert len(result) == 0

    def test_parse_single_expr(self):
        result = parse_smtlib2_problem(parse_sexp(lex_sexp("(set-logic QF_BV)")))
        assert len(result) == 1
        assert result[0].tree_to_string() == "SetLogicCommandASTNode Logic: QF_BV"

    @staticmethod
    def __test_parse(smtlib_problem: str, expected_ast: str):
        under_test = ast_trafo.FunctionDefinitionInliner()
        input_ast = parse_smtlib2_problem(parse_sexp(lex_sexp(smtlib_problem)))
        result = under_test.transform(input_ast)
        result_ast = ""
        for x in result:
            assert isinstance(x, ast.ASTNode)
            result_ast += "\n" + x.tree_to_string(12)

        assert expected_ast == result_ast, "Problem instance:\n" + smtlib_problem\
            + "\nExpected AST:\n" + expected_ast + "\nActual AST:\n" + result_ast

    def test_for_no_definitions(self):
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

    def test_fun_def_with_const_ref(self):
        problem = """(set-logic QF_BV)
                     (declare-const z (_ BitVec 4))
                     (define-fun foo ((x (_ BitVec 4)) (y (_ BitVec 4))) (_ BitVec 8) (concat (bvor x y) z))
                     (assert (let ((z #b10010011)) (= (foo #b0001 #b1000) z)))
                     (check-sat)"""

        expected_result_ast = """
            SetLogicCommandASTNode Logic: QF_BV
            DeclareFunCommandASTNode FunctionName: z DomainSorts: [] RangeSort: (_ BitVec 4)
            AssertCommandASTNode
              LetTermASTNode Symbols: ['z']
                LiteralASTNode Literal: 147 Sort: (_ BitVec 8)
                FunctionApplicationASTNode Function: = Sort: Bool
                  LetTermASTNode Symbols: ['x', 'y']
                    LiteralASTNode Literal: 1 Sort: (_ BitVec 4)
                    LiteralASTNode Literal: 8 Sort: (_ BitVec 4)
                    FunctionApplicationASTNode Function: concat Sort: (_ BitVec 8)
                      FunctionApplicationASTNode Function: bvor Sort: (_ BitVec 4)
                        FunctionApplicationASTNode Function: x Sort: (_ BitVec 4)
                        FunctionApplicationASTNode Function: y Sort: (_ BitVec 4)
                      FunctionApplicationASTNode Function: z Sort: (_ BitVec 4)
                  FunctionApplicationASTNode Function: z Sort: (_ BitVec 8)
            CheckSATCommandASTNode"""

        self.__test_parse(problem, expected_result_ast)

    def test_nested_fun_def(self):
        problem = """(set-logic QF_BV)
                     (define-fun foo ((x (_ BitVec 4)) (y (_ BitVec 4))) (_ BitVec 4) (bvor x y))
                     (define-fun bar ((x (_ BitVec 4)) (z (_ BitVec 4))) (_ BitVec 4) (foo (bvand x z) z))
                     (assert (let ((z #b1001)) (= (bar #b0001 #b1000) z)))
                     (check-sat)"""

        expected_result_ast = """
            SetLogicCommandASTNode Logic: QF_BV
            AssertCommandASTNode
              LetTermASTNode Symbols: ['z']
                LiteralASTNode Literal: 9 Sort: (_ BitVec 4)
                FunctionApplicationASTNode Function: = Sort: Bool
                  LetTermASTNode Symbols: ['x', 'z']
                    LiteralASTNode Literal: 1 Sort: (_ BitVec 4)
                    LiteralASTNode Literal: 8 Sort: (_ BitVec 4)
                    LetTermASTNode Symbols: ['x', 'y']
                      FunctionApplicationASTNode Function: bvand Sort: (_ BitVec 4)
                        FunctionApplicationASTNode Function: x Sort: (_ BitVec 4)
                        FunctionApplicationASTNode Function: z Sort: (_ BitVec 4)
                      FunctionApplicationASTNode Function: z Sort: (_ BitVec 4)
                      FunctionApplicationASTNode Function: bvor Sort: (_ BitVec 4)
                        FunctionApplicationASTNode Function: x Sort: (_ BitVec 4)
                        FunctionApplicationASTNode Function: y Sort: (_ BitVec 4)
                  FunctionApplicationASTNode Function: z Sort: (_ BitVec 4)
            CheckSATCommandASTNode"""

        self.__test_parse(problem, expected_result_ast)
