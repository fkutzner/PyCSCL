from unittest import TestCase
from cscl.basic_gate_encoders import *
from tests.testutils.trivial_sat_solver import TrivialSATSolver
from tests.testutils.logging_clause_consumer_decorator import LoggingClauseConsumerDecorator


def encoder_returns_output_literal(encoder_fn):
    checker = TrivialSATSolver()
    variables = []
    for i in range(0, 10):
        variables.append(checker.create_variable())

    result = encoder_fn(checker, checker, [variables[0], variables[1]], variables[2])
    return result == variables[2]


def encoder_returns_new_output_literal_by_default(encoder_fn):
    checker = TrivialSATSolver()
    variables = []
    for i in range(0, 10):
        variables.append(checker.create_variable())

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
            inputs.append(checker.create_variable())

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
            inputs.append(checker.create_variable())

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


class TestEncodeBinaryXorGate(TestCase):
    def test_encode_binary_xor_gate_returns_output_literal(self):
        assert(encoder_returns_output_literal(encode_binary_xor_gate))

    def test_encode_binary_xor_gate_returns_new_output_literal_by_default(self):
        assert(encoder_returns_new_output_literal_by_default(encode_binary_xor_gate))

    def test_encode_xor_gate_create_gate(self):
        checker = TrivialSATSolver()
        inputs = [checker.create_variable(), checker.create_variable()]
        output = encode_binary_xor_gate(checker, checker, inputs)

        l1, l2 = inputs[0], inputs[1]

        assert (checker.solve([l1, l2, output]) is False)
        assert (checker.solve([l1, l2, -output]) is True)
        assert (checker.solve([-l1, -l2, output]) is False)
        assert (checker.solve([-l1, -l2, -output]) is True)
        assert (checker.solve([-l1, l2, output]) is True)
        assert (checker.solve([-l1, l2, -output]) is False)
        assert (checker.solve([l1, -l2, output]) is True)
        assert (checker.solve([l1, -l2, -output]) is False)


def create_trivial_sat_solver_with_10_vars():
    """
    Creates a TrivialSATSolver instance x with 10 variables for x.

    :return: (solver, variables). solver is the created solver, variables the list of
             created variables.
    """
    solver = TrivialSATSolver()
    variables = []
    for i in range(0, 10):
        variables.append(solver.create_variable())
    return solver, variables


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


def encode_binary_or_gate(clause_consumer: ClauseConsumer, variable_factory: CNFVariableFactory,
                          input_lits, output_lit=None):
    """
    Creates a binary OR gate.

    (Difference to production OR gate encoder: this is restricted to two inputs)

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param variable_factory: TODO
    :param input_lits: The gate's input literals.
    :param output_lit: The gate's output literal. If output_lit is None, a positive literal with a
                       new variable will be used as the gate's output literal.
    :return: The encoded gate's output literal.
    """
    if output_lit is None:
        output_lit = variable_factory.create_variable()

    clause_consumer.consume_clause([input_lits[0], input_lits[1], -output_lit])
    clause_consumer.consume_clause([-input_lits[0], output_lit])
    clause_consumer.consume_clause([-input_lits[1], output_lit])

    return output_lit


def encode_binary_and_gate(clause_consumer: ClauseConsumer, variable_factory: CNFVariableFactory,
                           input_lits, output_lit=None):
    """
    Creates a binary AND gate.

    (Difference to production AND gate encoder: this is restricted to two inputs)

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param input_lits: The gate's input literals.
    :param output_lit: The gate's output literal. If output_lit is None, a positive literal with a
                       new variable will be used as the gate's output literal.
    :return: The encoded gate's output literal.
    """
    if output_lit is None:
        output_lit = variable_factory.create_variable()

    clause_consumer.consume_clause([-input_lits[0], -input_lits[1], output_lit])
    clause_consumer.consume_clause([input_lits[0], -output_lit])
    clause_consumer.consume_clause([input_lits[1], -output_lit])

    return output_lit


class TestEncodeBinaryMuxGate(TestCase):
    def test_encode_binary_mux_gate_returns_output_literal(self):
        checker, variables = create_trivial_sat_solver_with_10_vars()
        result = encode_binary_mux_gate(checker, checker, [variables[0], variables[1], variables[2]], variables[3])
        assert result == variables[3]

    def test_encode_binary_mux_gate_returns_new_output_literal_by_default(self):
        checker, variables = create_trivial_sat_solver_with_10_vars()
        result = encode_binary_mux_gate(checker, checker, [variables[0], variables[1], variables[2]])
        return result not in variables and -result not in variables

    def test_encode_binary_mux_gate_is_equivalent_to_crafted_mux_gate(self):
        # Prove equivalency to a crafted binary MUX gate:
        checker, variables = create_trivial_sat_solver_with_10_vars()
        sel, lhs, rhs = variables[0:3]

        # Add production MUX:
        logging_checker = LoggingClauseConsumerDecorator(checker)
        production_mux_out = encode_binary_mux_gate(logging_checker, checker, [sel, lhs, rhs])

        # Add crafted MUX:
        lhs_active_out = encode_binary_and_gate(checker, checker, [-sel, lhs])
        rhs_active_out = encode_binary_and_gate(checker, checker, [sel, rhs])
        crafted_mux_out = encode_binary_or_gate(checker, checker, [lhs_active_out, rhs_active_out])

        # Prove equivalency:
        create_miter_problem(checker, production_mux_out, crafted_mux_out)
        assert (checker.solve() is False), \
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(crafted_mux_out) + ")"


class TestEncodeCNFConstraintAsGate(TestCase):
    def test_encode_cnf_constraint_as_gate_returns_output_literal(self):
        checker, variables = create_trivial_sat_solver_with_10_vars()
        result = encode_cnf_constraint_as_gate(checker, checker, [[variables[0]], [variables[1]]], variables[2])
        assert result == variables[2]

    def test_encode_cnf_constraint_as_gate_returns_new_output_literal_by_default(self):
        checker, variables = create_trivial_sat_solver_with_10_vars()
        result = encode_cnf_constraint_as_gate(checker, checker, [[variables[0]], [variables[1]]])
        return result not in variables and -result not in variables

    def test_encode_cnf_constraint_as_gate_encodes_empty_constraint_as_true(self):
        checker, variables = create_trivial_sat_solver_with_10_vars()
        logging_checker = LoggingClauseConsumerDecorator(checker)
        output = encode_cnf_constraint_as_gate(logging_checker, checker, [])
        assert (checker.solve([-output]) is False),\
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"
        assert (checker.solve([output]) is True),\
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"

    def test_encode_cnf_constraint_as_gate_encodes_negation(self):
        checker, variables = create_trivial_sat_solver_with_10_vars()
        logging_checker = LoggingClauseConsumerDecorator(checker)
        output = encode_cnf_constraint_as_gate(logging_checker, checker, [[-variables[0]]])
        assert (checker.solve([variables[0], output]) is False),\
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"
        assert (checker.solve([-variables[0], output]) is True),\
            "Bad encoding:\n" + logging_checker.to_string() + "(output: " + str(output) + ")"

    def test_encode_cnf_constraint_as_gate_encodes_or(self):
        checker, variables = create_trivial_sat_solver_with_10_vars()
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
        checker, variables = create_trivial_sat_solver_with_10_vars()
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
