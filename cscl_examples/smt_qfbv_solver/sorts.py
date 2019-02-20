import abc


class Sort(abc.ABC):
    """Base class for representations of sorts. Classes derived from Sort must be immutable."""
    pass


class BooleanSort(Sort):
    """The Boolean sort."""
    def __str__(self):
        return "Bool"


class BitvectorSort(Sort):
    """The bitvector sort."""

    def __init__(self, length: int):
        """
        Initializes a BitvectorSort object.

        :param length: The bitvector length, in bits.
        """
        self.__len = length

    def get_len(self):
        """Returns the bitvector length, in bits."""
        return self.__len

    def __str__(self):
        return "(_ BitVec " + str(self.__len) + ")"


class IntegerSort(Sort):
    """The integer sort."""
    def __str__(self):
        return "Int"


class SortContext:
    """A caching factory for Sort objects"""
    def __init__(self):
        self.__int_sort = IntegerSort()
        self.__bv_sorts = dict()
        self.__bool_sort = BooleanSort()

    def get_int_sort(self):
        """
        Returns the Integer sort.
        :return: the Integer sort.
        """
        return self.__int_sort

    def get_bv_sort(self, length: int):
        """
        Returns the Bitvector sort of the given length.

        :param length: The length of the bitvector, in bits.
        :return: the Bitvector sort for the specified length.
        """
        if length in self.__bv_sorts.keys():
            return self.__bv_sorts[length]
        new_sort = BitvectorSort(length)
        self.__bv_sorts[length] = new_sort
        return new_sort

    def get_bool_sort(self):
        """
        Returns the Boolean sort.

        :return: the Boolean sort.
        """
        return self.__bool_sort
