# PyCSCL Changelog

This changelog's format is based on [keep a changelog 1.0.0](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]
### Added
Encoders:
- Binomial at-most-k constraint encoder
- LTSeq at-most-k constraint encoder
- AND, OR, binary XOR gate constraint encoders
- Binary MUX gate constraint encoder
- Half adder and full adder gate constraint encoder
- Bitvector AND, OR, XOR gate constraint encoder
- Ripple-carry bitvector adder gate constraint encoder
- Parallel bitvector multiplier gate constraint encoder
- Signed (2's complement) and unsigned bitvector comparison gate constraint encoder

Examples:
- Integer factorization problem encoder
- SAT-based Sudoku solver
- prerequisites for a simple QF_BV SMT solver
