"""
Pyfranca lexer tests.
"""

import unittest
from pyfranca import Lexer


class BaseTestCase(unittest.TestCase):

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


class TestCheckRegularExpressions(BaseTestCase):
    """Test regular expression used by the lexer """

    def test_integer_valid_syntax(self):
        """test an integer """
        tokenized_data = self._tokenize("1234\n2345\n0x1234\n0X56789\n0xabcdef\n0XABCDEF\n0b10\n0B101")
        self.assertEqual(tokenized_data[0].type, "INTEGER_VAL")
        self.assertEqual(tokenized_data[0].value, 1234)

        self.assertEqual(tokenized_data[1].type, "INTEGER_VAL")
        self.assertEqual(tokenized_data[1].value, 2345)

        self.assertEqual(tokenized_data[2].type, "HEXADECIMAL_VAL")
        self.assertEqual(tokenized_data[2].value, 0x1234)

        self.assertEqual(tokenized_data[3].type, "HEXADECIMAL_VAL")
        self.assertEqual(tokenized_data[3].value, 0x56789)

        self.assertEqual(tokenized_data[4].type, "HEXADECIMAL_VAL")
        self.assertEqual(tokenized_data[4].value, 0xabcdef)

        self.assertEqual(tokenized_data[5].type, "HEXADECIMAL_VAL")
        self.assertEqual(tokenized_data[5].value, 0xabcdef)

        self.assertEqual(tokenized_data[6].type, "BINARY_VAL")
        self.assertEqual(tokenized_data[6].value, 0b10)

        self.assertEqual(tokenized_data[7].type, "BINARY_VAL")
        self.assertEqual(tokenized_data[7].value, 0b101)

    def test_string_valid_syntax(self):
        """test a string """
        tokenized_data = self._tokenize("\"This is a string\"")
        self.assertEqual(tokenized_data[0].type, "STRING_VAL")
        self.assertEqual(tokenized_data[0].value, "This is a string")

        tokenized_data = self._tokenize("\"This is a string \n with an newline\"")
        self.assertEqual(tokenized_data[0].type, "STRING_VAL")
        self.assertEqual(tokenized_data[0].value, "This is a string \n with an newline")

    def test_boolean_valid_syntax(self):
        """test a boolean value """
        tokenized_data = self._tokenize("true\nfalse")
        self.assertEqual(tokenized_data[0].type, "BOOLEAN_VAL")
        self.assertEqual(tokenized_data[0].value, True)
        self.assertEqual(tokenized_data[1].type, "BOOLEAN_VAL")
        self.assertEqual(tokenized_data[1].value, False)

    def test_integerinvalid_syntax(self):
        """test a boolean value """
        tokenized_data = self._tokenize("0xgabcdefg")
        for t in tokenized_data:
            self.assertNotEqual(t.type, "HEXADECIMAL_VAL")

    def test_booleaninvalid_syntax(self):
        """test a boolean value """
        tokenized_data = self._tokenize("istrue\nisfalse")
        for t in tokenized_data:
            self.assertNotEqual(t.type, "BOOLEAN_VAL")

    def test_float_valid_syntax(self):
        """test a float value """
        tokenized_data = self._tokenize("1.1f\n-2.2f\n3.3e3f\n-4.4e4f\n5.5e-5f"
                                        "-6.6e-6f\n0.00001f\n-0.000002f\n1e4f\n-1e4f"
                                        ".1f\n-.2f\n.3e3f\n-.4e4f\n.5e-5f"
                                        "-.6e-6f\n.00001f\n-.000002f"
                                        )
        cnt = 0
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[0].value, "1.1f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-2.2f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "3.3e3f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-4.4e4f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "5.5e-5f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-6.6e-6f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "0.00001f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-0.000002f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "1e4f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-1e4f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".1f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.2f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".3e3f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.4e4f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".5e-5f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.6e-6f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".00001f")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.000002f")

    def test_double_valid_syntax(self):
        """test a double value """
        tokenized_data = self._tokenize("1.1d\n-2.2d\n3.3e3d\n-4.4e4d\n5.5e-5d"
                                        "-6.6e-6d\n0.00001d\n-0.000002d\n1e4d\n-1e4d"
                                        ".1d\n-.2d\n.3e3d\n-.4e4d\n.5e-5d"
                                        "-.6e-6d\n.00001d\n-.000002d"
                                        )

        cnt = 0
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[0].value, "1.1d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-2.2d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "3.3e3d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-4.4e4d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "5.5e-5d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-6.6e-6d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "0.00001d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-0.000002d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "1e4d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-1e4d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".1d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.2d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".3e3d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.4e4d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".5e-5d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.6e-6d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, ".00001d")
        cnt += 1
        self.assertEqual(tokenized_data[cnt].type, "REAL_VAL")
        self.assertEqual(tokenized_data[cnt].value, "-.000002d")

    def test_real_valid_syntax(self):
        """test a real value """
        self.tokenize("1.1\n-2.2\n3.3e3\n-4.4e4\n5.5e-5"
                      "-6.6e-6\n0.00001\n-0.000002\n1e4\n-1e4"
                      ".1\n-.2\n.3e3\n-.4e4\n.5e-5"
                      "-.6e-6\n.00001\n-.000002")
        self.check("REAL_VAL", "1.1")
        self.check("REAL_VAL", "-2.2")
        self.check("REAL_VAL", "3.3e3")
        self.check("REAL_VAL", "-4.4e4")
        self.check("REAL_VAL", "5.5e-5")
        self.check("REAL_VAL", "-6.6e-6")
        self.check("REAL_VAL", "0.00001")
        self.check("REAL_VAL", "-0.000002")
        self.check("REAL_VAL", "1e4")
        self.check("REAL_VAL", "-1e4")
        self.check("REAL_VAL", ".1")
        self.check("REAL_VAL", "-.2")
        self.check("REAL_VAL", ".3e3")
        self.check("REAL_VAL", "-.4e4")
        self.check("REAL_VAL", ".5e-5")
        self.check("REAL_VAL", "-.6e-6")
        self.check("REAL_VAL", ".00001")
        self.check("REAL_VAL", "-.000002")

    def test_doublefloat_invalid_syntax(self):
        """test a text containing .f """
        tokenized_data = self._tokenize("""
                package org.franca.examples
               0ef .ef  -1ef   ef ed .ed
                }
            """)
        for t in tokenized_data:
            self.assertNotEqual(t.type, "REAL_VAL")

    def test_type_valid_syntax(self):
        """test an integer """
        self.tokenize("const Boolean b1 = true")
        self.check("CONST", 'const')
        self.check("BOOLEAN", 'Boolean')
        self.check("ID", 'b1')
        self.check("=", '=')
        self.check("BOOLEAN_VAL", True)

    def test_type_invalid_syntax(self):
        """test an integer """
        self.tokenize("const boolean b1 = true")
        self.check("CONST", 'const')
        self.check("ID", 'boolean')
        self.check("ID", 'b1')
        self.check("=", '=')
        self.check("BOOLEAN_VAL", True)

    def test_type_mult_expression(self):
        """test an integer """
        self.tokenize("const UInt32 abc = 3 + 5 * 5")
        self.check("CONST", 'const')
        self.check("UINT32", 'UInt32')
        self.check("ID", 'abc')
        self.check("=", '=')
        self.check("INTEGER_VAL", 3)
        self.check("PLUS", "+")
        self.check("INTEGER_VAL", 5)
        self.check("TIMES", "*")
        self.check("INTEGER_VAL", 5)

    def test_type_add_expression(self):
        """test an integer """
        self.tokenize("const UInt32 abc = 5 + 5")
        self.check("CONST", 'const')
        self.check("UINT32", 'UInt32')
        self.check("ID", 'abc')
        self.check("=", '=')
        self.check("INTEGER_VAL", 5)
        self.check("PLUS", "+")
        self.check("INTEGER_VAL", 5)

    def test_type_diff_expression(self):
        """test an integer """
        self.tokenize("const UInt32 abc = 5 - 5")
        self.check("CONST", 'const')
        self.check("UINT32", 'UInt32')
        self.check("ID", 'abc')
        self.check("=", '=')
        self.check("INTEGER_VAL", 5)
        self.check("MINUS", "-")
        self.check("INTEGER_VAL", 5)

    def test_type_div_expression(self):
        """test an integer """
        self.tokenize("const UInt32 abc = 5 / 5")
        self.check("CONST", 'const')
        self.check("UINT32", 'UInt32')
        self.check("ID", 'abc')
        self.check("=", '=')
        self.check("INTEGER_VAL", 5)
        self.check("DIVIDE", "/")
        self.check("INTEGER_VAL", 5)

    def test_type_parenthesis_expression(self):
        """test an integer """
        self.tokenize("const UInt32 abc = (5-5)/2")
        self.check("CONST", 'const')
        self.check("UINT32", 'UInt32')
        self.check("ID", 'abc')
        self.check("=", '=')
        self.check("(", '(')
        self.check("INTEGER_VAL", 5)
        self.check("INTEGER_VAL", -5)
        self.check(")")
        self.check("DIVIDE", "/")
        self.check("INTEGER_VAL", 2)

    def test_type_bracket_expression_array(self):
        """test an integer """
        self.tokenize("const Array1 full = [ 1, 2, 2+3, 100*100+100 ]")
        self.check("CONST", 'const')
        self.check("ID", 'Array1')
        self.check("ID", 'full')
        self.check("=")
        self.check("[")
        self.check("INTEGER_VAL", 1)
        self.check(",")
        self.check("INTEGER_VAL", 2)
        self.check(",")
        self.check("INTEGER_VAL", 2)
        self.check("INTEGER_VAL", 3)
        self.check(",")
        self.check("INTEGER_VAL", 100)
        self.check("TIMES", "*")
        self.check("INTEGER_VAL", 100)
        self.check("INTEGER_VAL", 100)
        self.check("]")

    def test_type_brace_expression_aruct(self):
        """test an integer """
        self.tokenize("const Struct1 s1 = { e1: true, e2: 1, e3: \"foo\"}")
        self.check("CONST", 'const')
        self.check("ID", 'Struct1')
        self.check("ID", 's1')
        self.check("=")
        self.check("{")
        self.check("ID", "e1")
        self.check(":")
        self.check("BOOLEAN_VAL", True)
        self.check(",")
        self.check("ID", "e2")
        self.check(":")
        self.check("INTEGER_VAL", 1)
        self.check(",")
        self.check("ID", "e3")
        self.check(":")
        self.check("STRING_VAL", "foo")
        self.check("}")

    def test_type_brace_expression_map(self):
        """test an integer """
        self.tokenize("const Map1 m1 = [ 1 => \"one\", 2 => \"two\"]")
        self.check("CONST", 'const')
        self.check("ID", 'Map1')
        self.check("ID", 'm1')
        self.check("=")
        self.check("[")
        self.check("INTEGER_VAL", 1)
        self.check("ASSIGN", "=>")
        self.check("STRING_VAL", "one")
        self.check(",")
        self.check("INTEGER_VAL", 2)
        self.check("ASSIGN", "=>")
        self.check("STRING_VAL", "two")
        self.check("]")

    def test_type_boolean_expression(self):
        """test an integer """
        self.tokenize("const Boolean b2 = MAX_COUNT > 3")
        self.check("CONST", 'const')
        self.check("BOOLEAN", 'Boolean')
        self.check("ID", 'b2')
        self.check("=")
        self.check("ID", 'MAX_COUNT')
        self.check("GT", ">")
        self.check("INTEGER_VAL", 3)

    def test_type_boolean_expression(self):
        """test an integer """
        self.tokenize("const Boolean b3 = (a && b) || foo ==\"bar\"")
        self.check("CONST", 'const')
        self.check("BOOLEAN", 'Boolean')
        self.check("ID", 'b3')
        self.check("=")
        self.check("(")
        self.check("ID", 'a')
        self.check("LAND", "&&")
        self.check("ID", 'b')
        self.check(")")
        self.check("LOR", "||")
        self.check("ID", "foo")
        self.check("EQ", "==")
        self.check("STRING_VAL", "bar")
