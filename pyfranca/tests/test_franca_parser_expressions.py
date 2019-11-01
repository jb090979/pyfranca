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
                const UInt32 u3 = 50-3*2
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(constant.name, "u1")
        self.assertEqual(constant.expression.value, 55)
        self.assertEqual(constant.value, None)

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(constant.name, "u2")
        self.assertEqual(constant.value, None)
        expr = constant.expression
        self.assertIsInstance(expr, ast.Term)
        self.assertEqual(expr.operator, "-")
        self.assertEqual(expr.operand1.value, 5)
        self.assertEqual(expr.operand2.value, 3)

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
                const UInt32 u8 =  4+-5
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, 3)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand2.operand1.operand1.value, 5)
        self.assertEqual(constant.expression.operand2.operand1.operator, "*")
        self.assertEqual(constant.expression.operand2.operand1.operand2.value, 4)
        self.assertEqual(constant.expression.operand2.operand2.value, 5)
        self.assertEqual(constant.expression.operand2.operator, "+")

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3)
        self.assertEqual(constant.expression.operand1.operand2.value, 5)
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.operand2.value, 5)
        self.assertEqual(constant.expression.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u3"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3)
        self.assertEqual(constant.expression.operand1.operand2.value, 5)
        self.assertEqual(constant.expression.operand1.operator, "/")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.operand2.value, 5)
        self.assertEqual(constant.expression.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u4"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, 5)

        constant = package.typecollections["TC"].constants["u5"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, 5)

        constant = package.typecollections["TC"].constants["u6"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, -5)

        constant = package.typecollections["TC"].constants["u7"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, 5)

        constant = package.typecollections["TC"].constants["u8"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.value, -5)

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
                const Float u8 = 4.0F+-5.0F
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, 3.0)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand2.operand1.operand1.value, 5.0)
        self.assertEqual(constant.expression.operand2.operand1.operator, "*")
        self.assertEqual(constant.expression.operand2.operand1.operand2.value, 4.0)
        self.assertEqual(constant.expression.operand2.operand2.value, 6.0)
        self.assertEqual(constant.expression.operand2.operator, "+")

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3.0)
        self.assertEqual(constant.expression.operand1.operand2.value, 5.0)
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.operand2.value, 5.0)
        self.assertEqual(constant.expression.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u3"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3.0)
        self.assertEqual(constant.expression.operand1.operand2.value, 5.0)
        self.assertEqual(constant.expression.operand1.operator, "/")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.operand2.value, 5.0)
        self.assertEqual(constant.expression.operand2.operator, "*")

        constant = package.typecollections["TC"].constants["u4"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, 5.0)

        constant = package.typecollections["TC"].constants["u5"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, 5.0)

        constant = package.typecollections["TC"].constants["u6"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "-")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, -5.0)

        constant = package.typecollections["TC"].constants["u7"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, 5.0)

        constant = package.typecollections["TC"].constants["u8"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand1.value, 4.0)
        self.assertEqual(constant.expression.operand2.value, -5.0)

    def test_arithmetic_parentheses(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
                    package P
                    typeCollection TC {
                        const UInt32 u1 = (3+5)*(4+6)
                        const UInt32 u2 = 3 + (5 * 4) + 6
                        const UInt32 u3 = (( 3+ 4*5 ) / 3 * (5+-3))
                    }
                """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)
        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.name, "Int8")
        self.assertEqual(isinstance(constant.expression.operand1, ast.ParentExpression), True)
        self.assertEqual(constant.expression.operand1.name, "Int8")
        self.assertEqual(isinstance(constant.expression.operand1.term, ast.Term), True)
        self.assertEqual(constant.expression.operand1.term.operator, "+")
        self.assertEqual(constant.expression.operand1.term.operand1.value, 3.0)
        self.assertEqual(constant.expression.operand1.term.operand2.value, 5.0)

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, 3.0)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.ParentExpression), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1.term, ast.Term), True)
        self.assertEqual(constant.expression.operand2.operand1.term.operand1.value, 5.0)
        self.assertEqual(constant.expression.operand2.operand1.term.operator, "*")
        self.assertEqual(constant.expression.operand2.operand1.term.operand2.value, 4.0)
        self.assertEqual(constant.expression.operand2.operand2.value, 6.0)
        self.assertEqual(constant.expression.operand2.operator, "+")

        'checking complex numeric expression'
        constant = package.typecollections["TC"].constants["u3"]
        self.assertEqual(isinstance(constant.expression, ast.ParentExpression), True)
        self.assertEqual(isinstance(constant.expression.term, ast.Term), True)

        'Level 1'
        self.assertEqual(isinstance(constant.expression.term.operand1, ast.ParentExpression), True)
        self.assertEqual(constant.expression.term.operator, "/")
        self.assertEqual(isinstance(constant.expression.term.operand2, ast.Term), True)

        'Level2 Operand 1'
        self.assertEqual(isinstance(constant.expression.term.operand1.term, ast.Term), True)
        self.assertEqual(constant.expression.term.operand1.term.operand1.value, 3)
        self.assertEqual(constant.expression.term.operand1.term.operator, "+")
        self.assertEqual(isinstance(constant.expression.term.operand1.term.operand2, ast.Term), True)

        'Level3 Operand 1.2'
        self.assertEqual(constant.expression.term.operand1.term.operand2.operand1.value, 4)
        self.assertEqual(constant.expression.term.operand1.term.operand2.operator, "*")
        self.assertEqual(constant.expression.term.operand1.term.operand2.operand2.value, 5)

        'Level2 Operand 2'
        self.assertEqual(constant.expression.term.operand2.operand1.value, 3)
        self.assertEqual(constant.expression.term.operand2.operator, "*")
        self.assertEqual(isinstance(constant.expression.term.operand2.operand2, ast.ParentExpression), True)
        self.assertEqual(isinstance(constant.expression.term.operand2.operand2.term, ast.Term), True)

        'Level3 Operand 2.2'
        self.assertEqual(constant.expression.term.operand2.operand2.term.operand1.value, 5)
        self.assertEqual(constant.expression.term.operand2.operand2.term.operator, "+")
        self.assertEqual(constant.expression.term.operand2.operand2.term.operand2.value, -3)

    def test_expressions_with_references(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
                       package P
                       typeCollection TC {
                           const UInt32 u1 = x+y*z
                           const UInt32 u2 = x + 4 * z
                           const UInt32 u3 = x+4*z
                           const UInt32 u4 = 6 + y * 7
                           const UInt32 u5 = 6+y*7
                           
                           const UInt32 u6 = x*y+z
                           const UInt32 u7 = x * 5 + z
                           const UInt32 u8 = x*5+z
                           const UInt32 u9 = 8 * y + 9
                           const UInt32 u10 = 8*y+9
                       }
                   """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, None)
        self.assertEqual(isinstance(constant.expression.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.reference_name, 'x')
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand1.value, None)
        self.assertEqual(constant.expression.operand2.operand1.reference_name, 'y')
        self.assertEqual(constant.expression.operand2.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand2.value, None)
        self.assertEqual(constant.expression.operand2.operand2.reference_name, 'z')

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, None)
        self.assertEqual(isinstance(constant.expression.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.reference_name, 'x')
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand2.value, None)
        self.assertEqual(constant.expression.operand2.operand2.reference_name, 'z')

        constant = package.typecollections["TC"].constants["u3"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, None)
        self.assertEqual(isinstance(constant.expression.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.reference_name, 'x')
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand2.value, None)
        self.assertEqual(constant.expression.operand2.operand2.reference_name, 'z')

        constant = package.typecollections["TC"].constants["u4"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, 6)
        self.assertEqual(isinstance(constant.expression.operand1, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand1.value, None)
        self.assertEqual(constant.expression.operand2.operand1.reference_name, 'y')
        self.assertEqual(constant.expression.operand2.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2.operand2, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operand2.operand2.value, 7)

        constant = package.typecollections["TC"].constants["u5"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, 6)
        self.assertEqual(isinstance(constant.expression.operand1, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand1.value, None)
        self.assertEqual(constant.expression.operand2.operand1.reference_name, 'y')
        self.assertEqual(constant.expression.operand2.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2.operand2, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operand2.operand2.value, 7)

        constant = package.typecollections["TC"].constants["u6"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand1.value, None)
        self.assertEqual(constant.expression.operand1.operand1.reference_name, 'x')
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand2.value, None)
        self.assertEqual(constant.expression.operand1.operand2.reference_name, 'y')
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand2.value, None)
        self.assertEqual(isinstance(constant.expression.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.reference_name, 'z')

        constant = package.typecollections["TC"].constants["u7"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand1.value, None)
        self.assertEqual(constant.expression.operand1.operand1.reference_name, 'x')
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operand1.operand2.value, 5)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand2.value, None)
        self.assertEqual(isinstance(constant.expression.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.reference_name, 'z')

        constant = package.typecollections["TC"].constants["u8"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand1.value, None)
        self.assertEqual(constant.expression.operand1.operand1.reference_name, 'x')
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operand1.operand2.value, 5)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand2.value, None)
        self.assertEqual(isinstance(constant.expression.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.reference_name, 'z')

        constant = package.typecollections["TC"].constants["u9"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1.operand1, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 8)
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand2.value, None)
        self.assertEqual(constant.expression.operand1.operand2.reference_name, 'y')
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand2.value, 9)
        self.assertEqual(isinstance(constant.expression.operand2, ast.IntegerValue), True)

        constant = package.typecollections["TC"].constants["u10"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1.operand1, ast.IntegerValue), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 8)
        self.assertEqual(constant.expression.operand1.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand2.value, None)
        self.assertEqual(constant.expression.operand1.operand2.reference_name, 'y')
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand2.value, 9)
        self.assertEqual(isinstance(constant.expression.operand2, ast.IntegerValue), True)

    def test_expressions_with_fqn(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
                           package P
                           typeCollection TC {
                               const UInt32 u1 = p.x+p.y*p.z
    
                           }
                       """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["u1"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(constant.expression.operand1.value, None)
        self.assertEqual(isinstance(constant.expression.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.reference_name, 'p.x')
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand1.value, None)
        self.assertEqual(constant.expression.operand2.operand1.reference_name, 'p.y')
        self.assertEqual(constant.expression.operand2.operator, "*")
        self.assertEqual(isinstance(constant.expression.operand2.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand2.value, None)
        self.assertEqual(constant.expression.operand2.operand2.reference_name, 'p.z')

    def test_expression_in_enumeration(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
                           package P
                           typeCollection TC {
                               
                            enumeration e1 
                            { 
                                VALUE_1 = 100 
                                VALUE_2 = 100+1 
                                VALUE_3 = 30*30-23
                            }

                           }
                       """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

