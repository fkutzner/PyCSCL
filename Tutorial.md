# PyCSCL Tutorial

## Example: Using a Cardinality Constraint
```python
import cscl.dimacs_printer as dimacs
import cscl.cardinality_constraint_encoders as cardenc

dimacs_out = dimacs.DIMACSPrinter()

# DIMACSPrinter implements the CNFLiteralFactory role interface.
# Create 100 fresh literals with distinct variables:
some_literals = [dimacs_out.create_literal() for _ in range(0, 100)]

# Create a constraint that at most 7 literals in constrained_literals may have
# the value 'true':
constraint_clauses = cardenc.encode_at_most_k_constraint_ltseq(lit_factory=dimacs_out,
                                                               constrained_lits=some_literals,
                                                               k=7)

# DIMACSPrinter implements the ClauseConsumer role interface.
# Pass the constraint to the clause consumer:
for clause in constraint_clauses:
    dimacs_out.consume_clause(clause)

# Print the CNF formula as a DIMACS problem, passing the Python print()
# function as the receiver of DIMACS-problem lines:
dimacs_out.print(print)
```
