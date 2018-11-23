import abc


class ClauseConsumer(abc.ABC):
    """An interface for clause consumers, e.g. SAT solvers or CNF formula builders"""

    @abc.abstractmethod
    def consume_clause(self, clause):
        """
        Consumes a clause.

        :param clause: The clause to be consumed, a list of objects which have been created using create_variable().
        :return: None
        """
        pass

    @abc.abstractmethod
    def create_variable(self):
        """
        Creates a new variable that can be used in clauses passed to consume_clause.

        The type of the returned object is deliberately unspecified.

        :return: A variable that has not previously been returned by this method.
        """
        pass
