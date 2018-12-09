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
    elif parsed_sexp == "Bool":
        return sort_ctx.get_bool_sort()
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

    def get_parent(self):
        """
        Gets the scope's parent scope.

        :return: The current scope's parent scope.
        """


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


def parse_smtlib2_func_application_term(parsed_sexp, sort_ctx: sorts.SortContext,
                                        fun_scope: SyntacticFunctionScope) -> ast.TermASTNode:
    """
    Parses an STMLib2-formatted term that is given as a list and is not a let term.

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


def parse_smtlib2_let_term(parsed_sexp, sort_ctx: sorts.SortContext,
                           fun_scope: SyntacticFunctionScope) -> ast.LetTermASTNode:
    """
    Parses an SMTLib2-formatted let term.

    :param parsed_sexp: The term's s-expression.
    :param sort_ctx: The current sort context.
    :param fun_scope: The current function scope.
    :return: A LetTermASTNode representing parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed term.
    """
    if len(parsed_sexp) != 3 or type(parsed_sexp[1]) is not list:
        raise ValueError("Malformed let term")

    fun_scope_extension = SyntacticFunctionScope(fun_scope)

    let_defs = []
    for (x, y) in parsed_sexp[1]:
        defining_term = parse_smtlib2_term(y, sort_ctx, fun_scope)
        const_sort = defining_term.get_sort()
        const_sig = (lambda const_sort_: FunctionSignature(lambda z: const_sort_ if len(z) == 0 else None,
                                                           0, True))(const_sort)
        fun_scope_extension.add_signature(x, const_sig)
        let_defs.append((x, defining_term))

    enclosed_term = parse_smtlib2_term(parsed_sexp[2], sort_ctx, fun_scope_extension)
    return ast.LetTermASTNode(let_defs, enclosed_term)


def parse_smtlib2_term(parsed_sexp, sort_ctx: sorts.SortContext, fun_scope: SyntacticFunctionScope) -> ast.TermASTNode:
    """
    Parses an SMTLib2-formatted term.

    :param parsed_sexp: The term's s-expression.
    :param sort_ctx: The current sort context.
    :param fun_scope: The current function scope.
    :return: A TermASTNode representing parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed term.
    """
    if type(parsed_sexp) is not list:
        return parse_smtlib2_flat_term(parsed_sexp, sort_ctx, fun_scope)
    if parsed_sexp[0] == "let":
        return parse_smtlib2_let_term(parsed_sexp, sort_ctx, fun_scope)
    return parse_smtlib2_func_application_term(parsed_sexp, sort_ctx, fun_scope)


def parse_cmd_assert(parsed_sexp, sort_ctx: sorts.SortContext, scope: SyntacticFunctionScope):
    """
    Parses an SMTLib2-formatted assert command.

    :param parsed_sexp: The assert command's s-expression.
    :param sort_ctx: The current sort context.
    :param scope: The current scope.
    :return: An AssertCommandASTNode representing parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed term.
    """
    if len(parsed_sexp) != 2:
        raise ValueError("The assert command requires exactly one argument")
    term = parse_smtlib2_term(parsed_sexp[1], sort_ctx, scope)
    if not isinstance(term.get_sort(), sorts.BooleanSort):
        raise ValueError("The argument of assert commands must be of the Boolean sort")
    return ast.AssertCommandASTNode(term)


def parse_cmd_declare_fun(parsed_sexp, sort_ctx: sorts.SortContext):
    """
    Parses an SMTLib2-formatted declare-fun command.

    :param parsed_sexp: The command's s-expression.
    :param sort_ctx: The current sort context.
    :return: A tuple x,y with x being a DeclareFunCommandASTNode representing parsed_sexp and y being the declared
             function's signature.
    :raises ValueError if parsed_sexp is a malformed term.
    """
    if len(parsed_sexp) != 4 or type(parsed_sexp[1]) != str or type(parsed_sexp[2]) != list:
        raise ValueError("Invalid declare-fun command")
    fun_name, domain_sorts_sexp, range_sort_sexp = parsed_sexp[1:]
    domain_sorts = [parse_smtlib2_sort(x, sort_ctx=sort_ctx) for x in domain_sorts_sexp]
    range_sort = parse_smtlib2_sort(range_sort_sexp, sort_ctx=sort_ctx)

    def __signature_fn(concrete_dom_sigs):
        if list(concrete_dom_sigs) == domain_sorts:
            return range_sort
        return None

    return ast.DeclareFunCommandASTNode(fun_name, domain_sorts, range_sort), FunctionSignature(__signature_fn,
                                                                                               len(domain_sorts),
                                                                                               True)


def parse_cmd_declare_const(parsed_sexp, sort_ctx: sorts.SortContext):
    """
    Parses an SMTLib2-formatted declare-const command.

    :param parsed_sexp: The command's s-expression.
    :param sort_ctx: The current sort context.
    :return: A tuple x,y with x being a DeclareFunCommandASTNode representing parsed_sexp and y being the declared
             function's signature.
    :raises ValueError if parsed_sexp is a malformed term.
    """
    if len(parsed_sexp) != 3 or type(parsed_sexp[1]) != str:
        raise ValueError("Invalid declare-const command")
    fun_name, range_sort_sexp = parsed_sexp[1:]
    range_sort = parse_smtlib2_sort(range_sort_sexp, sort_ctx=sort_ctx)

    def __signature_fn(concrete_dom_sigs):
        if len(concrete_dom_sigs) == 0:
            return range_sort
        return None

    return ast.DeclareFunCommandASTNode(fun_name, [], range_sort), FunctionSignature(__signature_fn,
                                                                                     0, True)


def parse_smtlib2_problem(parsed_sexp):
    """
    Parses an SMTLib2-formatted SMT problem.

    This parser currently only supports a subset of SMTLib2. TODO: document the supported SMTLib2 subset.

    :param parsed_sexp: The command's s-expression.
    :return: A list of ASTNodes, representing parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed problem.
    """
    problem_toplevel_function_scope = SyntacticFunctionScope(None)
    sort_context = sorts.SortContext()
    push_level = 0

    def parse_command(sexp):
        nonlocal problem_toplevel_function_scope  # Needs to be changed by push and pop commands
        nonlocal push_level  # Needs to be changed by push and pop commands

        if len(sexp) == 0:
            raise ValueError("Missing command")
        command = sexp[0]

        if command == "assert":
            return parse_cmd_assert(sexp, sort_context, problem_toplevel_function_scope)

        elif command == "check-sat":
            return ast.CheckSATCommandASTNode()

        elif command == "declare-fun":
            ast_node, fun_signature = parse_cmd_declare_fun(sexp, sort_context)
            problem_toplevel_function_scope.add_signature(ast_node.get_fun_name(), fun_signature)
            return ast_node

        elif command == "declare-const":
            ast_node, fun_signature = parse_cmd_declare_const(sexp, sort_context)
            problem_toplevel_function_scope.add_signature(ast_node.get_fun_name(), fun_signature)
            return ast_node

        elif command == "set-logic":
            if len(sexp) != 2 or not type(sexp[1]) == str:
                raise ValueError("Invalid set-logic command")
            # TODO: parse the logic and extend the current function scope with the theory
            return ast.SetLogicCommandASTNode(sexp[1])

        elif command == "push":
            if len(sexp) > 2:
                raise ValueError("Invalid push command")
            amnt = 1 if len(sexp) == 1 else int(sexp[1])
            if amnt < 0:
                raise ValueError("Invalid negative argument for push command")

            for i in range(0, amnt):
                new_scope = SyntacticFunctionScope(problem_toplevel_function_scope)
                problem_toplevel_function_scope = new_scope

            push_level += amnt

        elif command == "pop":
            if len(sexp) > 2:
                raise ValueError("Invalid pop command")
            amnt = 1 if len(sexp) == 1 else int(sexp[1])
            if amnt < 0:
                raise ValueError("Invalid negative argument for pop command")

            if push_level - amnt < 0:
                raise ValueError("Invalid pop command: no corresponding push command")

            for i in range(0, amnt):
                problem_toplevel_function_scope = problem_toplevel_function_scope.get_parent()

            push_level -= amnt

        elif command == "set-info":
            pass  # Ignore set-info commands

        else:
            raise ValueError("Unsupported command " + command)

    return [parse_command(x) for x in parsed_sexp]
