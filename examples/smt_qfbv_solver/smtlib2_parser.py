from typing import Union
import examples.smt_qfbv_solver.sorts as sorts
import examples.smt_qfbv_solver.ast as ast


def parse_smtlib2_literal(lit_string: str, sort_ctx: sorts.SortContext) -> Union[ast.LiteralASTNode, type(None)]:
    """
    Parses an SMTLib2-format literal.

    :param lit_string: The string representation of the literal.
    :param sort_ctx: A sort context.
    :return: A new LiteralASTNode corresponding to lit_string, with its sort obtained from sort_ctx.
    :raises ValueError if the literal is malformed or unsupported.
    """
    if len(lit_string) == 0:
        raise ValueError("Malformed literal")

    if '.' in lit_string:
        raise ValueError("Decimals are not supported")

    if lit_string.isnumeric():
        if lit_string.startswith("00"):
            raise ValueError("Illegal extra leading 0 in integer literal")
        return ast.LiteralASTNode(int(lit_string), sort_ctx.get_int_sort())
    elif lit_string.startswith("#b"):
        lit_value = 0
        exp = 0
        for i in reversed(range(2, len(lit_string))):
            lit_value |= (1 << exp) if lit_string[i] == '1' else 0
            exp += 1
        return ast.LiteralASTNode(lit_value, sort_ctx.get_bv_sort(len(lit_string)-2))
    elif lit_string.startswith("\""):
        # not supported
        raise ValueError("String literals are not supported")
    return None


def parse_smtlib2_sort(parsed_sexp, sort_ctx: sorts.SortContext):
    """
    Parses an SMTLib2-formatted sort expression.

    :param parsed_sexp: The sort's s-expression, e.g. "Int" or ["_", "BitVec", "32"].
    :param sort_ctx: A sort context.
    :return: The sort corresponding to parsed_sexp.
    :raises ValueError if parsed_sexp is not a well-formed sort s-expression, or if the sort is unsupported.
    """
    if parsed_sexp == "Int":
        return sort_ctx.get_int_sort()
    elif len(parsed_sexp) == 3 and parsed_sexp[0:2] == ["_", "BitVec"]:
        length_str = parsed_sexp[2]
        if not length_str.isnumeric() or '.' in length_str:
            raise ValueError("Illegal BitVec type length in " + str(parsed_sexp))
        return sort_ctx.get_bv_sort(int(length_str))
    raise ValueError("Unsupported sort " + str(parsed_sexp))


class FunctionSignature:
    """
    A function signature.
    """

    def __init__(self, domain_sorts_to_range_sort_fn, arity: int, is_shadowable: bool):
        """
        Initializes the FunctionSignature object.

        :param domain_sorts_to_range_sort_fn: The function determining the represented function's signature.
                                              For Sort objects s1, ..., sN, domain_sorts_to_range_sort_fn((s1, ..., sN))
                                              returns the function's range sort for parameter sorts s1, ..., sN;
                                              If s1, ..., sN is not part of the function's domain, None is returned.
        :param arity: The function's arity.
        :param is_shadowable: True iff the function may be shadowed and may shadow other functions; False otherwise.
        """
        self.__dtr_fun = domain_sorts_to_range_sort_fn
        self.__arity = arity
        self.__is_shadowable = is_shadowable

    def get_range_sort(self, domain_sorts):
        """
        Gets the function's range sort for domain sorts s1, ..., sN.

        :param domain_sorts: The query's domain sorts.
        :return: The corresponding range sort, or None domain_sorts is not part of the function's domain.
        """
        return self.__dtr_fun(domain_sorts)

    def get_arity(self):
        """
        Gets the function's arity.

        :return: The function's arity.
        """
        return self.__arity

    def is_shadowable(self):
        """
        Returns True iff the function may be shadowed and may shadow other function declarations.

        :return: True iff the function may be shadowed and may shadow other function declarations.
        """
        return self.__is_shadowable


class SyntacticFunctionScope:
    """
    A scope of function declarations.
    """

    def __init__(self, parent_scope):
        """
        Initializes the SyntacticFunctionScope object.

        :param parent_scope: The scope's parent scope. If the scope has no parent scope, this argument must be None.
        """
        self.__parent = parent_scope
        self.__signatures = dict()

    def get_signature(self, func_name: str) -> Union[FunctionSignature, type(None)]:
        """
        Gets the function signature for a function.

        If this scope does not contain a matching function signature and this scope has
        a parent scope, the parent scope is queried for a function signature for func_name.

        :param func_name: The function's name.
        :return: The function's signature. If the scope has no function with name func_name, None is returned instead.
        """
        if func_name in self.__signatures.keys():
            return self.__signatures[func_name]
        elif self.__parent is not None:
            return self.__parent.get_signature(func_name)
        else:
            return None

    def add_signature(self, func_name: str, signature: FunctionSignature):
        """
        Adds a function signature to the scope.

        :param func_name: The function's name.
        :param signature: The function's signature.
        :return: None
        :raises ValueError if adding a function named func_name is prevented by the existence of a same-named,
                           unshadowable function in this scope.
        """
        if self.has_unshadowable_signature(func_name):
            raise ValueError("Function " + func_name + " cannot be redefined or shadowed")
        self.__signatures[func_name] = signature

    def has_unshadowable_signature(self, func_name):
        """
        Determines whether the given function name is associated with an unshadowable function.

        :param func_name: The function's name.
        :return: True iff the given function name is associated with an unshadowable function.
        """
        func_signature = self.get_signature(func_name)
        if func_signature is None:
            return False
        else:
            return not func_signature.is_shadowable()

    def set_parent(self, new_parent):
        """
        Sets the scope's parent scope.

        :param new_parent: The new parent scope.
        :return: None
        """
        self.__parent = new_parent


def parse_smtlib2_flat_term(parsed_sexp, sort_ctx: sorts.SortContext,
                            fun_scope: SyntacticFunctionScope) -> ast.TermASTNode:
    """
    Parses an STMLib2-formatted term that is not a list, i.e. is a literal or a constant symbol.

    :param parsed_sexp: The term's s-expression.
    :param sort_ctx: The current sort context.
    :param fun_scope: The current function scope.
    :return: A LiteralASTNode if parsed_sexp represents a literal, or a FunctionApplicationASTNode if parsed_sexp
             represents a constant symbol. The returned AST node represents parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed term.
    """
    lit = parse_smtlib2_literal(parsed_sexp, sort_ctx)
    if lit is not None:
        return lit
    else:
        constant_sig = fun_scope.get_signature(parsed_sexp)
        if constant_sig is None or constant_sig.get_arity() != 0:
            raise ValueError("Malformed constant")
        else:
            return ast.FunctionApplicationASTNode(parsed_sexp, tuple(), constant_sig.get_range_sort(tuple()))


def parse_smtlib2_complex_term(parsed_sexp, sort_ctx: sorts.SortContext,
                               fun_scope: SyntacticFunctionScope) -> ast.TermASTNode:
    """
    Parses an STMLib2-formatted term that is given as a list.

    :param parsed_sexp: The term's s-expression.
    :param sort_ctx: The current sort context.
    :param fun_scope: The current function scope.
    :return: A FunctionApplicationASTNode representing parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed term.
    """
    if len(parsed_sexp) == 0:
        raise ValueError("Empty term")

    fname = parsed_sexp[0]
    fsig = fun_scope.get_signature(fname)

    if fsig is None:
        raise ValueError("Undeclared function " + fname)
    if fsig.get_arity() != len(parsed_sexp)-1:
        raise ValueError("Illegal number of arguments for function " + fname)

    args = [parse_smtlib2_term(x, sort_ctx, fun_scope) for x in parsed_sexp[1:]]

    term_sort = fsig.get_range_sort((x.get_sort() for x in args))
    if term_sort is None:
        raise ValueError("Illegally typed arguments for function " + fname)

    return ast.FunctionApplicationASTNode(fname, args, term_sort)


def parse_smtlib2_term(parsed_sexp, sort_ctx: sorts.SortContext, fun_scope: SyntacticFunctionScope) -> ast.TermASTNode:
    """
    Parses an STMLib2-formatted term.

    :param parsed_sexp: The term's s-expression.
    :param sort_ctx: The current sort context.
    :param fun_scope: The current function scope.
    :return: A TermASTNode representing parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed term.
    """
    if type(parsed_sexp) is not list:
        return parse_smtlib2_flat_term(parsed_sexp, sort_ctx, fun_scope)
    return parse_smtlib2_complex_term(parsed_sexp, sort_ctx, fun_scope)
