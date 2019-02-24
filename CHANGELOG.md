# PyCSCL Changelog

This changelog's format is based on [keep a changelog 1.0.0](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2019-02-24
### Added
Encoders:
- Binomial at-most-k constraint encoder
- LTSeq at-most-k constraint encoder
- AND, OR, binary XOR gate constraint encoders
- Binary MUX gate constraint encoder
- Half adder and full adder gate constraint encoder
- Bitvector AND, OR, XOR gate constraint encoder
- Ripple-carry bitvector adder gate constraint encoder
- Ripple-carry bitvector subtractor gate constraint encoder (for 2's complement signed integers)
- Parallel bitvector multiplier gate constraint encoder
- Unsigned bitvector divider and remainder gate constraint encoder (simple long division)
- Signed (2's complement) and unsigned bitvector comparison gate constraint encoder

Examples:
- Integer factorization problem encoder
- SAT-based Sudoku solver
- prerequisites for a simple QF_BV SMT solver
