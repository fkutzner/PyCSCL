from unittest import TestCase
from cscl.dimacs_printer import DIMACSPrinter


def dimacs_printer_conversion_test(printer_under_test, clauses, expected_output):
    for clause in clauses:
        printer_under_test.consume_clause(clause)

    actual_output = []
    printer_under_test.print(lambda x: actual_output.append(x))
    assert (actual_output == expected_output), "Expected output: "\
                                               + str(expected_output) + " vs. actual output: " + str(actual_output)


class TestDIMACSPrinter(TestCase):
    def test_prints_empty(self):
        under_test = DIMACSPrinter()
        dimacs_printer_conversion_test(under_test, [], ["p cnf 0 0"])

    def test_prints_empty_clause(self):
        under_test = DIMACSPrinter()
        dimacs_printer_conversion_test(under_test, [[]], ["p cnf 0 1", " 0"])

    def test_prints_one_nonempty_clause(self):
        under_test = DIMACSPrinter()
        var1 = under_test.create_literal()
        var2 = under_test.create_literal()
        dimacs_printer_conversion_test(under_test, [[var1, -var2]], ["p cnf 2 1", "1 -2 0"])

    def test_prints_multiple_clauses(self):
        under_test = DIMACSPrinter()
        var1 = under_test.create_literal()
        var2 = under_test.create_literal()
        var3 = under_test.create_literal()

        clauses = [[var1, var2, -var3], [-var2], [var1, var3]]
        expected_output = ["p cnf 3 3", "1 2 -3 0", "-2 0", "1 3 0"]
        dimacs_printer_conversion_test(under_test, clauses, expected_output)
