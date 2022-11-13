# The list of compatible types

type_equilvalence = {
                    ("int", "int", '+') : "int",
                    ("int", "int", '-') : "int",
                    ("int", "int", '*') : "int",
                    ("int", "int", '/') : "int",
                    ("float", "float", '+') : "float",
                    ("float", "float", '-') : "float",
                    ("float", "float", '*') : "float",
                    ("float", "float", '/') : "float",
                    ("int", "float", "*") : "float",
                    }