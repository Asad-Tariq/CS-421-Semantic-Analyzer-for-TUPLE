from tuple_spec import *
from typing import Dict, Tuple


class Lexer:
    """An lexical analyzer."""

    def __init__(self, input_stream: str, symbol_table: Dict[int, str], symbol_count: int) -> None:
        """Initializes the lexer for the given portion of the input stream.

        Args:
        - self: this lexer, the one to create. Mandatory object reference.
        - input_stream: the portion of the input stream being tokenized - a
        particular line.
        - symbol_table: the maintained symbol table.
        - symbol_count: the number of entries in the symbol table.

        Returns:
        None.
        """

        self.input = input_stream + '\n'
        self.cur_char = ''
        self.cur_pos = -1
        self.symbol_table = symbol_table
        self.symbol_count = symbol_count
        self.error = ""
        self.__next_char()

    def __next_char(self, step: int = 1) -> None:
        """Updates the file pointer by the given step - a default jump of
        one - and in turn, updates the current character being processed.

        Args:
        - self: mandatory object reference.
        - step: an integer corresponding to the increment to the file pointer.
        It has a default value of one.

        Returns:
        None.
        """

        self.cur_pos += step
        if self.cur_pos >= len(self.input):
            self.cur_char = '\0'  # EOF char
        else:
            self.cur_char = self.input[self.cur_pos]

    def peek(self) -> str:
        """Returns the lookahead character.

        Args:
        - self: mandatory object reference.

        Returns:
        the character at the next position from the one currently being
        pointed to.
        """

        if self.cur_pos + 1 >= len(self.input):
            return '\0'
        return self.input[self.cur_pos + 1]

    def __find_symb_tbl_ix(self, identifier: str) -> int:
        """Retrieves the symbol table index for an identifier that
        is already recorded in the symbol table.

        Args:
        - self: mandatory object reference.
        - identified: the identifier to look for.

        Returns:
        an integer corresponding to the specified identifier's index
        in the symbol table
        """

        for ix, val in self.symbol_table.items():
            if val == f'{identifier}, id':
                return ix

    def __check_comment(self) -> str:
        """Evaluates and returns a token corresponding to whether or not
        a valid comment is encountered or not.

        Args:
        - self: mandatory object reference.

        Returns:
        a token that denotes the validity of the encountered comment.
        """

        token = ""
        if self.peek() == "$":
            self.__next_char(2)
            while self.cur_char != "$":
                self.__next_char()
            if self.peek() == "/":
                token = "<Comment>"
                self.__next_char(2)
            elif self.peek() == "\n":
                token = "<Invalid Comment>"
                self.error = "Comment not closed properly!"
                while self.cur_char != "\n":
                    self.__next_char()
            elif self.peek() == "$":
                while self.peek() != "/":
                    self.__next_char()
                if self.peek() == "/":
                    token = "<Comment>"
                    self.__next_char(2)
        elif self.cur_char in arithmetic_op:
            # if a '/' is encountered, record as arithmetic operator
            token = f'<{self.cur_char}>'
            self.__next_char()

        return token

    def __check_key_dt_id(self) -> str:
        """Evaluates and returns a token corresponding to whether or not
        a keyword, data-type or (valid/invalid) identifier is encountered.

        Args:
        - self: mandatory object reference.

        Returns:
        a token that denotes whether or not a reserved word, data-type or
        identifier is encountered.
        """

        save_string = ""
        token = ""
        while self.cur_char in letters or self.cur_char in digits or self.cur_char in underscore:
            save_string += self.cur_char
            self.__next_char()
        if self.cur_char == ".":
            token = "<Invalid Identifier!>"
            self.error = f'{save_string}{self.cur_char} (Invalid Identifier!)'
            self.__next_char()
        elif self.cur_char not in whitespaces.keys() and self.cur_char not in punctuation \
                and self.cur_char not in arithmetic_op:
            token = "<Invalid Identifier!>"
            self.error = f'{save_string} (Invalid Identifier!)'
        elif save_string in keywords:
            token = f'<keyword, {save_string}>'
        elif save_string in data_types:
            token = f'<dt, {save_string}>'
        else:
            if f'{save_string}, id' not in self.symbol_table.values():
                self.symbol_table[self.symbol_count] = f'{save_string}, id'
                token = f'<id, {self.symbol_count}>'
                self.symbol_count += 1
            else:
                token = f'<id, {self.__find_symb_tbl_ix(save_string)}>'

        return token

    def __checkFloat(self) -> Tuple[str, bool]:
        """Evaluates and returns a string and a boolean flag corresponding
        to the read float value and whether or not the value is valid/invalid,
        respectively.

        Args:
        - self: mandatory object reference.

        Returns:
        a tuple of both the read float value and a boolean flag denoting if the
        read value is valid or not.
        """

        save_string = ""
        if self.peek() not in digits and self.peek() != "E":
            while self.cur_char != "\n":
                save_string += self.cur_char
                self.__next_char()
            return save_string, False
        else:
            save_string += self.cur_char
            self.__next_char()
            if self.cur_char in digits:
                if self.peek() in [punc for punc in punctuation if punc != "."] \
                        or self.peek() in whitespaces.keys():
                    save_string += self.cur_char
                    self.__next_char()
                    return save_string, True
                if self.peek() == "E":
                    save_string += self.cur_char
                    self.__next_char()
                    if self.peek() in digits or self.peek() in letters:
                        while self.cur_char != "\n":
                            save_string += self.cur_char
                            self.__next_char()
                        return save_string, False
                    else:
                        save_string += self.cur_char
                        self.__next_char()
                        return save_string, True
                elif self.peek() in digits:
                    while self.cur_char in digits:
                        save_string += self.cur_char
                        self.__next_char()
                    if self.cur_char in [punc for punc in punctuation if punc != "."] \
                            or self.cur_char in whitespaces.keys():
                        return save_string, True
                    if self.cur_char not in digits:
                        if self.cur_char == "E":
                            if self.peek() not in digits:
                                while self.cur_char not in [punc for punc in punctuation if punc != "."] \
                                        and self.cur_char not in whitespaces.keys():
                                    save_string += self.cur_char
                                    self.__next_char()
                                return save_string, True
                        while self.cur_char != "\n":
                            save_string += self.cur_char
                            self.__next_char()
                        return save_string, False
                    if self.peek() == "E":
                        save_string += self.cur_char
                        self.__next_char()
                        if self.peek() in digits or self.peek() in letters:
                            while self.cur_char != "\n":
                                save_string += self.cur_char
                                self.__next_char()
                            return save_string, False
                        else:
                            save_string += self.cur_char
                            self.__next_char()
                            return save_string, True
                    else:
                        return save_string, True
                else:
                    while self.cur_char not in [punc for punc in punctuation if punc != "."] \
                            and self.cur_char not in whitespaces.keys():
                        save_string += self.cur_char
                        self.__next_char()
                    return save_string, False
            else:
                while self.cur_char != "\n":
                    save_string += self.cur_char
                    self.__next_char()
                return save_string, False

    def __check_digit(self) -> str:
        """Evaluates and returns a token corresponding to the read number.

        Args:
        - self: mandatory object reference.

        Returns:
        a string tokenizing the read numeric value.
        """

        save_string = ""
        token = ""
        if self.peek() in letters:
            token = "<Unsupported character>"
            self.error = f'{save_string} (Unsupported character found with digit!)'
        else:
            while self.cur_char in digits:
                save_string += self.cur_char
                self.__next_char()
            if self.cur_char == ".":
                floatString, isFloat = self.__checkFloat()
                if isFloat:
                    token = f'<float, {save_string}{floatString}>'
                else:
                    token = "<Invalid Float!>"
                    self.error = f'{save_string}{floatString} (Invalid Float!)'
            else:
                token = f'<num, {save_string}>'

        return token

    def __check_arith_op(self) -> str:
        """Evaluates and returns a token corresponding to the read arithmetic
        operator or a negative numeric value.

        Args:
        - self: mandatory object reference.

        Returns:
        a string tokenizing the read arithmetic operator or negative numeric value.
        """

        save_string = ""
        if self.cur_char == "-" and self.peek() in digits:
            save_string += self.cur_char
            self.__next_char()
            while self.cur_char in digits:
                save_string += self.cur_char
                self.__next_char()
            token = f'<num, {save_string}>'
        else:
            token = f'<{self.cur_char}>'
            self.__next_char()

        return token

    def __check_assign_op(self) -> str:
        """Evaluates and returns a token corresponding to the read assignment
        operator.

        Args:
        - self: mandatory object reference.

        Returns:
        a string tokenizing the read assignment operator.
        """

        if self.peek() != "=":
            token = f'<assign, {self.cur_char}>'
            self.__next_char()
            return token
        else:
            token = self.__check_rel_op()
            self.__next_char()

        return token

    def __check_rel_op(self) -> str:
        """Evaluates and returns a token corresponding to the read relational
        operator.

        Args:
        - self: mandatory object reference.

        Returns:
        a string tokenizing the read relational operator.
        """

        if self.peek() == "=":
            key = self.cur_char + "="
            tok = f'<rel_op, {relational_op_double[key]}>'
            self.__next_char(2)
        else:
            key = self.cur_char
            tok = f'<rel_op, {relational_ops_single[key]}>'
            self.__next_char()

        return tok

    def __check_string_literal(self) -> str:
        """Evaluates and returns a token corresponding to the read string
        literal.

        Args:
        - self: mandatory object reference.

        Returns:
        a string tokenizing the read string literal.
        """

        save_string = ""
        self.__next_char()
        while self.cur_char != "\"":
            save_string += self.cur_char
            self.__next_char()
        token = f'<literal, {save_string}>'
        self.__next_char()

        return token

    def __check_char_const(self) -> str:
        """Evaluates and returns a token corresponding to the read character
        literal.

        Args:
        - self: mandatory object reference.

        Returns:
        a string tokenizing the read character literal.
        """

        save_string = self.cur_char
        self.__next_char()
        while self.cur_char != "'" and self.cur_char != "\n" and self.cur_char not in punctuation:
            save_string += self.cur_char
            self.__next_char()
        if len(save_string) == 1:
            token = f'<char_constant, {save_string}>'
        else:
            token = f'<Invalid char constant!, {save_string}>'
            self.error = f'{save_string} (Invalid char constant!)'
        if self.peek() != "\0":
            self.__next_char()

        return token

    def __check_punctuation(self) -> str:
        """Evaluates and returns a token corresponding to the read punctuator.

        Args:
        - self: mandatory object reference.

        Returns:
        a string tokenizing the read punctuator.
        """

        token = f'<punctuator, {self.cur_char}>'
        self.__next_char()
        return token

    def __check_whitespaces(self) -> str:
        """Evaluates and returns a token corresponding to the read whitespace
        character.

        Args:
        - self: mandatory object reference.

        Returns:
        a string tokenizing the read whitespace character.
        """

        tok = f'<{whitespaces[self.cur_char]}>'
        self.__next_char()
        return tok

    def get_token(self) -> Tuple[str, Dict[int, str], int, str]:
        """On the basis of the character encountered, the most relevant
        category is determined and in turn, a token is generated.

        Args:
        - self: mandatory object reference.

        Returns:
        a tuple containing the generated token, the updated symbol table, symbol
        count and a error message if the character(s) encountered during tokenization
        were invalid.
        """

        token = ""
        if self.cur_char == "/":
            token = self.__check_comment()
        elif self.cur_char in letters:
            token = self.__check_key_dt_id()
        elif self.cur_char in digits:
            token = self.__check_digit()
        elif self.cur_char in arithmetic_op:
            token = self.__check_arith_op()
        elif self.cur_char in assignment:
            token = self.__check_assign_op()
        elif self.cur_char in relational_ops_single:
            token = self.__check_rel_op()
        elif self.cur_char == "\"":
            token = self.__check_string_literal()
        elif self.cur_char == "'":
            token = self.__check_char_const()
        elif self.cur_char in punctuation:
            token = self.__check_punctuation()
        elif self.cur_char in whitespaces.keys():
            token = self.__check_whitespaces()
        else:
            token = self.error = "<Character not recognised!>"

        # reset error string for next token
        err_cpy = self.error
        self.error = ""

        return token, self.symbol_table, self.symbol_count, err_cpy
