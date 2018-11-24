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
