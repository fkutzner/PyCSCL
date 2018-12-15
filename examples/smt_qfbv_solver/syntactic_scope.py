from typing import Union, Tuple


class FunctionSignature:
    """
    A function signature.
    """

    def __init__(self, domain_sorts_to_range_sort_fn, arity: int, is_shadowable: bool, num_parameters: int = 0):
        """
        Initializes the FunctionSignature object.

        :param domain_sorts_to_range_sort_fn: The function determining the represented function's signature.
                                              For Sort objects s1, ..., sN, domain_sorts_to_range_sort_fn((s1, ..., sN))
                                              returns the function's range sort for parameter sorts s1, ..., sN;
                                              If s1, ..., sN is not part of the function's domain, None is returned.
        :param arity: The function's arity.
        :param is_shadowable: True iff the function may be shadowed and may shadow other functions; False otherwise.
        :param num_parameters: The non-negative number of the function's parameters. If the function is not
                               parametrized, num_parameters must be 0.
        """
        self.__dtr_fun = domain_sorts_to_range_sort_fn
        self.__arity = arity
        self.__is_shadowable = is_shadowable
        self.__num_parameters = num_parameters

    def get_range_sort(self, domain_sorts):
        """
        Gets the function's range sort for domain sorts s1, ..., sN.

        :param domain_sorts: The query's domain sorts.
        :return: The corresponding range sort, or None domain_sorts is not part of the function's domain.
        """
        return self.__dtr_fun(domain_sorts)

    def get_arity(self):
        """
        Gets the function's arity.

        :return: The function's arity.
        """
        return self.__arity

    def get_num_parameters(self):
        """
        Gets the number of the function's numeral parameters.

        This value is used to reflect the number N of parameters a function F has in a (_ F <p0> <p1> ... <pN>) term.

        :return: the number of the function's numeral parameters.
        """

    def is_shadowable(self):
        """
        Returns True iff the function may be shadowed and may shadow other function declarations.

        :return: True iff the function may be shadowed and may shadow other function declarations.
        """
        return self.__is_shadowable


class SyntacticFunctionScope:
    """
    A scope of function declarations.
    """

    def __init__(self, parent_scope):
        """
        Initializes the SyntacticFunctionScope object.

        :param parent_scope: The scope's parent scope. If the scope has no parent scope, this argument must be None.
        """
        self.__parent = parent_scope
        self.__signatures = dict()

    def get_signature(self, func_name: str) -> Union[Tuple[FunctionSignature, str], type(None)]:
        """
        Gets the function signature for a function.

        If this scope does not contain a matching function signature and this scope has
        a parent scope, the parent scope is queried for a function signature for func_name.

        :param func_name: The function's name.
        :return: If the scope has no function with name func_name, None is returned. Otherwise, a tuple (f,n) is
                 returned with f being the function's signature and n being the function's name.
        """
        if func_name in self.__signatures.keys():
            return self.__signatures[func_name]
        elif self.__parent is not None:
            return self.__parent.get_signature(func_name)
        else:
            return None

    def add_signature(self, func_name: str, signature: FunctionSignature):
        """
        Adds a function signature to the scope.

        :param func_name: The function's name.
        :param signature: The function's signature.
        :return: None
        :raises ValueError if adding a function named func_name is prevented by the existence of a same-named,
                           unshadowable function in this scope.
        """
        if self.has_unshadowable_signature(func_name):
            raise ValueError("Function " + func_name + " cannot be redefined or shadowed")
        self.__signatures[func_name] = (signature, func_name)

    def has_unshadowable_signature(self, func_name):
        """
        Determines whether the given function name is associated with an unshadowable function.

        :param func_name: The function's name.
        :return: True iff the given function name is associated with an unshadowable function.
        """
        func_signature = self.get_signature(func_name)
        if func_signature is None:
            return False
        else:
            return not func_signature[0].is_shadowable()

    def set_parent(self, new_parent):
        """
        Sets the scope's parent scope.

        :param new_parent: The new parent scope.
        :return: None
        """
        self.__parent = new_parent

    def get_parent(self):
        """
        Gets the scope's parent scope.

        :return: The current scope's parent scope.
        """

    @staticmethod
    def mangle_parametrized_function_name(name: str):
        """
        Mangles the name of a parametrized function such that its name is not a symbol.

        :param name: The function's name.
        :return: The mangled name.
        """
        return "0!" + name

    @staticmethod
    def demangle_parametrized_function_name(name: str):
        """
        Demangles the name of a parametrized function.

        :param name: The function's mangled name.
        :return: The demangled name.
        """
        if len(name) < 2 or name[0:1] != "0!":
            raise ValueError("Cannot demangle non-mangled function name " + name)
        return name[2:]
