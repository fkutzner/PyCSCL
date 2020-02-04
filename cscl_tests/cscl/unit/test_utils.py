import unittest
from cscl.utils import with_activation_literals
from cscl.interfaces import ClauseConsumer


class TestClauseConsumer(ClauseConsumer):
    def __init__(self):
        self._clauses = list()

    def consume_clause(self, clause):
        self._clauses.append(list(sorted(clause)))

    def get_clauses(self):
        return list(self._clauses)


class TestActivationLiteralsDecorator(unittest.TestCase):
    def test_decorate_with_range_of_lits(self):
        decoree = TestClauseConsumer()
        decorated = with_activation_literals(decoree, range(10, 13))
        decorated.consume_clause((1, -2, 3))
        self.assertEqual(decoree.get_clauses(), [[-2, 1, 3, 10, 11, 12]])
        decorated.consume_clause((5, 9))
        self.assertEqual(decoree.get_clauses(), [[-2, 1, 3, 10, 11, 12], [5, 9, 10, 11, 12]])

    def test_duplicates_are_removed(self):
        decoree = TestClauseConsumer()
        decorated = with_activation_literals(decoree, [1, 2])
        decorated.consume_clause((2, -1, 5))
        self.assertEqual(decoree.get_clauses(), [[-1, 1, 2, 5]])
