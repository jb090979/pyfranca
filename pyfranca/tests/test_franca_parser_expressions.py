"""
Pyfranca parser tests.
"""

import unittest

from pyfranca import LexerException, ParserException, Parser, ast


class BaseTestCase(unittest.TestCase):

    @staticmethod
    def _parse(data):
        parser = Parser()
        package = parser.parse(data)
        return package

    def _assertParse(self, data):
        package = self._parse(data)
        self.assertIsInstance(package, ast.Package)
        return package

class TestExpressionInteger(BaseTestCase):
    """Test that unsupported Franca features fail appropriately."""

    @unittest.skip
    def test_expressions(self):
        """Franca 0.9.2, section 5.2.1"""
        package =  self._assertParse("""
            package P
            typeCollection TC {
                const UInt32 u1 = 55
                const UInt32 u2 = 5-3
                const UInt32 u3 = 50-3*2
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(constant.name, "u1")
        self.assertEqual(constant.value.value, 55)
        self.assertEqual(constant.expression, None)

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(constant.name, "u2")
        self.assertEqual(constant.value, None)
        expr = constant.expression
        self.assertIsInstance(expr, ast.Operator)
        self.assertEqual(expr.name, "-")
        self.assertEqual(expr.operand1.value, 5)
        self.assertEqual(expr.operand2.value, 3)

    @unittest.skip
    def test_arithmetic_operator_integer_numbers(self):
        """Franca 0.9.2, section 5.2.1"""
        package =  self._assertParse("""
            package P
            typeCollection TC {
                const UInt32 u1 = 3 + 5 * 4 + 5
                const UInt32 u2 = 3 * 5 + 4 * 5
                const UInt32 u3 = 3 / 5 - 4 * 5
                const UInt32 u4 = 4 +5
                const UInt32 u5 = 4-5
                const UInt32 u6 = 4--5
                const UInt32 u7 = 4+ 5
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operand2.value, 5)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.operand1.value, 3)
        self.assertEqual(constant.expression.operand1.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Operator), True)
        self.assertEqual(constant.expression.operand1.operand2.operand1.value, 5)
        self.assertEqual(constant.expression.operand1.operand2.operand2.value, 4)
        self.assertEqual(constant.expression.operand1.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Operator), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3)
        self.assertEqual(constant.expression.operand1.operand2.value, 5)
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Operator), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.operand2.value, 5)
        self.assertEqual(constant.expression.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u3"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Operator), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3)
        self.assertEqual(constant.expression.operand1.operand2.value, 5)
        self.assertEqual(constant.expression.operand1.operator, "/")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Operator), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.operand2.value, 5)
        self.assertEqual(constant.expression.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u4"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, 5)

        constant = package.typecollections["TC"].constants["u5"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, 5)

        constant = package.typecollections["TC"].constants["u6"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, -5)

        constant = package.typecollections["TC"].constants["u7"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, 5)

    @unittest.skip
    def test_arithmetic_operator_real_numbers(self):
        """Franca 0.9.2, section 5.2.1"""
        package =  self._assertParse("""
            package P
            typeCollection TC {
                const Float u1 = 3.0F + 5.0F * 4.0F + 6.0F
                const Float u2 = 3.0F * 5.0F + 4.0F * 5.0F
                const Float u3 = 3.0F / 5.0F - 4.0F * 5.0F
                const Float u4 = 4.0F +5.0F
                const Float u5 = 4.0F-5.0F
                const Float u6 = 4.0F--5.0F
                const Float u7 = 4.0F+ 5.0F
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operand2.value, 6.0)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.operand1.value, 3.0)
        self.assertEqual(constant.expression.operand1.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Operator), True)
        self.assertEqual(constant.expression.operand1.operand2.operand1.value, 5.0)
        self.assertEqual(constant.expression.operand1.operand2.operand2.value, 4.0)
        self.assertEqual(constant.expression.operand1.operand2.operator , "*")

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Operator), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3.0)
        self.assertEqual(constant.expression.operand1.operand2.value, 5.0)
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Operator), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.operand2.value, 5.0)
        self.assertEqual(constant.expression.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u3"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Operator), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3.0)
        self.assertEqual(constant.expression.operand1.operand2.value, 5.0)
        self.assertEqual(constant.expression.operand1.operator, "/")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Operator), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.operand2.value, 5.0)
        self.assertEqual(constant.expression.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u4"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, 5.0)

        constant = package.typecollections["TC"].constants["u5"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, 5.0)

        constant = package.typecollections["TC"].constants["u6"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, -5.0)

        constant = package.typecollections["TC"].constants["u7"]
        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, 5.0)

    def test_arithmetic_parentheses(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
                    package P
                    typeCollection TC {
                        const UInt32 u1 = (3+5)*(4+6)
                    }
                """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)
        constant = package.typecollections["TC"].constants["u1"]

        self.assertEqual(isinstance(constant.expression, ast.Operator), True)
        self.assertEqual(constant.expression.name, "IntegerValue")

        self.assertEqual(isinstance(constant.expression.operand1, ast.ParentExpression), True)
        self.assertEqual(constant.expression.operand1.name, "IntegerValue")

        self.assertEqual(isinstance(constant.expression.operand1.term, ast.Operator), True)
        self.assertEqual(constant.expression.operand1.term.operator, "+")
        self.assertEqual(constant.expression.operand1.term.operand1.value, 3.0)
        self.assertEqual(constant.expression.operand1.term.operand2.value, 5.0)
