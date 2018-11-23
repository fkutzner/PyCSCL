import cscl.clause_consumer


class TrivialSATSolver(cscl.clause_consumer.ClauseConsumer):
    """
    A trivial SAT solver.

    This solver is intended for testing constraint encoders and, due to its extremely simple
    implementation, should only be used for problems with a small amount of variables (<= 20)
    and a small amount of clauses (<= 100).
    """

    def __init__(self):
        self.__clauses = []
        self.__variable_assignments = []

    def __get_num_variables(self):
        return len(self.__variable_assignments)

    def __set_assignment(self, lit, value):
        self.__variable_assignments[abs(lit)-1] = (value if lit > 0 else (not value))

    def __get_assignment(self, lit):
        var_assgn = self.__variable_assignments[abs(lit)-1]
        if var_assgn is None:
            return None
        return var_assgn if lit > 0 else not var_assgn

    def __is_satisfied(self, clause):
        for lit in clause:
            if self.__get_assignment(lit) is not False:
                return True
        return False

    def __solve(self, current_var, assignment):
        self.__set_assignment(current_var, assignment)

        for clause in self.__clauses:
            if not self.__is_satisfied(clause):
                return False

        next_var = current_var+1
        if next_var > self.__get_num_variables():
            return True

        result = self.__solve(next_var, False) or self.__solve(next_var, True)
        self.__set_assignment(current_var, None)
        return result

    def consume_clause(self, clause):
        self.__clauses.append(clause)

    def create_variable(self):
        var_id = self.__get_num_variables() + 1
        self.__variable_assignments.append(None)
        return var_id

    def solve(self):
        """
        Determines the satisfiability of the consumed problem, interpreted as a CNF formula in clausal form.

        :return: True if the consumed problem is satisfiable, otherwise False.
        """
        if any((len(elem) == 0) for elem in self.__clauses):
            return False
        if self.__get_num_variables() == 0:
            return True
        return self.__solve(1, False) or self.__solve(1, True)
