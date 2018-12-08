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
