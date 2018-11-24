from cscl.clause_consumer import CNFVariableFactory


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


def encode_at_most_k_constraint_binomial(variable_factory: CNFVariableFactory, k: int, constrained_lits: list):
    """
    Creates a CNF constraint C such that for all literal assignments L of C, the following holds:
    At most k of the literals contained in constrained_lits are assigned true.

    This encoder uses the binomial encoding, producing len(constrained_lits) over k+1 clauses,
    each of size k. No new variables are introduced.

    :param variable_factory: The variable factory to be used for creating new CNF variables.
    :param k: See above.
    :param constrained_lits: The literals to be constrained.
    :return: The constraint in CNF clausal form, a list of lists of literals.
    """

    result = []
    for subset in subsets_of_size_k(constrained_lits, k+1):
        result.append(list(map(lambda x: -x, subset)))
    return result
