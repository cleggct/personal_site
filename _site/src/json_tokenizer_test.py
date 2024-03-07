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