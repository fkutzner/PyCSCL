import abc


class CNFLiteralFactory(abc.ABC):
    """A role interface for CNF literal factories, e.g. SAT solvers or CNF formula builders"""

    @abc.abstractmethod
    def create_literal(self):
        """
        Creates a literal with a new variable.

        More precisely, for each distinct objects l1, l2 returned by this method, the following holds:
        1. -l1 != l1 and -(-l1) = l1
        2. l1 != l2 and -l1 != -l2 and -l1 != l2

        :return: A literal L such that neither L nor -L has previously been returned by this method.
        """
        pass


class ClauseConsumer(abc.ABC):
    """A role interface for clause consumers, e.g. SAT solvers or CNF formula builders"""

    @abc.abstractmethod
    def consume_clause(self, clause):
        """
        Consumes a clause.

        :param clause: The clause to be consumed, a list of objects which have been created using create_literal().
        :return: None
        """
        pass


class SatSolver(CNFLiteralFactory, ClauseConsumer):
    """An interface for SAT solvers."""

    @abc.abstractmethod
    def solve(self, assumptions: list):
        """
        Determines whether the problem is satisfiable.

        :param assumptions: A list of literals whose assignment shall be forced to true during the solving process.
                            For each literal l in assumptions, either l or -l must have been produced via
                            create_literal().
        :return: True if the problem is satisfiable; False if the problem is not satisfiable; None if the solver
                 did not reach a conclusion (e.g. due to a timeout).
        """
        pass

    @abc.abstractmethod
    def get_assignment(self, lit):
        """
        Gets the assignment of the given literal within the model produced by the previous call to solve().

        This method may only be called when the previous call to solve() returned True.

        :param lit: A literal l such that l or -l has been produced via create_literal.
        :return: True if lit has a positive assignment, False if lit has a negative assignment, None if lit
                 has no assignment.
        """
        pass
