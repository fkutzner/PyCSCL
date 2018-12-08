import abc
import examples.smt_qfbv_solver.sorts as sorts


class ASTNode(abc.ABC):
    """Base class for SMTLib2-language AST nodes."""

    @abc.abstractmethod
    def get_child_nodes(self):
        """
        Gets the node's child nodes.

        :return: The node's child nodes, a sequence of ASTNode objects.
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


class CommandASTNode(ASTNode, abc.ABC):
    """Base class for Command AST nodes."""
    pass


class AssertCommandASTNode(ASTNode):
    """AST node class for the assert command."""
    def __init__(self, asserted_term):
        self.__child_nodes = (asserted_term,)

    def get_child_nodes(self):
        return self.__child_nodes

    def __str__(self):
        return self.__class__.__name__


class PushPopCommandASTNode(ASTNode):
    """AST node class for the push and pop commands."""

    def __init__(self, is_push):
        """
        Initializes the PushPopCommandASTNode object.

        :param is_push: True iff the node is a push command node, False otherwise.
        """
        self.__is_push = is_push

    def get_child_nodes(self):
        return tuple()

    def is_push(self):
        """
        Determines whether the node represents a push or a pop command.

        :return: True iff the node represents a push command, False otherwise.
        """
        return self.__is_push

    def __str__(self):
        return self.__class__.__name__ + " " + ("Push" if self.__is_push else "Pop")


class CheckSATCommandASTNode(ASTNode):
    """AST node class for the check-sat command."""

    def get_child_nodes(self):
        return tuple()

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

    def __str__(self):
        sorts_as_str = [str(sort) for sort in self.__domain_sorts]

        return self.__class__.__name__ + " FunctionName: " + self.__fun_name \
            + " DomainSorts: " + str(sorts_as_str) \
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

    def get_logic_name(self):
        """
        Returns the SMT theory passed to set-logic command.

        :return: the name of the SMT theory passed to the set-logic command.
        """
        return self.__logic_name

    def __str__(self):
        return self.__class__.__name__ + " Logic: " + self.__logic_name


class TermASTNode(ASTNode, abc.ABC):
    """Base class for term AST nodes."""

    @abc.abstractmethod
    def get_sort(self) -> sorts.Sort:
        """
        Returns the term's sort.

        :return: the term's sort.
        """
        pass


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

    def get_literal(self):
        """
        Returns the literal.

        :return: the literal.
        """
        return self.__literal

    def __str__(self):
        return self.__class__.__name__ + " Literal: " + str(self.__literal) + " Sort: " + str(self.__sort)


class FunctionApplicationASTNode(TermASTNode):
    """AST node class for terms representing a function application."""

    def __init__(self, fname, argument_nodes, sort):
        """
        Initializes the FunctionApplicationASTNode object.

        :param fname: The function name.
        :param argument_nodes: The AST nodes of the function arguments.
        :param sort: The function's range sort.
        """
        self.__sort = sort
        self.__argument_nodes = argument_nodes
        self.__fname = fname

    def get_sort(self):
        return self.__sort

    def get_child_nodes(self):
        return tuple(self.__argument_nodes)

    def get_function_name(self):
        """
        Returns the applied function's name.

        :return: the applied function's name.
        """
        return self.__fname

    def __str__(self):
        return self.__class__.__name__ + " Function: " + self.__fname + " Sort: " + str(self.__sort)
