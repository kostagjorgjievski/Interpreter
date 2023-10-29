from intbase import InterpreterBase
from intbase import ErrorType
from brewparse import parse_program
import collections

class Interpreter(InterpreterBase):
    def __init__(self, console_output=True, inp=None, trace_output=False):
        super().__init__(console_output, inp)
        #self.variable_to_value = {}
        #self.statements_values = []
        self.allowed_operations = ["+", "-", "*", "/", "==", "!=", "<", "<=", ">", ">=", "&&", "||"]
        self.call_stack = []
        self.all_functions_names_to_args = collections.defaultdict(list)
        self.all_functions = None



    def evaluate_func(self, function):
        for statement in function.get("statements"):
            result, ret = self.process_statement(statement)
            if ret:
                return result
        return None

    def func_arg_pass(self, var_name, var_value):
        self.call_stack[-1][var_name] = var_value

    def get_variable(self, var_name):
        for scope in self.call_stack[::-1]:
            if var_name in scope:
                return scope[var_name]
        
        self.error(ErrorType.NAME_ERROR, "Variable is not defined: " + str(var_name))

    def set_variable(self, var_name, var_value):
        
        for scope in self.call_stack[::-1]:
            if var_name in scope:
                scope[var_name] = var_value
                return
        self.call_stack[-1][var_name] = var_value

    def get_func(self, name, arg_count):
        for func in self.all_functions:
            if func.get("name") == name:
                if arg_count in self.all_functions_names_to_args[name]:
                    return func
        self.error(ErrorType.NAME_ERROR, "Function not found " + str(name))

    def process_statement(self, statement):
        # first we need to determine statement type (assignment or function call)
        statement_type = None

        #processing of arguments

        if statement.elem_type == "=":
            statement_type = "assignment"
        elif statement.elem_type == "fcall":
            statement_type = "function_call"
        elif statement.elem_type == "if":
            statement_type = "if"
        elif statement.elem_type == "while":
            statement_type = "while"
        elif statement.elem_type == "return":
            statement_type = "return"
        else:
            self.error(ErrorType.TYPE_ERROR, "Invalid statement type")



        # Evaluatiing expressions
        # if expression type is operation, call one func to evaluate
        # if expression type is function call, call another func to evalue
        if statement_type  == "assignment":
            statement_name = statement.get("name")
            statement_expression = statement.get("expression")
            # self.variable_to_value[statement_name] = self.evaluate_exp(statement_expression)
            var_name = statement_name
            var_value = self.evaluate_exp(statement_expression)
            self.set_variable(var_name, var_value)
        elif statement_type == "function_call":
            return_val = self.evaluate_expression_function_call(statement)
            if return_val != None:
                return return_val
        elif statement_type == "if":
            return_val, ret = self.evaluate_expression_if(statement)
            if ret:
                return [return_val, ret]
        elif statement_type == "while":
            return_val, ret = self.evaluate_expression_while(statement)
            if ret:
                return [return_val, True]
        elif statement_type == "return":
            statement_expression = statement.get("expression")
            return_val = self.evaluate_exp(statement_expression)
            return [return_val, True]
        else:
            self.error(ErrorType.FAULT_ERROR, "Invalid Statement Expression")

        return [None, False]

    def evaluate_expression_while(self, statement):
        MAX_ITERATIONS = 10000
        iterations = 0
        while self.evaluate_exp(statement.get("condition")): 
            if iterations > MAX_ITERATIONS:
                self.error("Max Iterations Error", "Max Iterations Error")
            for inside_statements in statement.get("statements"):
                res, ret = self.process_statement(inside_statements)
                if inside_statements.elem_type == "return" or ret == True:
                    return res
            iterations += 1
        return [None, False]

    def evaluate_expression_if(self, statement):
        res = self.evaluate_exp(statement.get("condition"))
        if res:
            for inside_statements in statement.get("statements"):
                if inside_statements.elem_type == "return":
                    return [self.process_statement(inside_statements), True]
                else:
                    self.process_statement(inside_statements)
        if not res and statement.get("else_statements") != None:
            for else_statements in statement.get("else_statements"):
                if else_statements.elem_type == "return":
                    return [self.process_statement(else_statements), True]
                else:
                    self.process_statement(else_statements)
        return [None, False]

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
            return [first_value, second_value]

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
            val = first_value and second_value
            if isinstance(val, bool) == False:
                self.error(ErrorType.TYPE_ERROR, "Operation must evaluate to bool")
            return val 
        elif expression.elem_type == "||":
            val = first_value or second_value
            if isinstance(val, bool) == False:
                self.error(ErrorType.TYPE_ERROR, "Operation must evaluate to bool")
            return val 
        elif expression.elem_type == "==":
            val = first_value == second_value
            if isinstance(val, bool) == False:
                self.error(ErrorType.TYPE_ERROR, "Operation must evaluate to bool")
            return val 
        elif expression.elem_type == "!=":
            val = first_value != second_value
            if isinstance(val, bool) == False:
                self.error(ErrorType.TYPE_ERROR, "Operation must evaluate to bool")
            return val 
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

        if first_value is None or second_value is None:
            if expression.elem_type == "==":
                return first_value == second_value
            elif expression.elem_type == "!=":
                return first_value != second_value
            else:
                self.error(ErrorType.TYPE_ERROR, "Invalid comparison between nil values")

        if type(first_value) != type(second_value):
            self.error(ErrorType.TYPE_ERROR, "Types have to be the same to preform operations'" + expression.elem_type + "' || " + str(type(first_value)) + " - " + str(type(second_value)) )

        if isinstance(first_value, bool) and isinstance(second_value, bool):
            return self.evaluate_boolean_operation(first_value, second_value, expression)

        if isinstance(first_value, int) and isinstance(second_value, int):
            return self.evaluate_integer_operation(first_value, second_value, expression)

        if isinstance(first_value, str) and isinstance(second_value, str):
            return self.evaluate_string_operation(first_value, second_value, expression)
         
        return 0


    def evaluate_exp(self, op):
        if op == None:
            return None
        if op.elem_type == "var":
            var_name = self.get_variable(op.dict.get("name"))
            # var_name = op.dict.get("name")
            # if var_name not in self.variable_to_value:
            #     self.error(ErrorType.NAME_ERROR, "Variable does not exist in map")
            return var_name
        if str(op.elem_type) in self.allowed_operations:
            return self.evaluate_expression_operation(op)
        if op.elem_type == "fcall":
            res = self.evaluate_expression_function_call(op)
            if isinstance(res, list):
                return res[0]
            else:
                return res
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
        if op.elem_type == "nil":
            return None

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
                    #self.output(prompt)
                try:
                    user_input = super().get_input()
                    return int(user_input)
                except ValueError:
                    self.error(ErrorType.TYPE_ERROR, "Input is not an integer | " + str(user_input))
            ### GPT citation ends here
        elif name_of_func in self.all_functions_names_to_args:
            #process custom functions
            input_argument_count = len(statement.get("args"))
            func = self.get_func(name_of_func, input_argument_count)
            if func != None:
                self.call_stack.append({})
                
                if input_argument_count in self.all_functions_names_to_args[func.get("name")]:
                    #func def with diff number of args 
                    for arg, input_value in zip(func.get("args"), statement.get("args")):
                        val = self.evaluate_exp(input_value)
                        self.func_arg_pass(arg.get("name"), val)

                    res = self.evaluate_func(func)
                    self.call_stack.pop()
                    return res
                else:
                    self.error(ErrorType.NAME_ERROR, "Function with that amount of arguments not found")
            else:
                self.error(ErrorType.NAME_ERROR, "Function not found: " + str(name_of_func))


        elif name_of_func == "inputs":
            if len(statement.get("args")) > 1:
                self.error(ErrorType.NAME_ERROR, "Inputs takes only one paramenter")
            else:
                if statement.get("args"):
                    prompt = self.evaluate_exp(statement.get("args")[0])
                    #self.output(prompt)
                user_input = super().get_input()
                return str(user_input)
        else:
            self.error(ErrorType.NAME_ERROR, "Function not found")

        return

    def evaluate_print(self, args):
        print_string = ""
        for arg in args:
            res = self.evaluate_exp(arg)
            if isinstance(res, list):
                res = res[0]
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
        self.all_functions = ast.get("functions")

        for func in self.all_functions:
            self.all_functions_names_to_args[func.get("name")].append(len(func.get("args")))

        main = self.get_func("main", 0)
        if not main:
            self.error(ErrorType.NAME_ERROR, "main is not defined")
    
        statements = main.get("statements")
        self.call_stack.append({})
        for statement in statements:
            res, ret = self.process_statement(statement)
            if ret:
                return res
        self.call_stack.pop()
        return -404


        