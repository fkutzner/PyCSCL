import math
from cscl.interfaces import ClauseConsumer, CNFLiteralFactory, SatSolver
import cscl.bitvector_gate_encoders as bv


def create_uint_bitvec_constant(clause_consumer: ClauseConsumer,
                                lit_factory: CNFLiteralFactory,
                                constant: int, size: int):
    """
    Encodes an unsigned integer constant as a bitvector.

    :param clause_consumer: The clause consumer to receive the constraining clauses.
    :param lit_factory: The literal factory with which to create the bitvector literals.
    :param constant: An arbitrary non-negative integer.
    :param size: The size of the bitvector to be constructed; an arbitrary non-negative integer.
    :return: A bitvector of size bits, with the bit at index X being constrained to the value of
             the X'th bit of constant.
    """
    if constant < 0 or size < 0:
        raise ValueError("Illegal constant or size argument")

    result = [lit_factory.create_literal() for _ in range(0, size)]
    for i in range(0, size):
        if (constant & (1 << i)) != 0:
            clause_consumer.consume_clause([result[i]])
        else:
            clause_consumer.consume_clause([-result[i]])
    return result


def bitvec_to_uint(bitvec, solver: SatSolver):
    """
    Reads out the value of the given bitvector as an unsigned integer.

    :param bitvec: A vector [l0, ..., lN] of literals.
    :param solver: A SAT solver that currently has a model (i.e. a problem-satisfying variable assignment).
    :return: The unsigned integer representation of bitvec's value within the current model, with the value of lX
             being the X'th bit of the result.
    """
    result = 0
    for i in range(0, len(bitvec)):
        bit = solver.get_assignment(bitvec[i])
        if bit:
            result |= (1 << i)
    return result


def factorize(x: int, solver: SatSolver):
    """
    Decomposes the given integer into two factors.

    :param x: An integer that is greater than 1.
    :param solver: A SAT solver.
    :return: If x is not a prime number, a tuple (y, z) with y != 1 and z != 1 and x=y*z is returned.
             If x is a prime number, None is returned.
    """
    if x < 2:
        raise ValueError("x must not be smaller than 2")

    n_bits = math.ceil(math.log2(x))+1

    # Fix the multiplication output:
    x_constant = create_uint_bitvec_constant(solver, solver, x, n_bits)

    # Create input literals:
    lhs = [solver.create_literal() for _ in range(0, n_bits)]
    rhs = [solver.create_literal() for _ in range(0, n_bits)]

    # Create constraints that neither lhs nor lhs may represent the numbers 0 or 1:
    solver.consume_clause(lhs[1:])
    solver.consume_clause(rhs[1:])

    # Encode a multiplier whose overflow output is required to be false in all solutions:
    pin_to_false = solver.create_literal()
    solver.consume_clause([-pin_to_false])
    bv.encode_bv_parallel_unsigned_mul_gate(clause_consumer=solver,
                                            lit_factory=solver,
                                            lhs_input_lits=lhs,
                                            rhs_input_lits=rhs,
                                            output_lits=x_constant,
                                            overflow_lit=pin_to_false)

    solution_found = solver.solve([])
    if not solution_found:
        return None
    else:
        return bitvec_to_uint(lhs, solver), bitvec_to_uint(rhs, solver)
