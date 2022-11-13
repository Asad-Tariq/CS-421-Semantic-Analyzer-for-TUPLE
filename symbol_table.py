class Record:
    ''''A record in the symbol table'''
    
    def __init__(self, name, return_type, scope, size):
        '''Initializes a record in the symbol table.
        
        Args:
        - name: the name of the symbol.
        - return_type: the return type of the symbol.
        - scope: the scope of the symbol.
        - size: the size of the symbol.

        Returns:
        None.
        '''
        
        self.name = name
        self.return_type = return_type
        self.scope = scope
        self.size = size

class SymbolTable:
    '''A symbol table'''

    def __init__(self):
        '''Initializes a symbol table.
        
        Args:
        None.

        Returns:
        None.
        '''
        
        self.table = []

    def lookup(self, name, return_type, scope) -> bool:
        ''' Looks up a symbol in the symbol table.

        Args:
        - name: the name of the symbol.
        - return_type: the return type of the symbol.
        - scope: the scope of the symbol.
        
        Returns:
        - True: if the symbol is in the symbol table.
        - False: if the symbol is not in the symbol table.
        '''

        if len(self.table) > 0:
            for record in self.table:
                if record.name == name and record.return_type == return_type and record.scope == scope:
                    return True
            return False

        else:
            return False

    def enter(self, name, return_type, scope, size) -> None:
        ''' Enters a symbol into the symbol table.
        
        Args:
        - name: the name of the symbol.
        - return_type: the return type of the symbol.
        - scope: the scope of the symbol.
        - size: the size of the symbol.

        Returns:
        None.
        '''

        self.table.append(Record(name, return_type, scope, size))

    def check_return_type(self, name, scope) -> str:
        ''' Checks the return type of a symbol in the symbol table.
        
        Args:
        - name: the name of the symbol.
        - scope: the scope of the symbol.

        Returns:
        - return_type: the return type of the symbol.
        '''

        if len(self.table) > 0:
            for record in self.table:
                if record.name == name and record.scope == scope:
                    return record.return_type
                elif record.name == name and record.scope != scope:
                    if record.scope == 0:
                        return record.return_type
            return None

    def print_table(self) -> None:
        ''' Prints the symbol table.

        Args:
        None.

        Returns:
        None.
        '''

        for record in self.table:
            print("record name: ", record.name)
            print("record return type: ", record.return_type)
            print("record scope: ", record.scope)
            print("record size: ", record.size)