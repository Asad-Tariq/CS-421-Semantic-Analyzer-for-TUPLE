from compatibility_spec import *

class Record:
    def __init__(self, name, return_type, scope, size):
        self.name = name
        self.return_type = return_type
        self.scope = scope
        self.size = size

class SymbolTable:
    def __init__(self):
        self.table = []

    def lookup(self, name, return_type, scope):
        if len(self.table) > 0:
            for record in self.table:
                if record.name == name and record.return_type == return_type and record.scope == scope:
                    return True
            return False

        else:
            return False

    def enter(self, name, return_type, scope, size):
        self.table.append(Record(name, return_type, scope, size))

    def check_return_type(self, name, scope):
        if len(self.table) > 0:
            for record in self.table:
                if record.name == name and record.scope == scope:
                    return record.return_type
            return None

    def print_table(self):
        for record in self.table:
            print("record name: ", record.name)
            print("record return type: ", record.return_type)
            print("record scope: ", record.scope)
            print("record size: ", record.size)