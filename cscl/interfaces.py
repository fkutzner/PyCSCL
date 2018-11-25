import abc


class CNFVariableFactory(abc.ABC):
    """A role interface for CNF variable factories, e.g. SAT solvers or CNF formula builders"""

    @abc.abstractmethod
    def create_variable(self):
        """
        Creates a new variable that can be used in clauses passed to consume_clause.

        The type of the returned object is deliberately unspecified.

        :return: A variable that has not previously been returned by this method.
        """
        pass


class ClauseConsumer(abc.ABC):
    """A role interface for clause consumers, e.g. SAT solvers or CNF formula builders"""

    @abc.abstractmethod
    def consume_clause(self, clause):
        """
        Consumes a clause.

        :param clause: The clause to be consumed, a list of objects which have been created using create_variable().
        :return: None
        """
        pass


class SatSolver(CNFVariableFactory):
    """A role interface for SAT solvers."""

    @abc.abstractmethod
    def solve(self, assumptions: list):
        """
        Determines whether the problem is satisfiable.

        :param assumptions: A list of literals whose assignment shall be forced to true during the solving process.
                            For each literal l in assumptions, either l or -l must have been produced via
                            create_variable().
        :return: True if the problem is satisfiable; False if the problem is not satisfiable; None if the solver
                 did not reach a conclusion (e.g. due to a timeout).
        """
        pass

    @abc.abstractmethod
    def get_assignment(self, lit):
        """
        Gets the assignment of the given literal within the model produced by the previous call to solve().

        This method may only be called when the previous call to solve() returned True.

        :param lit: A literal l such that l or -l has been produced via create_variable.
        :return: True if lit has a positive assignment, False if lit has a negative assignment, None if lit
                 has no assignment.
        """
        pass