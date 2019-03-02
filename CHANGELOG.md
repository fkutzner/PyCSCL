# PyCSCL Changelog

This changelog's format is based on [keep a changelog 1.0.0](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
### Added
- generic at-least-k cardinality constraint encoder
- generic exactly-k cardinality constraint encoder
- Commander at-most-k cardinality constraint encoder

## [0.1.0] - 2019-02-24
### Added
Encoders:
- binomial at-most-k cardinality constraint encoder
- LTSeq at-most-k cardinality constraint encoder
- AND, OR, binary XOR gate constraint encoders
- binary MUX gate constraint encoder
- half adder and full adder gate constraint encoder
- bitvector AND, OR, XOR gate constraint encoder
- ripple-carry bitvector adder gate constraint encoder
- ripple-carry bitvector subtractor gate constraint encoder (for 2's complement signed integers)
- parallel bitvector multiplier gate constraint encoder
- unsigned bitvector divider and remainder gate constraint encoder (simple long division)
- signed (2's complement) and unsigned bitvector comparison gate constraint encoder

Examples:
- integer factorization problem encoder
- SAT-based Sudoku solver
- prerequisites for a simple QF_BV SMT solver
