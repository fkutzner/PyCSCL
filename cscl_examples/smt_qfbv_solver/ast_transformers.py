import abc
from typing import List
import cscl_examples.smt_qfbv_solver.ast as ast


class ASTTransformer(abc.ABC):
    """
    Base class for AST transformations.
    """

    @abc.abstractmethod
    def transform(self, ast_nodes: List[ast.ASTNode]) -> List[ast.ASTNode]:
        """
        Transforms the AST (possibly in a destructive manner).

        :param ast_nodes: The AST, given as a list of AST nodes.
        :return: The transformed AST, as a list of AST nodes.
        """
        pass


class FunctionDefinitionInliner(ASTTransformer):
    @staticmethod
    def __create_expansion(term: ast.FunctionApplicationASTNode,
                           definition: ast.DefineFunCommandASTNode) -> ast.TermASTNode:
        """
        Expands a term wrt. a given definition.

        :param term: A function-application AST node.
        :param definition: The AST node defining the function of term.
        :return: The result of expanding term wrt. definition.
        """
        assert term.get_declaration().get_name() == definition.get_fun_name()
        parm_names = [x for x, _ in definition.get_formal_parameters()]
        defining_term = definition.get_child_nodes()[0]
        if len(parm_names) > 0:
            arg_terms = term.get_child_nodes()
            parm_bindings = zip(parm_names, arg_terms)
            assert isinstance(defining_term, ast.TermASTNode)
            result = ast.LetTermASTNode(list(parm_bindings), defining_term)
            defining_term_clone = defining_term.clone({definition: result}, dict())
            result.set_enclosed_term(defining_term_clone)
            return result
        else:
            return defining_term.clone(dict(), dict())

    def __transform_term(self, term: ast.TermASTNode) -> ast.TermASTNode:
        """
        Destructively expands all function symbols occurring in the given term that have
        a definition via define-fun.

        :param term: The term to be transformed.
        :return: The transformed term.
        """
        # TODO: expansion cycle detection
        if isinstance(term, ast.FunctionApplicationASTNode) \
           and isinstance(term.get_declaration().get_declaring_ast_node(), ast.DefineFunCommandASTNode):
            definition = term.get_declaration().get_declaring_ast_node()
            result = self.__create_expansion(term, definition)
        else:
            result = term

        # Transform child nodes.
        children = result.get_child_nodes()
        for i in range(0, len(children)):
            result.set_child_node(i, self.__transform_term(children[i]))

        return result

    def transform(self, ast_nodes: List[ast.ASTNode]) -> List[ast.ASTNode]:
        """
        Destructively expands all function symbols having a definition via define-fun.

        :param ast_nodes: The AST, given as a list of AST nodes.
        :return: The transformed AST, as a list of AST nodes.
        """
        for node in ast_nodes:
            if isinstance(node, ast.AssertCommandASTNode):
                node.set_child_node(0, self.__transform_term(node.get_child_nodes()[0]))
        return [x for x in ast_nodes if not isinstance(x, ast.DefineFunCommandASTNode)]
