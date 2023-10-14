import unittest
from interpreterv1 import Interpreter

class InterpreterTest(unittest.TestCase):

    # ...previous test methods

    def test_nested_expression(self):
        program = '''
        func main() {
            b = ((5 + 3) - (2 - 3));
            print(b);  // Expected Output: 9
        }
        '''
        interpreter = Interpreter()
        interpreter.run(program)
        self.assertEqual(interpreter.get_output(), ['9'])

    def test_function_call_with_input(self):
        program = '''
        func main() {
            c = inputi("Enter a number: ");  // Assume user enters 7
            print(c);  // Expected Output: 7
        }
        '''
        interpreter = Interpreter(inp=['7'])
        interpreter.run(program)
        self.assertEqual(interpreter.get_output(), ['7'])

    def test_combining_input_and_arithmetic(self):
        program = '''
        func main() {
            d = inputi("Enter a number: ") + 5;  // Assume user enters 8
            print(d);  // Expected Output: 13
        }
        '''
        interpreter = Interpreter(inp=['8'])
        interpreter.run(program)
        self.assertEqual(interpreter.get_output(), ['13'])


if __name__ == '__main__':
    unittest.main()
