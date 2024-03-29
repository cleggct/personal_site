```
from enum import Enum
import re
from typing import Tuple

number_pattern = re.compile(r'^[-+]?(\d*\.\d+|\d+(\.\d*)?)$')
escape_sequence_pattern = re.compile(r'[\\\'"nrtbf]')
whitespace_pattern = re.compile(r'\s')

class TokenType(Enum):
    BEGIN_OBJECT = 1
    BEGIN_ARRAY = 2
    END_OBJECT = 3
    END_ARRAY = 4
    VALUE_SEPARATOR = 5
    NAME_SEPARATOR = 6
    BEGIN_STRING = 7
    END_STRING = 8
    NULL = 9
    TRUE = 10
    FALSE = 11
    WHITESPACE = 12
    NUMBER = 13
    STRING_CHAR = 14
    ERROR = 15
    END = 16

class Tokenizer:

    def __init__(self, inputs):
        """Initializes tokenizer with input stream inputs."""
        self.inputs = inputs
        self.lineno = 1  # current line being parsed
        self.charno = 1  # current character being parsed
        self.current_line = "" # characters read so far on current line.
        self.buffer = None # token read from input that has not yet been parsed
        self.token_stream = self._tokenizer(inputs)

    def seeing(self, token_type) -> bool:
        """Returns True if next token in the input stream is of the given type."""
        t = self.next_token()
        if isinstance(token_type, str):
            return t[1] == token_type
        else:
            return t[0] == token_type

    def match(self, token_type) -> str:
        """Consumes next token in input stream.  

        Expects it to be of type token_type.  If not, generates error.
        """
        t = self.get()
        if isinstance(token_type, str):
            if t[1] != token_type:
                raise RuntimeError(f"Expected token of {token_type} but got {t[1]}")
        else:
            if t[0] != token_type:
                raise RuntimeError(f"Expected token of type {token_type} but got {t[0]}")
        return t[1]

    def match_string(self) -> str:
        """Matches a string token, e.g., "char*". """
        self.match(TokenType.BEGIN_STRING)
        s = ""
        while not self.seeing(TokenType.END_STRING):
            s = s + self.get()[1]
        self.match(TokenType.END_STRING)
        return s
    
    def match_number(self) -> str:
        """Matches a number token, e.g., 123.45"""
        return self.match(TokenType.NUMBER)

    def match_value(self):
        if self.seeing(TokenType.BEGIN_OBJECT):
            return self.match_object()
        elif self.seeing(TokenType.BEGIN_ARRAY):
            return self.match_array()
        elif self.seeing(TokenType.BEGIN_STRING):
            return self.match_string()
        elif self.seeing(TokenType.NUMBER):
            return self.get()
        elif self.seeing(TokenType.NULL):
            return self.get()
        elif self.seeing(TokenType.TRUE):
            return self.get()
        elif self.seeing(TokenType.FALSE):
            return self.get()
        else:
            raise RuntimeError(f"Invalid token in match_value: {self.next_token()}")

    def match_object(self):
        """Matches a an object."""
        self.match(TokenType.BEGIN_OBJECT)
        d = {}
        while True:
            key = self.match_string()
            self.match(TokenType.NAME_SEPARATOR)
            value = self.match_value()
            d[key] = value
            if self.seeing(TokenType.END_OBJECT):
                break
            self.match(TokenType.VALUE_SEPARATOR)
        self.match(TokenType.END_OBJECT)
        return d

    def match_array(self):
        self.match(TokenType.BEGIN_ARRAY)
        l = []
        while True:
            l.append(self.match_value())
            if self.seeing(TokenType.END_ARRAY):
                break
            self.match(TokenType.VALUE_SEPARATOR)
        self.match(TokenType.END_ARRAY)
        return l

    def get(self) -> Tuple[TokenType, str]:
        """Consumes next token and returns it."""
        if self.buffer:
            token = self.buffer
            self.buffer = None
        else:
            token = next(self.token_stream)
        return token

    def get_str(self) -> str:
        """Consumes next token and returns string component of it."""
        return self.get()[1]

    def next_token(self) -> Tuple[TokenType, str]:
        """Returns the next token that has not been parsed without consuming it"""
        if not self.buffer:
            self.buffer = next(self.token_stream)
        return self.buffer

    def _tokenizer(self, inputs):

        reading_string = False
        buffer = ''
        escaped = False
        reading_number = False

        for char in inputs:

            if reading_number and not number_pattern.match(buffer + char):
                number = buffer
                buffer = ''
                reading_number = False
                yield (TokenType.NUMBER, number)
            
            if not reading_string:
                if char == '\n':
                    self.lineno += 1
                    self.charno = 1
                else:
                    self.charno += 1

                if char == '{':
                    yield (TokenType.BEGIN_OBJECT, char)
                elif char == '[':
                    yield (TokenType.BEGIN_ARRAY, char) 
                elif char == ',':
                    yield (TokenType.VALUE_SEPARATOR, char)
                elif char == ':':
                    yield (TokenType.NAME_SEPARATOR, char)
                elif char == '}':
                    yield (TokenType.END_OBJECT, char)
                elif char == ']':
                    yield (TokenType.END_ARRAY, char)
                elif char == '"':
                    reading_string = True
                    yield (TokenType.BEGIN_STRING, char)
                elif whitespace_pattern.match(char):
                    continue
                    # yield (TokenType.WHITESPACE, char)
                else:
                    buffer += char
                    if buffer == 'false':
                        old_buffer = buffer
                        buffer = ''
                        yield (TokenType.FALSE, old_buffer)
                    elif buffer == 'null':
                        old_buffer = buffer
                        buffer = ''
                        yield (TokenType.NULL, old_buffer)
                    elif buffer == 'true':
                        old_buffer = buffer
                        buffer = ''
                        yield (TokenType.TRUE, old_buffer)
                    elif number_pattern.match(buffer):
                        reading_number = True
                    else:
                        if len(buffer) > 5:
                            old_buffer = buffer
                            buffer = ''
                            yield (TokenType.ERROR, old_buffer)
                            
            else: #we are in the midst of reading a string
                if escaped: #if the last character was an escape

                    if escape_sequence_pattern.match(char):
                        escaped = False
                        yield (TokenType.STRING_CHAR, f'\\{char}')
                    else:
                        escaped = False
                        yield (TokenType.ERROR, f'\\{char}')

                else: #the last character was not an escape
                    if char == '\\': #if we read an escape, set the escaped flag
                        escaped = True
                    elif char == '"':
                        reading_string = False
                        yield (TokenType.END_STRING, char)
                    else:
                        yield (TokenType.STRING_CHAR, char)
        
        if reading_number:
            number = buffer
            buffer = ''
            reading_number = False
            yield (TokenType.NUMBER, number)

        yield (TokenType.END, '')


if __name__ == "__main__":
    print("Enter some JSON code to tokenize:")
    while True:
        s = input()
        t = Tokenizer(list(s))
        while True:
            token = t.get()
            print(token)
            if token[0] == TokenType.END:
                break