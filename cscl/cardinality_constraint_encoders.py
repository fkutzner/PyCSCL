"""Cardinality constraint encoders

This module provides at-most-k constraint encoders. An at-most-k constraint encoding for a set L of literals
is satisfied if and only if no more than k elements in L have the value assignment 'true'.
"""

from cscl.interfaces import CNFLiteralFactory


def subsets_of_size_k(collection, k):
    """
    Computes all subsets of size k.

    :param collection: A list.
    :param k: A non-negative integer.
    :return: A list containing all size-k subsets of collection.
    """
    # Potential optimization: make this a generator

    assert(k >= 0)

    # Base cases:
    if k > len(collection):
        return []
    if k == 0:
        return [[]]
    if k == len(collection):
        return [collection]

    next_smaller_subsets = subsets_of_size_k(collection[1:], k-1)
    next_subsets = subsets_of_size_k(collection[1:], k)

    def extend_list(lst, item):
        lst_copy = lst[:]
        lst_copy.append(item)
        return lst_copy

    return next_subsets + list(map(lambda x: extend_list(x, collection[0]), next_smaller_subsets))


def encode_at_most_k_constraint_binomial(lit_factory: CNFLiteralFactory, k: int, constrained_lits: list):
    """
    Creates a CNF constraint C such that for all literal assignments L of C, the following holds:
    At most k of the literals contained in constrained_lits are assigned true.

    This encoder uses the binomial encoding, producing len(constrained_lits) over k+1 clauses,
    each of size k. No new variables are introduced.

    :param lit_factory: The literal factory to be used for creating literals with new CNF variables.
    :param k: See above.
    :param constrained_lits: The literals to be constrained.
    :return: The constraint in CNF clausal form, a list of lists of literals.
    """

    result = []
    for subset in subsets_of_size_k(constrained_lits, k+1):
        result.append(list(map(lambda x: -x, subset)))
    return result


def encode_at_most_k_constraint_ltseq(lit_factory: CNFLiteralFactory, k: int, constrained_lits: list):
    """
    Creates a CNF constraint C such that for all literal assignments L of C, the following holds:
    At most k of the literals contained in constrained_lits are assigned true.

    This encoder uses the sequential counter encoding, producing O(k*len(constrained_lits)) clauses
    and O(k*len(constrained_lits)) new variables.

    Source for this encoding:
     Carsten Sinz. Towards an optimal CNF encoding of Boolean cardinality constraints.
     In Proc. of the 11th Intl. Conf. on Principles and Practice of Constraint Program-
     ming (CP 2005), pages 827–831, Sitges, Spain, October 2005.

    :param lit_factory: The literal factory to be used for creating literals with new CNF variables.
    :param k: See above.
    :param constrained_lits: The literals to be constrained.
    :return: The constraint in CNF clausal form, a list of lists of literals.
    """
    if k == 0:
        return list(map(lambda x: [-x], constrained_lits))
    if len(constrained_lits) == 0:
        return []
    if len(constrained_lits) == 1:
        # Here, k >= len(constrained_lits)
        return []

    n = len(constrained_lits)
    registers = []
    for i in range(0, n):
        register = []
        for j in range(0, k):
            register.append(lit_factory.create_literal())
        registers.append(register)
    # registers[i][j] represents the j'th bit of register i
    # register[i] represents (as a unary number) the number of literals in constrained_lits[0],
    # ..., constrained_lits[i] that are assigned to true.

    # See the source paper for a description of the encoding
    result = [[-constrained_lits[0], registers[0][0]]]

    for i in range(1, k):
        result.append([-registers[0][i]])

    for i in range(1, n-1):
        result.append([-constrained_lits[i], registers[i][0]])
        result.append([-registers[i-1][0], registers[i][0]])

        for j in range(1, k):
            result.append([-constrained_lits[i], -registers[i-1][j-1], registers[i][j]])
            result.append([-registers[i-1][j], registers[i][j]])

        result.append([-constrained_lits[i], -registers[i-1][k-1]])

    result.append([-constrained_lits[n-1], -registers[n-2][k-1]])

    return result
