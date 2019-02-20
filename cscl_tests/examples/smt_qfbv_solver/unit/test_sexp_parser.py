import unittest
import cscl_examples.smt_qfbv_solver.sexp_parser as sep


class TestLexSExp(unittest.TestCase):
    def test_returns_empty_seq_for_empty_string(self):
        result = list(x for x in sep.lex_sexp(""))
        assert result == [], "Unexpected result " + str(result)

    def test_returns_empty_seq_for_whitespace_string(self):
        result = list(x for x in sep.lex_sexp("  \t\n \r"))
        assert result == [], "Unexpected result " + str(result)

    def test_lex_single_open_paren(self):
        result = list(x for x in sep.lex_sexp("("))
        assert result == ["("], "Unexpected result " + str(result)

    def test_lex_single_close_paren(self):
        result = list(x for x in sep.lex_sexp(")"))
        assert result == [")"], "Unexpected result " + str(result)

    def test_lex_word(self):
        result = list(x for x in sep.lex_sexp("foo"))
        assert result == ["foo"], "Unexpected result " + str(result)

    def test_lex_word_with_parens(self):
        result = list(x for x in sep.lex_sexp("(foo)"))
        assert result == ["(", "foo", ")"], "Unexpected result " + str(result)

    def test_lex_word_with_nested_parens(self):
        result = list(x for x in sep.lex_sexp("(foo ( bar))"))
        assert result == ["(", "foo", "(", "bar", ")", ")"], "Unexpected result " + str(result)


class TestParseSExp(unittest.TestCase):
    def test_returns_empty_list_for_empty_string(self):
        result = sep.parse_sexp(iter([]))
        assert result == [], "Unexpected result " + str(result)

    def test_parse_word(self):
        result = sep.parse_sexp(iter(["foo"]))
        assert result == ["foo"], "Unexpected result " + str(result)

    def test_parse_two_words(self):
        result = sep.parse_sexp(iter(["foo", "bar"]))
        assert result == ["foo", "bar"], "Unexpected result " + str(result)

    def test_parse_list_expr(self):
        result = sep.parse_sexp(iter(["(", "foo", ")"]))
        assert result == [["foo"]], "Unexpected result " + str(result)

    def test_parse_two_list_exprs(self):
        result = sep.parse_sexp(iter(["(", "foo", ")", "(", "bar", ")"]))
        assert result == [["foo"], ["bar"]], "Unexpected result " + str(result)

    def test_parse_nested_list_exprs(self):
        result = sep.parse_sexp(iter(["(", "foo", "1", "2", "(", "bar", "(", "baz", "0", ")", "bam",
                                     ")", ")", "(", "bar", ")"]))
        assert result == [["foo", "1", "2", ["bar", ["baz", "0"], "bam"]], ["bar"]],\
            "Unexpected result " + str(result)

    def test_refuses_malformed_sexp(self):
        with self.assertRaises(ValueError):
            sep.parse_sexp(iter(["(", "foo", "(", "bar", ")"]))
