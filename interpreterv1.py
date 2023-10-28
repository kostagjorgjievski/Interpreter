from intbase import InterpreterBase
from intbase import ErrorType
from brewparse import parse_program

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        self.variable_to_value = {}
        self.statements_values = []
        self.allowed_operations = ["+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">=", "&&", "||"]

    def find_main_func(self, node):
        for func in node.get("functions"):
            if func.get("name") == "main":
                return [True, func]

        return [False, None]

    def process_statement(self, statement):
        # first we need to determine statement type (assignment or function call)
        statement_type = None

        if statement.elem_type == "=":
            statement_type = "assignment"
        elif statement.elem_type == "fcall":
            statement_type = "function_call"
        elif statement.elem_type == "if":
            statement_type = "if"
        elif statement.elem_type == "while":
            statement_type = "while"
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid statement type")

        statement_name = statement.get("name")


        # Evaluatiing expressions
        # if expression type is operation, call one func to evaluate
        # if expression type is function call, call another func to evalue
        if statement_type  == "assignment":
            statement_expression = statement.get("expression")
            self.variable_to_value[statement_name] = self.evaluate_exp(statement_expression)
        elif statement_type == "function_call":
            self.variable_to_value[statement_name] = self.evaluate_expression_function_call(statement)
        elif statement_type == "if":
            self.evaluate_expression_if(statement)
            return
        elif statement_type == "while":
            self.evaluate_expression_while(statement)
            return

        return self.statements_values.append(self.variable_to_value[statement_name])

    def evaluate_expression_while(self, statement):
        while self.evaluate_exp(statement.get("condition")):
            for inside_statements in statement.get("statements"):
                self.process_statement(inside_statements)

    def evaluate_expression_if(self, statement):
        res = self.evaluate_exp(statement.get("condition"))
        if res:
            for inside_statements in statement.get("statements"):
                self.process_statement(inside_statements)
        if not res and statement.get("else_statements") != None:
            for else_statements in statement.get("else_statements"):
                self.process_statement(else_statements)
        return

    def evaluate_expression_assignment(self, expression):
        return evaluate_exp(expression)


    def get_first_second_value(self, expression):
        if not expression.get("op1") or not expression.get("op2"):
            self.error(ErrorType.NAME_ERROR, "Expression op not found")
        
        first_value = self.evaluate_exp(expression.get("op1"))
        second_value = self.evaluate_exp(expression.get("op2"))


        if isinstance(first_value, bool) and isinstance(second_value, bool):
            return [first_value, second_value]

        if first_value == None or second_value == None:
            self.error(ErrorType.NAME_ERROR, "Operation value does not exist")

        return [first_value, second_value]


    def evaluate_integer_operation(self, first_value, second_value, expression):
        #TO DO (HANDLE URINARY OPERATORS)
        if expression == None:
            return 0
            # MIGHT CAUSE ERROR
        if expression.elem_type == "+":
            return first_value + second_value
        elif expression.elem_type == "-":
            return first_value - second_value
        elif expression.elem_type == "/":
            try:
                return first_value // second_value
            except ZeroDivisionError:
                self.error(ErrorType.ZERO_DIVISION, "You cannot divide by zero")
        elif expression.elem_type == "*":
            return first_value * second_value
        elif expression.elem_type == "==":
            return first_value == second_value
        elif expression.elem_type == "!=":
            return first_value != second_value
        elif expression.elem_type == "<":
            return first_value < second_value
        elif expression.elem_type == "<=":
            return first_value <= second_value
        elif expression.elem_type == ">":
            return first_value > second_value
        elif expression.elem_type == ">=":
            return first_value >= second_value
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid integer operation '" + expression.elem_type + "',  first_value = " + str(first_value) + " second_value = " + str(second_value))
        return

    def evaluate_boolean_operation(self, first_value, second_value, expression):
        #gotta deal with unary opeartor !
        if expression is None:
            return False
            # MIGHT CAUSE ERROR
        if expression.elem_type == "&&":
            return first_value and second_value
        elif expression.elem_type == "||":
            return first_value or second_value
        elif expression.elem_type == "==":
            return first_value == second_value
        elif expression.elem_type == "!=":
            return first_value != second_value
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid boolean operation '" + expression.elem_type + "' ")
            
    def evaluate_string_operation(self, first_value, second_value, expression):
        if expression == None:
            return 0
            # MIGHT CAUSE ERROR
        if expression.elem_type == "+":
            return first_value + second_value
        elif expression.elem_type == "==":
            return first_value == second_value
        elif expression.elem_type == "!=":
            return first_value != second_value
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid string operation '" + expression.elem_type + "' ")


    def evaluate_expression_operation(self, expression):
        first_value, second_value = self.get_first_second_value(expression)
        if type(first_value) != type(second_value):
            self.error(ErrorType.TYPE_ERROR, "Types have to be the same to preform operations'" + expression.elem_type + "' ")

        if isinstance(first_value, bool) and isinstance(second_value, bool):
            return self.evaluate_boolean_operation(first_value, second_value, expression)

        if isinstance(first_value, int) and isinstance(second_value, int):
            return self.evaluate_integer_operation(first_value, second_value, expression)


        if isinstance(first_value, str) and isinstance(second_value, str):
            return self.evaluate_string_operation(first_value, second_value, expression)
         
        return 0


    def evaluate_exp(self, op):

        if op.elem_type == "var":
            var_name = op.dict.get("name")
            if var_name not in self.variable_to_value:
                self.error(ErrorType.NAME_ERROR, "Variable does not exist in map")
            return self.variable_to_value[var_name]
        if str(op.elem_type) in self.allowed_operations:
            return self.evaluate_expression_operation(op)
        if op.elem_type == "fcall":
            return self.evaluate_expression_function_call(op)
        if op.elem_type == "int":
            return op.dict.get("val")
        if op.elem_type == "string":
            return op.dict.get("val")
        if op.elem_type == "bool":
            return op.dict.get("val")
        if op.elem_type == "neg":
            return (-1) * self.evaluate_exp(op.dict.get("op1"))
        if op.elem_type == "!":
            return not op.dict.get("op1")

        self.error(ErrorType.NAME_ERROR, "Value not found: " + str(op.elem_type))

    def evaluate_expression_function_call(self, statement):
        name_of_func = statement.get("name")
        if name_of_func == "print":
            self.evaluate_print(statement.get("args"))
        elif name_of_func == "inputi":
            ### 99->109 The following code was written using the help of ChatGPT to solve
            ### test case where inputi was not working properly.
            if len(statement.get("args")) > 1:
                self.error(ErrorType.NAME_ERROR, "Inputi takes only one paramenter")
            else:
                if statement.get("args"):
                    prompt = self.evaluate_exp(statement.get("args")[0])
                    #self.output(prompt) COMMENTED FOR TESTING
                try:
                    user_input = super().get_input()
                    return int(user_input)
                except ValueError:
                    self.error(ErrorType.TYPE_ERROR, "Input is not an integer")
            ### GPT citation ends here
        elif name_of_func in "inputs":
            #process custom functions
            user_input = super().get_input()
            return str(user_input)
        else:
            self.error(ErrorType.NAME_ERROR, "Function not found")

        return

    def evaluate_print(self, args):
        print_string = ""
        for arg in args:
            res = self.evaluate_exp(arg)
            #Dealing with bools is different
            if isinstance(res, bool):
                print_string += str(res).lower()
            else:
                print_string += str(res)
        self.output(print_string)

    # def evaluate_inputi(self, args):
    #     promt_string = ""
    #     for arg in args:
    #         promt_string += str(self.evaluate_exp(arg))
    #     self.output(promt_string)
    #     input_val = self.get_input()

    #     while input_val is None:
    #         input_val = self.get_input()
    #     return input_val

    def run(self, program):
        ast = parse_program(program)

        valid, main = self.find_main_func(ast)
        if not valid:
            self.error(ErrorType.NAME_ERROR, "main is not defined")

        all_functions = ast.get("functions")
        for func in all_functions:
            print(func)

        statements = main.get("statements")
        for statement in statements:
            self.process_statement(statement)

        return -404


        