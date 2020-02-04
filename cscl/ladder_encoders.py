"""Encoders for the ladder constraint"""

from cscl.interfaces import ClauseConsumer, CNFLiteralFactory


def encode_ladder_constraint_on_literals(clause_consumer: ClauseConsumer, literals):
    """
    Encodes the ladder constraint on the given literals.

    If literals[i] is assigned False, this constraint forces all literals literals[j] with
    j > i to be assigned False, too.

    :param clause_consumer: The clause consumer receiving the constraint clauses.
    :param literals:        The iterable of literals to be constrained.
    """
    prev_lit = None
    for lit in literals:
        if prev_lit is not None:
            clause_consumer.consume_clause((-lit, prev_lit))
        prev_lit = lit


def encode_ladder_constraint(clause_consumer: ClauseConsumer, lit_factory: CNFLiteralFactory, num_vars):
    """
    Creates a ladder constraint of the given size

    Let literals be the resulting sequence of literals. If literals[i] is assigned False, this
    constraint forces all literals literals[j] with j > i to be assigned False, too.

    :param clause_consumer: The clause consumer receiving the constraint clauses.
    :param lit_factory:     A literal factory.
    :param num_vars:        The desired non-negative size of the constraint.
    :return: A sequence `literals` consisting of `num_vars` literals constrained as described above.
    """
    if num_vars < 0:
        raise ValueError('num_vars must not be negative')

    ladder_lits = tuple(lit_factory.create_literal() for _ in range(0, num_vars))
    encode_ladder_constraint_on_literals(clause_consumer, ladder_lits)
    return ladder_lits
