
def ensure_tuple_or_list(x):
    """
    :param x: An iterable object
    :return: x if x is a list or a tuple; tuple(x) otherwise
    """
    if isinstance(x, tuple) or isinstance(x, list):
        return x
    else:
        return tuple(x)
