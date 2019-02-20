def lex_sexp(sexp_string: str):
    """
    Tokenizes an s-expression string not containing comments.

    Example: lex_sexp transforms the string " \n \t  (a ( bc d) 1)" into the sequence
    ("(", "a", "(", "bc", "d", ")", "1", ")").

    :param sexp_string: An s-expression string that does not contain comments.
    :return: An iterator iterating over the tokens contained in sexp_string.
    """
    cursor = 0
    while cursor != len(sexp_string):
        if sexp_string[cursor].isspace():
            cursor += 1
            continue

        if sexp_string[cursor] == '(':
            yield "("
            cursor += 1
        elif sexp_string[cursor] == ')':
            yield ")"
            cursor += 1
        else:
            cursor_ahead = cursor+1
            while cursor_ahead != len(sexp_string) \
                    and (not sexp_string[cursor_ahead].isspace()) \
                    and sexp_string[cursor_ahead] != '(' \
                    and sexp_string[cursor_ahead] != ')':
                cursor_ahead += 1
            yield sexp_string[cursor:cursor_ahead]
            cursor = cursor_ahead


def parse_sexp(sexp_iter):
    """
    Transforms a sequence of s-expression tokens (given in string form) into a corresponding tree of strings.

    The given sequence is interpreted as the elements of an enclosing list expression, i.e.
    with a prepended "(" token and an appended ")" token.

    Example: parse_sexp transforms the sequence ("(", "a", "(", "bc", "d", ")", "1", ")", "5")
    into the structure [["a" ["bc" "d"] "1"], "5"].

    :param sexp_iter: An iterator iterating over the tokens contained in in a s-expression.
    :return: The tree-structure representation of sexp_iter, with s-expression lists being represented
             using Python lists.
    :raises ValueError when sexp_string is malformed.
    """

    results = []

    def __recursively_parse_sexp():
        result = []
        found_expression_end = False
        for token_ in sexp_iter:
            if token_ == ")":
                found_expression_end = True
                break
            elif token_ == "(":
                result.append(__recursively_parse_sexp())
            else:
                result.append(token_)

        if not found_expression_end:
            raise ValueError("Unterminated symbolic expression")
        return result

    for token in sexp_iter:
        if token == "(":
            results.append(__recursively_parse_sexp())
        else:
            results.append(token)

    return results
