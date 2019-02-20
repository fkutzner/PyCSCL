import unittest
import cscl_examples.smt_qfbv_solver.sorts as sorts
import cscl_examples.smt_qfbv_solver.syntactic_scope as synscope
import cscl_examples.smt_qfbv_solver.ast as ast


class TestSyntacticFunctionScope(unittest.TestCase):
    def test_has_added_signature(self):
        sort_ctx = sorts.SortContext()
        sig = ast.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        decl = ast.FunctionDeclaration("foo", sig)

        under_test = synscope.SyntacticFunctionScope(None)
        under_test.add_declaration(decl)

        lookup_result = under_test.get_declaration("foo")
        assert lookup_result is decl

    def test_queries_parent_scope(self):
        sort_ctx = sorts.SortContext()
        sig = ast.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        decl = ast.FunctionDeclaration("foo", sig)

        parent = synscope.SyntacticFunctionScope(None)
        under_test = synscope.SyntacticFunctionScope(parent)
        parent.add_declaration(decl)

        lookup_result = under_test.get_declaration("foo")
        assert lookup_result is decl

    def test_set_parent_scope(self):
        sort_ctx = sorts.SortContext()
        sig = ast.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, True)
        decl = ast.FunctionDeclaration("foo", sig)

        parent = synscope.SyntacticFunctionScope(None)
        under_test = synscope.SyntacticFunctionScope(None)
        under_test.set_parent(parent)
        parent.add_declaration(decl)

        lookup_result = under_test.get_declaration("foo")
        assert lookup_result is decl

    def test_get_parent_scope(self):
        parent = synscope.SyntacticFunctionScope(None)
        child = synscope.SyntacticFunctionScope(parent)
        assert child.get_parent() is parent

    def test_refuses_to_add_when_unshadowable(self):
        sort_ctx = sorts.SortContext()
        sig = ast.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                    1, False)
        decl = ast.FunctionDeclaration("foo", sig)

        parent = synscope.SyntacticFunctionScope(None)
        parent.add_declaration(decl)

        under_test = synscope.SyntacticFunctionScope(parent)
        with self.assertRaises(ValueError):
            under_test.add_declaration(decl)
