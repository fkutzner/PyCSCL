import unittest
import cscl_examples.factorization as fact
from cscl_tests.testutils.trivial_sat_solver import TrivialSATSolver


class TestFactorization(unittest.TestCase):
    @staticmethod
    def __check_result(factors, expected_factors):
        assert factors is not None, "Unexpectedly found no factors"

        lfactors = list(factors)
        lexpected = list(expected_factors)
        assert lfactors == lexpected or lfactors == [lexpected[1], lexpected[0]],\
            "Unexpected factors: " + str(factors)

    def test_refuses_to_factorize_negatives(self):
        solver = TrivialSATSolver()
        with self.assertRaises(ValueError):
            fact.factorize(-1, solver)

    def test_refuses_to_factorize_0(self):
        solver = TrivialSATSolver()
        with self.assertRaises(ValueError):
            fact.factorize(0, solver)

    def test_refuses_to_factorize_1(self):
        solver = TrivialSATSolver()
        with self.assertRaises(ValueError):
            fact.factorize(1, solver)

    def test_factorizes_21(self):
        # 21 = 7*3 (primes)
        solver = TrivialSATSolver()
        result = fact.factorize(21, solver)
        self.__check_result(result, (7, 3))

    def test_factorizes_77(self):
        # 77 = 11*7 (primes)
        solver = TrivialSATSolver()
        result = fact.factorize(77, solver)
        self.__check_result(result, (11, 7))

    def test_factorizes_2101(self):
        # 2101 = 191*11 (primes)
        solver = TrivialSATSolver()
        result = fact.factorize(2101, solver)
        self.__check_result(result, (191, 11))
