from lexer import *
from parser_spec import *
from compatibility_spec import *
from symbol_table import *
from typing import Dict, Tuple, List
import re


class Parser:
    """A recursive descent parser."""

    def __init__(self, token_list: List[str], symbol_table: Dict[int, str]) -> None:
        """Initializes the parser with the token stream from the lexer and the
        symbol table.

        Args:
        - self: this parser, the one to create. Mandatory object reference.
        - token_list: the token stream passed from the lexer.
        - symbol_table: the maintained symbol table.

        Returns:
        None.
        """

        self.token_list = token_list
        self.symbol_table = symbol_table
        self.token_index = 0
        self.current_token = self.token_list[self.token_index]
        self.current_function = ""
        self.parser_trace = []
        self.error_stream = {}
        self.semantic_errors = {}
        self.line_count = 0
        self.scope = 0
        self.parsing_symb_table = SymbolTable()
        self.return_stmt_type = None
        self.parser_trace.append("Scope: " + str(self.scope))

    def __checkToken(self) -> List[str]:
        """Returns the lexical unit and attribute of the current token.

        Args:
        - self: mandatory object reference.

        Returns:
        A split representation of the current token.
        """

        return self.current_token.split(", ")

    def __peekToken(self) -> str:
        """Returns the lookahead token. If the token stream has been parsed then
        the End of Stream token is returned.

        Args:
        - self: mandatory object reference.

        Returns:
        The lookahead token.
        """

        if self.token_index + 1 >= len(self.token_list):
            return "<$>"  # EOS token
        return self.token_list[self.token_index + 1]  

    def __nextToken(self) -> None:
        """Updates the current token.

        Args:
        - self: mandatory object reference.

        Returns:
        The lookahead token.
        """

        # increment pointer
        self.token_index += 1

        # upadate token if within bounds
        if self.token_index < len(self.token_list):
            self.current_token = self.token_list[self.token_index]

    def __updateTokens(self) -> Tuple[List[str], str]:
        """Returns the lexical unit and attribute of the current token in 
        addition to, the lookahead

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        tok = self.__checkToken()
        peek_tok = self.__peekToken()
        tok, peek_tok = self.__skipNewLine(tok, peek_tok)

        return tok, peek_tok

    def __skipNewLine(self, tok, peek_tok) -> Tuple[List[str], str]:
        """Skips the new line token.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        if tok[0] == "<newline>":
            self.__nextToken()
            tok, peek_tok = self.__updateTokens()
            self.line_count += 1
        
        return tok, peek_tok
    
    def __recordingErrors(self, tok, peek_tok) -> Tuple[List[str], str]:
        """Records the error and returns the next token.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        if len(tok) == 1:
            error = "Expected " + tok[0] + " but found " + peek_tok
        else:
            error = tok[1][:-1] + " cannot be parsed"
        
        self.parser_trace.append("Parsing Error!")
        try:
            self.error_stream[self.line_count].append(error)
        except KeyError:
            self.error_stream[self.line_count] = [error]
        
        # The panic recovery system
        self.__nextToken()
        tok, peek_tok = self.__updateTokens()

        return tok, peek_tok
    
    def __lookup(self, name, return_type) -> bool:
        """Checks if a variable/function is declared.

        Args:
        - self: mandatory object reference.
        - name: the name of the variable/function.
        - return_type: the return type of the variable/function.

        Returns:
        True if the variable/function is declared, False otherwise.
        """

        return self.parsing_symb_table.lookup(name, return_type, self.scope)

    def __redeclaration(self, name, return_type, id_type) -> None:
        """Checks for redeclaration of a variable/function.

        Args:
        - self: mandatory object reference.
        - name: the name of the variable/function.
        - return_type: the return type of the variable/function.
        - id_type: the type of the redeclaration to check.

        Returns:
        None.
        """

        if id_type == "Function":
            size = 2
        else:
            size = 1

        if self.__lookup(name, return_type) == False:
            self.parsing_symb_table.enter(name, return_type, self.scope, size)
        else:
            self.parser_trace.append("Re-declaration Error!")
            error = id_type + " " + name + " already defined in scope " + str(self.scope)
            try:
                self.semantic_errors[self.line_count].append(error)
            except KeyError:
                self.semantic_errors[self.line_count] = [error]
    
    def __undeclared(self, name, return_type) -> None:
        """Checks if a variable/function is declared.

        Args:
        - self: mandatory object reference.
        - name: the name of the variable/function.
        - return_type: the return type of the variable/function.

        Returns:
        True if the variable/function is declared, False otherwise.
        """

        if self.__lookup(name, return_type) == False:
            self.parser_trace.append("Undeclared Error!")
            error = "Undeclared identifier " + name
            try:
                self.semantic_errors[self.line_count].append(error)
            except KeyError:
                self.semantic_errors[self.line_count] = [error]

    def __incompatibility(self) -> None:
        """Checks for type incompatibility.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        self.parser_trace.append("Type Incompatibility Error!")
        error = "Type Incompatibility"
        try:
            self.semantic_errors[self.line_count].append(error)
        except KeyError:
            self.semantic_errors[self.line_count] = [error]
    
    def __checkassignment(self, type_one, type_two) -> bool:
        """Checks for assignment incompatibility.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        return type_one == type_two

    def __program(self) -> None:
        """The production rules for the 'Program' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN PROGRAM")
        tok, peek_tok = self.__updateTokens()
        function_name = None
        return_type = None

        if tok[0] in firstSet["program"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                return_type = tok[1][:-1]
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.current_function = tok[1]
                function_name = re.search("(.+?),", self.symbol_table[int(self.current_function[:-1])]).group(1)
                self.__redeclaration(function_name, return_type, "Function")
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["paramList"]:
                self.__paramList()
                # print("IN PROGRAM")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.parser_trace.append("In " + re.search("(.+?),", self.symbol_table[int(self.current_function[:-1])]).group(1) + "()")
                self.scope += 1
                self.parser_trace.append("Scope: " + str(self.scope))
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                # print("IN PROGRAM")
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.parser_trace.append("Exiting " + re.search("(.+?),", self.symbol_table[int(self.current_function[:-1])]).group(1) + "()")
                self.scope -= 1
                self.parser_trace.append("Scope: " + str(self.scope))
            if peek_tok in followSet["program"]:
                self.parser_trace.append("EOF")
                return
            
        if tok[0] in followSet["program"] or peek_tok in followSet["program"]:
            self.parser_trace.append("EOF")
            return

        if tok[0] not in firstSet["program"] or tok[1] not in firstSet["program"]:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            self.__program()

    def __paramList(self) -> None:
        """The production rules for the 'ParamList' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN PARAMLIST")
        tok, peek_tok = self.__updateTokens()
        param_name = None
        param_type = None

        if tok[0] in firstSet["paramList"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                param_type = tok[1][:-1]
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                param_name = re.search("(.+?),", self.symbol_table[int(tok[1][:-1])]).group(1)
                self.__redeclaration(param_name, param_type, "Identifier")
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["pList"]:
                self.__pList()
                # print("IN PARAMLIST")
                tok, peek_tok = self.__updateTokens()

        if tok[1] in followSet["paramList"]:
            return 

        if tok[0] not in firstSet["paramList"] and tok[1] not in firstSet["paramList"]:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __pList(self) -> None:
        """The production rules for the 'PList' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN PLIST")
        tok, peek_tok = self.__updateTokens()
        param_name = None
        param_type = None

        if tok[1] in firstSet["pList"]:
            if tok[1] == ",>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                param_type = tok[1][:-1]
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                param_name = re.search("(.+?),", self.symbol_table[int(tok[1][:-1])]).group(1)
                self.__redeclaration(param_name, param_type, "Identifier")
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["pList"]:
                self.__pList()
        
        elif tok[1] in followSet["pList"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __stmts(self) -> None:
        """The production rules for the 'Stmts' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN STMTS")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
            if tok[0] in firstSet["stmtsPrime"] or tok[1] in firstSet["stmtsPrime"]:
                self.__stmtsPrime()
                # print("IN STMTS")
                tok, peek_tok = self.__updateTokens()
            else:
                self.parser_trace.append("Parsing Error!")
                return
        
        elif tok[1] in followSet["stmts"]:
            self.parser_trace.append("matched <" + tok[1])
            
            self.__nextToken()
            # print("IN STMTS")
        
        elif "epsilon" in firstSet["stmts"] and tok[1] not in firstSet["stmts"] and tok[0] not in firstSet["stmts"]:
            self.__stmts()
            # print("IN STMTS")
            tok, peek_tok = self.__updateTokens()
        
        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __stmtsPrime(self) -> None:
        """The production rules for the "Stmts'" non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN STMTSPRIME")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["stmtsPrime"] or tok[1] in firstSet["stmtsPrime"]:
            if tok[0] in firstSet["decStmts"]:
                self.__decStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            if tok[0] in firstSet["assignStmt"]:
                self.__assignStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            if tok[1] in firstSet["forStmt"]:
                self.__forStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            if tok[1] in firstSet["ifStmt"]:
                self.__ifStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            if tok[1] in firstSet["returnStmt"]:
                self.return_stmt_type = self.__returnStmt()
                tok, peek_tok = self.__updateTokens()
                self.__stmtsPrime()
            else:
                return

        elif tok[1] in followSet["stmtsPrime"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __decStmt(self) -> None:
        """The production rules for the 'DecStmts' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN DECSTMT")
        tok, peek_tok = self.__updateTokens()
        identifier_name = None
        identifier_type = None

        if tok[0] in firstSet["decStmts"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                identifier_type = tok[1][:-1]
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                identifier_name = re.search("(.+?),", self.symbol_table[int(tok[1][:-1])]).group(1)
                self.__redeclaration(identifier_name, identifier_type, "Identifier")
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["optionalAssign"]:
                self.__optionalAssign()
                # print("IN DECSTMT")
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 1:
                if tok[0] in firstSet["list"]:
                    self.__list()
                    # print("IN DECSTMT")
                    tok, peek_tok = self.__updateTokens()
            if len(tok) == 2:
                if tok[1] in firstSet["list"]:
                    self.__list()
                    # print("IN DECSTMT")
                    tok, peek_tok = self.__updateTokens()
            if len(tok) == 2 and tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["decStmts"] or tok[1] in followSet["decStmts"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __list(self) -> None:
        """The production rules for the 'List' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN LIST")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["list"]:
            if tok[1] == ",>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["optionalAssign"]:
                self.__optionalAssign()
                # print("IN DECSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] in firstSet["list"]:
                self.__list()
            else:
                return
        
        elif tok[0] in followSet["list"]:
            return

        elif tok[1] in followSet["list"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __optionalAssign(self) -> None:
        """The production rules for the 'OptionalAssign' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN OPTIONALASSIGN")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["optionalAssign"]:
            self.parser_trace.append("matched <" + tok[1])
            self.__nextToken()
            tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                # print("IN OPTIONALASSIGN")
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 1:
                if tok[0] == ";>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
            elif len(tok) == 2:
                if tok[1] == ";>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
            else:
                return
        
        elif tok[0] in followSet["optionalAssign"]:
            return

        elif tok[1] in followSet["optionalAssign"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __assignStmt(self) -> None:
        """The production rules for the 'AssignStmt' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN ASSIGNSTMT")
        tok, peek_tok = self.__updateTokens()
        identifier_name = None
        identifier_type = None

        if tok[0] in firstSet["assignStmt"]:
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                identifier_name = re.search("(.+?),", self.symbol_table[int(tok[1][:-1])]).group(1)
                identifier_type = self.parsing_symb_table.check_return_type(identifier_name, self.scope)
                self.__undeclared(identifier_name, identifier_type)
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 2 and tok[1] == "=>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"]:
                expr_type = self.__expr()
                # print("IN ASSIGNSTMT")
                if self.__checkassignment(identifier_type, expr_type) == False:
                    self.parser_trace.append("ERROR: Type mismatch in assignment")
                    error = "ERROR: Type mismatch in assignment"
                    try:
                        self.semantic_errors[self.line_count].append(error)
                    except KeyError:
                        self.semantic_errors[self.line_count] = [error]
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 2 and tok[1] in firstSet["expr"]:
                expr_type = self.__expr()
                # print("IN ASSIGNSTMT")
                tok, peek_tok = self.__updateTokens()
            if len(tok) == 2 and tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()

        elif tok[1] in followSet["assignStmt"]:
            return
        
        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __expr(self) -> None:
        """The production rules for the 'Expr' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN EXPR")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
            if tok[0] in firstSet["t"] or tok[1] in firstSet["t"]:
                t_type = self.__t()
                # print("IN EXPR")
            if tok[1] in firstSet["ePrime"]:
                e_prime_type = self.__ePrime(t_type)
                return e_prime_type
                # print("IN EXPR")
            if "epsilon" in firstSet["ePrime"] and tok[1] not in firstSet["ePrime"]:
                e_prime_type = self.__ePrime(t_type)
                return e_prime_type
                # print("IN EXPR")

        elif tok[0] in followSet["expr"]:
            return e_prime_type

        elif tok[1] in followSet["expr"]:
            return e_prime_type

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __ePrime(self, left_type) -> None:
        """The production rules for the "Expr'" non-terminal.

        Args:
        - self: mandatory object reference.
        - left_type: the type of the left side of the expression.

        Returns:
        None.
        """

        # print("IN EPRIME")
        tok, peek_tok = self.__updateTokens()

        if len(tok) == 1:
            if tok[0][1:] in firstSet["ePrime"]:
                if tok[0][1:] == "+>":
                    self.parser_trace.append("matched <" + tok[0][1:])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
                if tok[0][1:] in firstSet["t"] or tok[0] in firstSet["t"]:
                    t_type = self.__t()
                    # print("IN EPRIME")
                    # tok, peek_tok = self.__updateTokens()
                    if (left_type, t_type, "+") not in type_equilvalence.keys():
                        self.__incompatibility()
                        return None
                    else:
                        return type_equilvalence[(left_type, t_type, "+")]
                if len(tok) == 1:
                    if tok[0] in firstSet["ePrime"]:
                        e_prime_type = self.__ePrime()
                        tok, peek_tok = self.__updateTokens()
                if len(tok) == 2:
                    if tok[1] in firstSet["ePrime"]:
                        e_prime_type = self.__ePrime()
                        tok, peek_tok = self.__updateTokens()
                else:
                    if (left_type, t_type, "+") not in type_equilvalence.keys():
                        self.__incompatibility()
                        return t_type
                    else:
                        return type_equilvalence[(left_type, t_type, "+")]

            else:
                if (left_type, t_type, "+") not in type_equilvalence.keys():
                    self.__incompatibility()
                    return t_type
                else:
                    return type_equilvalence[(left_type, t_type, "+")]

        elif len(tok) == 2:
            if tok[0] in firstSet["ePrime"]:
                if tok[0] == "+>":
                    self.parser_trace.append("matched <" + tok[0][1:])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
                if tok[0] in firstSet["t"]:
                    t_type = self.__t()
                    # print("IN EPRIME")
                    tok, peek_tok = self.__updateTokens()
                if tok[1] in firstSet["ePrime"]:
                    e_prime_type = self.__ePrime()
                else:
                    if (left_type, t_type, "+") not in type_equilvalence.keys():
                        self.__incompatibility()
                        return t_type
                    else:
                        return type_equilvalence[(left_type, t_type, "+")]

            else:
                return left_type
                # if (left_type, t_type, "+") not in type_equilvalence.keys():
                #     self.__incompatibility()
                #     return t_type
                # else:
                #     return type_equilvalence[(left_type, t_type, "+")]

        elif tok[0][1:] in followSet["ePrime"]:
            return t_type

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return t_type

    def __t(self) -> None:
        """The production rules for the 'T' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN T")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["t"] or tok[1] in firstSet["t"]:
            if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
                f_type = self.__f()
                # print("f_type: ", f_type)
                # tok, peek_tok = self.__updateTokens()
                # print("IN T")

            if len(tok) == 2:
                if tok[1] in firstSet["tPrime"]:
                    t_prime_type = self.__tPrime(f_type)
                    # print("IN T")
                    tok, peek_tok = self.__updateTokens()
            
            if "epsilon" in firstSet["tPrime"] and tok[0] not in firstSet["tPrime"]:
                t_prime_type = self.__tPrime(f_type)
                return t_prime_type
                # print("IN T")

        elif tok[0] in followSet["t"]:
            return t_prime_type

        elif tok[1] in followSet["t"]:
            return t_prime_type

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return t_prime_type

    def __tPrime(self, f_type) -> None:
        """The production rules for the "T'" non-terminal.

        Args:
        - self: mandatory object reference.
        - f_type: the type of the 'f' non-terminal.

        Returns:
        None.
        """

        # print("IN TPRIME")
        tok, peek_tok = self.__updateTokens()

        if len(tok) == 2:
            if tok[1] in firstSet["tPrime"]:
                if tok[1] == "*>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.__nextToken()
                if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
                    f_type = self.__f()
                    # print("IN TPRIME")
                    tok, peek_tok = self.__updateTokens()
                if tok[1] in firstSet["tPrime"]:
                    f_type = self.__tPrime(f_type)
                    # print("IN TPRIME")
                return f_type

            else:
                return f_type

        elif len(tok) == 1:
            if tok[0][1:] in firstSet["tPrime"]:
                if tok[0][1:] == "*>":
                    self.parser_trace.append("matched <" + tok[0][1:])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
                if tok[0] in firstSet["f"]:
                    f_type = self.__f()
                    # print("IN TPRIME")
                    tok, peek_tok = self.__updateTokens()
                if len(tok) == 2 and tok[1] in firstSet["tPrime"]:
                    f_type = self.__f()
                    # print("IN TPRIME")
                    tok, peek_tok = self.__updateTokens()
                if tok[0][1:] in firstSet["tPrime"]:
                    f_type = self.__tPrime(f_type)
                    # print("IN TPRIME")
                    return f_type
                else:
                    return f_type
            
            else:
                return f_type

        elif tok[0][1:] in followSet["tPrime"]:
            return f_type
        
        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return f_type

    def __f(self) -> None:
        """The production rules for the 'F' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN F")
        tok, peek_tok = self.__updateTokens()
        return_type = None

        if tok[0] in firstSet["f"] or tok[1] in firstSet["f"]:
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                    self.__expr()
                    # print("IN F")
                if tok[1] == ")>":
                    self.parser_trace.append("matched <" + tok[1])
                    self.__nextToken()
                    tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                identifier_name = re.search("(.+?),", self.symbol_table[int(tok[1][:-1])]).group(1)
                return_type = self.parsing_symb_table.check_return_type(identifier_name, self.scope)
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                return return_type
                
        elif tok[0] in followSet["f"]:
            return return_type

        elif tok[1] in followSet["f"]:
            return return_type

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return return_type

    def __forStmt(self) -> None:
        """The production rules for the 'ForStmt' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN FORSTMT")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["forStmt"]:  
            if tok[1] == "for>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["type"]:
                self.__type()
                # print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if "epsilon" in firstSet["type"] and tok[1] not in firstSet["type"]:
                self.__type()
                # print("IN FORSTMT")
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                # print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                # print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<rel_op":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                # print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<id":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<+>" and peek_tok == "<+>":
                self.parser_trace.append("matched " + tok[0][0:2] + peek_tok[1:2] + ">")
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.scope += 1
                self.parser_trace.append("Scope: " + str(self.scope))
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                # print("IN FORSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.scope -= 1
                self.parser_trace.append("Scope: " + str(self.scope))
        
        elif tok[0] in followSet["forStmt"]:
            return

        elif tok[1] in followSet["forStmt"]:
            return
        
        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __type(self) -> None:
        """The production rules for the 'Type' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN TYPE")
        tok, peek_tok = self.__updateTokens()

        if tok[0] in firstSet["type"]:
            if tok[0] == "<dt":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            else:
                return

        elif tok[0] in followSet["type"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __ifStmt(self) -> None:
        """The production rules for the 'IfStmt' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN IFSTMT")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["ifStmt"]:
            if tok[1] == "if>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "(>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                # print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[0] == "<rel_op":
                self.parser_trace.append("matched " + tok[0] + ", " + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                self.__expr()
                # print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ")>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.scope += 1
                self.parser_trace.append("Scope: " + str(self.scope))
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                # print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.scope -= 1
                self.parser_trace.append("Scope: " + str(self.scope))
            if tok[1] in firstSet["optionalElse"]:
                self.__optionalElse()
                # print("IN IFSTMT")
                tok, peek_tok = self.__updateTokens()

        elif tok[0] in followSet["ifStmt"]:
            return

        elif tok[1] in followSet["ifStmt"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __optionalElse(self) -> None:
        """The production rules for the 'OptionalElse' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN OPTIONALELSE")
        tok, peek_tok = self.__updateTokens()

        if tok[1] in firstSet["optionalElse"]:
            if tok[1] == "else>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.scope += 1
                self.parser_trace.append("Scope: " + str(self.scope))
            if tok[1] == "{>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["stmts"] or tok[1] in firstSet["stmts"]:
                self.__stmts()
                # print("IN OPTIONALELSE")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == "}>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                self.scope -= 1
                self.parser_trace.append("Scope: " + str(self.scope))
            else:
                return

        elif tok[0] in followSet["optionalElse"]:
            return

        elif tok[1] in followSet["optionalElse"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def __returnStmt(self) -> None:
        """The production rules for the 'ReturnStmt' non-terminal.

        Args:
        - self: mandatory object reference.

        Returns:
        None.
        """

        # print("IN RETURNSTMT")
        tok, peek_tok = self.__updateTokens()
        
        if tok[1] in firstSet["returnStmt"]:
            if tok[1] == "return>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
            if tok[0] in firstSet["expr"] or tok[1] in firstSet["expr"]:
                expr_type = self.__expr()
                # print("IN RETURNSTMT")
                tok, peek_tok = self.__updateTokens()
            if tok[1] == ";>":
                self.parser_trace.append("matched <" + tok[1])
                self.__nextToken()
                tok, peek_tok = self.__updateTokens()
                return expr_type

        elif tok[0] in followSet["returnStmt"]:
            return

        elif tok[1] in followSet["returnStmt"]:
            return

        else:
            tok, peek_tok = self.__recordingErrors(tok, peek_tok)
            return

    def parseToken(self) -> List[str]:
        """Public method that instigates the parsing.

        Args:
        - self: mandatory object reference.

        Returns:
        The output of the parser in the form of a trace of the syntax analysis.
        """

        self.__program()
        # self.parsing_symb_table.print_table()
        return self.parser_trace, self.error_stream, self.semantic_errors, self.parsing_symb_table
            