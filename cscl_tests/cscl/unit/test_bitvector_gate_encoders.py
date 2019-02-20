import abc
import unittest
import itertools
import cscl.bitvector_gate_encoders as bvg
import cscl.interfaces as cscl_if
from cscl_tests.testutils.trivial_sat_solver import TrivialSATSolver
from cscl_tests.testutils.logging_clause_consumer_decorator import LoggingClauseConsumerDecorator


class TestLiteralFactory(cscl_if.CNFLiteralFactory):
    def __init__(self):
        self.max_var = 0

    def create_literal(self):
        self.max_var += 1
        return self.max_var

    def get_num_variables(self):
        return self.max_var

    def has_literal(self, lit):
        return lit != 0 and abs(lit) <= self.max_var


class CollectingClauseConsumer(cscl_if.ClauseConsumer):
    def __init__(self):
        self.clauses = []

    def consume_clause(self, clause):
        self.clauses.append(clause)

    def has_clause(self, clause):
        return clause in self.clauses

    def get_clauses_in_consumption_order(self):
        return self.clauses[:]

    def get_num_clauses(self):
        return len(self.clauses)


class TestEncodeGateVector(unittest.TestCase):
    def test_is_noop_on_empty_inputs(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        def __should_not_be_called(*_):
            assert False, "This function should not be called"

        result = bvg.encode_gate_vector(clause_consumer, lit_factory,
                                        __should_not_be_called,
                                        lhs_input_lits=[], rhs_input_lits=[], output_lits=[])
        assert len(result) == 0
        assert clause_consumer.get_num_clauses() == 0
        assert lit_factory.get_num_variables() == 0

    def test_throws_exception_when_input_vec_lengths_mismatch(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        def __noop_encoder(*_):
            pass

        lits = [lit_factory.create_literal() for _ in range(10)]

        with self.assertRaises(ValueError):
            bvg.encode_gate_vector(clause_consumer, lit_factory,
                                   __noop_encoder,
                                   lhs_input_lits=[lits[0]],
                                   rhs_input_lits=[lits[1], lits[2]],
                                   output_lits=[lits[3]])

        assert clause_consumer.get_num_clauses() == 0
        assert lit_factory.get_num_variables() == 10

    def test_throws_exception_when_output_vec_length_mismatches(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        def __noop_encoder(*_):
            pass

        lits = [lit_factory.create_literal() for _ in range(10)]

        with self.assertRaises(ValueError):
            bvg.encode_gate_vector(clause_consumer, lit_factory,
                                   __noop_encoder,
                                   lhs_input_lits=[lits[0], lits[1]],
                                   rhs_input_lits=[lits[2], lits[3]],
                                   output_lits=[lits[4]])

        assert clause_consumer.get_num_clauses() == 0
        assert lit_factory.get_num_variables() == 10

    def test_generates_None_literals_when_no_outputs_specified(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lits = [lit_factory.create_literal() for _ in range(10)]
        collected_output_lits = []

        def __output_collecting_encoder(_1, _2, _3, output_lit):
            collected_output_lits.append(output_lit)
            return output_lit

        result = bvg.encode_gate_vector(clause_consumer, lit_factory, __output_collecting_encoder,
                                        lhs_input_lits=[lits[0], lits[1]],
                                        rhs_input_lits=[lits[2], lits[3]],
                                        output_lits=None)

        assert result == collected_output_lits
        assert result == [None, None]

    @staticmethod
    def __create_recording_encoder(recording_target: list):
        def __recording_encoder(*args):
            recording_target.append(args)
            return -1
        return __recording_encoder

    def test_calls_basic_encoder_once_for_unary_bit_vectors(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()
        recording_target = []
        bvg.encode_gate_vector(clause_consumer, lit_factory,
                               self.__create_recording_encoder(recording_target),
                               lhs_input_lits=[1],
                               rhs_input_lits=[2],
                               output_lits=[3])
        expected_rt = [(clause_consumer, lit_factory, (1, 2), 3)]
        assert recording_target == expected_rt,\
            "Unexpected encoder calls:\n" + str(recording_target) + "\nvs.\n" + str(expected_rt)

    def test_calls_basic_encoder_thrice_for_ternary_bit_vectors(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()
        recording_target = []
        bvg.encode_gate_vector(clause_consumer, lit_factory,
                               self.__create_recording_encoder(recording_target),
                               lhs_input_lits=[10, 20, 30],
                               rhs_input_lits=[11, 21, 31],
                               output_lits=[1, 2, 3])
        expected_rt = [(clause_consumer, lit_factory, (10, 11), 1),
                       (clause_consumer, lit_factory, (20, 21), 2),
                       (clause_consumer, lit_factory, (30, 31), 3)]
        assert recording_target == expected_rt,\
            "Unexpected encoder calls:\n" + str(recording_target) + "\nvs.\n" + str(expected_rt)


def int_to_bitvec(i, result_width):
    return tuple(1 if (i & 1 << idx) != 0 else 0 for idx in range(0, result_width))


def apply_truth_table_setting(positive_lits, setting):
    return [x if s >= 1 else -x for x, s in zip(positive_lits, setting)]


class TestEncodeBVRippleCarryAdderGate(unittest.TestCase):

    @staticmethod
    def __test_for_truth_table(arity, use_carry_in, use_carry_out, truth_table):

        for table_entry in truth_table:
            input_setting, output_setting = table_entry
            lhs_setting, rhs_setting, carry_in_setting = input_setting
            output_setting, carry_out_setting = output_setting

            checker = TrivialSATSolver()

            lhs_input_lits = [checker.create_literal() for _ in range(0, arity)]
            rhs_input_lits = [checker.create_literal() for _ in range(0, arity)]
            carry_in = checker.create_literal() if use_carry_in else None
            carry_out = checker.create_literal() if use_carry_out else None

            clause_consumer = LoggingClauseConsumerDecorator(checker)
            output_lits = bvg.encode_bv_ripple_carry_adder_gate(clause_consumer, checker,
                                                                lhs_input_lits, rhs_input_lits,
                                                                output_lits=None, carry_in_lit=carry_in,
                                                                carry_out_lit=carry_out)

            # Compute the SAT solver assumption setting for this entry:
            probe_lhs = apply_truth_table_setting(lhs_input_lits, lhs_setting)
            probe_rhs = apply_truth_table_setting(rhs_input_lits, rhs_setting)
            if use_carry_in:
                probe_lhs.append(carry_in if carry_in_setting >= 1 else -carry_in)

            probe_out = apply_truth_table_setting(output_lits, output_setting)
            if use_carry_out:
                probe_out.append(carry_out if carry_out_setting >= 1 else -carry_out)

            # Check that the truth table entry satisfies the encoding:
            assumptions_pos = list(itertools.chain(probe_lhs, probe_rhs, probe_out))
            assert checker.solve(assumptions_pos) is True,\
                "Encoding failed for truth table entry " + str(table_entry) + "\n(should be satisfiable, but is not)"\
                + "\nEncoding:\n" + clause_consumer.to_string()\
                + "\nAssumptions: " + str([x for x in assumptions_pos])

            # Check that the gate encodes a function by excluding the output configuration:
            clause_consumer.consume_clause([-x for x in probe_out])
            assumptions_neg = list(itertools.chain(probe_lhs, probe_rhs))
            assert checker.solve(assumptions_neg) is False,\
                "Encoding failed for truth table entry " + str(table_entry) + "\n(function property violated)"\
                + "\nEncoding:\n" + clause_consumer.to_string()\
                + "\nAssumptions: " + str([x for x in assumptions_neg])

    @staticmethod
    def __generate_full_truth_table(input_width, carry_in_settings):
        result = []

        for lhs_setting in range(0, 2**input_width):
            for rhs_setting in range(0, 2**input_width):
                for carry_in_setting in carry_in_settings:
                    expected_output = lhs_setting + rhs_setting + carry_in_setting
                    expected_carry_output = 1 if expected_output & 2**input_width != 0 else 0

                    # Remove "overflowing" bit from output:
                    if expected_carry_output == 1:
                        expected_output = expected_output ^ 2**input_width

                    input_setting = (int_to_bitvec(lhs_setting, input_width),
                                     int_to_bitvec(rhs_setting, input_width),
                                     carry_in_setting)
                    output_setting = (int_to_bitvec(expected_output, input_width),
                                      expected_carry_output)

                    result.append((input_setting, output_setting))
        return result

    def __truthtable_based_test(self, input_width, use_carry_in, use_carry_out):
        carry_in_settings = [0, 1] if use_carry_in else [0]
        truth_table = self.__generate_full_truth_table(input_width=input_width, carry_in_settings=carry_in_settings)
        self.__test_for_truth_table(input_width, use_carry_in=use_carry_in, use_carry_out=use_carry_out,
                                    truth_table=truth_table)

    def test_for_bv_width_1_no_carries(self):
        self.__truthtable_based_test(1, use_carry_in=False, use_carry_out=False)

    def test_for_bv_width_1_input_carry(self):
        self.__truthtable_based_test(1, use_carry_in=True, use_carry_out=False)

    def test_for_bv_width_1_output_carry(self):
        self.__truthtable_based_test(1, use_carry_in=False, use_carry_out=True)

    def test_for_bv_width_1_all_carries(self):
        self.__truthtable_based_test(1, use_carry_in=True, use_carry_out=True)

    def test_for_bv_width_2_no_carries(self):
        self.__truthtable_based_test(2, use_carry_in=False, use_carry_out=False)

    def test_for_bv_width_2_input_carry(self):
        self.__truthtable_based_test(2, use_carry_in=True, use_carry_out=False)

    def test_for_bv_width_2_output_carry(self):
        self.__truthtable_based_test(2, use_carry_in=False, use_carry_out=True)

    def test_for_bv_width_2_all_carries(self):
        self.__truthtable_based_test(2, use_carry_in=True, use_carry_out=True)

    def test_for_bv_width_3_no_carries(self):
        self.__truthtable_based_test(3, use_carry_in=False, use_carry_out=False)

    def test_for_bv_width_3_input_carry(self):
        self.__truthtable_based_test(3, use_carry_in=True, use_carry_out=False)

    def test_for_bv_width_3_output_carry(self):
        self.__truthtable_based_test(3, use_carry_in=False, use_carry_out=True)

    def test_for_bv_width_3_all_carries(self):
        self.__truthtable_based_test(3, use_carry_in=True, use_carry_out=True)

    def test_for_bv_width_4_no_carries(self):
        self.__truthtable_based_test(4, use_carry_in=False, use_carry_out=False)

    def test_for_bv_width_4_input_carry(self):
        self.__truthtable_based_test(4, use_carry_in=True, use_carry_out=False)

    def test_for_bv_width_4_output_carry(self):
        self.__truthtable_based_test(4, use_carry_in=False, use_carry_out=True)

    def test_for_bv_width_4_all_carries(self):
        self.__truthtable_based_test(4, use_carry_in=True, use_carry_out=True)


class AbstractTruthTableBasedBitvectorGateTest(abc.ABC):
    """
    Base class for truth-table-based bitvector-gate tests.
    """
    def __init__(self):
        # This mixin may only be used with test cases, since it uses assertRaises:
        assert isinstance(self, unittest.TestCase)

    @abc.abstractmethod
    def encode_gate_under_test(self, clause_consumer: cscl_if.ClauseConsumer,
                               lit_factory: cscl_if.CNFLiteralFactory, gate_arity: int):
        """
        Encodes the gate under test for the given agate arity, using `lit_factory` to create new literals
        and `clause_consumer` to store the result.

        :param clause_consumer: The clause consumer receiving the gate encoding.
        :param lit_factory: The literal factory used to create new literals.
        :param gate_arity: The gate's arity.
        :return: a tuple (x,y) with x being the concatenation of the gate's input literals
                 and y being the concatenation of the gate's output literals. Note: the order and amount
                 of literals contained in x must equal the order and amount of assignments in the truth
                 table's input setting tuples (i.e. the i'th literal in x has the same meaning as the
                 i'th entry in the truth table's input settings). Likewise, the order and amount of literals
                 in y must equal the order and amount of assignments in the truth table's output setting
                 tuples.
        """
        pass

    @abc.abstractmethod
    def generate_truth_table(self, gate_arity: int):
        """
        Generates the truth which the encoder returned by __get_bitvector_gate_encoder_under_test()
        is supposed to satisfy.

        :param gate_arity: A nonzero, non-negative integer.
        :return: A tuple [x_1, x_2, ..., x_(2^(gate_arity+1))] with, for all 1 <= i <= 2^(gate_arity+1), x_i is a tuple
                 (l+r, o) with l, r, o being tuples of length `gate_arity` containing elements in {0, 1}.
                 l signifies the left-hand-side input assignment, r signifies the right-hand-side
                 assignment, o signifies the output assignment. If there are two tuples (x, y1) and (x, y2), then
                 y1 = y2.
        """

    @abc.abstractmethod
    def get_bitvector_gate_encoder_under_test(self):
        """
        Returns the bitvector gate encoder function under test.
        :return: the bitvector gate encoder function under test.
        """
        pass

    @abc.abstractmethod
    def is_encoder_under_test_bv_predicate(self):
        """
        Returns True iff the encoder returned by get_bitvector_gate_encoder_under_test
        encodes a bitvector predicate function
        (i.e. the gate has a single output literal) and False iff the gate is a "full"
        bitvector gate function (i.e. the gate has W output literals, where W is the
        gate's arity).

        :return: a bool value as described above.
        """
        pass

    def __test_for_truth_table(self, gate_arity: int):
        truth_table = self.generate_truth_table(gate_arity)

        for table_entry in truth_table:
            input_setting, output_setting = table_entry

            checker = TrivialSATSolver()
            clause_consumer = LoggingClauseConsumerDecorator(checker)

            # Encode the bitvector gate
            input_lits, output_lits = self.encode_gate_under_test(clause_consumer, checker, gate_arity)

            # Check that the setting satisfies the constraint
            probe_input = apply_truth_table_setting(input_lits, input_setting)
            probe_output = apply_truth_table_setting(output_lits, output_setting)
            assumptions_pos = probe_input + probe_output
            has_correct_value = checker.solve(assumptions_pos)
            if not has_correct_value:
                if checker.solve(probe_input):
                    print("The gate forces an incorrect model:")
                    checker.print_model()
                else:
                    print("The gate has no satisfiable assignment for this input configuration")

            assert has_correct_value,\
                "Encoding failed for truth table entry " + str(table_entry) + "\n(should be satisfiable, but is not)" \
                + "\nEncoding:\n" + clause_consumer.to_string() \
                + "\nAssumptions: " + str(assumptions_pos)

            # Check that no other output setting satisfies the constraint
            clause_consumer.consume_clause([-x for x in probe_output])
            assumptions_neg = probe_input
            is_functional_rel = not checker.solve(assumptions_neg)
            if not is_functional_rel:
                print("Unexpectedly found model:")
                checker.print_model()
            assert is_functional_rel,\
                "Encoding failed for truth table entry " + str(table_entry) + "\n(function property violated)"\
                + "\nEncoding:\n" + clause_consumer.to_string()\
                + "\nAssumptions: " + str(assumptions_neg)

    def test_conforms_to_truth_table_for_bv_width_1(self):
        self.__test_for_truth_table(gate_arity=1)

    def test_conforms_to_truth_table_for_bv_width_2(self):
        self.__test_for_truth_table(gate_arity=2)

    def test_conforms_to_truth_table_for_bv_width_3(self):
        self.__test_for_truth_table(gate_arity=3)

    def test_conforms_to_truth_table_for_bv_width_4(self):
        self.__test_for_truth_table(gate_arity=4)

    def test_refuses_input_bv_with_length_mismatch(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 2)]

        encoder_under_test = self.get_bitvector_gate_encoder_under_test()
        # See assertion in __init__:
        # noinspection PyCallByClass
        # noinspection PyTypeChecker
        with unittest.TestCase.assertRaises(self, ValueError):
            encoder_under_test(clause_consumer=clause_consumer,
                               lit_factory=lit_factory,
                               lhs_input_lits=lhs_input_lits,
                               rhs_input_lits=rhs_input_lits)

    def test_uses_and_returns_provided_output_literals(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        output_lits = lit_factory.create_literal() if self.is_encoder_under_test_bv_predicate() \
            else [lit_factory.create_literal() for _ in range(0, 3)]

        encoder_under_test = self.get_bitvector_gate_encoder_under_test()
        if self.is_encoder_under_test_bv_predicate():
            result = encoder_under_test(clause_consumer=clause_consumer,
                                        lit_factory=lit_factory,
                                        lhs_input_lits=lhs_input_lits,
                                        rhs_input_lits=rhs_input_lits,
                                        output_lit=output_lits)
        else:
            result = encoder_under_test(clause_consumer=clause_consumer,
                                        lit_factory=lit_factory,
                                        lhs_input_lits=lhs_input_lits,
                                        rhs_input_lits=rhs_input_lits,
                                        output_lits=output_lits)

        assert result == output_lits

    def test_creates_output_literals_if_none_provided(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        all_inputs = lhs_input_lits + rhs_input_lits

        encoder_under_test = self.get_bitvector_gate_encoder_under_test()
        result = encoder_under_test(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits)

        if self.is_encoder_under_test_bv_predicate():
            assert result not in all_inputs
            assert -result not in all_inputs
        else:
            assert not any(x in all_inputs for x in result)
            assert not any(-x in all_inputs for x in result)


class AbstractTruthTableBasedBitvectorToBitvectorGateTest(AbstractTruthTableBasedBitvectorGateTest):
    """
    Base class for truth-table-based bitvector-gate tests where the encoded gate's output represents
    a bitvector (i.e. the gate encoder returns a list of literals).
    """
    def test_refuses_output_bv_with_length_mismatch(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        output_lits = [lit_factory.create_literal() for _ in range(0, 2)]

        encoder_under_test = self.get_bitvector_gate_encoder_under_test()
        # See assertion in __init__:
        # noinspection PyCallByClass
        # noinspection PyTypeChecker
        with unittest.TestCase.assertRaises(self, ValueError):
            encoder_under_test(clause_consumer=clause_consumer,
                               lit_factory=lit_factory,
                               lhs_input_lits=lhs_input_lits,
                               rhs_input_lits=rhs_input_lits,
                               output_lits=output_lits)

    def is_encoder_under_test_bv_predicate(self):
        return False


class AbstractTruthTableBasedPlainBitvectorToBitvectorGateTest(AbstractTruthTableBasedBitvectorToBitvectorGateTest):
    """
    Base class for truth-table-based bitvector-gate tests where the encoded gate's output represents
    a bitvector (i.e. the gate encoder returns a list of literals), where the bitvector encoder takes
    no more arguments than
        - clause_consumer: the clause consumer
        - lit_factory: the literal factory
        - lhs_input_lits, rhs_input_lits: the lhs rsp. rhs input literals
        - output_lits: the output literals (optional argument)
    """

    def encode_gate_under_test(self, clause_consumer: cscl_if.ClauseConsumer,
                               lit_factory: cscl_if.CNFLiteralFactory, gate_arity: int):
        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, gate_arity)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, gate_arity)]

        encoder_under_test = self.get_bitvector_gate_encoder_under_test()
        output_lits = encoder_under_test(clause_consumer=clause_consumer,
                                         lit_factory=lit_factory,
                                         lhs_input_lits=lhs_input_lits,
                                         rhs_input_lits=rhs_input_lits)

        return lhs_input_lits+rhs_input_lits, output_lits


class AbstractTruthTableBasedPlainBitvectorPredicateGateTest(AbstractTruthTableBasedBitvectorGateTest):
    """
    Base class for truth-table-based bitvector-gate tests where the encoded gate's output is a single
    literal, where the bitvector encoder takes no more arguments than
        - clause_consumer: the clause consumer
        - lit_factory: the literal factory
        - lhs_input_lits, rhs_input_lits: the lhs rsp. rhs input literals
        - output_lit: the output literal (optional argument)
    """

    def encode_gate_under_test(self, clause_consumer: cscl_if.ClauseConsumer,
                               lit_factory: cscl_if.CNFLiteralFactory, gate_arity: int):
        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, gate_arity)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, gate_arity)]

        encoder_under_test = self.get_bitvector_gate_encoder_under_test()
        output_lit = encoder_under_test(clause_consumer=clause_consumer,
                                        lit_factory=lit_factory,
                                        lhs_input_lits=lhs_input_lits,
                                        rhs_input_lits=rhs_input_lits)

        return lhs_input_lits+rhs_input_lits, [output_lit]


    def is_encoder_under_test_bv_predicate(self):
        return True


#
# Tests for "plain" bitvector functions (and, or, xor, subtraction):
#

def generate_truth_table_for_binary_op(gate_arity: int, binary_op):
    """
    Generates a truth table using the given binary operation on integers.

    :param gate_arity: The gate's arity.
    :param binary_op: A function mapping two integers to an integer.
    :return: The truth table for a gate applying binary_op to the input bitvectors. Only the first `gate_arity`
             bits of the result of invoking binary_op are considered. The returned object is a truth table in
             the sense of AbstractTruthTableBasedBitvectorGateTest's documentation, with all possible input assignments
             occurring in the truth table.
    """
    truth_table = []
    for lhs, rhs in itertools.product(range(0, 2 ** gate_arity), range(0, 2 ** gate_arity)):
        output = binary_op(lhs, rhs)
        table_entry = (int_to_bitvec(lhs, gate_arity) + int_to_bitvec(rhs, gate_arity),
                       int_to_bitvec(output, gate_arity))
        truth_table.append(table_entry)
    return truth_table


class TestEncodeBVAndGate(unittest.TestCase, AbstractTruthTableBasedPlainBitvectorToBitvectorGateTest):
    """
    Test for bvg.encode_bv_and_gate
    """
    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_and_gate

    def generate_truth_table(self, gate_arity: int):
        return generate_truth_table_for_binary_op(gate_arity, lambda x, y: x & y)


class TestEncodeBVOrGate(unittest.TestCase, AbstractTruthTableBasedPlainBitvectorToBitvectorGateTest):
    """
    Test for bvg.encode_bv_or_gate
    """
    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_or_gate

    def generate_truth_table(self, gate_arity: int):
        return generate_truth_table_for_binary_op(gate_arity, lambda x, y: x | y)


class TestEncodeBVXorGate(unittest.TestCase, AbstractTruthTableBasedPlainBitvectorToBitvectorGateTest):
    """
    Test for bvg.encode_bv_xor_gate
    """
    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_xor_gate

    def generate_truth_table(self, gate_arity: int):
        return generate_truth_table_for_binary_op(gate_arity, lambda x, y: x ^ y)


class TestEncodeBvRippleCarrySubGate(unittest.TestCase, AbstractTruthTableBasedPlainBitvectorToBitvectorGateTest):
    """
    Test for bvg.encode_bv_ripple_carry_sub_gate
    """
    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_ripple_carry_sub_gate

    def generate_truth_table(self, gate_arity: int):
        truth_table = []
        for lhs, rhs in itertools.product(range(0, 2**gate_arity), range(0, 2**gate_arity)):
            output = lhs - rhs
            table_entry = (int_to_bitvec(lhs, gate_arity) + int_to_bitvec(rhs, gate_arity),
                           int_to_bitvec(output, gate_arity))
            truth_table.append(table_entry)
        return truth_table


#
# Tests for binary predicates (sle, ule, equality):
#

def generate_truth_table_for_bv_predicate(gate_arity: int, predicate):
    """
    Generates a truth table using the given binary predicate on integers.

    :param gate_arity: The gate's arity.
    :param predicate: A function mapping tuples (l, r, w) to a bool, with all but the lowermost w bits of l and r being
                      ignored.
    :return: The truth table for a gate applying predicate to the input bitvectors.
             The returned object is a truth table in the sense of AbstractTruthTableBasedBitvectorGateTest's
             documentation, with all possible input assignments occurring in the truth table.
    """
    truth_table = []
    for lhs, rhs in itertools.product(range(0, 2 ** gate_arity), range(0, 2 ** gate_arity)):
        output = predicate(lhs, rhs, gate_arity)
        table_entry = (int_to_bitvec(lhs, gate_arity) + int_to_bitvec(rhs, gate_arity),
                       (1,) if output is True else (0,))
        truth_table.append(table_entry)
    return truth_table


class TestEncodeBVUnsignedLessThanOrEqualCompGate(unittest.TestCase,
                                                  AbstractTruthTableBasedPlainBitvectorPredicateGateTest):
    """
    Test for bvg.encode_bv_ule_gate
    """

    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_ule_gate

    def generate_truth_table(self, gate_arity: int):
        predicate = lambda l, r, width: (l & (2**width - 1)) <= (r & (2**width - 1))
        return generate_truth_table_for_bv_predicate(gate_arity, predicate)


class TestEncodeBVSignedLessThanOrEqualCompGate(unittest.TestCase,
                                                AbstractTruthTableBasedPlainBitvectorPredicateGateTest):
    """
    Test for bvg.encode_bv_sle_gate
    """

    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_sle_gate

    def generate_truth_table(self, gate_arity: int):
        def __sign_extend(x: int, from_width: int):
            assert from_width > 0
            sign = 1 if (x & (1 << (from_width-1))) != 0 else 0
            sign_extension_mask = ~((1 << from_width) - 1)
            if sign == 0:
                return x & ~sign_extension_mask
            else:
                return x | sign_extension_mask

        predicate = lambda l, r, width: __sign_extend(l, width) <= __sign_extend(r, width)
        return generate_truth_table_for_bv_predicate(gate_arity, predicate)


class TestEncodeBVEqualityCompGate(unittest.TestCase,
                                   AbstractTruthTableBasedPlainBitvectorPredicateGateTest):
    """
    Test for bvg.encode_bv_eq_gate
    """

    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_eq_gate

    def generate_truth_table(self, gate_arity: int):
        predicate = lambda l, r, width: (l & (2**width - 1)) == (r & (2**width - 1))
        return generate_truth_table_for_bv_predicate(gate_arity, predicate)


#
# Tests for binary multiplier gates:
#

class TestEncodeParallelBVMultiplierGateEncoder(AbstractTruthTableBasedBitvectorToBitvectorGateTest,
                                                abc.ABC):
    """
    Test for bvg.encode_bv_parallel_mul_gate
    """

    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_parallel_mul_gate

    @abc.abstractmethod
    def is_test_with_overflow_output(self) -> bool:
        pass

    def generate_truth_table(self, gate_arity: int):
        result = []
        include_overflow_bit = self.is_test_with_overflow_output()

        for lhs_setting in range(0, 2 ** gate_arity):
            for rhs_setting in range(0, 2 ** gate_arity):
                expected_output = lhs_setting * rhs_setting
                expected_overflow = 1 if ((expected_output >> gate_arity) != 0) else 0
                expected_output = expected_output & ((1 << gate_arity) - 1)

                input_setting = int_to_bitvec(lhs_setting, gate_arity) + int_to_bitvec(rhs_setting, gate_arity)
                output_setting = int_to_bitvec(expected_output, gate_arity) + \
                    (expected_overflow,) if include_overflow_bit else tuple()
                result.append((input_setting, output_setting))
        return result

    def encode_gate_under_test(self, clause_consumer: cscl_if.ClauseConsumer,
                               lit_factory: cscl_if.CNFLiteralFactory, gate_arity: int):
        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, gate_arity)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, gate_arity)]
        overflow_lit = lit_factory.create_literal() if self.is_test_with_overflow_output() else None

        encoder_under_test = self.get_bitvector_gate_encoder_under_test()
        output_lits = encoder_under_test(clause_consumer=clause_consumer,
                                         lit_factory=lit_factory,
                                         lhs_input_lits=lhs_input_lits,
                                         rhs_input_lits=rhs_input_lits,
                                         overflow_lit=overflow_lit)

        if overflow_lit is None:
            return lhs_input_lits+rhs_input_lits, output_lits
        else:
            return lhs_input_lits+rhs_input_lits, (output_lits + [overflow_lit])


class TestEncodeParallelBVMultiplierGateEncoderWithOverflowLit(unittest.TestCase,
                                                               TestEncodeParallelBVMultiplierGateEncoder):
    def is_test_with_overflow_output(self) -> bool:
        return True


class TestEncodeParallelBVMultiplierGateEncoderWithoutOverflowLit(unittest.TestCase,
                                                                  TestEncodeParallelBVMultiplierGateEncoder):
    def is_test_with_overflow_output(self) -> bool:
        return False


#
# Tests for bitvector MUX:
#

class TestEncodeBVMuxGateEncoder(unittest.TestCase,
                                 AbstractTruthTableBasedBitvectorToBitvectorGateTest):
    """
    Test for bvg.encode_bv_mux_gate
    """

    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_mux_gate

    def generate_truth_table(self, gate_arity: int):
        result = []

        for lhs_setting in range(0, 2 ** gate_arity):
            for rhs_setting in range(0, 2 ** gate_arity):
                for select_lhs_setting in (0, 1):
                    expected_output = lhs_setting if select_lhs_setting is 1 else rhs_setting

                    input_setting = int_to_bitvec(lhs_setting, gate_arity) + int_to_bitvec(rhs_setting, gate_arity) \
                        + int_to_bitvec(select_lhs_setting, 1)
                    output_setting = int_to_bitvec(expected_output, gate_arity)
                    result.append((input_setting, output_setting))
        return result

    def encode_gate_under_test(self, clause_consumer: cscl_if.ClauseConsumer,
                               lit_factory: cscl_if.CNFLiteralFactory, gate_arity: int):
        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, gate_arity)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, gate_arity)]
        select_lhs_lit = lit_factory.create_literal()

        output_lits = bvg.encode_bv_mux_gate(clause_consumer=clause_consumer,
                                             lit_factory=lit_factory,
                                             lhs_input_lits=lhs_input_lits,
                                             rhs_input_lits=rhs_input_lits,
                                             select_lhs_lit=select_lhs_lit)

        return lhs_input_lits+rhs_input_lits+[select_lhs_lit], output_lits


#
# Tests for bitvector division encoders:
#

class TestEncodeBvLongUDivGate(unittest.TestCase, AbstractTruthTableBasedPlainBitvectorToBitvectorGateTest):
    """
    Test for bvg.encode_bv_long_udiv_gate
    """
    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_long_udiv_gate

    def generate_truth_table(self, gate_arity: int):
        truth_table = []
        for lhs, rhs in itertools.product(range(0, 2**gate_arity), range(0, 2**gate_arity)):
            output = int(lhs/rhs) if rhs != 0 else 0
            table_entry = (int_to_bitvec(lhs, gate_arity) + int_to_bitvec(rhs, gate_arity),
                           int_to_bitvec(output, gate_arity))
            truth_table.append(table_entry)

        return truth_table


class TestEncodeBvLongURemGate(unittest.TestCase, AbstractTruthTableBasedPlainBitvectorToBitvectorGateTest):
    """
    Test for bvg.encode_bv_long_urem_gate
    """
    def get_bitvector_gate_encoder_under_test(self):
        return bvg.encode_bv_long_urem_gate

    def generate_truth_table(self, gate_arity: int):
        truth_table = []
        for lhs, rhs in itertools.product(range(0, 2**gate_arity), range(0, 2**gate_arity)):
            output = (lhs % rhs) if rhs != 0 else 0
            table_entry = (int_to_bitvec(lhs, gate_arity) + int_to_bitvec(rhs, gate_arity),
                           int_to_bitvec(output, gate_arity))
            truth_table.append(table_entry)

        return truth_table


#
# Tests for unary bitvector gate encoders:
#

class TestEncodeStaggeredOrGate(unittest.TestCase):

    def test_returns_empty_list_when_no_inputs_provided(self):
        clause_consumer = CollectingClauseConsumer()
        lit_factory = TestLiteralFactory()
        result = bvg.encode_staggered_or_gate(clause_consumer=clause_consumer, lit_factory=lit_factory, input_lits=[])
        assert result == [], "Unexpected result " + str(result)

    def test_raises_exception_when_input_and_output_sizes_mismatch(self):
        clause_consumer = CollectingClauseConsumer()
        lit_factory = TestLiteralFactory()
        with self.assertRaises(ValueError):
            bvg.encode_staggered_or_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                                         input_lits=[lit_factory.create_literal()],
                                         output_lits=[lit_factory.create_literal(), lit_factory.create_literal()])

    def test_encodes_equivalency_for_unary_input(self):
        solver = TrivialSATSolver()
        input_lit = solver.create_literal()
        output_lit = solver.create_literal()
        bvg.encode_staggered_or_gate(clause_consumer=solver, lit_factory=solver,
                                     input_lits=[input_lit],
                                     output_lits=[output_lit])

        assert solver.solve([]) is True, "Without further constraints, the gate encoding must be satisfiable"
        assert solver.solve([input_lit, -output_lit]) is False, "Unexpected: input not equivalent to output"
        assert solver.solve([-input_lit, output_lit]) is False, "Unexpected: input not equivalent to output"

    def test_is_staggered_or_gate_for_ternary_input(self):
        for test_index in range(0, 8):
            solver = TrivialSATSolver()
            input_lits = [solver.create_literal() for _ in range(0, 3)]
            output_lits = bvg.encode_staggered_or_gate(clause_consumer=solver, lit_factory=solver,
                                                       input_lits=input_lits)
            test_input = [input_lits[i] if (test_index & (1 << i)) != 0 else -input_lits[i] for i in range(0, 3)]
            expected_output = [output_lits[i] if any(x > 0 for x in test_input[i:]) else -output_lits[i]
                               for i in range(0, 3)]

            maps_input = solver.solve(test_input + expected_output)
            assert maps_input, "The gate under test violates its input/output spec"

            solver.consume_clause([-o for o in expected_output])
            assert not solver.solve(test_input), "Unexpected: encoding is not a gate encoding"
