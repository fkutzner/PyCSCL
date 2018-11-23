from unittest import TestCase

from cscl.basic_gate_encoders import encode_or_gate

from tests.testutils.trivial_sat_solver import TrivialSATSolver


class TestEncodeOrGate(TestCase):
    def test_encode_or_gate_returns_output_literal(self):
        checker = TrivialSATSolver()
        vars = []
        for i in range(0, 10):
            vars.append(checker.create_variable())

        result = encode_or_gate(checker, [vars[0]], vars[1])
        assert(result == vars[1])

    def test_encode_or_gate_returns_new_output_literal_by_default(self):
        checker = TrivialSATSolver()
        vars = []
        for i in range(0, 10):
            vars.append(checker.create_variable())

        result = encode_or_gate(checker, [vars[0]])
        assert (not result in vars and not -result in vars)

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

        for i in range(0, 2**n - 2):
            assumptions = inputs[:]
            for j in range(0, n):
                if (i & (1 << j)) != 0:
                    assumptions[j] = -assumptions[j]
            assumptions.append(-output)
            assert (checker.solve(assumptions) is False)
            assumptions[n] = -assumptions[n]
            assert (checker.solve(assumptions) is True)

        if n > 0:
            assumptions = inputs[:]
            assumptions.append(output)
            assert (checker.solve(assumptions) is True)
            assumptions[n] = -assumptions[n]
            assert (checker.solve(assumptions) is False)
        else:
            assert (checker.solve([output]) is False)
            assert (checker.solve([-output]) is True)

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
