import abc
import examples.smt_qfbv_solver.sorts as sorts
import examples.smt_qfbv_solver.syntactic_scope as synscope


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

        comp_signature = synscope.FunctionSignature(__comp_sig_fn, 2, False)

        target.add_signature("=", comp_signature)
        target.add_signature("distinct", comp_signature)

    @staticmethod
    def __add_ite_fn(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __ite_sig_fn(x):
            if len(x) == 3 and x[0] is sort_ctx.get_bool_sort() and (x[1] is x[2]):
                return x[1]
            return None
        target.add_signature("ite", synscope.FunctionSignature(__ite_sig_fn, 3, False))

    @staticmethod
    def __add_not_fn(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __not_sig_fn(x):
            if len(x) == 1 and isinstance(x[0], sorts.BooleanSort):
                return sort_ctx.get_bool_sort()
            return None

        target.add_signature("not", synscope.FunctionSignature(__not_sig_fn, 1, False))

    @staticmethod
    def __add_binary_fns(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __binary_bool_sig_fn(x):
            if len(x) == 2 and isinstance(x[0], sorts.BooleanSort) and (x[0] is x[1]):
                return sort_ctx.get_bool_sort()
            return None

        binary_bool_signature = synscope.FunctionSignature(__binary_bool_sig_fn, 2, False)

        target.add_signature("=>", binary_bool_signature)
        target.add_signature("and", binary_bool_signature)
        target.add_signature("or", binary_bool_signature)
        target.add_signature("xor", binary_bool_signature)

    @staticmethod
    def __add_constants(target: synscope.SyntacticFunctionScope, sort_ctx: sorts.SortContext):
        def __constant_bool_sig_fn(_):
            return sort_ctx.get_bool_sort()
        target.add_signature("true", synscope.FunctionSignature(__constant_bool_sig_fn, 0, False))
        target.add_signature("false", synscope.FunctionSignature(__constant_bool_sig_fn, 0, False))

    def create_syntactic_scope(self,
                               sort_ctx: sorts.SortContext) -> synscope.SyntacticFunctionScope:
        result = synscope.SyntacticFunctionScope(None)
        self.__add_comparison_fns(result, sort_ctx)
        self.__add_ite_fn(result, sort_ctx)
        self.__add_not_fn(result, sort_ctx)
        self.__add_binary_fns(result, sort_ctx)
        self.__add_constants(result, sort_ctx)
        return result
