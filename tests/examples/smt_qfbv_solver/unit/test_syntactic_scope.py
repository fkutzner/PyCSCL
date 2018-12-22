import unittest
import examples.smt_qfbv_solver.sorts as sorts
import examples.smt_qfbv_solver.syntactic_scope as synscope
import examples.smt_qfbv_solver.ast as ast


class TestSyntacticFunctionScope(unittest.TestCase):
    def test_has_added_signature(self):
        sort_ctx = sorts.SortContext()
        sig = synscope.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                         1, True)
        under_test = synscope.SyntacticFunctionScope(None)
        under_test.add_signature("foo", sig)
        decl = ast.DeclareFunCommandASTNode("foo", [sort_ctx.get_bv_sort(2)], sort_ctx.get_int_sort())
        under_test.add_declaration("foo", decl)

        lookup_result = under_test.get_signature("foo")
        assert lookup_result is not None
        result_sig, result_name = lookup_result
        assert result_sig is sig
        assert result_name == "foo"
        assert under_test.get_declaration("foo") is decl

    def test_queries_parent_scope(self):
        sort_ctx = sorts.SortContext()
        sig = synscope.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                         1, True)
        parent = synscope.SyntacticFunctionScope(None)
        under_test = synscope.SyntacticFunctionScope(parent)
        parent.add_signature("foo", sig)
        decl = ast.DeclareFunCommandASTNode("foo", [sort_ctx.get_bv_sort(2)], sort_ctx.get_int_sort())
        parent.add_declaration("foo", decl)

        lookup_result = under_test.get_signature("foo")
        assert lookup_result is not None
        result_sig, result_name = lookup_result
        assert result_sig is sig
        assert result_name == "foo"
        assert under_test.get_declaration("foo") is decl

    def test_set_parent_scope(self):
        sort_ctx = sorts.SortContext()
        sig = synscope.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                         1, True)
        parent = synscope.SyntacticFunctionScope(None)
        under_test = synscope.SyntacticFunctionScope(None)
        under_test.set_parent(parent)
        parent.add_signature("foo", sig)
        decl = ast.DeclareFunCommandASTNode("foo", [sort_ctx.get_bv_sort(2)], sort_ctx.get_int_sort())
        parent.add_declaration("foo", decl)

        lookup_result = under_test.get_signature("foo")
        assert lookup_result is not None
        result_sig, result_name = lookup_result
        assert result_sig is sig
        assert result_name == "foo"
        assert under_test.get_declaration("foo") is decl

    def test_get_parent_scope(self):
        parent = synscope.SyntacticFunctionScope(None)
        child = synscope.SyntacticFunctionScope(parent)
        assert child.get_parent() is parent

    def test_refuses_to_add_when_unshadowable(self):
        sort_ctx = sorts.SortContext()
        sig = synscope.FunctionSignature(lambda x: sort_ctx.get_int_sort() if x == [sort_ctx.get_bv_sort(2)] else None,
                                         1, False)
        parent = synscope.SyntacticFunctionScope(None)
        parent.add_signature("foo", sig)

        under_test = synscope.SyntacticFunctionScope(parent)
        with self.assertRaises(ValueError):
            under_test.add_signature("foo", sig)
