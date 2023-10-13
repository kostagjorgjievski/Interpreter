from intbase.py import InterpreterBase
from brewparse import parse_program

class Interpreter(InterpreterBase):
    def run(program):
        ast = parse_program(program)
        print(ast)