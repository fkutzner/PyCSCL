from cscl.interfaces import ClauseConsumer, CNFLiteralFactory


class DIMACSPrinter(ClauseConsumer, CNFLiteralFactory):
    """
    A DIMACS CNF printer.
    """

    def __init__(self):
        self.clauses = []
        self.num_vars = 0

    def consume_clause(self, clause):
        self.clauses.append(clause)

    def create_literal(self):
        self.num_vars += 1
        return self.num_vars

    def print(self, line_print_fn):
        """
        Prints the collected clauses using the given printing function.

        :param line_print_fn: A function accepting a string as its sole argument. The DIMACS output
                              is passed line-by-line to line_print_fn.
        :return: None
        """
        line_print_fn("p cnf " + str(self.num_vars) + " " + str(len(self.clauses)))
        for clause in self.clauses:
            line_print_fn((' '.join(map(str, clause))) + " 0")
