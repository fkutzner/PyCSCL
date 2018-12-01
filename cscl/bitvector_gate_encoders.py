from cscl.interfaces import CNFLiteralFactory, ClauseConsumer
import cscl.basic_gate_encoders as gates


def encode_gate_vector(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory, basic_gate_encoder_fn,
                       lhs_input_lits, rhs_input_lits, output_lits=None):
    """
    Encodes a vector of binary gates.

    For input literals lhs_input_lits = [l1, ..., lN], rhs_input_lits = [r1, ..., rN],
    output_lits = [o1, ..., oN], this function encodes N gates o1 <-> g(l1, r1),
    o2 <-> g(l2, r2), ..., oN <-> g(lN, rN), using the basic gate encoder function
    basic_gate_encoder_fn, which must be a binary gate encoder of the cscl.basic_gate_encoders
    package.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param basic_gate_encoder_fn: a binary gate encoder function of the cscl.basic_gate_encoders package.
    :param lhs_input_lits: The list of left-hand-side input literals.
    :param rhs_input_lits: The list of right-hand-side input literals. The length of rhs_input_lits must
                           be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, N gate output literals,
                        each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :return: The list of gate output literals, containing len(lhs_input_lits) literals, with
             output_lit[i] <-> g(lhs_input_lits[i], rhs_input_lits[i]) for all i in
             range(0, len(lhs_input_lits)).
    """
    if len(lhs_input_lits) != len(rhs_input_lits):
        raise ValueError("lhs_input_lits and rhs_input_lits must have the same size")

    if output_lits is None:
        output_lits = [None] * len(lhs_input_lits)
    elif len(lhs_input_lits) != len(output_lits):
        raise ValueError("If output_lits is not None, it must have the same size as lhs_input_lits")

    return [basic_gate_encoder_fn(clause_consumer, lit_factory, (lhs, rhs), output_lit)
            for lhs, rhs, output_lit in zip(lhs_input_lits, rhs_input_lits, output_lits)]


def encode_bv_and_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                       lhs_input_lits, rhs_input_lits, output_lits=None):
    """
    Encodes a bitvector AND gate.


    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals.
    :param rhs_input_lits: The list of right-hand-side input literals. The length of rhs_input_lits must
                           be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, N gate output literals,
                        each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :return: The list of gate output literals, containing len(lhs_input_lits) literals, with
             output_lit[i] <-> (lhs_input_lits[i] AND rhs_input_lits[i]) for all i in
             range(0, len(lhs_input_lits)).
    """
    return encode_gate_vector(clause_consumer, lit_factory,
                              gates.encode_and_gate,
                              lhs_input_lits, rhs_input_lits, output_lits)


def encode_bv_or_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                      lhs_input_lits, rhs_input_lits, output_lits=None):
    """
    Encodes a bitvector OR gate.


    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals.
    :param rhs_input_lits: The list of right-hand-side input literals. The length of rhs_input_lits must
                           be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, N gate output literals,
                        each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :return: The list of gate output literals, containing len(lhs_input_lits) literals, with
             output_lit[i] <-> (lhs_input_lits[i] OR rhs_input_lits[i]) for all i in
             range(0, len(lhs_input_lits)).
    """

    return encode_gate_vector(clause_consumer, lit_factory,
                              gates.encode_or_gate,
                              lhs_input_lits, rhs_input_lits, output_lits)


def encode_bv_xor_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                       lhs_input_lits, rhs_input_lits, output_lits=None):
    """
    Encodes a bitvector XOR gate.


    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals.
    :param rhs_input_lits: The list of right-hand-side input literals. The length of rhs_input_lits must
                           be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, N gate output literals,
                        each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :return: The list of gate output literals, containing len(lhs_input_lits) literals, with
             output_lit[i] <-> (lhs_input_lits[i] XOR rhs_input_lits[i]) for all i in
             range(0, len(lhs_input_lits)).
    """

    return encode_gate_vector(clause_consumer, lit_factory,
                              gates.encode_binary_xor_gate,
                              lhs_input_lits, rhs_input_lits, output_lits)


def encode_bv_ripple_carry_adder_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                                      lhs_input_lits, rhs_input_lits, carry_in_lit=None,
                                      output_lits=None, carry_out_lit=None):
    """
    Encodes a ripple-carry-adder-gate constraint.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals, in LSB-to-MSB order.
    :param rhs_input_lits: The list of right-hand-side input literals, in LSB-to-MSB order. The length of
                           rhs_input_lits must be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, N gate output literals,
                        each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :param carry_in_lit: None or a literal. If carry_in_lit is a literal, carry_in_lit is used as the adder's
                         carry input value. Otherwise, a fixed carry input value of 0 is used.
    :param carry_out_lit: None or a literal. If carry_out_lit is a literal, a gate is created constraining carry_out_lit
                          to the adder's carry output value.
    :return: The list of gate output literals in LSB-to-MSB order, containing len(lhs_input_literals) literals.
             The i'th literal of output_lits signifies the i'th bit of the sum.
    """
    width = len(lhs_input_lits)

    if width == 0:
        return []

    if output_lits is None:
        output_lits = [lit_factory.create_literal() for _ in range(0, width)]

    # Carries: carries[i] is the carry-out of full-adder no. i for i in range(0,width)
    # If carries[i] is None, the carry output is irrelevant and does not need to be encoded
    carries = [lit_factory.create_literal() for _ in range(0, width-1)]
    carries.append(carry_out_lit)

    # Encode the first adder. If there is a carry_in_lit, use a full adder, otherwise, use
    # a half adder:
    if carry_in_lit is not None:
        adder_input = (lhs_input_lits[0], rhs_input_lits[0], carry_in_lit)
        gates.encode_full_adder_sum_gate(clause_consumer, lit_factory, adder_input, output_lits[0])
        if carries[0] is not None:
            gates.encode_full_adder_carry_gate(clause_consumer, lit_factory, adder_input, carries[0])
    else:
        adder_input = (lhs_input_lits[0], rhs_input_lits[0])
        gates.encode_binary_xor_gate(clause_consumer, lit_factory, adder_input, output_lits[0])
        if carries[0] is not None:
            gates.encode_and_gate(clause_consumer, lit_factory, adder_input, carries[0])

    # Encode the rest of the adder:
    for i in range(1, width):
        adder_input = (lhs_input_lits[i], rhs_input_lits[i], carries[i-1])
        gates.encode_full_adder_sum_gate(clause_consumer, lit_factory, adder_input, output_lits[i])
        if carries[i] is not None:
            gates.encode_full_adder_carry_gate(clause_consumer, lit_factory, adder_input, carries[i])

    return output_lits
