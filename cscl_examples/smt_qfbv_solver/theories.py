import abc
import cscl_examples.smt_qfbv_solver.sorts as sorts
import cscl_examples.smt_qfbv_solver.syntactic_scope as synscope
import cscl_examples.smt_qfbv_solver.ast as ast


class TheorySyntacticFunctionScopeFactory(abc.ABC):
    """
    Base class for SyntacticFunctionScopeFactory factories for an SMT theory
    """

    @abc.abstractmethod
    def create_syntactic_scope(self,
                               sort_ctx: sorts.SortContext) -> synscope.SyntacticFunctionScope:
        """
        Creates a SyntacticFunctionScope containing the theory's function signatures.

        :param sort_ctx: The sort context for the function signatures.
        :return: A syntactic function scope containing the theory's function signatures.
        """
        pass


class CoreSyntacticFunctionScopeFactory(TheorySyntacticFunctionScopeFactory):
    """
    A SyntacticFunctionScopeFactory for the Core theory.

    See http://smtlib.cs.uiowa.edu/theories-Core.shtml
    """

    @staticmethod
    def __add_comparison_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __comp_sig_fn(x):
            if len(x) == 2 and (x[0] is x[1]):
                return sort_ctx.get_bool_sort()
            return None

        comp_signature = ast.FunctionSignature(__comp_sig_fn, 2, False)

        target.add_declaration(ast.FunctionDeclaration("=", comp_signature))
        target.add_declaration(ast.FunctionDeclaration("distinct", comp_signature))

    @staticmethod
    def __add_ite_fn(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __ite_sig_fn(x):
            if len(x) == 3 and x[0] is sort_ctx.get_bool_sort() and (x[1] is x[2]):
                return x[1]
            return None
        target.add_declaration(ast.FunctionDeclaration("ite", ast.FunctionSignature(__ite_sig_fn, 3, False)))

    @staticmethod
    def __add_not_fn(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __not_sig_fn(x):
            if len(x) == 1 and isinstance(x[0], sorts.BooleanSort):
                return sort_ctx.get_bool_sort()
            return None

        target.add_declaration(ast.FunctionDeclaration("not", ast.FunctionSignature(__not_sig_fn, 1, False)))

    @staticmethod
    def __add_binary_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __binary_bool_sig_fn(x):
            if len(x) == 2 and isinstance(x[0], sorts.BooleanSort) and (x[0] is x[1]):
                return sort_ctx.get_bool_sort()
            return None

        binary_bool_signature = ast.FunctionSignature(__binary_bool_sig_fn, 2, False)

        target.add_declaration(ast.FunctionDeclaration("=>", binary_bool_signature))
        target.add_declaration(ast.FunctionDeclaration("and", binary_bool_signature))
        target.add_declaration(ast.FunctionDeclaration("or", binary_bool_signature))
        target.add_declaration(ast.FunctionDeclaration("xor", binary_bool_signature))

    @staticmethod
    def __add_constants(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __constant_bool_sig_fn(_):
            return sort_ctx.get_bool_sort()
        target.add_declaration(ast.FunctionDeclaration("true", ast.FunctionSignature(__constant_bool_sig_fn,
                                                                                     0, False)))
        target.add_declaration(ast.FunctionDeclaration("false", ast.FunctionSignature(__constant_bool_sig_fn,
                                                                                      0, False)))

    def create_syntactic_scope(self,
                               sort_ctx: sorts.SortContext) -> synscope.SyntacticFunctionScope:
        result = synscope.SyntacticFunctionScope(None)
        self.__add_comparison_fns(result, sort_ctx)
        self.__add_ite_fn(result, sort_ctx)
        self.__add_not_fn(result, sort_ctx)
        self.__add_binary_fns(result, sort_ctx)
        self.__add_constants(result, sort_ctx)
        return result


class FixedSizeBVSyntacticFunctionScopeFactory(TheorySyntacticFunctionScopeFactory):
    """
    A SyntacticFunctionScopeFactory for the FixedSizeBitVectors theory.

    See http://smtlib.cs.uiowa.edu/theories-FixedSizeBitVectors.shtml
    """

    @staticmethod
    def __add_concat_fn(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __concat_sig_fn(x):
            if len(x) == 2 and all(isinstance(z, sorts.BitvectorSort) for z in x):
                return sort_ctx.get_bv_sort(x[0].get_len() + x[1].get_len())
        target.add_declaration(ast.FunctionDeclaration("concat",
                                                       ast.FunctionSignature(__concat_sig_fn, 2, False)))

    @staticmethod
    def __add_extract_fn(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __extract_sig_fn(x):
            if len(x) == 3 and type(x[0]) is int and type(x[1]) is int and isinstance(x[2], sorts.BitvectorSort):
                i, j = x[0:2]
                if (x[2].get_len() > i) and (i >= j) and (j >= 0):
                    return sort_ctx.get_bv_sort(i - j + 1)
        decl = synscope.SyntacticFunctionScope.mangle_parametrized_function_name("extract")
        sig = ast.FunctionSignature(__extract_sig_fn, 1, False, 2)
        target.add_declaration(ast.FunctionDeclaration(decl, sig))

    @staticmethod
    def __add_bv_neg_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __neg_sig_fn(x):
            if len(x) == 1 and isinstance(x[0], sorts.BitvectorSort):
                return sort_ctx.get_bv_sort(x[0].get_len())
        neg_sig = ast.FunctionSignature(__neg_sig_fn, 1, False)
        target.add_declaration(ast.FunctionDeclaration("bvneg", neg_sig))
        target.add_declaration(ast.FunctionDeclaration("bvnot", neg_sig))

    @staticmethod
    def __add_bv_binary_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __binary_sig_fn(x):
            if len(x) == 2 and all(isinstance(z, sorts.BitvectorSort) for z in x) and x[0].get_len() == x[1].get_len():
                return sort_ctx.get_bv_sort(x[0].get_len())
        binary_sig = ast.FunctionSignature(__binary_sig_fn, 2, False)

        for name in ("bvand", "bvor", "bvadd", "bvmul", "bvudiv", "bvurem", "bvshl", "bvlshr"):
            target.add_declaration(ast.FunctionDeclaration(name, binary_sig))

    @staticmethod
    def __add_comparison_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __comp_sig_fn(x):
            if len(x) == 2 and all(isinstance(z, sorts.BitvectorSort) for z in x) and x[0].get_len() == x[1].get_len():
                return sort_ctx.get_bool_sort()

        target.add_declaration(ast.FunctionDeclaration("bvult",
                                                       ast.FunctionSignature(__comp_sig_fn, 2, False)))

    def create_syntactic_scope(self,
                               sort_ctx: sorts.SortContext) -> synscope.SyntacticFunctionScope:
        result = synscope.SyntacticFunctionScope(None)
        self.__add_concat_fn(result, sort_ctx)
        self.__add_extract_fn(result, sort_ctx)
        self.__add_bv_neg_fns(result, sort_ctx)
        self.__add_bv_binary_fns(result, sort_ctx)
        self.__add_comparison_fns(result, sort_ctx)

        return result


class QFBVExtSyntacticFunctionScopeFactory(TheorySyntacticFunctionScopeFactory):
    """
    A SyntacticFunctionScopeFactory for the extensions defined in the QF_BV logic.

    For the sake of simplicity, the extensions defined in the QF_BV logic (e.g. the bvnand function)
    are elevated to the "theory" status, even though they can be defined in terms of the FixedSizeBitVectors
    theory.

    See http://smtlib.cs.uiowa.edu/theories-FixedSizeBitVectors.shtml
        http://smtlib.cs.uiowa.edu/logics-all.shtml#QF_BV
    """

    @staticmethod
    def __add_bv_binary_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __binary_sig_fn(x):
            if len(x) == 2 and all(isinstance(z, sorts.BitvectorSort) for z in x) and x[0].get_len() == x[1].get_len():
                return sort_ctx.get_bv_sort(x[0].get_len())

        binary_sig = ast.FunctionSignature(__binary_sig_fn, 2, False)

        for name in ("bvnand", "bvnor", "bvxor", "bvxnor", "bvcomp", "bvsub", "bvsdiv", "bvsrem", "bvsmod", "bvashr"):
            target.add_declaration(ast.FunctionDeclaration(name, binary_sig))

    @staticmethod
    def __add_comparison_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __comp_sig_fn(x):
            if len(x) == 2 and all(isinstance(z, sorts.BitvectorSort) for z in x) and x[0].get_len() == x[1].get_len():
                return sort_ctx.get_bool_sort()
        comp_sig = ast.FunctionSignature(__comp_sig_fn, 2, False)

        for name in ("bvule", "bvugt", "bvuge", "bvslt", "bvsle", "bvsgt", "bvsge"):
            target.add_declaration(ast.FunctionDeclaration(name, comp_sig))

    @staticmethod
    def __add_repeat_fn(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __repeat_sig_fn(x):
            if len(x) == 2 and type(x[0]) is int and isinstance(x[1], sorts.BitvectorSort):
                return sort_ctx.get_bv_sort(x[0] * x[1].get_len())
        fname = synscope.SyntacticFunctionScope.mangle_parametrized_function_name("repeat")
        target.add_declaration(ast.FunctionDeclaration(fname,
                                                       ast.FunctionSignature(__repeat_sig_fn, 1, False, 1)))

    @staticmethod
    def __add_extend_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __extend_sig_fn(x):
            if len(x) == 2 and type(x[0]) is int and isinstance(x[1], sorts.BitvectorSort):
                return sort_ctx.get_bv_sort(x[0] + x[1].get_len())
        extend_sig = ast.FunctionSignature(__extend_sig_fn, 1, False, 1)
        zero_extend_name = synscope.SyntacticFunctionScope.mangle_parametrized_function_name("zero_extend")
        sign_extend_name = synscope.SyntacticFunctionScope.mangle_parametrized_function_name("sign_extend")
        target.add_declaration(ast.FunctionDeclaration(zero_extend_name, extend_sig))
        target.add_declaration(ast.FunctionDeclaration(sign_extend_name, extend_sig))

    @staticmethod
    def __add_rotate_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __rotate_sig_fn(x):
            if len(x) == 2 and type(x[0]) is int and isinstance(x[1], sorts.BitvectorSort):
                return sort_ctx.get_bv_sort(x[1].get_len())
        rotate_sig = ast.FunctionSignature(__rotate_sig_fn, 1, False, 1)
        rl_name = synscope.SyntacticFunctionScope.mangle_parametrized_function_name("rotate_left")
        rr_name = synscope.SyntacticFunctionScope.mangle_parametrized_function_name("rotate_right")
        target.add_declaration(ast.FunctionDeclaration(rl_name, rotate_sig))
        target.add_declaration(ast.FunctionDeclaration(rr_name, rotate_sig))

    def create_syntactic_scope(self,
                               sort_ctx: sorts.SortContext) -> synscope.SyntacticFunctionScope:
        result = synscope.SyntacticFunctionScope(None)
        self.__add_bv_binary_fns(result, sort_ctx)
        self.__add_comparison_fns(result, sort_ctx)
        self.__add_repeat_fn(result, sort_ctx)
        self.__add_extend_fns(result, sort_ctx)
        self.__add_rotate_fns(result, sort_ctx)
        return result
