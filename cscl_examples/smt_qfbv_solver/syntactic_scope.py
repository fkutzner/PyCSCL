from typing import Union
import cscl_examples.smt_qfbv_solver.ast as ast


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
        self.__decls = dict()

    def get_declaration(self, func_name: str) -> Union[ast.FunctionDeclaration, type(None)]:
        """
        Gets the declaration of a function.

        If this scope does not contain a matching function declaration and this scope has
        a parent scope, the parent scope is queried for a function declaration for func_name.

        :param func_name: The function's name.
        :return: If the scope has no function with name func_name, None is returned. Otherwise, the function's
                 declaration is returned.
        """
        if func_name in self.__decls.keys():
            return self.__decls[func_name]
        elif self.__parent is not None:
            return self.__parent.get_declaration(func_name)
        else:
            return None

    def add_declaration(self, declaration: ast.FunctionDeclaration):
        """
        Adds a function declaration to the scope.

        :param declaration: The function's declaration. No same-named signature must have previously been added to the
                            scope.
        :return: None
        :raises ValueError if adding a function named func_name is prevented by the existence of a same-named,
                           unshadowable function declaration in this scope.
        """
        func_name = declaration.get_name()
        assert func_name not in self.__decls.keys()
        if self.has_unshadowable_signature(func_name):
            raise ValueError("Function " + func_name + " cannot be redefined or shadowed")
        self.__decls[func_name] = declaration

    def has_unshadowable_signature(self, func_name):
        """
        Determines whether the given function name is associated with an unshadowable function.

        :param func_name: The function's name.
        :return: True iff the given function name is associated with an unshadowable function.
        """
        func_decl = self.get_declaration(func_name)
        if func_decl is None:
            return False
        else:
            return not func_decl.get_signature().is_shadowable()

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
        return self.__parent

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
