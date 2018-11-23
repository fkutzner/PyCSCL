from unittest import TestCase
from cscl.basic_gate_encoders import *
from tests.testutils.trivial_sat_solver import TrivialSATSolver


def encoder_returns_output_literal(encoder_fn):
    checker = TrivialSATSolver()
    variables = []
    for i in range(0, 10):
        variables.append(checker.create_variable())

    result = encoder_fn(checker, [variables[0]], variables[1])
    return result == variables[1]


def encoder_returns_new_output_literal_by_default(encoder_fn):
    checker = TrivialSATSolver()
    variables = []
    for i in range(0, 10):
        variables.append(checker.create_variable())

    result = encode_or_gate(checker, [variables[0]])
    return not result in variables and not -result in variables


class TestEncodeOrGate(TestCase):
    def test_encode_or_gate_returns_output_literal(self):
        assert(encoder_returns_output_literal(encode_or_gate))

    def test_encode_or_gate_returns_new_output_literal_by_default(self):
        assert(encoder_returns_new_output_literal_by_default(encode_or_gate))

    def encode_or_gate_n_ary_test_full(self, n):
        """
        Tests (via assert()) encode_or_gate for all combinations of outputs and n inputs.

        :param n: The non-negative number of inputs
        :return: None
        """
        checker = TrivialSATSolver()
        inputs = []
        for i in range(0, n):
            inputs.append(checker.create_variable())

        output = encode_or_gate(checker, inputs)

        for i in range(0, 2**n - 1):
            assumptions = inputs[:]
            for j in range(0, n):
                if (i & (1 << j)) != 0:
                    assumptions[j] = -assumptions[j]
            assumptions.append(-output)
            assert (checker.solve(assumptions) is False)
            assumptions[n] = -assumptions[n]
            assert (checker.solve(assumptions) is True)

        assumptions = list(map(lambda x: -x, inputs))
        assumptions.append(output)
        assert (checker.solve(assumptions) is False)
        assumptions[n] = -assumptions[n]
        assert (checker.solve(assumptions) is True)

    def test_encode_or_gate_create_nullary_or_gate(self):
        self.encode_or_gate_n_ary_test_full(0)

    def test_encode_or_gate_create_unary_or_gate(self):
        self.encode_or_gate_n_ary_test_full(1)

    def test_encode_or_gate_create_binary_or_gate(self):
        self.encode_or_gate_n_ary_test_full(2)

    def test_encode_or_gate_create_ternary_or_gate(self):
        self.encode_or_gate_n_ary_test_full(3)

    def test_encode_or_gate_create_quaternary_or_gate(self):
        self.encode_or_gate_n_ary_test_full(4)


class TestEncodeAndGate(TestCase):
    def test_encode_and_gate_returns_output_literal(self):
        assert(encoder_returns_output_literal(encode_and_gate))

    def test_encode_and_gate_returns_new_output_literal_by_default(self):
        assert(encoder_returns_new_output_literal_by_default(encode_and_gate))

    def encode_and_gate_n_ary_test_full(self, n):
        """
        Tests (via assert()) encode_and_gate for all combinations of outputs and n inputs.

        :param n: The non-negative number of inputs
        :return: None
        """

        checker = TrivialSATSolver()
        inputs = []
        for i in range(0, n):
            inputs.append(checker.create_variable())

        output = encode_and_gate(checker, inputs)

        for i in range(1, 2**n):
            assumptions = inputs[:]
            for j in range(0, n):
                if (i & (1 << j)) != 0:
                    assumptions[j] = -assumptions[j]
            assumptions.append(-output)
            assert (checker.solve(assumptions) is True)
            assumptions[n] = -assumptions[n]
            assert (checker.solve(assumptions) is False)

        assumptions = inputs[:]
        assumptions.append(output)
        assert (checker.solve(assumptions) is True)
        assumptions[n] = -assumptions[n]
        assert (checker.solve(assumptions) is False)

    def test_encode_and_gate_create_nullary_and_gate(self):
        self.encode_and_gate_n_ary_test_full(0)

    def test_encode_and_gate_create_unary_and_gate(self):
        self.encode_and_gate_n_ary_test_full(1)

    def test_encode_and_gate_create_binary_and_gate(self):
        self.encode_and_gate_n_ary_test_full(2)

    def test_encode_and_gate_create_ternary_and_gate(self):
        self.encode_and_gate_n_ary_test_full(3)

    def test_encode_and_gate_create_quaternary_and_gate(self):
        self.encode_and_gate_n_ary_test_full(4)
