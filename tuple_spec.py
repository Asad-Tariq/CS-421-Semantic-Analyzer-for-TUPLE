# the language specification for TUPLE

keywords = ["and", "break", "continue", "else", "false", "for", "if", "mod", "not", "or", "print", "return", "str", "then",
            "true", "void", "while"]
data_types = ["bool", "char", "int", "float"]
punctuation = ["{", "}", "(", ")", ";", "[", "]", "\'", "\"", ",", "."]
relational_ops_single = {"<": "LT", ">": "GT"}
relational_op_double = {"<=": "LE", ">=": "GE", "==": "EQ", "!=": "NE"}
arithmetic_op = ["+", "-", "*", "/", "^"]
assignment = "="
underscore = "_"
whitespaces = {" ": "blank", "\n": "newline", "\t": "tab"}
letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUWXYZ"
digits = "0123456789"
