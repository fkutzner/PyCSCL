"""
Rough performance tests for PyCSCL, measuring the produced amount of clauses per second
"""

from cscl.bitvector_gate_encoders import encode_bv_parallel_mul_gate
from cscl.cardinality_constraint_encoders import encode_at_most_k_constraint_ltseq
import cscl.interfaces as interfaces
import timeit


class PerfTestClauseConsumer(interfaces.CNFLiteralFactory, interfaces.ClauseConsumer):
    def __init__(self):
        self._nextVar = 0
        self._numClauses = 0
        self._numLits = 0

    def create_literal(self):
        self._nextVar += 1
        return self._nextVar

    def consume_clause(self, clause):
        self._numClauses += 1
        self._numLits += len(clause)

    def get_num_generated_clauses(self):
        return self._numClauses

    def get_num_literals_in_generated_clauses(self):
        return self._numLits


def perftest_bv_mul(sink):
    for i in range(1, 300):
        encode_bv_parallel_mul_gate(clause_consumer=sink, lit_factory=sink,
                                    lhs_input_lits=range(i, i+32),
                                    rhs_input_lits=range(i, i+32))


def perftest_card_ltseq(sink):
    for i in range(1, 2000):
        for c in encode_at_most_k_constraint_ltseq(sink, 10, range(i, i+64)):
            sink.consume_clause(c)


def run_performance_test(test_function):
    sink = PerfTestClauseConsumer()
    start = timeit.default_timer()
    test_function(sink)
    end = timeit.default_timer()

    elapsed_secs = end-start
    print(test_function.__name__ + ': #GeneratedClauses: ' + str(sink.get_num_generated_clauses())
          + ', #SumOfClauseLenghts: ' + str(sink.get_num_literals_in_generated_clauses())
          + ', #ElapsedSeconds: ' + '{0:.2f}'.format(elapsed_secs)
          + ', #ClausesPerSec: ' + '{0:.2f}'.format(sink.get_num_generated_clauses()/elapsed_secs))


if __name__ == '__main__':
    run_performance_test(perftest_bv_mul)
    run_performance_test(perftest_card_ltseq)
