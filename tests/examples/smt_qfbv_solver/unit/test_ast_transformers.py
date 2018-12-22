import unittest
import examples.smt_qfbv_solver.ast as ast
import examples.smt_qfbv_solver.ast_transformers as ast_trans
import examples.smt_qfbv_solver.sorts as sorts


class TestFunctionDefinitionInliner(unittest.TestCase):

    def test_does_not_modify_empty_ast(self):
        under_test = ast_trans.FunctionDefinitionInliner()
        result = under_test.transform([])
        assert result == []

    @staticmethod
    def __expect_ast(expected_ast_as_str, indent, actual_ast):
        actual_ast_as_str = "\n" + "\n".join(x.tree_to_string(indent) for x in actual_ast)
        assert expected_ast_as_str == actual_ast_as_str, "Mismatching ASTS\nExpected:" + expected_ast_as_str\
            + "\nActual:" + actual_ast_as_str

    def test_does_not_modify_ast_with_no_definitions(self):
        under_test = ast_trans.FunctionDefinitionInliner()
        sort_ctx = sorts.SortContext()

        set_logic_node = ast.SetLogicCommandASTNode("QF_BV")
        declare_fun_node = ast.DeclareFunCommandASTNode("foonction", [sort_ctx.get_int_sort()], sort_ctx.get_int_sort())
        term_1_node = ast.FunctionApplicationASTNode("foonction",
                                                     [ast.LiteralASTNode(3, sort_ctx.get_int_sort())],
                                                     sort_ctx.get_int_sort())
        term_2_node = ast.LetTermASTNode()
        term_2_node.set_definitions([("x", ast.LiteralASTNode(3, sort_ctx.get_int_sort()))])
        term_2_node.set_enclosed_term(ast.FunctionApplicationASTNode("x", [], sort_ctx.get_int_sort()))

        assert_node = ast.AssertCommandASTNode(
            ast.FunctionApplicationASTNode("=", [term_1_node, term_2_node], sort_ctx.get_bool_sort())
        )

        test_data = [set_logic_node, declare_fun_node, assert_node]

        expected_ast = """
            SetLogicCommandASTNode Logic: QF_BV
            DeclareFunCommandASTNode FunctionName: foonction DomainSorts: ['Int'] RangeSort: Int
            AssertCommandASTNode
              FunctionApplicationASTNode Function: = Sort: Bool
                FunctionApplicationASTNode Function: foonction Sort: Int
                  LiteralASTNode Literal: 3 Sort: Int
                LetTermASTNode Symbols: ['x']
                  LiteralASTNode Literal: 3 Sort: Int
                  FunctionApplicationASTNode Function: x Sort: Int"""

        self.__expect_ast(expected_ast, 12, under_test.transform(test_data))

    def test_inlines_constants(self):
        under_test = ast_trans.FunctionDefinitionInliner()
        sort_ctx = sorts.SortContext()

        set_logic_node = ast.SetLogicCommandASTNode("QF_BV")
        define_int_const_node = ast.DefineFunCommandASTNode("x", [], sort_ctx.get_int_sort(),
                                                            ast.LiteralASTNode(100, sort_ctx.get_int_sort()))
        define_bv_const_node = ast.DefineFunCommandASTNode("y", [], sort_ctx.get_bv_sort(10),
                                                           ast.LiteralASTNode(100, sort_ctx.get_bv_sort(10)))
        declare_fun_node = ast.DeclareFunCommandASTNode("foonction",
                                                        [sort_ctx.get_int_sort(), sort_ctx.get_bv_sort(10)],
                                                        sort_ctx.get_int_sort())

        # This term's constants must be replaced:
        term_1_node = ast.FunctionApplicationASTNode("foonction",
                                                     [ast.FunctionApplicationASTNode("x", [], sort_ctx.get_int_sort(),
                                                                                     declaration=define_int_const_node),
                                                      ast.FunctionApplicationASTNode("y", [], sort_ctx.get_int_sort(),
                                                                                     declaration=define_bv_const_node)],
                                                     sort_ctx.get_int_sort(),
                                                     declaration=declare_fun_node)

        # The let term's definitions shadow the constants and must not be replaced:
        term_2_node = ast.LetTermASTNode()
        term_2_node.set_definitions([("x", ast.LiteralASTNode(3, sort_ctx.get_int_sort())),
                                     ("y", ast.LiteralASTNode(3, sort_ctx.get_bv_sort(10)))])
        term_2_node.set_enclosed_term(ast.FunctionApplicationASTNode("foonction", [
                                         ast.FunctionApplicationASTNode("x", [], sort_ctx.get_int_sort(),
                                                                        declaration=term_2_node),
                                         ast.FunctionApplicationASTNode("y", [], sort_ctx.get_bv_sort(10),
                                                                        declaration=term_2_node)
                                      ], sort_ctx.get_int_sort()))

        assert_node = ast.AssertCommandASTNode(
            ast.FunctionApplicationASTNode("=", [term_1_node, term_2_node], sort_ctx.get_bool_sort())
        )

        test_data = [set_logic_node, define_int_const_node, define_bv_const_node,
                     declare_fun_node, assert_node]

        expected_ast = """
            SetLogicCommandASTNode Logic: QF_BV
            DeclareFunCommandASTNode FunctionName: foonction DomainSorts: ['Int', '(_ BitVec 10)'] RangeSort: Int
            AssertCommandASTNode
              FunctionApplicationASTNode Function: = Sort: Bool
                FunctionApplicationASTNode Function: foonction Sort: Int
                  LiteralASTNode Literal: 100 Sort: Int
                  LiteralASTNode Literal: 100 Sort: (_ BitVec 10)
                LetTermASTNode Symbols: ['x', 'y']
                  LiteralASTNode Literal: 3 Sort: Int
                  LiteralASTNode Literal: 3 Sort: (_ BitVec 10)
                  FunctionApplicationASTNode Function: foonction Sort: Int
                    FunctionApplicationASTNode Function: x Sort: Int
                    FunctionApplicationASTNode Function: y Sort: (_ BitVec 10)"""

        self.__expect_ast(expected_ast, 12, under_test.transform(test_data))

    def test_inlines_functions(self):
        under_test = ast_trans.FunctionDefinitionInliner()
        sort_ctx = sorts.SortContext()

        set_logic_node = ast.SetLogicCommandASTNode("QF_BV")
        fbody_node = ast.FunctionApplicationASTNode("+",
                                                    [ast.FunctionApplicationASTNode("x", [], sort_ctx.get_int_sort()),
                                                     ast.FunctionApplicationASTNode("y", [], sort_ctx.get_int_sort())],
                                                    sort_ctx.get_int_sort())
        define_fun_node = ast.DefineFunCommandASTNode("foonction",
                                                      [("x", sort_ctx.get_int_sort()),
                                                       ("y", sort_ctx.get_int_sort())],
                                                      sort_ctx.get_int_sort(),
                                                      fbody_node)
        fun_term_1_node = ast.FunctionApplicationASTNode("foonction",
                                                         [ast.LiteralASTNode(100, sort_ctx.get_int_sort()),
                                                          ast.LiteralASTNode(140, sort_ctx.get_int_sort())],
                                                         sort_ctx.get_int_sort(),
                                                         declaration=define_fun_node)
        fun_term_2_node = ast.FunctionApplicationASTNode("foonction",
                                                         [fun_term_1_node,
                                                          ast.LiteralASTNode(140, sort_ctx.get_int_sort())],
                                                         sort_ctx.get_int_sort(),
                                                         declaration=define_fun_node)

        assert_node = ast.AssertCommandASTNode(
            ast.FunctionApplicationASTNode("=", [ast.LiteralASTNode(100, sort_ctx.get_int_sort()), fun_term_2_node],
                                           sort_ctx.get_bool_sort()))

        test_data = [set_logic_node, define_fun_node, assert_node]

        expected_ast = """
            SetLogicCommandASTNode Logic: QF_BV
            AssertCommandASTNode
              FunctionApplicationASTNode Function: = Sort: Bool
                LiteralASTNode Literal: 100 Sort: Int
                LetTermASTNode Symbols: ['x', 'y']
                  LetTermASTNode Symbols: ['x', 'y']
                    LiteralASTNode Literal: 100 Sort: Int
                    LiteralASTNode Literal: 140 Sort: Int
                    FunctionApplicationASTNode Function: + Sort: Int
                      FunctionApplicationASTNode Function: x Sort: Int
                      FunctionApplicationASTNode Function: y Sort: Int
                  LiteralASTNode Literal: 140 Sort: Int
                  FunctionApplicationASTNode Function: + Sort: Int
                    FunctionApplicationASTNode Function: x Sort: Int
                    FunctionApplicationASTNode Function: y Sort: Int"""

        self.__expect_ast(expected_ast, 12, under_test.transform(test_data))

