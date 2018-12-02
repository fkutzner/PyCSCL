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

    if len(rhs_input_lits) != width or (output_lits is not None and (len(output_lits) != width)):
        raise ValueError("Bitvector length mismatch")

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


def encode_bv_naive_unsigned_mul_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                                      lhs_input_lits, rhs_input_lits, output_lits=None, overflow_lit=None):
    """
    (Naively) encodes an unsigned bitector multiplication constraint, with truncation on overflow.

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
    :param overflow_lit: Iff overflow_lit is not None, gates are added forcing the value of overflow_lit to be true
                         iff the product of lhs_input_lits and rhs_input_lits cannot be expressed using
                         len(output_lits) bits.
    :return: The list of gate output literals in LSB-to-MSB order, containing len(lhs_input_literals) literals.
             The i'th literal of output_lits signifies the i'th bit of the product.
    """
    width = len(lhs_input_lits)

    if width == 0:
        return []

    if width == 1:
        if overflow_lit is not None:
            clause_consumer.consume_clause([-overflow_lit])
        output_lit = output_lits[0] if output_lits is not None else None
        return [gates.encode_and_gate(clause_consumer, lit_factory, lhs_input_lits + rhs_input_lits, output_lit)]

    if output_lits is None:
        output_lits = [lit_factory.create_literal() for _ in range(0, width)]

    # For each lhs input lit l, create a product rhs_input_lits * l. These will be shifted and summed up.
    partial_products = [encode_bv_and_gate(clause_consumer, lit_factory, rhs_input_lits, [l] * width)
                        for l in lhs_input_lits]

    constantly_0 = lit_factory.create_literal()
    clause_consumer.consume_clause([-constantly_0])

    # Summation of increasingly shifted partial products:
    # Potential optimization: use smaller adders to get rid of the constantly_0 literal
    # Potential optimization: compute overflow_lit more efficiently
    intermediate_sum_lits = partial_products[0] + [constantly_0]
    for i in range(1, width-1):
        summand_lits = [constantly_0] * i + partial_products[i]
        carry_lit = lit_factory.create_literal()
        assert len(summand_lits) == len(intermediate_sum_lits)
        intermediate_sum_lits = encode_bv_ripple_carry_adder_gate(clause_consumer, lit_factory,
                                                                  summand_lits, intermediate_sum_lits,
                                                                  carry_out_lit=carry_lit)
        intermediate_sum_lits += [carry_lit]

    assert len(intermediate_sum_lits) == (2*width)-1, "Computed " + str(len(intermediate_sum_lits))\
                                                      + " intermediate sum bits instead of " + str((2*width)-1)

    # Add the final partial product. The output of this final operation contains the multiplier's output
    # literals, which may be specified by the user, which is why this is performed after the summation loop:
    final_summand_lits = [constantly_0] * (width-1) + partial_products[width-1]
    final_carry_lit = lit_factory.create_literal()
    overflow_lits = [lit_factory.create_literal() for _ in range(0, width-1)]

    encode_bv_ripple_carry_adder_gate(clause_consumer, lit_factory,
                                      final_summand_lits, intermediate_sum_lits,
                                      output_lits=(output_lits + overflow_lits), carry_out_lit=final_carry_lit)

    if overflow_lit:
        gates.encode_or_gate(clause_consumer, lit_factory, overflow_lits + [final_carry_lit], overflow_lit)

    return output_lits


def encode_bv_parallel_unsigned_mul_gate(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory,
                                         lhs_input_lits, rhs_input_lits, output_lits=None, overflow_lit=None):
    """
    Encodes an unsigned bitector multiplication constraint, using parallel addition of partial products.

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
