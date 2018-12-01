import abc
import unittest
import cscl.bitvector_gate_encoders as bvg
import cscl.interfaces as cscl_if
import cscl.basic_gate_encoders


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
