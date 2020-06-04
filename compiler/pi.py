from compiler.core.Interpreter import Interpreter
from compiler.core.Lexer import Lexer
from compiler.core.Number import Number
from compiler.core.Parser import Parser
from compiler.core.util.Context import Context
from compiler.core.util.SymbolTable import SymbolTable

global_symbol_table = SymbolTable()
global_symbol_table.set("NULL", Number(0))
global_symbol_table.set("FALSE", Number(0))
global_symbol_table.set("TRUE", Number(1))


def run(fn, text):
    # Crear Tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generar el arbol
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # Ejecutar el programa
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    result = interpreter.visit(ast.node, context)

    return result.value, result.error
