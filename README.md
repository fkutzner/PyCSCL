# PyCSCL

PyCSCL is a collection of boolean constraint encoders. You can use it
e.g. to reduce hard combinatorial problems to the [Boolean satisifability
problem (SAT)](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem).

Though PyCSCL is designed not to depend on a specific SAT solver interface,
it contains a simple and easy-to-use binding for
SAT solvers implementing the 
[IPASIR](https://github.com/biotomas/ipasir) interface.

## Encoders

##### Cardinality (at-most-k) constraint encoders
- Binomial encoding
- LTSeq encoding

Package: `cscl.cardinality_constraint_encoders`

##### Gate constraint encoders
- AND, OR, binary XOR gates
- Binary MUX gates
- Half adder and full adder gates

Package: `cscl.basic_gate_encoders`

##### Bitvector constraint encoders
- Bitvector AND, OR, XOR gates
- Ripple-carry bitvector adder and (2's complement) subtractor gates
- Parallel bitvector multiplier gate
- Signed (2's complement) and unsigned bitvector comparison gate

Package: `cscl.bitvector_gate_encoders`

## Examples
- `examples.factorization`: [integer factorization](https://en.wikipedia.org/wiki/Integer_factorization) problem encoder
- `examples.sudoku`: SAT-based [Sudoku](https://en.wikipedia.org/wiki/Sudoku) solver
- `examples.smt_qfbv_solver` (under construction): simple QF_BV
  [SMT](https://en.wikipedia.org/wiki/Satisfiability_modulo_theories) solver
