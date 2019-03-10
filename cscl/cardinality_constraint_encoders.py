"""Cardinality constraint encoders

This module provides at-most-k constraint encoders. An at-most-k constraint encoding for a set L of literals
is satisfied if and only if no more than k elements in L have the value assignment 'true'.
"""

from cscl.interfaces import CNFLiteralFactory
import itertools


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


def chunks(l: list, chunk_size: int):
    """
    Partitions the given list into chunks of the given size (approximately).

    :param l: A list.
    :param chunk_size: An integer in the interval [1, len(l)].
    :return: An iterable sequence of lists forming a partition of l, preserving the order of the elements in of l. Each
             list L in this sequence has a length of at most chunk_size, with all but the last list in the returned
             sequence having a length of chunk_size.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must not be 0 or negative")

    total_items_yielded = 0
    while total_items_yielded < len(l):
        if total_items_yielded + chunk_size >= len(l):
            yield l[total_items_yielded:]
            total_items_yielded = len(l)
        else:
            yield l[total_items_yielded:total_items_yielded+chunk_size]
            total_items_yielded += chunk_size


def encode_at_least_k_constraint(lit_factory: CNFLiteralFactory, k: int, constrained_lits: list,
                                 encode_at_most_k_constraint_fn):
    """
    Creates a CNF constraint C such that for all literal assignments L of C, the following holds:
    At least k of the literals contained in constrained_lits are assigned true.

    This encoder uses an at-most-k constraint encoder function to encode the at-least-k constraint.

    :param lit_factory: The literal factory to be used for creating literals with new CNF variables.
    :param k: See above.
    :param constrained_lits: The literals to be constrained.
    :param encode_at_most_k_constraint_fn: an at-most-k constraint encoder function.
    :return: The constraint in CNF clausal form, a list of lists of literals.
    """
    return encode_at_most_k_constraint_fn(lit_factory, len(constrained_lits)-k, [-l for l in constrained_lits])


def encode_exactly_k_constraint(lit_factory: CNFLiteralFactory, k: int, constrained_lits: list,
                                encode_at_most_k_constraint_fn):
    """
    Creates a CNF constraint C such that for all literal assignments L of C, the following holds:
    Exactly k of the literals contained in constrained_lits are assigned true.

    This encoder uses an at-most-k constraint encoder function to encode the constraint.

    :param lit_factory: The literal factory to be used for creating literals with new CNF variables.
    :param k: See above.
    :param constrained_lits: The literals to be constrained.
    :param encode_at_most_k_constraint_fn: an at-most-k constraint encoder function.
    :return: The constraint in CNF clausal form, a list of lists of literals.
    """
    return encode_at_most_k_constraint_fn(lit_factory, k, constrained_lits) \
        + encode_at_least_k_constraint(lit_factory, k, constrained_lits, encode_at_most_k_constraint_fn)


def encode_at_most_k_constraint_commander(lit_factory: CNFLiteralFactory, k: int, constrained_lits: list):
    """
    Creates a CNF constraint C such that for all literal assignments L of C, the following holds:
    At most k of the literals contained in constrained_lits are assigned true.

    See the cited paper for upper bounds on clauses rsp. variables added by this encoder.

    Source for this encoding:
     Frisch, Alan M., and Paul A. Giannaros. "Sat encodings of the at-most-k constraint. some old, some new, some fast,
     some slow." Proc. of the Tenth Int. Workshop of Constraint Modelling and Reformulation. 2010.

    :param lit_factory: The literal factory to be used for creating literals with new CNF variables.
    :param k: See above.
    :param constrained_lits: The literals to be constrained.
    :return: The constraint in CNF clausal form, a list of lists of literals.
    """
    if k == 0:
        return list(map(lambda x: [-x], constrained_lits))
    if len(constrained_lits) <= 1 or len(constrained_lits) <= k:
        # at-most-k constraint is always satisfied, don't add any constraining clauses
        return []

    # See the cited paper for a description of the encoding.

    group_size = min(k+2, len(constrained_lits))
    groups = list(chunks(constrained_lits, group_size))

    # commanders[i][j] corresponds to c_{i,j} in the source paper:
    commanders = [[lit_factory.create_literal() for _ in range(0, k)] for _ in groups]

    # For each group, add at-least-k and at-most-k constraints for the group and its commander literals:
    group_constraints = []
    for idx, group in enumerate(groups):
        group_with_commanders = group + [-c for c in commanders[idx]]
        group_constraints += encode_exactly_k_constraint(lit_factory, k, group_with_commanders,
                                                         encode_at_most_k_constraint_binomial)

    # Break symmetries by ordering the commander literals:
    order_commanders = [[-group_commanders[i], group_commanders[i+1]]
                        for group_commanders, i in itertools.product(commanders, range(0, k-1))]

    # At most k commander literals may be true at any time:
    flat_commanders = [c for group_commanders in commanders for c in group_commanders]
    at_most_k_commanders = encode_at_most_k_constraint_commander(lit_factory=lit_factory, k=k,
                                                                 constrained_lits=flat_commanders)

    return group_constraints + order_commanders + at_most_k_commanders
