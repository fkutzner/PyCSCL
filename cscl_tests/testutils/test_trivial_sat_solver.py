from unittest import TestCase
from cscl_tests.testutils.trivial_sat_solver import TrivialSATSolver


class TestTrivialSATSolver(TestCase):
    def test_create_literal_is_int(self):
        under_test = TrivialSATSolver()
        self.assertTrue(isinstance(under_test.create_literal(), int))

    def test_create_literal_results_are_distinct(self):
        under_test = TrivialSATSolver()
        variables = [under_test.create_literal() for _ in range(0, 1000)]
        self.assertTrue(len(variables) == len(set(variables)))

    def test_solve_empty_problem(self):
        under_test = TrivialSATSolver()
        self.assertTrue(under_test.solve() is True)

    def test_solve_problem_with_empty_clause(self):
        under_test = TrivialSATSolver()
        under_test.consume_clause([])
        self.assertTrue(under_test.solve() is False)

    def test_solve_problem_with_single_unit_clause(self):
        under_test = TrivialSATSolver()
        under_test.consume_clause([under_test.create_literal()])
        self.assertTrue(under_test.solve())

    def test_solve_problem_with_noncontradictory_unit_clauses(self):
        under_test = TrivialSATSolver()
        variables = [under_test.create_literal() for _ in range(0, 10)]

        under_test.consume_clause([variables[2]])
        under_test.consume_clause([variables[4]])
        under_test.consume_clause([-variables[5]])
        self.assertTrue(under_test.solve())

    def test_solve_problem_with_contradictory_unit_clauses(self):
        under_test = TrivialSATSolver()
        variables = [under_test.create_literal() for _ in range(0, 10)]

        under_test.consume_clause([variables[2]])
        under_test.consume_clause([variables[4]])
        under_test.consume_clause([-variables[4]])
        self.assertFalse(under_test.solve())

    def test_solve_satisfiable_3sat_problem(self):
        under_test = TrivialSATSolver()
        var = [under_test.create_literal() for _ in range(0, 10)]

        under_test.consume_clause([var[1], var[3], var[5]])
        under_test.consume_clause([-var[1], -var[7], var[5]])
        under_test.consume_clause([-var[3], -var[7], -var[0]])
        under_test.consume_clause([-var[9], -var[6], -var[1]])
        self.assertTrue(under_test.solve())

    def test_solve_unsatisfiable_2sat_problem(self):
        under_test = TrivialSATSolver()
        var = [under_test.create_literal() for _ in range(0, 10)]

        under_test.consume_clause([-var[1], var[3]])
        under_test.consume_clause([-var[3], var[8]])
        under_test.consume_clause([-var[8], -var[1]])
        under_test.consume_clause([var[4], var[1]])
        under_test.consume_clause([-var[4], var[7]])
        under_test.consume_clause([-var[7], -var[4]])
        self.assertFalse(under_test.solve())

    def test_solve_3sat_problem_with_assumptions_sat(self):
        under_test = TrivialSATSolver()
        var = [under_test.create_literal() for _ in range(0, 10)]

        under_test.consume_clause([var[1], var[3], var[5]])
        under_test.consume_clause([-var[1], -var[7], var[5]])
        under_test.consume_clause([-var[3], -var[7], -var[0]])
        under_test.consume_clause([-var[9], -var[6], var[1]])
        self.assertTrue(under_test.solve([var[1], var[7], var[6]]))

    def test_solve_3sat_problem_with_assumptions_unsat(self):
        under_test = TrivialSATSolver()
        var = [under_test.create_literal() for _ in range(0, 10)]

        under_test.consume_clause([var[1], var[3], var[5]])
        under_test.consume_clause([var[1], -var[7], -var[5]])
        under_test.consume_clause([-var[3], -var[7], -var[0]])
        under_test.consume_clause([-var[9], -var[6], var[1]])
        self.assertFalse(under_test.solve([-var[1], -var[3], var[7]]))

    def test_get_forced_assignment(self):
        under_test = TrivialSATSolver()
        var = [under_test.create_literal() for _ in range(0, 10)]

        under_test.consume_clause([var[1], var[3], var[5]])
        under_test.consume_clause([-var[1], -var[7], var[5]])
        under_test.consume_clause([-var[3], -var[7], -var[0]])
        under_test.consume_clause([-var[9], -var[6], -var[1]])
        self.assertTrue(under_test.solve([var[1], var[7], var[6]]))

        self.assertTrue(under_test.get_assignment(var[1]))
        self.assertFalse(under_test.get_assignment(-var[1]))
        self.assertTrue(under_test.get_assignment(var[7]))
        self.assertFalse(under_test.get_assignment(-var[7]))
        self.assertTrue(under_test.get_assignment(var[6]))
        self.assertFalse(under_test.get_assignment(-var[6]))
        self.assertTrue(under_test.get_assignment(var[5]))
        self.assertFalse(under_test.get_assignment(-var[5]))
        self.assertFalse(under_test.get_assignment(var[9]))
        self.assertTrue(under_test.get_assignment(-var[9]))
