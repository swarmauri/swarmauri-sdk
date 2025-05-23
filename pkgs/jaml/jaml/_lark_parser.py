from importlib.resources import files
from lark import Lark
import jaml

# Read the grammar file from the package.
grammar = files(jaml).joinpath("grammar.lark").read_text()
parser = Lark(
    grammar, parser="earley", lexer="dynamic_complete", propagate_positions=True
)
