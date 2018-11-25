from cscl.interfaces import ClauseConsumer


class LoggingClauseConsumerDecorator(ClauseConsumer):
    """
    A ClauseConsumer that logs the collected clauses.
    """

    def __init__(self, decorated_clause_consumer: ClauseConsumer):
        """
        Constructs a LoggingClauseConsumerDecorator object.

        :param decorated_clause_consumer: The ClauseConsumer to be decorated.
        """
        self.decorated_clause_consumer = decorated_clause_consumer
        self.clauses = []

    def consume_clause(self, clause):
        self.clauses.append(clause)
        self.decorated_clause_consumer.consume_clause(clause)

    def to_string(self):
        """
        Returns a string representation of the clauses added via consume_clause(),
        preserving their order of consumption.

        :return: a string as described above.
        """
        result = ""
        for clause in self.clauses:
            result += str(clause) + "\n"
        return result
