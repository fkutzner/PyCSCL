import cscl.interfaces


class TrivialSATSolver(cscl.interfaces.SatSolver):
    """
    A simple DPLL-like SAT solver.

    This solver is intended for testing constraint encoders and, due to its extremely simple
    implementation, should only be used for problems with a small amount of variables (<= 20)
    and a small amount of clauses (<= 100). This solver is deliberately kept simple to avoid
    bugs within the test infrastructure.
    """

    def __init__(self):
        self.__clauses = []
        self.__lit_occurrence_map = {}
        self.__variable_assignments = []
        self.__last_model = None

    def __get_num_variables(self):
        return len(self.__variable_assignments)

    def __set_assignment(self, lit, value):
        self.__variable_assignments[abs(lit)-1] = (value if lit > 0 else (not value))

    def __get_assignment(self, lit):
        var_assgn = self.__variable_assignments[abs(lit)-1]
        if var_assgn is None:
            return None
        return var_assgn if lit > 0 else not var_assgn

    def __get_clause_status(self, clause):
        """
        Gets the status of a given clause.

        :param clause: A clause.
        :return: A tuple (c, l) representing the clause status. If c is True, the current variable assignment falsifies
                 the given clause and l has the value None. If c is False and l is not None, l is the single literal l
                 in the given clause with l having an indeterminate value. If c is False and l is None, the clause
                 contains multiple literals with indeterminate values.
        """
        amnt_indeterminate_lits = 0
        last_indeterminate_lit = None
        for lit in clause:
            assignment = self.__get_assignment(lit)
            if assignment is True:
                return False, None  # no conflict, no forced assignment
            if assignment is None:
                last_indeterminate_lit = lit
                amnt_indeterminate_lits += 1

        if amnt_indeterminate_lits == 0:
            return True, None  # conflict, no forced assignment
        elif amnt_indeterminate_lits == 1:
            return False, last_indeterminate_lit  # no conflict, but forced assignment last_indeterminate_lit
        else:
            return False, None  # no conflict, no forced assignment

    def __propagate(self, root_propagation_lit):
        """
        Performs all variable assignments forced due to the current setting of root_propagation_lit.

        :param root_propagation_lit: The assignment to propagate. The value of root_propagation_lit must be determinate.
        :return: A tuple (c, l). l is the list of additional assignments made during propagation, represented as
                 literals whose value is True. The assignment is consistent with the clauses iff c is False.
        """
        propagation_queue = [root_propagation_lit]
        level_assignments = [root_propagation_lit]

        while len(propagation_queue) > 0:
            lit_to_propagate = propagation_queue.pop()
            possibly_false_clauses = self.__lit_occurrence_map[-lit_to_propagate]
            for clause in possibly_false_clauses:
                is_conflict, propagation_lit = self.__get_clause_status(clause)
                if is_conflict:
                    return True, level_assignments
                elif propagation_lit is not None:
                    level_assignments.append(propagation_lit)
                    self.__set_assignment(abs(propagation_lit), propagation_lit > 0)
                    propagation_queue.append(propagation_lit)
        return False, level_assignments

    def __solve(self, current_var, assignment):
        self.__set_assignment(current_var, assignment)
        current_lit = current_var * (1 if assignment else -1)

        conflict_detected, level_assignments = self.__propagate(current_lit)

        def __undo_current_level_assignments():
            for x in level_assignments:
                self.__set_assignment(abs(x), None)

        if conflict_detected:
            __undo_current_level_assignments()
            return False

        next_var = current_var+1
        while next_var <= self.__get_num_variables() and (self.__get_assignment(next_var) is not None):
            next_var = next_var+1

        if next_var > self.__get_num_variables():
            self.__last_model = self.__variable_assignments[:]
            __undo_current_level_assignments()
            return True

        result = self.__solve(next_var, False) or self.__solve(next_var, True)
        __undo_current_level_assignments()
        return result

    def consume_clause(self, clause):
        # The clause status getter function relies on each clause containing distinct literals:
        shrinked_clause = list(set(clause))
        shrinked_clause.sort()
        self.__clauses.append(shrinked_clause)
        for lit in shrinked_clause:
            self.__lit_occurrence_map[lit].append(shrinked_clause)

    def create_literal(self):
        var_id = self.__get_num_variables() + 1
        self.__variable_assignments.append(None)
        self.__lit_occurrence_map[var_id] = []
        self.__lit_occurrence_map[-var_id] = []
        return var_id

    def solve(self, assumptions=()):
        if any((len(elem) == 0) for elem in self.__clauses):
            return False
        if self.__get_num_variables() == 0:
            return True

        # Cleaning up the variable setting in case the solver is being invoked incrementally:
        for i in range(1, self.__get_num_variables()+1):
            self.__set_assignment(i, None)

        for assumption in assumptions:
            self.__set_assignment(abs(assumption), assumption > 0)
            conflict_detected, _ = self.__propagate(assumption)
            if conflict_detected:
                return False

        initial_var = 1
        while initial_var <= self.__get_num_variables() and (self.__get_assignment(initial_var) is not None):
            initial_var = initial_var + 1
        if initial_var > self.__get_num_variables():
            return True

        return self.__solve(initial_var, False) or self.__solve(initial_var, True)

    def get_assignment(self, lit):
        assert self.__last_model is not None
        var = abs(lit) - 1
        if var >= len(self.__last_model):
            return None
        var_assgn = self.__last_model[var]
        if var_assgn is None:
            return None
        return var_assgn if lit > 0 else not var_assgn

    def has_variable_of_lit(self, lit):
        return abs(lit) <= self.__get_num_variables()

    def print_model(self):
        assert self.__last_model is not None
        for i in range(0, self.__get_num_variables()):
            print("Var: " + str(i+1) + "\t Value: " + str(self.get_assignment(i+1)))
