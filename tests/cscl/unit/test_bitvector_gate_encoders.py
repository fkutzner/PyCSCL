import abc
import unittest
import itertools
import cscl.bitvector_gate_encoders as bvg
import cscl.interfaces as cscl_if
import cscl.basic_gate_encoders
from tests.testutils.trivial_sat_solver import TrivialSATSolver
from tests.testutils.logging_clause_consumer_decorator import LoggingClauseConsumerDecorator


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
            assert False, "This function should get be called"

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


class AbstractTestBasicBitvectorGateEncoder(abc.ABC):
    """Abstract test case for testing bitvector gate-constraints where the i'th output
       literal is only dependent on the i'th left-hand-side and the i'th right-hand-side
       input literal, via a gate constraint G.

       This mixin may only be used with abstract classes or classes deriving from
       unittest.TestCase."""

    def __init__(self):
        # This mixin may only be used with test cases, since it uses assertRaises:
        assert isinstance(self, unittest.TestCase)

    @abc.abstractmethod
    def get_bv_gate_encoder_under_test(self):
        """
        Gets the bitvector gate encoder under test.

        :return: the bitvector gate encoder under test, a function having the same
                 signature as the encode_bv_and_gate function.
        """
        pass

    @abc.abstractmethod
    def get_basic_gate_encoder_of_bv_gate_encoder(self):
        """
        Gets the (non-bitvector) basic gate encoder encoding the gate constraint G

        :return: a basic gate encoder function, a function having the same signature
                 as cscl.basic_gate_encoders.encode_and_gate
        """
        pass

    def test_is_noop_on_empty_inputs(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        under_test = self.get_bv_gate_encoder_under_test()
        result = under_test(clause_consumer, lit_factory,
                            lhs_input_lits=[], rhs_input_lits=[], output_lits=[])
        assert len(result) == 0
        assert clause_consumer.get_num_clauses() == 0
        assert lit_factory.get_num_variables() == 0

    def test_throws_exception_when_input_vec_lengths_mismatch(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()
        lits = [lit_factory.create_literal() for _ in range(10)]

        # See assertion in __init__:
        # noinspection PyCallByClass
        # noinspection PyTypeChecker
        with unittest.TestCase.assertRaises(self, ValueError):
            under_test = self.get_bv_gate_encoder_under_test()
            under_test(clause_consumer, lit_factory,
                       lhs_input_lits=[lits[0]],
                       rhs_input_lits=[lits[1], lits[2]],
                       output_lits=[lits[3]])

        assert clause_consumer.get_num_clauses() == 0
        assert lit_factory.get_num_variables() == 10

    def test_throws_exception_when_output_vec_length_mismatches(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()
        lits = [lit_factory.create_literal() for _ in range(10)]

        # See assertion in __init__:
        # noinspection PyCallByClass
        # noinspection PyTypeChecker
        with unittest.TestCase.assertRaises(self, ValueError):
            under_test = self.get_bv_gate_encoder_under_test()
            under_test(clause_consumer, lit_factory,
                       lhs_input_lits=[lits[0], lits[1]],
                       rhs_input_lits=[lits[2], lits[3]],
                       output_lits=[lits[4]])

        assert clause_consumer.get_num_clauses() == 0
        assert lit_factory.get_num_variables() == 10

    def test_generates_literals_when_no_outputs_specified_at_all(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()
        lits = [lit_factory.create_literal() for _ in range(10)]

        under_test = self.get_bv_gate_encoder_under_test()
        result = under_test(clause_consumer, lit_factory,
                            lhs_input_lits=[lits[0], lits[1]],
                            rhs_input_lits=[lits[2], lits[3]],
                            output_lits=None)

        assert lit_factory.get_num_variables() == 12
        assert len(result) == 2
        assert all(x not in lits and -x not in lits for x in result)
        assert all(lit_factory.has_literal(x) for x in result)

    def test_generates_literals_for_unspecified_outputs(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()
        lits = [lit_factory.create_literal() for _ in range(10)]

        under_test = self.get_bv_gate_encoder_under_test()
        result = under_test(clause_consumer, lit_factory,
                            lhs_input_lits=[lits[0], lits[1]],
                            rhs_input_lits=[lits[2], lits[3]],
                            output_lits=[lits[4], None])

        assert len(result) == 2
        assert lit_factory.get_num_variables() == 11
        assert result[1] not in lits and -result[1] not in lits
        assert lit_factory.has_literal(result[1])

    def test_creates_unary_bv_gate(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()
        lits = [lit_factory.create_literal() for _ in range(10)]

        under_test = self.get_bv_gate_encoder_under_test()
        under_test(clause_consumer, lit_factory,
                   lhs_input_lits=[lits[1]], rhs_input_lits=[lits[2]],
                   output_lits=[lits[3]])

        expected_clause_consumer = CollectingClauseConsumer()
        basic_ge_of_under_test = self.get_basic_gate_encoder_of_bv_gate_encoder()
        basic_ge_of_under_test(expected_clause_consumer, lit_factory, [lits[1], lits[2]], lits[3])

        assert(clause_consumer.get_clauses_in_consumption_order() ==
               expected_clause_consumer.get_clauses_in_consumption_order())

    def test_creates_ternary_bv_gate(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()
        lits = [lit_factory.create_literal() for _ in range(32)]

        under_test = self.get_bv_gate_encoder_under_test()
        under_test(clause_consumer, lit_factory,
                   lhs_input_lits=[lits[10], lits[20], lits[30]],
                   rhs_input_lits=[lits[11], lits[21], lits[31]],
                   output_lits=[lits[1], lits[2], lits[3]])

        expected_clause_consumer = CollectingClauseConsumer()
        basic_ge_of_under_test = self.get_basic_gate_encoder_of_bv_gate_encoder()
        basic_ge_of_under_test(expected_clause_consumer, lit_factory, [lits[10], lits[11]], lits[1])
        basic_ge_of_under_test(expected_clause_consumer, lit_factory, [lits[20], lits[21]], lits[2])
        basic_ge_of_under_test(expected_clause_consumer, lit_factory, [lits[30], lits[31]], lits[3])

        assert(clause_consumer.get_clauses_in_consumption_order() ==
               expected_clause_consumer.get_clauses_in_consumption_order())


class TestEncodeBVAndGate(unittest.TestCase, AbstractTestBasicBitvectorGateEncoder):

    def get_bv_gate_encoder_under_test(self):
        return cscl.bitvector_gate_encoders.encode_bv_and_gate

    def get_basic_gate_encoder_of_bv_gate_encoder(self):
        return cscl.basic_gate_encoders.encode_and_gate


class TestEncodeBVOrGate(unittest.TestCase, AbstractTestBasicBitvectorGateEncoder):

    def get_bv_gate_encoder_under_test(self):
        return cscl.bitvector_gate_encoders.encode_bv_or_gate

    def get_basic_gate_encoder_of_bv_gate_encoder(self):
        return cscl.basic_gate_encoders.encode_or_gate


class TestEncodeBVXorGate(unittest.TestCase, AbstractTestBasicBitvectorGateEncoder):

    def get_bv_gate_encoder_under_test(self):
        return cscl.bitvector_gate_encoders.encode_bv_xor_gate

    def get_basic_gate_encoder_of_bv_gate_encoder(self):
        return cscl.basic_gate_encoders.encode_binary_xor_gate


def int_to_bitvec(i, result_width):
    assert i >= 0
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


class AbstractTestUnsignedBVMultiplierGate(abc.ABC):

    def __init__(self):
        # This mixin may only be used with test cases, since it uses assertRaises:
        assert isinstance(self, unittest.TestCase)

    @abc.abstractmethod
    def get_bv_umul_encoder_under_test(self):
        """
        Gets the bitvector gate encoder under test.

        :return: the bitvector gate encoder under test, a function having the same
                 signature as the encode_bv_and_gate function.
        """
        pass

    def __test_for_truth_table(self, arity, use_overflow_lit, truth_table):
        encoder_under_test = self.get_bv_umul_encoder_under_test()

        for table_entry in truth_table:
            input_setting, output_setting = table_entry
            lhs_setting, rhs_setting = input_setting
            output_setting, overflow_setting = output_setting

            checker = TrivialSATSolver()
            clause_consumer = LoggingClauseConsumerDecorator(checker)

            lhs_input_lits = [checker.create_literal() for _ in range(0, arity)]
            rhs_input_lits = [checker.create_literal() for _ in range(0, arity)]
            overflow_lit = checker.create_literal() if use_overflow_lit else None

            output_lits = encoder_under_test(clause_consumer, checker,
                                             lhs_input_lits, rhs_input_lits, overflow_lit=overflow_lit)

            probe_lhs = apply_truth_table_setting(lhs_input_lits, lhs_setting)
            probe_rhs = apply_truth_table_setting(rhs_input_lits, rhs_setting)
            probe_output = apply_truth_table_setting(output_lits, output_setting)
            if use_overflow_lit:
                probe_output.append(overflow_lit if overflow_setting > 0 else -overflow_lit)

            probe_input = probe_lhs + probe_rhs

            # Check that the setting satisfies the constraint
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

    @staticmethod
    def __generate_full_truth_table(input_width):
        result = []

        for lhs_setting in range(0, 2 ** input_width):
            for rhs_setting in range(0, 2 ** input_width):
                expected_output = lhs_setting * rhs_setting
                expected_overflow = 1 if ((expected_output >> input_width) != 0) else 0
                expected_output = expected_output & ((1 << input_width) - 1)
                input_setting = (int_to_bitvec(lhs_setting, input_width),
                                 int_to_bitvec(rhs_setting, input_width))
                output_setting = (int_to_bitvec(expected_output, input_width),
                                  expected_overflow)
                result.append((input_setting, output_setting))
        return result

    def __truthtable_based_test(self, input_width, use_overflow_lit):
        truth_table = self.__generate_full_truth_table(input_width=input_width)
        self.__test_for_truth_table(input_width, use_overflow_lit=use_overflow_lit, truth_table=truth_table)

    def test_for_bv_width_1_no_overflow_out(self):
        self.__truthtable_based_test(1, use_overflow_lit=False)

    def test_for_bv_width_1_with_overflow_out(self):
        self.__truthtable_based_test(1, use_overflow_lit=True)

    def test_for_bv_width_2_no_overflow_out(self):
        self.__truthtable_based_test(2, use_overflow_lit=False)

    def test_for_bv_width_2_with_overflow_out(self):
        self.__truthtable_based_test(2, use_overflow_lit=True)

    def test_for_bv_width_3_no_overflow_out(self):
        self.__truthtable_based_test(3, use_overflow_lit=False)

    def test_for_bv_width_3_with_overflow_out(self):
        self.__truthtable_based_test(3, use_overflow_lit=True)

    def test_for_bv_width_4_no_overflow_out(self):
        self.__truthtable_based_test(4, use_overflow_lit=False)

    def test_for_bv_width_4_with_overflow_out(self):
        self.__truthtable_based_test(4, use_overflow_lit=True)

    def test_refuses_input_bv_with_length_mismatch(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 2)]

        encoder_under_test = self.get_bv_umul_encoder_under_test()
        # See assertion in __init__:
        # noinspection PyCallByClass
        # noinspection PyTypeChecker
        with unittest.TestCase.assertRaises(self, ValueError):
            encoder_under_test(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits)

    def test_refuses_output_bv_with_length_mismatch(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        output_lits = [lit_factory.create_literal() for _ in range(0, 2)]

        encoder_under_test = self.get_bv_umul_encoder_under_test()
        # See assertion in __init__:
        # noinspection PyCallByClass
        # noinspection PyTypeChecker
        with unittest.TestCase.assertRaises(self, ValueError):
            encoder_under_test(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits, output_lits)

    def test_uses_returns_output_literals(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        output_lits = [lit_factory.create_literal() for _ in range(0, 3)]

        encoder_under_test = self.get_bv_umul_encoder_under_test()
        result = encoder_under_test(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits, output_lits)
        assert result == output_lits

    def test_creates_output_literals_if_none_provided(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        all_inputs = lhs_input_lits + rhs_input_lits

        encoder_under_test = self.get_bv_umul_encoder_under_test()
        result = encoder_under_test(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits)
        assert not any(x in all_inputs for x in result)
        assert not any(-x in all_inputs for x in result)


class TestEncodeNaiveUnsignedBVMultiplierGate(unittest.TestCase, AbstractTestUnsignedBVMultiplierGate):
    def get_bv_umul_encoder_under_test(self):
        return bvg.encode_bv_naive_unsigned_mul_gate


class TestEncodeParallelUnsignedBVMultiplierGate(unittest.TestCase, AbstractTestUnsignedBVMultiplierGate):
    def get_bv_umul_encoder_under_test(self):
        return bvg.encode_bv_parallel_unsigned_mul_gate


class AbstractBinaryBitvectorPredicateTest(abc.ABC):
    def __init__(self):
        # This mixin may only be used with test cases, since it uses assertRaises:
        assert isinstance(self, unittest.TestCase)

    @abc.abstractmethod
    def get_bv_predicate_encoder_under_test(self):
        """
        Gets the bitvector gate encoder under test.

        :return: the bitvector gate encoder under test, a function having the same
                 signature as the encode_bv_unsigned_leq_gate function.
        """
        pass

    @abc.abstractmethod
    def get_predicate(self):
        """
        Gets the (integer-level) predicate to construct the gate's truth table.

        :return: A function f(lhs: int, rhs: int, width: int) -> bool, with lhs and rhs being the arguments of the
                 predicate, and width specifying how many consecutive bits (starting with the least significant bit)
                 of lhs rsp. rhs are relevant.
        """

    def __create_truth_table(self, width: int):
        predicate = self.get_predicate()
        truth_table = []
        for lhs, rhs in itertools.product(range(0, 2**width), range(0, 2**width)):
            p_value = 1 if predicate(lhs, rhs, width) else 0
            table_entry = ((int_to_bitvec(lhs, width), int_to_bitvec(rhs, width)), p_value)
            truth_table.append(table_entry)
        return truth_table

    def __truth_table_based_test(self, width):
        encoder_under_test = self.get_bv_predicate_encoder_under_test()
        truth_table = self.__create_truth_table(width)

        checker = TrivialSATSolver()
        clause_consumer = LoggingClauseConsumerDecorator(checker)
        lhs_lits = [checker.create_literal() for _ in range(0, width)]
        rhs_lits = [checker.create_literal() for _ in range(0, width)]

        output_lit = encoder_under_test(clause_consumer, checker, lhs_lits, rhs_lits)
        for table_entry in truth_table:
            input_setting, output_setting = table_entry
            lhs_setting, rhs_setting = input_setting

            probe_lhs = apply_truth_table_setting(lhs_lits, lhs_setting)
            probe_rhs = apply_truth_table_setting(rhs_lits, rhs_setting)
            probe_out = output_lit if output_setting == 1 else -output_lit

            # Check that the truth table setting satisfies the gate encoding:
            assumptions_pos = probe_lhs + probe_rhs + [probe_out]
            is_satisfiable_pos = checker.solve(assumptions_pos)
            assert is_satisfiable_pos, "Expected the gate encoding to be satisfied for truth table entry " + \
                                       str(table_entry) + ", but it is not.\n" + \
                                       "Encoding:\n" + clause_consumer.to_string() + \
                                       "\nAssumptions: " + str(assumptions_pos)

            # Check that the gate encodes a functional relation:
            assumptions_neg = probe_lhs + probe_rhs + [-probe_out]
            is_satisfiable_neg = checker.solve(assumptions_pos)
            assert is_satisfiable_neg, "The gate encoding does not embody a functional relation for inputs of truth" + \
                                       "table entry " + str(table_entry) + ".\n" + \
                                       "Encoding:\n" + clause_consumer.to_string() + \
                                       "\nAssumptions: " + str(assumptions_neg)

    def test_conforms_to_truth_table_for_bv_width_1(self):
        self.__truth_table_based_test(1)

    def test_conforms_to_truth_table_for_bv_width_2(self):
        self.__truth_table_based_test(2)

    def test_conforms_to_truth_table_for_bv_width_3(self):
        self.__truth_table_based_test(3)

    def test_conforms_to_truth_table_for_bv_width_4(self):
        self.__truth_table_based_test(4)

    # TODO: The following methods are similar to their counterparts in AbstractTestUnsignedBVMultiplierGate,
    #       maybe make these a mixin?
    def test_refuses_input_bv_with_length_mismatch(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 2)]

        encoder_under_test = self.get_bv_predicate_encoder_under_test()
        # See assertion in __init__:
        # noinspection PyCallByClass
        # noinspection PyTypeChecker
        with unittest.TestCase.assertRaises(self, ValueError):
            encoder_under_test(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits)

    def test_returns_output_literals(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        output_lit = lit_factory.create_literal()

        encoder_under_test = self.get_bv_predicate_encoder_under_test()
        result = encoder_under_test(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits, output_lit)
        assert result == output_lit

    def test_creates_output_literal_if_none_provided(self):
        lit_factory = TestLiteralFactory()
        clause_consumer = CollectingClauseConsumer()

        lhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        rhs_input_lits = [lit_factory.create_literal() for _ in range(0, 3)]
        all_inputs = lhs_input_lits + rhs_input_lits

        encoder_under_test = self.get_bv_predicate_encoder_under_test()
        result = encoder_under_test(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits)
        assert (result not in all_inputs) and (-result not in all_inputs)


class TestEncodeBVLessThanOrEqualCompGate(unittest.TestCase, AbstractBinaryBitvectorPredicateTest):
    def get_bv_predicate_encoder_under_test(self):
        return bvg.encode_bv_unsigned_leq_gate

    def get_predicate(self):
        return lambda l, r, width: (l & (2**width - 1)) <= (r & (2**width - 1))


class TestEncodeBVEqualityCompGate(unittest.TestCase, AbstractBinaryBitvectorPredicateTest):
    def get_bv_predicate_encoder_under_test(self):
        return bvg.encode_bv_eq_gate

    def get_predicate(self):
        return lambda l, r, width: (l & (2**width - 1)) == (r & (2**width - 1))
