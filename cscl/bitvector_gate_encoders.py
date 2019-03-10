"""Bitvector constraint encoders

This module provides constraint encoders for gate-like constraints on bitvectors (ie. arrays of literals), such as
bitwise boolean functions and modulo arithmetic.
"""

from cscl.interfaces import CNFLiteralFactory, ClauseConsumer
import cscl.basic_gate_encoders as gates

# TODO: support Plaisted-Greenbaum encoders


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
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
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
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
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
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
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
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
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

    if len(rhs_input_lits) != width or (output_lits is not None and (len(output_lits) != width)):
        raise ValueError("Bitvector length mismatch")

    if width == 0:
        return []

    if output_lits is None:
        output_lits = [lit_factory.create_literal() for _ in range(0, width)]

    output_lits = [o if o is not None else lit_factory.create_literal() for o in output_lits]

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


def encode_bv_ripple_carry_sub_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                                    lhs_input_lits, rhs_input_lits, output_lits=None):
    """
    Encodes a subtraction-gate constraint using a ripple carry adder.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals, in LSB-to-MSB order.
    :param rhs_input_lits: The list of right-hand-side input literals, in LSB-to-MSB order. The length of
                           rhs_input_lits must be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :return: The list of gate output literals in LSB-to-MSB order, containing len(lhs_input_literals) literals.
             The i'th literal of output_lits signifies the i'th bit of the difference.
    """
    flipped_rhs = [-x for x in rhs_input_lits]
    constantly_1 = lit_factory.create_literal()
    clause_consumer.consume_clause([constantly_1])
    return encode_bv_ripple_carry_adder_gate(clause_consumer, lit_factory,
                                             lhs_input_lits=lhs_input_lits,
                                             rhs_input_lits=flipped_rhs,
                                             carry_in_lit=constantly_1,
                                             output_lits=output_lits)


def encode_bv_parallel_mul_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                                lhs_input_lits, rhs_input_lits, output_lits=None, overflow_lit=None):
    """
    Encodes a bitvector multiplication-gate constraint, using parallel addition of partial products.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals, in LSB-to-MSB order.
    :param rhs_input_lits: The list of right-hand-side input literals, in LSB-to-MSB order. The length of
                           rhs_input_lits must be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :param overflow_lit: Iff overflow_lit is not None, gates are added forcing the value of overflow_lit to be true
                         iff the product of lhs_input_lits and rhs_input_lits cannot be expressed using
                         len(output_lits) bits.
    :return: The list of gate output literals in LSB-to-MSB order, containing len(lhs_input_literals) literals.
             The i'th literal of output_lits signifies the i'th bit of the product.
    """

    width = len(lhs_input_lits)
    if len(rhs_input_lits) != width or (output_lits is not None and len(output_lits) != width):
        raise ValueError("Mismatching bitvector sizes")
    if width == 0:
        return []

    # Implementation:
    #
    # 1. Encode W=width partial products P(0), ..., P(W-1) with P(i) = rhs_input_lits * [W times lhs_input_lits[i]]
    #    (0 <= i < W)
    # 2. Encode partial sums S(0), ..., S(W-1) with S(0) = P(0)[0:W] and for 1 <= i < W,
    #    S(i) = S(i-1)[1:] + P(i)[0:W-i]
    # 3. For 0 <= i < W, S(i)[0] is the i'th output bit. If any overflow condition occurred in step 2 or any
    #    partial sum bit not used in step 2 is set to true, the multiplication has an overflow condition.
    #
    # Example for W=4:
    #
    #                               P(0)[3] P(0)[2] P(0)[1] P(0)[0]
    #  +                 P(1)[3]    P(1)[2] P(1)[1] P(1)[0]
    #  +         P(2)[3] P(2)[2]    P(2)[1] P(2)[0]
    #  + P(3)[3] P(3)[2] P(3)[1]    P(3)[0]
    #  -----------------------------------------------------------
    #      (can be discarded)     | out[3]  out[2]  out[1]  out[0]  = Output
    #
    # Partial sums for output computation:
    #
    # S(0)[0:W]   = P(0)[0:W]
    # S(1)[0:W-1] = S(0)[1:W] + P(1)[0:W-1]
    # S(2)[0:W-2] = S(1)[1:W-1] + P(2)[0:W-2]
    # S(3)[0:W-3] = S(2)[1:W-2] + P(3)[0:W-3]

    def __create_fresh_lits(n):
        return [lit_factory.create_literal() for _ in range(0, n)]

    if output_lits is None:
        output_lits = __create_fresh_lits(width)
    else:
        output_lits = list(map(lambda l: lit_factory.create_literal() if l is None else l, output_lits))

    # Directly include the lowermost output bit in the first partial product:
    partial_products = [[output_lits[0]] + __create_fresh_lits(width-1)]
    lowest_lhs = lhs_input_lits[0]
    encode_bv_and_gate(clause_consumer, lit_factory, rhs_input_lits, [lowest_lhs] * width, partial_products[0])

    # Don't compute partial sum bits which are discarded anyway:
    if overflow_lit is not None:
        partial_products += [encode_bv_and_gate(clause_consumer, lit_factory, rhs_input_lits, [l] * width)
                             for l in lhs_input_lits[1:]]
    else:
        partial_products += [encode_bv_and_gate(clause_consumer, lit_factory,
                                                rhs_input_lits[0:width-i], [lhs_input_lits[i]] * (width-i))
                             for i in range(1, width)]

    # Compute the partial sums, directly forcing the output literal setting. partial_sums[i] corresponds to S(i+1)
    partial_sums = [([output_lits[i]] + __create_fresh_lits(width-i-1)) for i in range(1, width)]
    # partial_sum_carries[i] is the carry bit for the computation of partial_sums[i]:
    partial_sum_carries = __create_fresh_lits(width-1) if overflow_lit is not None else [None]*(width-1)

    current_partial_sum = partial_products[0][1:width]
    for i in range(1, width):
        current_partial_product = partial_products[i][0:width-i]
        partial_sum_accu = partial_sums[i-1]
        assert len(current_partial_sum) == width - i
        encode_bv_ripple_carry_adder_gate(clause_consumer, lit_factory,
                                          lhs_input_lits=current_partial_sum,
                                          rhs_input_lits=current_partial_product,
                                          output_lits=partial_sum_accu,
                                          carry_out_lit=partial_sum_carries[i-1])
        current_partial_sum = partial_sum_accu[1:]

    # Check if an overflow occurred:
    if overflow_lit is not None:
        overflow_indicators = partial_sum_carries[:]
        for i in range(1, width):
            overflow_indicators += partial_products[i][width-i:width]
        gates.encode_or_gate(clause_consumer, lit_factory, overflow_indicators, overflow_lit)

    return output_lits


def encode_bv_ule_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                       lhs_input_lits, rhs_input_lits, output_lit=None):
    """
    Encodes a less-than-or-equal-to-comparison gate for bitvectors representing unsigned integers.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals, in LSB-to-MSB order.
    :param rhs_input_lits: The list of right-hand-side input literals, in LSB-to-MSB order. The length of
                           rhs_input_lits must be the same as the length of lhs_input_lits.
    :param output_lit: The gate's output literal. If output_lit is None, a positive literal with a
                       new variable will be used as the gate's output literal.
    :return: The encoded gate's output literal.
    """

    if len(lhs_input_lits) != len(rhs_input_lits):
        raise ValueError("Sizes of lhs_input_lits and rhs_input_lits illegally mismatching")

    if output_lit is None:
        output_lit = lit_factory.create_literal()

    # Base cases:
    if len(lhs_input_lits) == 0:
        clause_consumer.consume_clause([output_lit])
        return output_lit

    if len(lhs_input_lits) == 1:
        gates.encode_and_gate(clause_consumer, lit_factory, [lhs_input_lits[0], -rhs_input_lits[0]], -output_lit)
        return output_lit

    # Recursion: lhs <= rhs <-> (lhs[0] < rhs[0] or (lhs[0] == rhs[0] and lhs[1:] <= rhs[1:])
    width = len(lhs_input_lits)
    rest_leq = encode_bv_ule_gate(clause_consumer, lit_factory,
                                  lhs_input_lits[:width-1], rhs_input_lits[:width-1])

    lhs_msb, rhs_msb = lhs_input_lits[width-1], rhs_input_lits[width-1]
    msb_is_lt = gates.encode_and_gate(clause_consumer, lit_factory, [-lhs_msb, rhs_msb])
    msb_is_eq = -gates.encode_binary_xor_gate(clause_consumer, lit_factory, [lhs_msb, rhs_msb])

    leq_if_first_is_eq = gates.encode_and_gate(clause_consumer, lit_factory, [msb_is_eq, rest_leq])
    return gates.encode_or_gate(clause_consumer, lit_factory, [msb_is_lt, leq_if_first_is_eq], output_lit)


def encode_bv_sle_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                       lhs_input_lits, rhs_input_lits, output_lit=None):
    """
    Encodes a less-than-or-equal-to-comparison gate for bitvectors representing signed integers
    in two's complement encoding.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals, in LSB-to-MSB order.
    :param rhs_input_lits: The list of right-hand-side input literals, in LSB-to-MSB order. The length of
                           rhs_input_lits must be the same as the length of lhs_input_lits.
    :param output_lit: The gate's output literal. If output_lit is None, a positive literal with a
                       new variable will be used as the gate's output literal.
    :return: The encoded gate's output literal.
    """

    if len(lhs_input_lits) != len(rhs_input_lits):
        raise ValueError("Sizes of lhs_input_lits and rhs_input_lits illegally mismatching")

    if output_lit is None:
        output_lit = lit_factory.create_literal()

    if len(lhs_input_lits) == 0:
        clause_consumer.consume_clause([output_lit])
        return output_lit

    if len(lhs_input_lits) == 1:
        return gates.encode_or_gate(clause_consumer, lit_factory, [lhs_input_lits[0], -rhs_input_lits[0]], output_lit)

    width = len(lhs_input_lits)
    lhs_msb = lhs_input_lits[width-1]
    rhs_msb = rhs_input_lits[width-1]
    rest_leq = encode_bv_ule_gate(clause_consumer, lit_factory,
                                  lhs_input_lits=lhs_input_lits[:width-1],
                                  rhs_input_lits=rhs_input_lits[:width-1])
    msb_eq = -gates.encode_binary_xor_gate(clause_consumer, lit_factory, input_lits=[lhs_msb, rhs_msb])
    same_sign_and_leq = gates.encode_and_gate(clause_consumer, lit_factory, input_lits=[msb_eq, rest_leq])
    lhs_neg_and_rhs_pos = gates.encode_and_gate(clause_consumer, lit_factory, input_lits=[lhs_msb, -rhs_msb])
    return gates.encode_or_gate(clause_consumer, lit_factory,
                                input_lits=[lhs_neg_and_rhs_pos, same_sign_and_leq],
                                output_lit=output_lit)


def encode_bv_eq_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                      lhs_input_lits, rhs_input_lits, output_lit=None):
    """
    Encodes a equality-comparison gate for bitvectors.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals, in LSB-to-MSB order.
    :param rhs_input_lits: The list of right-hand-side input literals, in LSB-to-MSB order. The length of
                           rhs_input_lits must be the same as the length of lhs_input_lits.
    :param output_lit: The gate's output literal. If output_lit is None, a positive literal with a
                       new variable will be used as the gate's output literal.
    :return: The encoded gate's output literal.
    """

    if len(lhs_input_lits) != len(rhs_input_lits):
        raise ValueError("Sizes of lhs_input_lits and rhs_input_lits illegally mismatching")

    if output_lit is None:
        output_lit = lit_factory.create_literal()

    differences = encode_bv_xor_gate(clause_consumer, lit_factory, lhs_input_lits, rhs_input_lits)
    gates.encode_or_gate(clause_consumer, lit_factory, differences, -output_lit)
    return output_lit


def encode_bv_mux_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                       lhs_input_lits, rhs_input_lits, select_lhs_lit=None, output_lits=None):
    """
    Encodes a bitvector multiplexer gate. The gate's output literals are forced to equal lhs_input_lits if
    select_lhs_lit has the value True. If select_lhs_lit has the value False, the output literals are forced
    to equal rhs_input_lits.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals.
    :param rhs_input_lits: The list of right-hand-side input literals.
    :param select_lhs_lit: The selector literal controlling whether the output literals are tied to lhs_input_lits
                           or to rhs_input_lits. If select_lhs_lit is None, this gate represents the arbitrary
                           choice of an element in {lhs_input_lits, rhs_input_lits}.
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :return: The list of gate output literals in LSB-to-MSB order, containing len(lhs_input_literals) literals.
             The i'th literal of output_lits represents the value of the expression
             `if selector_lit then lhs_input_lits[i] else lhs_input_lits[i]`.
    """
    select_lhs_lit = lit_factory.create_literal() if select_lhs_lit is None else select_lhs_lit

    lhs_selection = encode_bv_and_gate(clause_consumer=clause_consumer,
                                       lit_factory=lit_factory,
                                       lhs_input_lits=lhs_input_lits,
                                       rhs_input_lits=[select_lhs_lit]*len(lhs_input_lits))
    rhs_selection = encode_bv_and_gate(clause_consumer=clause_consumer,
                                       lit_factory=lit_factory,
                                       lhs_input_lits=rhs_input_lits,
                                       rhs_input_lits=[-select_lhs_lit]*len(rhs_input_lits))
    return encode_bv_or_gate(clause_consumer=clause_consumer,
                             lit_factory=lit_factory,
                             lhs_input_lits=lhs_selection,
                             rhs_input_lits=rhs_selection,
                             output_lits=output_lits)


def encode_staggered_or_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                             input_lits, output_lits=None):
    """
    Given a bitvector `[x_1, x_2, ..., x_n]`, returns a bitvector `[y_1, y_2, ..., y_n]` constrained
    such that for all `1 <= i <= n`: `y_i <-> (x_i or x_{i+1} or ... or x_n)`

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param input_lits: The list of literals [x_1, x_2, ..., x_n]
    :param output_lits: The list of output literals [y_1, y_2, ..., y_n], or None. If output_lits is none,
                        len(lhs_input_lits) gate output literals, each having a new variable, are created. Otherwise,
                        output_lits must be a list with length len(lhs_input_lits), with each contained element either
                        being a literal or None. If the i'th entry of output_lits is None, a literal with a new variable
                        is created as the i'th output literal.
    :return: literals `[y_1, y_2, ..., y_n]` constrained as described above.
    """
    width = len(input_lits)
    if output_lits is not None and len(output_lits) != width:
        raise ValueError("Mismatching bitvector sizes")
    if width == 0:
        return []

    if output_lits is None:
        result = [lit_factory.create_literal() for _ in range(0, width)]
    else:
        result = [out_lit if out_lit is not None else lit_factory.create_literal() for out_lit in output_lits]

    gates.encode_or_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                         input_lits=[input_lits[-1]], output_lit=result[-1])

    for idx in reversed(range(0, width-1)):
        gates.encode_or_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                             input_lits=[input_lits[idx], result[idx+1]], output_lit=result[idx])

    return result


def encode_bv_long_udiv_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                             lhs_input_lits, rhs_input_lits, output_lits=None, remainder_output_lits=None):
    """
    Encodes a bitvector division gate using the "long" integer division algorithm (see e.g.
    https://en.wikipedia.org/wiki/Division_algorithm#Integer_division_(unsigned)_with_remainder), for unsigned integers.
    This division encoding is one of the simplest and likely very inefficient.

    This divider sets x/0 = 0 for all possible inputs x.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals, in LSB-to-MSB order.
    :param rhs_input_lits: The list of right-hand-side input literals, in LSB-to-MSB order. The length of
                           rhs_input_lits must be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :param remainder_output_lits: The list of remainder literals in LSB-to-MSB order, or None. If remainder_lits
                                  is not None, it must contain exactly as many literals as `lhs_input_lits`, and
                                  it will be constrained to represent the remainder of the division.
    :return: The list of gate output literals in LSB-to-MSB order, containing len(lhs_input_literals) literals.
             The i'th literal of output_lits signifies the i'th bit of the quotient.
    """
    width = len(lhs_input_lits)
    if len(rhs_input_lits) != width or (output_lits is not None and len(output_lits) != width)\
            or (remainder_output_lits is not None and len(remainder_output_lits) != width):
        raise ValueError("Mismatching bitvector sizes")
    if width == 0:
        return []

    def __create_fresh_lits(n):
        return [lit_factory.create_literal() for _ in range(0, n)]

    constantly_false = lit_factory.create_literal()
    clause_consumer.consume_clause([-constantly_false])

    divisor_any_higher_bits_nonzero = encode_staggered_or_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                                                               input_lits=rhs_input_lits)

    quotient = __create_fresh_lits(width)

    remainder = list()
    for step_idx in reversed(range(0, width)):
        remainder = [lhs_input_lits[step_idx]] + remainder

        # storing the comparison remainder>=divisior in quotient[step_idx]
        if len(remainder) == len(rhs_input_lits):
            # divisor has exaxtly as many bits as remainder: perform a direct comparison
            encode_bv_ule_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                               lhs_input_lits=rhs_input_lits, rhs_input_lits=remainder, output_lit=quotient[step_idx])
        else:
            # divisor has more bits than the remainder. Save some variable introductions by comparing the divisor's
            # extra bits separately:
            lower_bit_comparison = encode_bv_ule_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                                                      lhs_input_lits=rhs_input_lits[0:len(remainder)],
                                                      rhs_input_lits=remainder)
            higher_bits_comparison = divisor_any_higher_bits_nonzero[len(remainder)]
            gates.encode_and_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                                  input_lits=[lower_bit_comparison, -higher_bits_comparison],
                                  output_lit=quotient[step_idx])

        remainder_minus_divisor = encode_bv_ripple_carry_sub_gate(clause_consumer=clause_consumer,
                                                                  lit_factory=lit_factory,
                                                                  lhs_input_lits=remainder,
                                                                  rhs_input_lits=rhs_input_lits[0:len(remainder)])

        # If remainder>=divisior, then remainder := remainder - divisor
        remainder = encode_bv_mux_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                                       lhs_input_lits=remainder_minus_divisor, rhs_input_lits=remainder,
                                       select_lhs_lit=quotient[step_idx])

    rhs_is_zero = -gates.encode_or_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                                        input_lits=rhs_input_lits)

    # If the user specified remainder literals, use them when appropriate
    if remainder_output_lits is not None:
        encode_bv_and_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                           lhs_input_lits=[-rhs_is_zero] * width, rhs_input_lits=remainder,
                           output_lits=remainder_output_lits)

    # Tie the gate output to False if rhs is 0:
    return encode_bv_and_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                              lhs_input_lits=[-rhs_is_zero]*width, rhs_input_lits=quotient,
                              output_lits=output_lits)


def encode_bv_long_urem_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                             lhs_input_lits, rhs_input_lits, output_lits=None):
    """
    Encodes a bitvector division remainder gate using the "long" integer division algorithm (see e.g.
    https://en.wikipedia.org/wiki/Division_algorithm#Integer_division_(unsigned)_with_remainder), for unsigned integers.
    This division encoding is one of the simplest and likely very inefficient.

    This divider sets x/0 = 0 for all possible inputs x.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param lit_factory: The CNF literal factory to be used for creating literals with new variables.
    :param lhs_input_lits: The list of left-hand-side input literals, in LSB-to-MSB order.
    :param rhs_input_lits: The list of right-hand-side input literals, in LSB-to-MSB order. The length of
                           rhs_input_lits must be the same as the length of lhs_input_lits.
    :param output_lits: The list of output literals, or None. If output_lits is none, len(lhs_input_lits) gate output
                        literals, each having a new variable, are created. Otherwise, output_lits must be a list
                        with length len(lhs_input_lits), with each contained element either being a literal
                        or None. If the i'th entry of output_lits is None, a literal with a new variable is
                        created as the i'th output literal.
    :return: The list of gate output literals in LSB-to-MSB order, containing len(lhs_input_literals) literals.
             The i'th literal of output_lits signifies the i'th bit of the remainder.
    """

    if output_lits is None:
        output_lits = [lit_factory.create_literal() for _ in lhs_input_lits]
    else:
        output_lits = [lit_factory.create_literal() if x is None else x for x in output_lits]

    encode_bv_long_udiv_gate(clause_consumer=clause_consumer, lit_factory=lit_factory,
                             lhs_input_lits=lhs_input_lits, rhs_input_lits=rhs_input_lits,
                             remainder_output_lits=output_lits)

    return output_lits
