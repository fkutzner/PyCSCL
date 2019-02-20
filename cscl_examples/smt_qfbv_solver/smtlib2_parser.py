from typing import Union
import re
import cscl_examples.smt_qfbv_solver.sorts as sorts
import cscl_examples.smt_qfbv_solver.ast as ast
import cscl_examples.smt_qfbv_solver.theories as theories
from cscl_examples.smt_qfbv_solver.syntactic_scope import SyntacticFunctionScope
from cscl_examples.smt_qfbv_solver.ast import FunctionSignature, FunctionDeclaration


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


simple_symbol_regex = re.compile("[a-zA-Z~!@$%^&*+=<>.?/-][0-9a-zA-Z~!@$%^&*+=<>.?/-]*")
reserved_words = ("let", "par", "_", "!", "as", "forall", "exists", "NUMERAL", "DECIMAL", "STRING",
                  "set-logic", "assert", "declare-fun", "declare-const", "define-fun", "define-const",
                  "check-sat", "push", "pop", "get-model", "get-unsat-core", "set-info", "get-info",
                  "declare-sort", "define-sort", "get-assertions", "get-proof", "get-value", "get-assignment",
                  "get-option", "set-option", "exit")


def parse_smtlib2_symbol(symbol: str) -> str:
    if len(symbol) >= 2 and symbol[0] == '|' and symbol[len(symbol)-1] == '|':
        raise ValueError("Error parsing symbol " + symbol + ": quoted symbols not supported yet")
    else:
        if ' ' not in symbol\
                and symbol not in reserved_words\
                and simple_symbol_regex.match(symbol):
            return symbol
        else:
            raise ValueError("Illegal symbol " + symbol)


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
        constant_decl = fun_scope.get_declaration(parsed_sexp)
        if constant_decl is None or constant_decl.get_signature().get_arity() != 0:
            raise ValueError("Malformed constant")
        else:
            return ast.FunctionApplicationASTNode(constant_decl, tuple())


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

    if type(parsed_sexp[0]) is list:
        param_fn_sexp = parsed_sexp[0]
        if len(param_fn_sexp) < 2\
                or param_fn_sexp[0] != "_"\
                or not all(x.isnumeric() for x in param_fn_sexp[2:]):
            raise ValueError("Malformed parametrized function expression " + str(param_fn_sexp))
        fname = SyntacticFunctionScope.mangle_parametrized_function_name(param_fn_sexp[1])
        fparams = tuple(int(x) for x in param_fn_sexp[2:])
    else:
        fname = parsed_sexp[0]
        fparams = tuple()

    if fun_scope.get_declaration(fname) is None:
        raise ValueError("Undeclared function " + fname)

    args = [parse_smtlib2_term(x, sort_ctx, fun_scope) for x in parsed_sexp[1:]]

    # FunctionApplicationASTNode raises ValueError if the term is not well-sorted:
    return ast.FunctionApplicationASTNode(fun_scope.get_declaration(fname), args, fparams)


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
    var_decls = []
    for (x, y) in parsed_sexp[1]:
        name = parse_smtlib2_symbol(x)
        defining_term = parse_smtlib2_term(y, sort_ctx, fun_scope)
        const_sort = defining_term.get_sort()
        const_sig = (lambda const_sort_: FunctionSignature(lambda z: const_sort_ if len(z) == 0 else None,
                                                           0, True))(const_sort)
        const_decl = FunctionDeclaration(name, const_sig)
        fun_scope_extension.add_declaration(const_decl)
        let_defs.append((name, defining_term))
        var_decls.append(const_decl)

    enclosed_term = parse_smtlib2_term(parsed_sexp[2], sort_ctx, fun_scope_extension)
    result = ast.LetTermASTNode(let_defs, enclosed_term)
    for decl in var_decls:
        decl.set_declaring_ast_node(result)

    return result


def parse_smtlib2_underscore_bv_literal_term(parsed_sexp, sort_ctx: sorts.SortContext) -> ast.LiteralASTNode:
    """
    Parses an SMTLib2-formatted term matching "(_ bvX y)".

    :param parsed_sexp: The term's s-expression.
    :param sort_ctx: The current sort context.
    :return: A LiteralASTNode representing parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed term.
    """

    if len(parsed_sexp) != 3 or parsed_sexp[0] != "_" or parsed_sexp[1][0:2] != "bv" or not parsed_sexp[2].isnumeric():
        raise ValueError("Malformed literal term " + str(parsed_sexp))

    literal_str = parsed_sexp[1][2:]
    if not literal_str.isnumeric():
        raise ValueError("Malformed literal term " + str(parsed_sexp) + ": bad literal value")

    return ast.LiteralASTNode(int(literal_str), sort_ctx.get_bv_sort(int(parsed_sexp[2])))


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
    if parsed_sexp[0] == "_":
        return parse_smtlib2_underscore_bv_literal_term(parsed_sexp, sort_ctx)
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
    signature = FunctionSignature(__signature_fn, len(domain_sorts), True)

    decl_ast_node = ast.DeclareFunCommandASTNode(fun_name, domain_sorts, range_sort)
    return decl_ast_node, FunctionDeclaration(fun_name, signature, decl_ast_node)


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
    signature = FunctionSignature(__signature_fn, 0, True)

    decl_ast_node = ast.DeclareFunCommandASTNode(fun_name, [], range_sort)
    return decl_ast_node, FunctionDeclaration(fun_name, signature, decl_ast_node)


def parse_cmd_define_fun(parsed_sexp, sort_ctx: sorts.SortContext, scope: SyntacticFunctionScope):
    """
    Parses an SMTLib2-formatted define-fun command.

    :param parsed_sexp: The command's s-expression.
    :param sort_ctx: The current sort context.
    :param scope: The current function scope.
    :return: A tuple x,y with x being a DefineFunCommandASTNode representing parsed_sexp and y being the declared
             function's signature.
    :raises ValueError if parsed_sexp is a malformed command.
    """
    if len(parsed_sexp) != 5 or type(parsed_sexp[1]) != str or type(parsed_sexp[2]) != list:
        raise ValueError("Invalid define-fun command")
    fun_name, parameters_sexp, range_sort_sexp, defining_term_sexp = parsed_sexp[1:]

    function_scope = SyntacticFunctionScope(scope)
    domain_sorts = []
    formal_parameters = []
    for x in parameters_sexp:
        if type(x) != list or len(x) != 2:
            raise ValueError("Invalid define-fun command: malformed parameters")
        parameter_sym_str, parameter_ty_sexp = x
        parameter_sym = parse_smtlib2_symbol(parameter_sym_str)
        parameter_sort = parse_smtlib2_sort(parameter_ty_sexp, sort_ctx)
        parameter_sig = (lambda s: FunctionSignature(lambda t: s if len(t) == 0 else None, 0, True))(parameter_sort)
        function_scope.add_declaration(FunctionDeclaration(parameter_sym, parameter_sig))
        domain_sorts.append(parameter_sort)
        formal_parameters.append((parameter_sym, parameter_sort))

    range_sort = parse_smtlib2_sort(range_sort_sexp, sort_ctx=sort_ctx)
    defining_term = parse_smtlib2_term(defining_term_sexp, sort_ctx, function_scope)

    if range_sort is not defining_term.get_sort():
        raise ValueError("Invalid define-fun command: defining term sort does not match function range sort")

    def __signature_fn(concrete_dom_sigs):
        if list(concrete_dom_sigs) == domain_sorts:
            return range_sort
        return None

    defn_ast_node = ast.DefineFunCommandASTNode(fun_name, formal_parameters, range_sort, defining_term)
    signature = FunctionSignature(__signature_fn, len(domain_sorts), True)

    return defn_ast_node, FunctionDeclaration(fun_name, signature, defn_ast_node)


def parse_cmd_define_const(parsed_sexp, sort_ctx: sorts.SortContext, scope: SyntacticFunctionScope):
    """
    Parses an SMTLib2-formatted define-const command.

    :param parsed_sexp: The command's s-expression.
    :param sort_ctx: The current sort context.
    :param scope: The current function scope.
    :return: A tuple x,y with x being a DefineFunCommandASTNode representing parsed_sexp and y being the declared
             function's signature.
    :raises ValueError if parsed_sexp is a malformed command.
    """
    if len(parsed_sexp) != 4 or type(parsed_sexp[1]) != str:
        raise ValueError("Invalid declare-const command")
    define_fun_sexp = parsed_sexp[:2] + [[]] + parsed_sexp[2:]
    return parse_cmd_define_fun(define_fun_sexp, sort_ctx, scope)


def add_logic_as_parent(scope: SyntacticFunctionScope, sort_ctx: sorts.SortContext, logic: str):
    """
    Extends a given scope with the symbols of the given logic.

    The logic's symbols are defined in separate scopes, which are then added as a parent scope
    of `scope`. The original parent scope of `scope` is added as a parent scope of the scopes introduced
    by this function.

    :param scope: The scope to be extended.
    :param sort_ctx: The sort context.
    :param logic: The logic whose declarations shall to be added to the scope. Currently, only the QF_BV logic is
                  supported.
    :return: None
    :raises ValueError if the specified logic is unsupported.
    """
    if logic == "QF_BV":
        bv_scope = theories.FixedSizeBVSyntacticFunctionScopeFactory().create_syntactic_scope(sort_ctx)
        bvext_scope = theories.QFBVExtSyntacticFunctionScopeFactory().create_syntactic_scope(sort_ctx)
        bvext_scope.set_parent(bv_scope)
        bv_scope.set_parent(scope.get_parent())
        scope.set_parent(bvext_scope)
    else:
        raise ValueError("Unsupported logic " + logic)


def parse_smtlib2_problem(parsed_sexp):
    """
    Parses an SMTLib2-formatted SMT problem.

    This parser currently only supports a subset of SMTLib2. TODO: document the supported SMTLib2 subset.

    :param parsed_sexp: The command's s-expression.
    :return: A list of ASTNodes, representing parsed_sexp.
    :raises ValueError if parsed_sexp is a malformed problem.
    """

    sort_context = sorts.SortContext()
    core_theory = theories.CoreSyntacticFunctionScopeFactory().create_syntactic_scope(sort_context)
    problem_toplevel_function_scope = SyntacticFunctionScope(core_theory)
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
            ast_node, fun_decl = parse_cmd_declare_fun(sexp, sort_context)
            problem_toplevel_function_scope.add_declaration(fun_decl)
            return ast_node

        elif command == "declare-const":
            ast_node, fun_decl = parse_cmd_declare_const(sexp, sort_context)
            problem_toplevel_function_scope.add_declaration(fun_decl)
            return ast_node

        elif command == "define-fun":
            ast_node, fun_decl = parse_cmd_define_fun(sexp, sort_context, problem_toplevel_function_scope)
            problem_toplevel_function_scope.add_declaration(fun_decl)
            return ast_node

        elif command == "define-const":
            ast_node, fun_decl = parse_cmd_define_const(sexp, sort_context, problem_toplevel_function_scope)
            problem_toplevel_function_scope.add_declaration(fun_decl)
            return ast_node

        elif command == "set-logic":
            if len(sexp) != 2 or not type(sexp[1]) == str:
                raise ValueError("Invalid set-logic command")
            logic = sexp[1]
            add_logic_as_parent(problem_toplevel_function_scope, sort_context, logic)
            return ast.SetLogicCommandASTNode(logic)

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
            return ast.PushPopCommandASTNode(True, amnt)

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
            return ast.PushPopCommandASTNode(False, amnt)

        elif command == "set-info":
            pass  # Ignore set-info commands

        else:
            raise ValueError("Unsupported command " + command)

    return [x for x in (parse_command(x) for x in parsed_sexp) if x is not None]
