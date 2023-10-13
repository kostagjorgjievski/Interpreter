from intbase import InterpreterBase
from intbase import ErrorType
from brewparse import parse_program

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.variable_to_value = {}

    def find_main_func(self, node):
        if node.get("functions")[0].get("name") != "main":
            return [False, None]
        return [True, node.get("functions")[0]]

    def process_statement(self, statement):
        statement_name = statement.get("name")
        statement_expression = statement.get("expression")


        if statement_expression == None:
            self.error(ErrorType.TYPE_ERROR, "Statement expression is of None type")


        # Evaluatiing expressions
        # if expression type is operation, call one func to evaluate
        # if expression type is function call, call another func to evalue
        expression_type = None
        if statement_expression.elem_type in ["+", "-"]:
            self.variable_to_value[statement_name] = self.evaluate_expression_operation(statement_expression)
            print(self.variable_to_value)
        elif statement_expression.elem_type in "fcall":
            self.variable_to_value[statement_name] = self.evaluate_expression_function_call(statement_expression)
            print(self.variable_to_value)
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid statement for " + statement_name + ". The staement must match '+', '-', or 'fcall'.")


        for var, val in self.variable_to_value.items():
            print(var + " : " + str(val))
        return



    def evaluate_expression_operation(self, expression):
        mathematical_operation = None
        if expression == None:
            return 0
        if expression.elem_type == "+":
            mathematical_operation = "+"
        elif expression.elem_type == "-":
            mathematical_operation = "-"
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid mathematical operation '" + expression.elem_type)


        print(expression)
        if not expression.get("op1") or not expression.get("op2"):
            self.error(NAME_ERROR, "Expression op not found")

        print()
        print("OP1")
        print(expression.get("op1"))
        print(expression.get("op1").get("val"))
        print(expression.elem_type)

        first_value = None
        op1_type = self.determine_node_type(expression.get("op1"))
        print(op1_type)
        if op1_type == "var":
            var_name = expression.get("op1").dict
            if var_name not in self.variable_to_value:
                self.error(ErrorType.NAME_ERROR, "Variable does not exist in map")
            first_value = variable_to_value[var_name]
        elif op1_type == "value_int":
            first_value = expression.get("op1").dict.get("val")
        elif op1_type == "value_string":
            first_value = expression.get("op1").dict.get("val")
        elif op1_type == "expression_operation":
            first_value = evaluate_expression_operation(expression.get("op1"))
        elif op1_type == "expression_fcall":
            first_value = evaluate_expression_function_call(expression.get("op1"))
        else:
            self.error(ErrorType.NAME_ERROR, "Operation value does not exist: " + op1_type )


        second_value = None
        op2_type = self.determine_node_type(expression.get("op2"))
        if op2_type == "var":
            var_name = expression.get("op2").dict
            if var_name not in self.variable_to_value:
                self.error(ErrorType.NAME_ERROR, "Variable does not exist in map")
            second_value = variable_to_value[var_name]
        elif op2_type == "value_int":
            second_value = expression.get("op2").dict.get("val")
        elif op2_type == "value_string":
            second_value = expression.get("op2").dict.get("val")
        elif op2_type == "expression_operation":
            second_value = evaluate_expression_operation(expression.get("op2"))
        elif op2_type == "expression_fcall":
            second_value = evaluate_expression_function_call(expression.get("op2"))
        else:
            self.error(ErrorType.NAME_ERROR, "Operation value does not exist")



        if type(first_value) != type(second_value):
            self.error(ErrorType.TYPE_ERROR, "Expression Type Error Line 79")
        if mathematical_operation == "+":
            return first_value + second_value
        if mathematical_operation == "-":
            return first_value - second_value
         
        return 0


    def determine_node_type(self, op):
        if op.elem_type == "var":
            return "variable"
        if op.elem_type in ["+", "-"]:
            return "expression_operation"
        if op.elem_type == "fcall":
            return "expression_fcall"
        if op.elem_type == "int":
            return "value_int"
        if op.elem_type == "string":
            return "value_string"
        
        return None

    def evaluate_expression_function_call(self, statement_expression, statement_name):
        return


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
        