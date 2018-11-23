from cscl.clause_consumer import ClauseConsumer


def encode_or_gate(clause_consumer: ClauseConsumer, input_lits, output_lit = None):
    """
    Creates an OR gate.

    :param clause_consumer: The clause consumer to which the clauses of the gate encoding shall be added.
    :param input_lits: The gate's input literals.
    :param output_lit: The gate's output literal. If output_lit is None, a positive literal with a
                       new variable will be used as the gate's output literal.
    :return: The encoded gate's output literal.
    """
    if output_lit is None:
        output_lit = clause_consumer.create_variable()

    fwd_clause = input_lits[:]
    fwd_clause.append(-output_lit)
    clause_consumer.consume_clause(fwd_clause)

    for lit in input_lits:
        clause_consumer.consume_clause([-lit, output_lit])

    return output_lit
