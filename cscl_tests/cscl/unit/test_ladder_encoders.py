import unittest
import cscl.ladder_encoders as ladder_encoders
import cscl_tests.testutils.trivial_sat_solver as sat_solver
from cscl.interfaces import SatSolver


class LadderEncoderUnitTests(unittest.TestCase):
    def check_ladder_encoding_positive(self, ladder_literals, sat_solver_with_encoding: SatSolver):
        """Checks that assignments satisfying the ladder constraints are admissible"""
        ladder_len = len(ladder_literals)
        for i in range(0, ladder_len + 1):
            assumptions = list(ladder_literals[:i]) + list(-ladder_literals[j] for j in range(i, ladder_len))
            self.assertTrue(sat_solver_with_encoding.solve(assumptions), 'Failed at literal index ' + str(i))

    def check_ladder_encoding_negative(self, ladder_literals, sat_solver_with_encoding: SatSolver):
        """Checks that if the i'th literal is False, then all literals with index greater than i must be false, too"""
        ladder_len = len(ladder_literals)
        for i in range(0, ladder_len-1):
            clause_activator_lit = sat_solver_with_encoding.create_literal()
            sat_solver_with_encoding.consume_clause(list(ladder_literals[i+1:]) + [clause_activator_lit])
            assumptions = [-ladder_literals[i], -clause_activator_lit]
            self.assertFalse(sat_solver_with_encoding.solve(assumptions), 'Failed at literal index ' + str(i))

    def parameterized_test_encode_ladder_constraint(self, num_lits):
        solver = sat_solver.TrivialSATSolver()
        ladder_literals = list(ladder_encoders.encode_ladder_constraint(solver, solver, num_lits))
        self.assertEqual(len(ladder_literals), num_lits)
        self.check_ladder_encoding_positive(ladder_literals, solver)
        self.check_ladder_encoding_negative(ladder_literals, solver)

    def test_encode_ladder_constraint(self):
        for n in (0, 1, 2, 16):
            with self.subTest(msg=str(n) + ' literals'):
                self.parameterized_test_encode_ladder_constraint(n)

    def parameterized_test_encode_ladder_constraint_on_literals(self, num_lits):
        solver = sat_solver.TrivialSATSolver()
        ladder_literals = [solver.create_literal() for _ in range(0, num_lits)]
        ladder_encoders.encode_ladder_constraint_on_literals(solver, ladder_literals)
        self.assertEqual(len(ladder_literals), num_lits)
        self.check_ladder_encoding_positive(ladder_literals, solver)
        self.check_ladder_encoding_negative(ladder_literals, solver)

    def test_encode_ladder_constraint_on_literals(self):
        for n in (0, 1, 2, 16):
            with self.subTest(msg=str(n) + ' literals'):
                self.parameterized_test_encode_ladder_constraint_on_literals(n)
