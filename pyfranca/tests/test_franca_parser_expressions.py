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

    def test_expressions(self):
        """Franca 0.9.2, section 5.2.1"""
        package =  self._assertParse("""
            package P
            typeCollection TC {
                const UInt32 u1 = 55
                const UInt32 u2 = 5-3
                //const UInt32 u2 = (5+4)/2
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


