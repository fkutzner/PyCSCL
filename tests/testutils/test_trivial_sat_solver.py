from unittest import TestCase
from tests.testutils.trivial_sat_solver import TrivialSATSolver


class TestTrivialSATSolver(TestCase):
    def test_create_variable_is_int(self):
        under_test = TrivialSATSolver()
        assert(isinstance(under_test.create_variable(), int))

    def test_create_variable_results_are_distinct(self):
        under_test = TrivialSATSolver()
        variables = []
        for i in range(1, 1000):
            variables.append(under_test.create_variable())
        assert(len(variables) == len(set(variables)))

    def test_solve_empty_problem(self):
        under_test = TrivialSATSolver()
        assert(under_test.solve() is True)

    def test_solve_problem_with_empty_clause(self):
        under_test = TrivialSATSolver()
        under_test.consume_clause([])
        assert(under_test.solve() is False)

    def test_solve_problem_with_single_unit_clause(self):
        under_test = TrivialSATSolver()
        under_test.consume_clause([under_test.create_variable()])
        assert (under_test.solve() is True)

    def test_solve_problem_with_noncontradictory_unit_clauses(self):
        under_test = TrivialSATSolver()
        variables = []
        for i in range(1, 10):
            variables.append(under_test.create_variable())

        under_test.consume_clause([variables[2]])
        under_test.consume_clause([variables[4]])
        under_test.consume_clause([-variables[5]])
        assert (under_test.solve() is True)

    def test_solve_problem_with_contradictory_unit_clauses(self):
        under_test = TrivialSATSolver()
        variables = []
        for i in range(1, 10):
            variables.append(under_test.create_variable())

        under_test.consume_clause([variables[2]])
        under_test.consume_clause([variables[4]])
        under_test.consume_clause([-variables[4]])
        assert (under_test.solve() is False)

    def test_solve_satisfiable_3sat_problem(self):
        under_test = TrivialSATSolver()
        var = []
        for i in range(0, 10):
            var.append(under_test.create_variable())

        under_test.consume_clause([var[1], var[3], var[5]])
        under_test.consume_clause([-var[1], -var[7], var[5]])
        under_test.consume_clause([-var[3], -var[7], -var[0]])
        under_test.consume_clause([-var[9], -var[6], -var[1]])
        assert (under_test.solve() is True)

    def test_solve_unsatisfiable_2sat_problem(self):
        under_test = TrivialSATSolver()
        var = []
        for i in range(1, 10):
            var.append(under_test.create_variable())

        under_test.consume_clause([var[1], var[3]])
        under_test.consume_clause([-var[1], -var[7]])
        under_test.consume_clause([-var[3], -var[8]])
        under_test.consume_clause([var[7], var[8]])
        assert (under_test.solve() is False)

    def test_solve_3sat_problem_with_assumptions_sat(self):
        under_test = TrivialSATSolver()
        var = []
        for i in range(0, 10):
            var.append(under_test.create_variable())

        under_test.consume_clause([var[1], var[3], var[5]])
        under_test.consume_clause([-var[1], -var[7], var[5]])
        under_test.consume_clause([-var[3], -var[7], -var[0]])
        under_test.consume_clause([-var[9], -var[6], var[1]])
        assert (under_test.solve([var[1], var[7], var[6]]) is True)

    def test_solve_3sat_problem_with_assumptions_unsat(self):
        under_test = TrivialSATSolver()
        var = []
        for i in range(0, 10):
            var.append(under_test.create_variable())

        under_test.consume_clause([var[1], var[3], var[5]])
        under_test.consume_clause([var[1], -var[7], -var[5]])
        under_test.consume_clause([-var[3], -var[7], -var[0]])
        under_test.consume_clause([-var[9], -var[6], var[1]])
        assert (under_test.solve([-var[1], -var[3], var[7]]) is False)
