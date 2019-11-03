"""
Pyfranca parser tests.
"""

import unittest

from pyfranca import LexerException, ParserException, Parser, ast
from pyfranca import Lexer

class BaseTestCase(unittest.TestCase):

    @staticmethod
    def _parse(data):
        parser = Parser(debug=True, write_tables=True)
        package = parser.parse(data)
        return package

    def _assertParse(self, data):
        package = self._parse(data)
        self.assertIsInstance(package, ast.Package)
        return package

    def check(self, typeName, value=""):
        self.assertTrue(self.pos <= len(self.tokenized_data))
        self.assertEqual(self.tokenized_data[self.pos].type, typeName)

        if value == "":
            self.assertEqual(self.tokenized_data[self.pos].value, typeName)
        else:
            self.assertEqual(self.tokenized_data[self.pos].value, value)
        self.pos += 1

    @staticmethod
    def _tokenize(data):
        lexer = Lexer()
        tokenized_data = lexer.tokenize_data(data)
        return tokenized_data

    def tokenize(self, data):
        lexer = Lexer()
        self.tokenized_data = lexer.tokenize_data(data)
        self.pos = 0


class TestMisc(BaseTestCase):
    """Test parsing various FIDL examples."""

    def test_all_supported(self):
        package = self._assertParse("""
                          package P
                       typeCollection TC {
                           union Union1 {
                            UInt16 e1
                            Boolean e2
                            String e3
                            }
                            const Union1 uni1 = { e1: 1 }
                            const Union1 uni2 = { e3: "bar" }
                       }
        """)
        print("Stop here for debugging!")