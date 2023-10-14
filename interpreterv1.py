from intbase import InterpreterBase
from intbase import ErrorType
from brewparse import parse_program

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.variable_to_value = {}
        self.statements_values = []

    def find_main_func(self, node):
        if node.get("functions")[0].get("name") != "main":
            return [False, None]
        return [True, node.get("functions")[0]]

    def process_statement(self, statement):
        # first we need to determine statement type (assignment or function call)
        statement_type = None
        if statement.elem_type == "=":
            statement_type = "assignment"
        elif statement.elem_type == "fcall":
            statement_type = "function_call"
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid statement type")


        statement_name = statement.get("name")

        # Evaluatiing expressions
        # if expression type is operation, call one func to evaluate
        # if expression type is function call, call another func to evalue
        if statement_type  == "assignment":
            statement_expression = statement.get("expression")
            print("NAME: " + str(statement.get("name")))
            print("EXP: " + str(statement_expression) )
            self.variable_to_value[statement_name] = self.evaluate_exp(statement_expression)
            print(self.variable_to_value)
        elif statement_type == "function_call":
            self.variable_to_value[statement_name] = self.evaluate_expression_function_call(statement)

        return self.statements_values.append(self.variable_to_value[statement_name])


    def evaluate_expression_assignment(self, expression):
        return evaluate_exp(expression)

    def evaluate_expression_operation(self, expression):
        mathematical_operation = None
        if expression == None:
            return 0
        if expression.elem_type == "+":
            mathematical_operation = "+"
        elif expression.elem_type == "-":
            mathematical_operation = "-"
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid mathematical operation '" + expression.elem_type + "' ")


        print(expression)
        if not expression.get("op1") or not expression.get("op2"):
            self.error(ErrorType.NAME_ERROR, "Expression op not found")

        first_value = self.evaluate_exp(expression.get("op1"))
        second_value = self.evaluate_exp(expression.get("op2"))
        print(str(first_value) + " __________  " + str(second_value))
        if not first_value or not second_value:
            self.error(ErrorType.NAME_ERROR, "Operation value does not exist")



        if type(first_value) != type(second_value):
            self.error(ErrorType.TYPE_ERROR, "Expression Type Error Line 79")
        if mathematical_operation == "+":
            return first_value + second_value
        if mathematical_operation == "-":
            return first_value - second_value
         
        return 0


    def evaluate_exp(self, op):
        if op.elem_type == "var":
            var_name = op.dict.get("name")
            if var_name not in self.variable_to_value:
                self.error(ErrorType.NAME_ERROR, "Variable does not exist in map")
            return self.variable_to_value[var_name]
        if op.elem_type in ["+", "-"]:
            return self.evaluate_expression_operation(op)
        if op.elem_type == "fcall":
            return self.evaluate_expression_function_call(op)
        if op.elem_type == "int":
            return op.dict.get("val")
        if op.elem_type == "string":
            return op.dict.get("val")
        return None

    def evaluate_expression_function_call(self, statement):
        name_of_func = statement.get("name")
        if name_of_func == "print":
            self.evaluate_print(statement.get("args"))
        elif name_of_func == "inputi":
            return_val = int(self.evaluate_inputi(statement.get("args")))
            return return_val
        else:
            self.error(ErrorType.NAME_ERROR, "Function not found")

        return

    def evaluate_print(self, args):
        print_string = ""
        for arg in args:
            print_string += str(self.evaluate_exp(arg))
        self.output(print_string)

    def evaluate_inputi(self, args):
        promt_string = ""
        for arg in args:
            promt_string += str(self.evaluate_exp(arg))
        input_val = self.get_input(promt_string)
        return input_val

    def run(self, program):
        ast = parse_program(program)
        print()
        print(ast)

        valid, main = self.find_main_func(ast)

        if not valid:
            self.error(ErrorType.NAME_ERROR, "main is not defined")

        statements = main.get("statements")
        for statement in statements:
            self.process_statement(statement)


        