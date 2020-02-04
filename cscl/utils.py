from cscl.interfaces import ClauseConsumer
import itertools


def ensure_tuple_or_list(x):
    """
    :param x: An iterable object
    :return: x if x is a list or a tuple; tuple(x) otherwise
    """
    if isinstance(x, tuple) or isinstance(x, list):
        return x
    else:
        return tuple(x)


def with_activation_literals(clause_consumer: ClauseConsumer, activation_literals):
    """
    Decorates a ClauseConsumer such that it adds the given literals to each clause.

    :param clause_consumer:     A clause consumer.
    :param activation_literals: An iterable of literals.
    :return: A clause consumer that forwards clauses  to `clause_consumer`, adding the
             literals in `activation_literals` to each clause.
    """
    class CCWithActivationLiterals(ClauseConsumer):
        def __init__(self, decorated_clause_consumer, activation_literals):
            self._clause_consumer = decorated_clause_consumer
            self._activation_literals = tuple(activation_literals)

        def consume_clause(self, clause):
            clause = itertools.chain.from_iterable((self._activation_literals, clause))
            self._clause_consumer.consume_clause(sorted(set(clause)))

    return CCWithActivationLiterals(clause_consumer, activation_literals)
