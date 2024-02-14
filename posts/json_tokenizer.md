# Parsing JSON to HTML on the Fly

I wrote this code for tokenizing and parsing JSON to HTML on the fly.
It was meant as part of a system which would stream data from a backend
and render that data on a webpage in realtime. It didn't end up getting
used for its intended purpose so I decided to leave it up here. It was
a fun bit of code to write. I basically went about it by just looking at 
<a href="https://ecma-international.org/publications-and-standards/standards/ecma-404/">the ECMA specification for the JSON format</a>. I knew the tokenizer needed to be able to process
each symbol listed in there, so I designed it to do just that. The
tokenizer works by reading input one character at a time and basically
either categorizes the current character as one of the token types, or
otherwise modifies the state of the tokenizer to indicate that it is
reading some sort of continuous value like a string or int literal.
In this fashion, as characters of JSON data stream in, they
are mapped to one of a set of basic tokens which can then be
read by your parser to generate whatever kind of output you want in
response to each token. This saves the user from having to write
their own code to handle cases like checking when the same symbol is 
used for multiple distinct operations, reading a literal value
from stream data, etc. Of course, a project like this is useless
without unit tests. I have included those as well.

## Tokenizer/Parser

### json_tokenizer.py
---
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
```

## Unit Tests

### json_tokenizer_test.py
---
```
"""Unit tests for the json tokenizer."""

import unittest
from json_tokenizer import TokenType, Tokenizer

class TestJsonTokenizer(unittest.TestCase):

    def test_parses_empty_string(self):
        t = Tokenizer(list(''))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_numbers(self):
        t = Tokenizer(list('1.23'))
        self.assertEqual(t.get(), (TokenType.NUMBER, '1.23'))

    def test_parses_strings(self):
        t = Tokenizer(list('"Hello World!"'))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'H'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'e'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'l'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'l'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'o'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, ' '))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'W'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'o'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'r'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'l'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'd'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, '!'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))

    def test_parses_strings_with_escapes(self):
        test_string = '"\\t\\n\\\\\\""'
        t = Tokenizer(list(test_string))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, '\\t'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, '\\n'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, '\\\\'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, '\\"'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_lists(self):
        t = Tokenizer(list('["a", "b", 0]'))
        self.assertEqual(t.get(), (TokenType.BEGIN_ARRAY, '['))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'a'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.VALUE_SEPARATOR, ','))
        # self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'b'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.VALUE_SEPARATOR, ','))
        self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.NUMBER, '0'))
        self.assertEqual(t.get(), (TokenType.END_ARRAY, ']'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_objects(self):
        t = Tokenizer(list('{"Name": "John", "Age": 50}'))
        self.assertEqual(t.get(), (TokenType.BEGIN_OBJECT, '{'))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'N'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'a'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'm'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'e'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.NAME_SEPARATOR, ':'))
        # self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'J'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'o'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'h'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'n'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.VALUE_SEPARATOR, ','))
        # self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'A'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'g'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'e'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.NAME_SEPARATOR, ':'))
        # self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.NUMBER, '50'))
        self.assertEqual(t.get(), (TokenType.END_OBJECT, '}'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_empty_list(self):
        t = Tokenizer(list('[]'))
        self.assertEqual(t.get(), (TokenType.BEGIN_ARRAY, '['))
        self.assertEqual(t.get(), (TokenType.END_ARRAY, ']'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_empty_object(self):
        t = Tokenizer(list('{}'))
        self.assertEqual(t.get(), (TokenType.BEGIN_OBJECT, '{'))
        self.assertEqual(t.get(), (TokenType.END_OBJECT, '}'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    # def test_parses_whitespace(self):
    #     t = Tokenizer(list(' \n\t'))
    #     self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
    #     self.assertEqual(t.get(), (TokenType.WHITESPACE, '\n'))
    #     self.assertEqual(t.get(), (TokenType.WHITESPACE, '\t'))
    #     self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_nested_objects(self):
        t = Tokenizer(list('{ {"A"}, {} }'))
        self.assertEqual(t.get(), (TokenType.BEGIN_OBJECT, '{'))
        self.assertEqual(t.get(), (TokenType.BEGIN_OBJECT, '{'))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'A'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.END_OBJECT, '}'))
        self.assertEqual(t.get(), (TokenType.VALUE_SEPARATOR, ','))
        # self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.BEGIN_OBJECT, '{'))
        self.assertEqual(t.get(), (TokenType.END_OBJECT, '}'))
        self.assertEqual(t.get(), (TokenType.END_OBJECT, '}'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_nested_lists(self):
        t = Tokenizer(list('[["a", "b"], ["c"]]'))
        self.assertEqual(t.get(), (TokenType.BEGIN_ARRAY, '['))
        self.assertEqual(t.get(), (TokenType.BEGIN_ARRAY, '['))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'a'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.VALUE_SEPARATOR, ','))
        # self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'b'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.END_ARRAY, ']'))
        self.assertEqual(t.get(), (TokenType.VALUE_SEPARATOR, ','))
        # self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.BEGIN_ARRAY, '['))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'c'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.END_ARRAY, ']'))
        self.assertEqual(t.get(), (TokenType.END_ARRAY, ']'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_key_value_pairs(self):
        t = Tokenizer(list('"key": "value"'))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'k'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'e'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'y'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.NAME_SEPARATOR, ':'))
        # self.assertEqual(t.get(), (TokenType.WHITESPACE, ' '))
        self.assertEqual(t.get(), (TokenType.BEGIN_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'v'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'a'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'l'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'u'))
        self.assertEqual(t.get(), (TokenType.STRING_CHAR, 'e'))
        self.assertEqual(t.get(), (TokenType.END_STRING, '"'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_true(self):
        t = Tokenizer(list('{null}'))
        self.assertEqual(t.get(), (TokenType.BEGIN_OBJECT, '{'))
        self.assertEqual(t.get(), (TokenType.NULL, 'null'))
        self.assertEqual(t.get(), (TokenType.END_OBJECT, '}'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_false(self):
        t = Tokenizer(list('{true}'))
        self.assertEqual(t.get(), (TokenType.BEGIN_OBJECT, '{'))
        self.assertEqual(t.get(), (TokenType.TRUE, 'true'))
        self.assertEqual(t.get(), (TokenType.END_OBJECT, '}'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_null(self):
        t = Tokenizer(list('{false}'))
        self.assertEqual(t.get(), (TokenType.BEGIN_OBJECT, '{'))
        self.assertEqual(t.get(), (TokenType.FALSE, 'false'))
        self.assertEqual(t.get(), (TokenType.END_OBJECT, '}'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_integers(self):
        t = Tokenizer(list('1729'))
        self.assertEqual(t.get(), (TokenType.NUMBER, '1729'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_decimals(self):
        t = Tokenizer(list('3.1415926535'))
        self.assertEqual(t.get(), (TokenType.NUMBER, '3.1415926535'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_negative_values(self):
        t = Tokenizer(list('-1'))
        self.assertEqual(t.get(), (TokenType.NUMBER, '-1'))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_parses_end(self):
        t = Tokenizer(list(''))
        self.assertEqual(t.get(), (TokenType.END, ''))

    def test_match_function_works(self):
        t = Tokenizer(list('["a", 1, {}]'))
        t.match(TokenType.BEGIN_ARRAY)
        t.match(TokenType.BEGIN_STRING)
        t.match(TokenType.STRING_CHAR)
        t.match(TokenType.END_STRING)
        t.match(TokenType.VALUE_SEPARATOR)
        # t.match(TokenType.WHITESPACE)
        t.match(TokenType.NUMBER)
        t.match(TokenType.VALUE_SEPARATOR)
        # t.match(TokenType.WHITESPACE)
        t.match(TokenType.BEGIN_OBJECT)
        t.match(TokenType.END_OBJECT)
        t.match(TokenType.END_ARRAY)
        t.match(TokenType.END)

    def test_seeing_function_works(self): 
        t = Tokenizer(list('["a", 1, {}]'))
        self.assertTrue(t.seeing(TokenType.BEGIN_ARRAY))
        t.get()
        self.assertTrue(t.seeing(TokenType.BEGIN_STRING))
        t.get()
        self.assertTrue(t.seeing(TokenType.STRING_CHAR))
        t.get()
        self.assertTrue(t.seeing(TokenType.END_STRING))
        t.get()
        self.assertTrue(t.seeing(TokenType.VALUE_SEPARATOR))
        t.get()
        # self.assertTrue(t.seeing(TokenType.WHITESPACE))
        t.get()
        self.assertTrue(t.seeing(TokenType.NUMBER))
        t.get()
        self.assertTrue(t.seeing(TokenType.VALUE_SEPARATOR))
        t.get()
        # self.assertTrue(t.seeing(TokenType.WHITESPACE))
        t.get()
        self.assertTrue(t.seeing(TokenType.BEGIN_OBJECT))
        t.get()
        self.assertTrue(t.seeing(TokenType.END_OBJECT))
        t.get()
        self.assertTrue(t.seeing(TokenType.END_ARRAY))
        t.get()
        self.assertTrue(t.seeing(TokenType.END))

    def test_get_str_works(self):
        t = Tokenizer(list('{"a": 10, "b"}'))
        self.assertEqual(t.get_str(), '{')
        self.assertEqual(t.get_str(), '"')
        self.assertEqual(t.get_str(), 'a')
        self.assertEqual(t.get_str(), '"')
        self.assertEqual(t.get_str(), ':')
        self.assertEqual(t.get_str(), ' ')
        self.assertEqual(t.get_str(), '10')
        self.assertEqual(t.get_str(), ',')
        self.assertEqual(t.get_str(), ' ')
        self.assertEqual(t.get_str(), '"')
        self.assertEqual(t.get_str(), 'b')
        self.assertEqual(t.get_str(), '"')
        self.assertEqual(t.get_str(), '}')

    def test_next_token_works(self):
        t = Tokenizer(list('{}'))
        self.assertEqual(t.next_token(), (TokenType.BEGIN_OBJECT, '{')) 
        self.assertEqual(t.next_token(), (TokenType.BEGIN_OBJECT, '{'))
        t.get()
        self.assertEqual(t.next_token(), (TokenType.END_OBJECT, '}'))
        t.get()
        self.assertEqual(t.next_token(), (TokenType.END, ''))




if __name__ == "__main__":
    unittest.main()
```