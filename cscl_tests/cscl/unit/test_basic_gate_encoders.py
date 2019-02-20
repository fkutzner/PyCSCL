import abc
from unittest import TestCase
from cscl.basic_gate_encoders import *
from cscl_tests.testutils.trivial_sat_solver import TrivialSATSolver
from cscl_tests.testutils.logging_clause_consumer_decorator import LoggingClauseConsumerDecorator


def encoder_returns_output_literal(encoder_fn):
    checker = TrivialSATSolver()
    variables = []
    for i in range(0, 10):
        variables.append(checker.create_literal())

    result = encoder_fn(checker, checker, [variables[0], variables[1]], variables[2])
    return result == variables[2]


def encoder_returns_new_output_literal_by_default(encoder_fn):
    checker = TrivialSATSolver()
    variables = []
    for i in range(0, 10):
        variables.append(checker.create_literal())

    result = encoder_fn(checker, checker, [variables[0], variables[1]])
    return result not in variables and -result not in variables


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
            inputs.append(checker.create_literal())

        output = encode_or_gate(checker, checker, inputs)

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
            inputs.append(checker.create_literal())

        output = encode_and_gate(checker, checker, inputs)

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


def create_trivial_sat_solver_with_n_vars(n):
    """
    Creates a TrivialSATSolver instance x with n variables for x.

    :param n: The amount of variables to create
    :return: (solver, variables). solver is the created solver, variables the list of
             created variables.
    """
    solver = TrivialSATSolver()
    variables = []
    for i in range(0, n):
        variables.append(solver.create_literal())
    return solver, variables


class AbstractTruthTableBasedGateTest(abc.ABC):
    """Abstract test case for testing gate encoders by checking their encoding via variable assignments"""

    @abc.abstractmethod
    def get_gate_encoder_under_test(self):
        """
        Gets the gate encoder function under test.

        :return: the gate encoder function under test.
        """
        pass

    @abc.abstractmethod
    def get_gate_arity(self):
        """
        Gets the tested gate encoders's gate's arity.

        :return: the tested gate encoders's gate's arity.
        """
        pass

    @abc.abstractmethod
    def get_spec_truth_table(self):
        """
        Gets the truth table for the tested gate encoders's gate.

        :return: A sequence (t1, ..., tN) with tX = ((iX_1, ..., iX_M), oX) for X in 1...N, where M is the gate's arity;
                 N = 2^M; iX_1, ..., iX_M in {0, 1} (X in 1...N) being the input setting of row X, and oX (X in 1...N)
                 being the output setting of row X. Example: ( ((0, 0, 1), 0), ((1, 0, 1), 1) , ... )
        """
        pass

    def test_gate_returns_output_literal(self):
        arity = self.get_gate_arity()
        encoder_under_test = self.get_gate_encoder_under_test()
        checker, variables = create_trivial_sat_solver_with_n_vars(arity+1)
        result = encoder_under_test(checker, checker, variables[1:], variables[0])
        assert result == variables[0]

    def test_gate_returns_new_output_literal_by_default(self):
        arity = self.get_gate_arity()
        encoder_under_test = self.get_gate_encoder_under_test()
        checker, variables = create_trivial_sat_solver_with_n_vars(arity)
        result = encoder_under_test(checker, checker, variables)
        assert checker.has_variable_of_lit(result)
        assert result not in variables and -result not in variables

    def test_gate_fulfills_truth_table_spec(self):
        arity = self.get_gate_arity()
        encoder_under_test = self.get_gate_encoder_under_test()
        checker, variables = create_trivial_sat_solver_with_n_vars(arity+1)
        output_lit = variables[arity]
        input_lits = variables[0:arity]
        encoder_under_test(checker, checker, input_lits, output_lit)

        for input_bits, output_bit in self.get_spec_truth_table():
            input_signs = (-1 if x <= 0 else 1 for x in input_bits)
            input_lit_settings = tuple(x * y for x, y in zip(input_signs, input_lits))

            expected_sat_setting = list(input_lit_settings)
            expected_sat_setting.append(-output_lit if output_bit <= 0 else output_lit)
            expected_unsat_setting = list(input_lit_settings)
            expected_unsat_setting.append(output_lit if output_bit <= 0 else -output_lit)

            assert checker.solve(expected_sat_setting) is True,\
                "Gate failure for input setting " + str(input_bits) + ", output setting " + str(output_bit)\
                + "\n(should be satisfiable, but is not)"
            assert checker.solve(expected_unsat_setting) is False, \
                "Gate failure for input setting " + str(input_bits) + ", output setting " + str(1-output_bit)\
                + "\n(should not be satisfiable, but is)"


class TestEncodeBinaryXorGate(AbstractTruthTableBasedGateTest, TestCase):

    def get_gate_encoder_under_test(self):
        return encode_binary_xor_gate

    def get_gate_arity(self):
        return 3

    def get_spec_truth_table(self):
        return (((0, 0), 0),
                ((0, 1), 1),
                ((1, 0), 1),
                ((1, 1), 0))


class TestEncodeBinaryMuxGate(AbstractTruthTableBasedGateTest, TestCase):

    def get_gate_encoder_under_test(self):
        return encode_binary_mux_gate

    def get_gate_arity(self):
        return 3

    def get_spec_truth_table(self):
        return (((0, 0, 0), 0),
                ((0, 0, 1), 0),
                ((0, 1, 0), 1),
                ((0, 1, 1), 1),
                ((1, 0, 0), 0),
                ((1, 0, 1), 1),
                ((1, 1, 0), 0),
                ((1, 1, 1), 1))


class TestEncodeFullAdderSumGate(AbstractTruthTableBasedGateTest, TestCase):

    def get_gate_encoder_under_test(self):
        return encode_full_adder_sum_gate

    def get_gate_arity(self):
        return 3

    def get_spec_truth_table(self):
        return (((0, 0, 0), 0),
                ((0, 0, 1), 1),
                ((0, 1, 0), 1),
                ((0, 1, 1), 0),
                ((1, 0, 0), 1),
                ((1, 0, 1), 0),
                ((1, 1, 0), 0),
                ((1, 1, 1), 1))


class TestEncodeFullAdderCarryGate(AbstractTruthTableBasedGateTest, TestCase):

    def get_gate_encoder_under_test(self):
        return encode_full_adder_carry_gate

    def get_gate_arity(self):
        return 3

    def get_spec_truth_table(self):
        return (((0, 0, 0), 0),
                ((0, 0, 1), 0),
                ((0, 1, 0), 0),
                ((0, 1, 1), 1),
                ((1, 0, 0), 0),
                ((1, 0, 1), 1),
                ((1, 1, 0), 1),
                ((1, 1, 1), 1))


def create_miter_problem(clause_consumer: ClauseConsumer, circuit1_output, circuit2_output):
    """
    Adds clauses to clause_consumer asserting that circuit1_output and circuit2_output
    have distinct values.

    This can be used to check the equivalency of gates g and h:
    - Add the encoding of g to a fresh clause_consumer.
    - Add the encoding of h to a fresh clause_consumer. The inputs of h must match the inputs of g.
    - Let o_g be the output literal of g's encoding and o_h be the output literal of h's encoding.
      Call create_miter_problem(clause_consumer, o_g, o_h). This creates a circuit equivalency
      checking problem.
    - g and h are equivalent if and only if the CNF problem instance consumed by clause_consumer
      is unsatisfiable.

    This type of circuit equivalency checking problem is called miter problem.

    :param clause_consumer: A ClauseConsumer.
    :param circuit1_output: Any literal.
    :param circuit2_output: Any literal.
    :return: None
    """
    clause_consumer.consume_clause([circuit1_output, circuit2_output])
    clause_consumer.consume_clause([-circuit1_output, -circuit2_output])
    return None


class TestEncodeCNFConstraintAsGate(TestCase):
    def test_encode_cnf_constraint_as_gate_returns_output_literal(self):
        checker, variables = create_trivial_sat_solver_with_n_vars(10)
        result = encode_cnf_constraint_as_gate(checker, checker, [[variables[0]], [variables[1]]], variables[2])
        assert result == variables[2]

    def test_encode_cnf_constraint_as_gate_returns_new_output_literal_by_default(self):
        checker, variables = create_trivial_sat_solver_with_n_vars(10)
        result = encode_cnf_constraint_as_gate(checker, checker, [[variables[0]], [variables[1]]])
        return result not in variables and -result not in variables

    def test_encode_cnf_constraint_as_gate_encodes_empty_constraint_as_true(self):
        checker, variables = create_trivial_sat_solver_with_n_vars(10)
        logging_checker = LoggingClauseConsumerDecorator(checker)
        output = encode_cnf_constraint_as_gate(logging_checker, checker, [])
        assert (checker.solve([-output]) is False),\
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"
        assert (checker.solve([output]) is True),\
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"

    def test_encode_cnf_constraint_as_gate_encodes_negation(self):
        checker, variables = create_trivial_sat_solver_with_n_vars(10)
        logging_checker = LoggingClauseConsumerDecorator(checker)
        output = encode_cnf_constraint_as_gate(logging_checker, checker, [[-variables[0]]])
        assert (checker.solve([variables[0], output]) is False),\
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"
        assert (checker.solve([-variables[0], output]) is True),\
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"

    def test_encode_cnf_constraint_as_gate_encodes_or(self):
        checker, variables = create_trivial_sat_solver_with_n_vars(10)
        logging_checker = LoggingClauseConsumerDecorator(checker)
        output = encode_cnf_constraint_as_gate(logging_checker, checker, [[variables[0], variables[1]]])

        # Add a raw or gate and create an equivalency checking problem:
        checker.consume_clause([variables[0], variables[1], -variables[9]])
        checker.consume_clause([-variables[0], variables[9]])
        checker.consume_clause([-variables[1], variables[9]])
        create_miter_problem(checker, output, variables[9])

        assert (checker.solve() is False), \
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"

    def test_encode_cnf_constraint_as_gate_encodes_xor(self):
        checker, variables = create_trivial_sat_solver_with_n_vars(10)
        logging_checker = LoggingClauseConsumerDecorator(checker)
        output = encode_cnf_constraint_as_gate(logging_checker, checker, [[variables[0], variables[1]],
                                                                          [-variables[0], -variables[1]]])

        # Add a raw xor gate and create an equivalency checking problem:
        checker.consume_clause([variables[0], variables[1], -variables[9]])
        checker.consume_clause([-variables[0], -variables[1], -variables[9]])
        checker.consume_clause([variables[0], -variables[1], variables[9]])
        checker.consume_clause([-variables[0], variables[1], variables[9]])
        create_miter_problem(checker, output, variables[9])

        assert (checker.solve() is False), \
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"
