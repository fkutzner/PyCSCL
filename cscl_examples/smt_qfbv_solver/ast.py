import abc
from typing import Tuple, Iterable, Union
import cscl_examples.smt_qfbv_solver.sorts as sorts


class ASTNode(abc.ABC):
    """Base class for SMTLib2-language AST nodes."""

    @abc.abstractmethod
    def get_child_nodes(self):
        """
        Gets the node's child nodes.

        :return: The node's child nodes, a sequence of ASTNode objects.
        """
        pass

    @abc.abstractmethod
    def set_child_node(self, index: int, node):
        """
        Replaces the index'th child node by the given node.

        :param index: An integer with 0 <= index < len(get_child_nodes()).
        :param node: The node to be inserted as the index'th child node.
        :return: None.
        """
        pass

    def tree_to_string(self, indent=0):
        """
        Prints the AST tree rooted at this node to a string.

        :param indent: The current indentation level. By default, this value is 0.
        :return: A string representing the AST tree rooted at this node.
        """
        result = ((" " * indent) + str(self))
        for x in self.get_child_nodes():
            result += "\n" + x.tree_to_string(indent+2)
        return result


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
        return self.__num_parameters

    def is_shadowable(self):
        """
        Returns True iff the function may be shadowed and may shadow other function declarations.

        :return: True iff the function may be shadowed and may shadow other function declarations.
        """
        return self.__is_shadowable


class FunctionDeclaration:
    """
    A function declaration.
    """

    def __init__(self, name: str, signature: FunctionSignature, declaring_ast_node: ASTNode = None):
        """
        Initializes the FunctionDeclaration object.

        :param name: The function's name.
        :param signature: The function's signature.
        :param declaring_ast_node: The AST node declaring the function, or None if no such node exists.
        """
        self.__name = name
        self.__sig = signature
        self.__decl_node = declaring_ast_node

    def set_name(self, name: str):
        """
        Sets the function's name.

        :param name: The function's name.
        :return: None
        """
        self.__name = name

    def get_name(self) -> str:
        """
        Gets the function's name.

        :return: The function's name.
        """
        return self.__name

    def set_signature(self, signature: FunctionSignature):
        """
        Sets the function's signature.

        :param signature: The function's signature.
        :return: None
        """
        self.__sig = signature

    def get_signature(self) -> FunctionSignature:
        """
        Gets the function's signature.
        :return: The function's signature.
        """
        return self.__sig

    def set_declaring_ast_node(self, declaring_ast_node: ASTNode):
        """
        Sets the function's declaring AST node.
        :param declaring_ast_node: The function's declaring AST node.
        :return: None
        """
        self.__decl_node = declaring_ast_node

    def get_declaring_ast_node(self) -> Union[ASTNode, type(None)]:
        """
        Gets the function's declaring AST node.
        :return:  The function's declaring AST node, or None if no such node exists.
        """
        return self.__decl_node


class CommandASTNode(ASTNode, abc.ABC):
    """Base class for Command AST nodes."""
    pass


class TermASTNode(ASTNode, abc.ABC):
    """Base class for term AST nodes."""

    @abc.abstractmethod
    def get_sort(self) -> sorts.Sort:
        """
        Returns the term's sort.

        :return: the term's sort.
        """
        pass

    @abc.abstractmethod
    def clone(self, decl_ast_node_substitution_map, decl_clone_memoization):
        """
        Clones the AST node and its children.

        Sorts are reused instead of being cloned. Function declarations are cloned as needed:
        If the AST node of a declaration is associated with a replacement via decl_ast_node_substitution_map,
        the declaration is replaced by a function declaration associated with the replacing AST node. To avoid
        cloning FunctionDeclaration objects needlessly, the "original" is associated with the clone via the map
        decl_clone_memoization.

        :param decl_ast_node_substitution_map: A mapping of declaration AST node replacements.
        :param decl_clone_memoization: A mapping of function declaration replacements.
        :return: The cloned node.
        """
        pass


class AssertCommandASTNode(ASTNode):
    """AST node class for the assert command."""
    def __init__(self, asserted_term):
        self.__child_nodes = (asserted_term,)

    def get_child_nodes(self):
        return self.__child_nodes

    def set_child_node(self, index: int, node: ASTNode):
        if index != 0:
            raise ValueError("index " + str(index) + " out of bounds")
        self.__child_nodes = (node,)

    def __str__(self):
        return self.__class__.__name__


class PushPopCommandASTNode(ASTNode):
    """AST node class for the push and pop commands."""

    def __init__(self, is_push: bool, num_levels: int):
        """
        Initializes the PushPopCommandASTNode object.

        :param is_push: True iff the node is a push command node, False otherwise.
        :param num_levels: The non-negative argument to the push/pop command.
        """
        self.__is_push = is_push
        self.__num_levels = num_levels

    def get_child_nodes(self):
        return tuple()

    def set_child_node(self, index: int, node: ASTNode):
        raise ValueError("index " + str(index) + " out of bounds")

    def get_num_levels(self):
        """
        Returns the argument to the push/pop command.

        :return: the argument to the push/pop command.
        """
        return self.__num_levels

    def is_push(self):
        """
        Determines whether the node represents a push or a pop command.

        :return: True iff the node represents a push command, False otherwise.
        """
        return self.__is_push

    def __str__(self):
        return self.__class__.__name__ + " " + ("Push" if self.__is_push else "Pop") + " " + str(self.__num_levels)


class CheckSATCommandASTNode(ASTNode):
    """AST node class for the check-sat command."""

    def get_child_nodes(self):
        return tuple()

    def set_child_node(self, index: int, node: ASTNode):
        raise ValueError("index " + str(index) + " out of bounds")

    def __str__(self):
        return self.__class__.__name__


class DeclareFunCommandASTNode(ASTNode):
    """
    AST node class for the declare-fun command.

    Note that there is no AST node class dedicated to constant declarations, since
    constants are 0-ary functions.
    """

    def __init__(self, fun_name, domain_sorts, range_sort):
        """
        Initializes the DeclareFunCommandASTNode object.

        :param fun_name: The function's name.
        :param domain_sorts: A list of the function's domain sorts.
        :param range_sort: The function's range sort.
        """
        self.__fun_name = fun_name
        self.__domain_sorts = domain_sorts
        self.__range_sort = range_sort

    def get_fun_name(self):
        """
        Returns the function's name.

        :return: the function's name.
        """
        return self.__fun_name

    def get_domain_sorts(self):
        """
        Returns the function's domain sorts.

        :return: a sequence containing the function's domain sorts. The i'th element of this sequence is the sort
                 of the function's i'th parameter.
        """
        return self.__domain_sorts

    def get_range_sort(self):
        """
        Returns the function's range sort.

        :return: the function's range sort.
        """
        return self.__range_sort

    def get_child_nodes(self):
        return tuple()

    def set_child_node(self, index: int, node: ASTNode):
        raise ValueError("index " + str(index) + " out of bounds")

    def __str__(self):
        sorts_as_str = [str(sort) for sort in self.__domain_sorts]

        return self.__class__.__name__ + " FunctionName: " + self.__fun_name \
            + " DomainSorts: " + str(sorts_as_str) \
            + " RangeSort: " + str(self.__range_sort)


class DefineFunCommandASTNode(ASTNode):
    """
    AST node class for the define-fun command.

    Note that there is no AST node class dedicated to constant declarations, since
    constants are 0-ary functions.
    """

    def __init__(self, fun_name: str, formal_parameters: Iterable[Tuple[str, sorts.Sort]],
                 range_sort: sorts.Sort, defining_term: TermASTNode):
        """
        Initializes the DeclareFunCommandASTNode object.

        :param fun_name: The function's name.
        :param formal_parameters: the sequence of the function's formal parameters, with each formal parameter being a
                                  tuple (s,t) consisting of the parameter symbol s and the parameter's sort t.
        :param range_sort: The function's range sort.
        :param defining_term: The function's defining term. All unbound symbols occurring in defining_term must be
                              parameter symbols.
        """
        self.__fun_name = fun_name
        self.__formal_parameters = tuple(formal_parameters)
        self.__range_sort = range_sort
        self.__defining_term = defining_term

    def get_fun_name(self) -> str:
        """
        Returns the function's name.

        :return: the function's name.
        """
        return self.__fun_name

    def get_formal_parameters(self) -> Iterable[Tuple[str, sorts.Sort]]:
        """
        Returns the sequence of the function's formal parameters, with each formal parameter being a tuple (s,t)
        consisting of the parameter symbol s and the parameter's sort t.

        :return: the sequence of the function's formal parameters, with each formal parameter being a tuple (s,t)
                 consisting of the parameter symbol s and the parameter's sort t.
        """
        return self.__formal_parameters

    def get_range_sort(self) -> sorts.Sort:
        """
        Returns the function's range sort.

        :return: the function's range sort.
        """
        return self.__range_sort

    def get_child_nodes(self) -> Iterable[ASTNode]:
        return self.__defining_term,

    def set_child_node(self, index: int, node: ASTNode):
        if index != 0:
            raise ValueError("index " + str(index) + " out of bounds")
        self.__defining_term = node

    def __str__(self):
        parms_as_str = ["(" + parmName + ", " + str(parmType) + ")" for parmName, parmType in self.__formal_parameters]

        return self.__class__.__name__ + " FunctionName: " + self.__fun_name \
            + " FormalParameters: " + str(parms_as_str) \
            + " RangeSort: " + str(self.__range_sort)


class SetLogicCommandASTNode(ASTNode):
    """AST node class for the set-logic command."""

    def __init__(self, logic_name):
        """
        Initializes the SetLogicCommandASTNode object.

        :param logic_name: The name of the SMT theory.
        """
        self.__logic_name = logic_name

    def get_child_nodes(self):
        return tuple()

    def set_child_node(self, index: int, node: ASTNode):
        raise ValueError("index " + str(index) + " out of bounds")

    def get_logic_name(self):
        """
        Returns the SMT theory passed to set-logic command.

        :return: the name of the SMT theory passed to the set-logic command.
        """
        return self.__logic_name

    def __str__(self):
        return self.__class__.__name__ + " Logic: " + self.__logic_name


class LiteralASTNode(TermASTNode):
    """AST node class for literal values."""

    def __init__(self, literal, sort):
        """
        Initializes the LiteralASTNode object.

        :param literal: The literal's value, represented as an integer.
        :param sort: The literal's sort.
        """
        self.__sort = sort
        self.__literal = literal

    def get_sort(self):
        return self.__sort

    def get_child_nodes(self):
        return tuple()

    def set_child_node(self, index: int, node: ASTNode):
        raise ValueError("index " + str(index) + " out of bounds")

    def get_literal(self):
        """
        Returns the literal.

        :return: the literal.
        """
        return self.__literal

    def clone(self, decl_ast_node_substitution_map, decl_clone_memoization):
        return LiteralASTNode(self.__literal, self.__sort)

    def __str__(self):
        return self.__class__.__name__ + " Literal: " + str(self.__literal) + " Sort: " + str(self.__sort)


class LetTermASTNode(TermASTNode):
    """AST node class for let terms"""

    def __init__(self, pairs_of_symbols_and_defining_terms, enclosed_term: TermASTNode):
        """
        Initializes the LetTermASTNode object.

        :param pairs_of_symbols_and_defining_terms: a sequence of pairs (x,y) with x being a constant name and y being
                                            the term defining the constant named by x.
        :param enclosed_term: the term defining the value of the let statement.
        """

        self.__pairs_of_symbols_and_defining_terms = pairs_of_symbols_and_defining_terms
        self.__enclosed_term = enclosed_term

    def get_child_nodes(self):
        return [x[1] for x in self.__pairs_of_symbols_and_defining_terms] + [self.__enclosed_term]

    def set_child_node(self, index: int, node: ASTNode):
        if index < 0 or index > len(self.__pairs_of_symbols_and_defining_terms):
            raise ValueError("index " + str(index) + " out of bounds")
        if index < len(self.__pairs_of_symbols_and_defining_terms):
            sym, _ = self.__pairs_of_symbols_and_defining_terms[index]
            self.__pairs_of_symbols_and_defining_terms[index] = (sym, node)
        else:
            self.__enclosed_term = node

    def get_sort(self):
        return self.__enclosed_term.get_sort()

    def get_enclosed_term(self):
        """
        Returns the term defining the value of the let statement.

        :return: the term defining the value of the let statement.
        """
        return self.__enclosed_term

    def get_let_symbols_and_defining_terms(self):
        """
        Returns a sequence of pairs (x,y) with x being a constant name and y being the
        term defining the constant named by x.

        :return: a sequence of pairs (x,y) as described above.
        """
        return self.__pairs_of_symbols_and_defining_terms

    def set_enclosed_term(self, enclosed_term: ASTNode):
        """
        Sets the term enclosed by the let statement.
        :param enclosed_term: The new enclosed term.
        :return: None
        """
        self.__enclosed_term = enclosed_term

    def clone(self, decl_ast_node_substitution_map, decl_clone_memoization):
        assert self not in decl_ast_node_substitution_map.keys()

        replacing_let_term_node = LetTermASTNode(self.__pairs_of_symbols_and_defining_terms,
                                                 self.__enclosed_term)
        decl_ast_node_substitution_map[self] = replacing_let_term_node

        def_clones = [(name, term.clone(decl_ast_node_substitution_map, decl_clone_memoization))
                      for name, term in self.__pairs_of_symbols_and_defining_terms]
        enclosed_term_clone = self.__enclosed_term.clone(decl_ast_node_substitution_map, decl_clone_memoization)

        replacing_let_term_node.__pairs_of_symbols_and_defining_terms = def_clones
        replacing_let_term_node.__enclosed_term = enclosed_term_clone

        return replacing_let_term_node

    def __str__(self):
        return self.__class__.__name__ + " Symbols: " + str([x[0] for x in self.__pairs_of_symbols_and_defining_terms])


class FunctionApplicationASTNode(TermASTNode):
    """AST node class for terms representing a function application."""

    def __init__(self, declaration: FunctionDeclaration, argument_nodes, parameters: Tuple[int] = tuple()):
        """
        Initializes the FunctionApplicationASTNode object.

        :param declaration: The function's declaration.
        :param argument_nodes: The AST nodes of the function arguments.
        :param parameters: The function's parameters (i.e. the sequence of numerals in (_ fname num1 num2 ... numN)
                           expressions). If the function is not parametrized, this argument is required to be the
                           empty tuple.
        :raises ValueError if the function cannot be applied to the given arguments.
        """

        if len(argument_nodes) != declaration.get_signature().get_arity():
            raise ValueError("Illegal number of arguments for function " + declaration.get_name())

        arg_sorts = list(parameters) + [x.get_sort() for x in argument_nodes]
        self.__sort = declaration.get_signature().get_range_sort(arg_sorts)
        if self.__sort is None:
            raise ValueError("Illegally typed arguments for function " + declaration.get_name())

        self.__argument_nodes = argument_nodes
        self.__parameters = parameters
        self.__declaration = declaration

    def get_sort(self):
        return self.__sort

    def get_child_nodes(self):
        return tuple(self.__argument_nodes)

    def set_child_node(self, index: int, node: ASTNode):
        if index < 0 or index >= len(self.__argument_nodes):
            raise ValueError("index " + str(index) + " out of bounds")
        self.__argument_nodes[index] = node

    def get_parameters(self):
        """
        Returns the function's parameters, i.e. the sequence of numerals in (_ fname num1 num2 ... numN) expressions.
        If the function is not parametrized, the empty tuple is returned instead.

        :return: the function's parameters as described above.
        """
        return self.__parameters

    def get_declaration(self) -> FunctionDeclaration:
        """
        Gets the function's declaration, or None if no such node exists.
        :return: the function's declaration, or None if no such node exists.
        """
        return self.__declaration

    def set_declaration(self, declaration: FunctionDeclaration):
        """
        Sets the function's declaration.
        :param declaration: The function's declaration.
        :return: None
        :raises ValueError if the function cannot be applied to its arguments or if the new declaration would change
                           the term's sort.
        """
        if len(self.__argument_nodes) != declaration.get_signature().get_arity():
            raise ValueError("Illegal number of arguments for function " + declaration.get_name())

        arg_sorts = list(self.__parameters) + [x.get_sort() for x in self.__argument_nodes]
        new_sort = declaration.get_signature().get_range_sort(arg_sorts)
        if new_sort is None:
            raise ValueError("Illegally typed arguments for function " + declaration.get_name())
        if new_sort is not self.__sort:
            raise ValueError("New declaration illegally changes the term sort")
        self.__declaration = declaration

    def clone(self, decl_ast_node_substitution_map, decl_clone_memoization):
        argument_node_clones = [x.clone(decl_ast_node_substitution_map, decl_clone_memoization)
                                for x in self.__argument_nodes]
        parameters_clone = tuple(self.__parameters)

        if self.__declaration in decl_clone_memoization.keys():
            clone_decl = decl_clone_memoization[self.__declaration]
        elif self.__declaration.get_declaring_ast_node() in decl_ast_node_substitution_map.keys():
            new_declaring_node = decl_ast_node_substitution_map[self.__declaration.get_declaring_ast_node()]
            clone_decl = FunctionDeclaration(self.__declaration.get_name(),
                                             self.__declaration.get_signature(),
                                             new_declaring_node)
            decl_clone_memoization[self.__declaration] = clone_decl
        else:
            clone_decl = self.__declaration
        return FunctionApplicationASTNode(clone_decl, argument_node_clones, parameters_clone)

    def __str__(self):
        result = self.__class__.__name__ + " Function: " + self.__declaration.get_name() + " Sort: " + str(self.__sort)
        if len(self.__parameters) != 0:
            result += " Parameters: " + str(self.__parameters)
        return result
