import os
from lexer import *
from rd_parser import *
from typing import List, Dict, Tuple


def get_abs_file_path(path) -> str:
    """Returns the absolute file path of the indicated file.

    Args:
    - path: the relative path to the indicated file.

    Returns:
    the absolute path for the relative file.
    """

    # the absolute directory the script is in
    script_dir = os.path.dirname(__file__)
    return os.path.join(script_dir, path)


def write_token_stream(token_stream: Dict[int, str], file_num: int) -> None:
    """Writes the generated token stream from the lexical analysis to a file
    of the same name as the input file with the .out extension.

    Args:
    - token_stream: all the tokenized lexemes.
    - file_num: the test number of the file that was read.

    Returns:
    None.
    """
    
    # get absolute file path
    abs_file_path = get_abs_file_path(f'TokenStream\\test0{file_num}.out')
    
    # write the file
    with open(abs_file_path, "w") as stream:
        # the entire stream is written in a single line
        stream.write('\n'.join(token_stream.values()))


def write_symb_tbl(symbol_table: Dict[int, str], file_num: int) -> None:
    """Writes the symbol table generated from the lexical analysis to a file
    of the same name as the input with the .sym extension.

    Args:
    - symbol_table: all recorded entries in the symbol table.
    - file_num: the test number of the file that was read.

    Returns:
    None.
    """

    # get asolute file path
    abs_file_path = get_abs_file_path(f'SymbolTable\\test0{file_num}.sym')
    
    # write the file
    with open(abs_file_path, "w") as table:
        table.write("{:<8} {:<15}\n".format('Key', 'Symbol'))
        for ix, entry in symbol_table.items():
            table.write("{:<8} {:<15}\n".format(ix, entry))


def write_error_stream(error_stream: Dict[int, List[str]], file_num: int, error_type: str, count: int) -> None:
    """Writes the error stream generated from the lexical analysis to a file
    of the same name as the input with the .err extension.

    Args:
    - error_stream: all errors recorded during the lexical analysis.
    - file_num: the test number of the file that was read.

    Returns:
    None.
    """

    # get absolute file path
    abs_file_path = get_abs_file_path(f'ErrorStream\\test0{file_num}.err')

    # determine if appending or writing
    mode = ""
    if count == 1:
        mode = "w"
    else:
        mode = "a"
    
    # write the file
    with open(abs_file_path, mode) as error:
        if mode == "w":
            error.write("{:<10} {:<50} {:<20}\n".format('<line#>', '<error_found>', '<error_type>'))
        for line, errors in error_stream.items():
            for err in errors:
                error.write("{:<10} {:<50} {:<20}\n".format(line + 1, err, error_type))

def tokenize(lexer: Lexer, symbol_table: Dict[int, str], symbol_count: int,
             error_stream: Dict[int, List[str]], token_stream: Dict[int, str],
             line_num: int, token_list: List[str]) -> Tuple[int, Dict[int, str]]:
    """Tokenizes the given portion of the input stream - the line being
    read.

    Args:
    - lexer: object reference for the lexer instantiated with the current
    portion of the input stream.
    - symbol_table: the symbol table maintained for the lexical analysis.
    - symbol_count: an integer corresponding to the number of entries in
    the symbol table.
    - error_stream: a dictionary recording errors encountered (by line).
    - token_stream: a dictionary recording the tokenized lexemes (by line).
    - line_num: the number of the line/portion of the input stream that is
    being processed.

    Returns:
    updated values for the symbol count and table.
    """

    # store the tokenized lexemes for the current line

    # keep tokenizing till EOF encountered
    while lexer.peek() != '\0':
        # tokenize the given line
        token, new_symbl_tbl, new_symb_count, error = lexer.get_token()

        # add the new token to the current line's stream
        try:
            token_stream[line_num] += token
        except KeyError:
            token_stream[line_num] = token

        # update the symbol table
        symbol_table = new_symbl_tbl
        symbol_count = new_symb_count

        # update record of errors
        if error != "":
            try:
                error_stream[line_num].append(error)
            except KeyError:
                error_stream[line_num] = [error]

        token_list.append(token)

    return symbol_count, symbol_table, token_list


def write_parser_trace(parser_stream: List[str], file_num: int) -> None:
    """Writes the parser trace to a file.

    Args:
    - parser_stream: the trace of the parser.

    Returns:
    None.
    """

    # get absolute file path
    abs_file_path = get_abs_file_path(f'ParserTrace\\test0{file_num}.tr')
    
    # write the file
    with open(abs_file_path, "w") as trace:
        trace.write('\n'.join(parser_stream))


def main() -> None:
    """Program entry point. Reads the indicated test file line by line, passing
    each line to the lexer which tokenizes the given stream in addition to,
    recording any errors and populating the symbol table.

    After completion of the lexical analysis, all the streams - i.e., token, symbol
    and error are written to their respective files.

    Args:
    None.

    Returns:
    None.
    """ 

    # ask user for file number
    file_num = int(input("Enter the file number: "))

    # get absolute file path
    abs_file_path = get_abs_file_path(f'Tests\\test0{file_num}.tpl')
    
    # open the test file and read it
    with open(abs_file_path) as custom_test:
        lines = custom_test.readlines()

    # initialize all streams
    symbol_count = 1
    symbol_table = {}
    error_stream = {}
    token_stream = {}
    token_list = []

    # pass the input stream line by line
    for i in range(len(lines)):
        # initialize Lexer for the given portion of the stream
        lexer = Lexer(lines[i], symbol_table, symbol_count)

        # tokenize the line
        symbol_count, symbol_table, token_list = tokenize(lexer, symbol_table, symbol_count,
                                              error_stream, token_stream, i, token_list)

    # output the token stream to file
    write_token_stream(token_stream, file_num)

    # output the symbol table
    write_symb_tbl(symbol_table, file_num)

    # output the error stream
    write_error_stream(error_stream, file_num, "Lexical", 1)

    # unwantd tokens for the parser
    unwanted_tokens = {'<Comment>', '<tab>', '<blank>', '<Invalid Identifier!>', '<Invalid char constant!, \'a>'}

    # remove all unrequired tokens by the parser
    token_list = [token for token in token_list if token not in unwanted_tokens and token[:9] != '<Invalid']

    # pass the token list to the parser
    parser = Parser(token_list, symbol_table)
    
    # obtain the parser trace and list of errors from the parser class after parsing all tokens
    parser_trace, parsing_errors, semantic_errors = parser.parseToken()

    # output the parser trace
    write_parser_trace(parser_trace, file_num)

    # output the parsing errors
    write_error_stream(parsing_errors, file_num, "Parsing", 2)

    # ouptut the semantic errors
    write_error_stream(semantic_errors, file_num, "Semantic", 3)

# driver code
if __name__ == "__main__":
    main()
