import importlib.resources as pkg_resources
from lark import Lark
import jaml 

# Read the grammar file from the package.
grammar = pkg_resources.read_text(jaml, 'grammar.lark')

parser = Lark(grammar, parser="earley", lexer="dynamic_complete")
