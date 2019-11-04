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


class TestNumericExpression(BaseTestCase):
    """Test that unsupported Franca features fail appropriately."""

    def test_expressions(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
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
        package = self._assertParse("""
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
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3)
        self.assertEqual(constant.expression.operand1.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand2.operand1.value, 5)
        self.assertEqual(constant.expression.operand1.operand2.operator, "*")
        self.assertEqual(constant.expression.operand1.operand2.operand2.value, 4)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand2.value, 5)

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
        package = self._assertParse("""
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
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3.0)
        self.assertEqual(constant.expression.operand1.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand2.operand1.value, 5.0)
        self.assertEqual(constant.expression.operand1.operand2.operator, "*")
        self.assertEqual(constant.expression.operand1.operand2.operand2.value, 4.0)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand2.value, 6.0)

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
        self.assertEqual(constant.expression.operand1.term.operand1.value, 3)
        self.assertEqual(constant.expression.operand1.term.operand2.value, 5)

        constant = package.typecollections["TC"].constants["u2"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(constant.expression.operand1.operand1.value, 3)
        self.assertEqual(constant.expression.operand1.operator, "+")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.ParentExpression), True)
        self.assertEqual(constant.expression.operand1.operand2.term.operand1.value, 5)
        self.assertEqual(constant.expression.operand1.operand2.term.operator, "*")
        self.assertEqual(constant.expression.operand1.operand2.term.operand2.value, 4)
        self.assertEqual(constant.expression.operator, "+")
        self.assertEqual(constant.expression.operand2.value, 6)

        'checking complex numeric expression'
        constant = package.typecollections["TC"].constants["u3"]
        self.assertEqual(isinstance(constant.expression, ast.ParentExpression), True)
        self.assertEqual(isinstance(constant.expression.term, ast.Term), True)

        'Level 1'
        self.assertEqual(isinstance(constant.expression.term.operand1, ast.Term), True)
        self.assertEqual(constant.expression.term.operator, "*")
        self.assertEqual(isinstance(constant.expression.term.operand2, ast.ParentExpression), True)

        'Level2 Operand 1'
        self.assertEqual(isinstance(constant.expression.term.operand1.operand1, ast.ParentExpression), True)
        self.assertEqual(constant.expression.term.operand1.operator, "/")
        self.assertEqual(isinstance(constant.expression.term.operand1.operand2, ast.Value), True)
        self.assertEqual(constant.expression.term.operand1.operand2.value, 3)

        'Level3 Operand 1.2'
        self.assertEqual(isinstance(constant.expression.term.operand1.operand1.term, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.term.operand1.operand1.term.operand1, ast.Value), True)
        self.assertEqual(constant.expression.term.operand1.operand1.term.operand1.value, 3)
        self.assertEqual(constant.expression.term.operand1.operand2.value, 3)
        self.assertEqual(isinstance(constant.expression.term.operand1.operand1.term.operand2, ast.Term), True)

        'Level2 Operand 2'
        self.assertEqual(constant.expression.term.operand2.term.operand1.value, 5)
        self.assertEqual(constant.expression.term.operand2.term.operator, "+")
        self.assertEqual(isinstance(constant.expression.term.operand2.term.operand2, ast.Value), True)
        self.assertEqual(constant.expression.term.operand2.term.operand2.value, -3)

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
        self.assertEqual(isinstance(constant.expression.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.reference_name, 'x')
        self.assertEqual(constant.expression.operand1.value, None)
        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(constant.expression.operand2.operator, '*')
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.Value), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand1.value, 4)
        self.assertEqual(constant.expression.operand2.operator, "*")
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
                                VALUE_3 = 30*31-23
                                VALUE_4 
                            }

                           }
                       """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)
        enum = package.typecollections["TC"].enumerations["e1"]

        enumerator = enum.enumerators["VALUE_1"]
        self.assertEqual(isinstance(enumerator.expression, ast.Value), True)
        self.assertEqual(enumerator.expression.value, 100)
        self.assertEqual(enumerator.expression.name, "Int8")
        self.assertEqual(enumerator.name, "VALUE_1")

        enumerator = enum.enumerators["VALUE_2"]
        self.assertEqual(isinstance(enumerator.expression, ast.Term), True)
        self.assertEqual(enumerator.expression.value, None)
        self.assertEqual(enumerator.expression.operand1.value, 100)
        self.assertEqual(enumerator.expression.operand2.value, 1)
        self.assertEqual(enumerator.expression.operator, "+")
        self.assertEqual(enumerator.expression.name, "Int8")
        self.assertEqual(enumerator.name, "VALUE_2")

        enumerator = enum.enumerators["VALUE_3"]
        self.assertEqual(isinstance(enumerator.expression, ast.Term), True)
        self.assertEqual(enumerator.expression.value, None)
        self.assertEqual(isinstance(enumerator.expression.operand1, ast.Term), True)
        self.assertEqual(enumerator.expression.operand1.operand1.value, 30)
        self.assertEqual(enumerator.expression.operand1.operand2.value, 31)
        self.assertEqual(enumerator.expression.operand1.operator, "*")
        self.assertEqual(enumerator.expression.operand2.value, 23)
        self.assertEqual(enumerator.expression.operator, "-")
        self.assertEqual(enumerator.expression.name, "Int8")
        self.assertEqual(enumerator.name, "VALUE_3")

        enumerator = enum.enumerators["VALUE_4"]
        self.assertEqual(enumerator.expression, None)
        self.assertEqual(enumerator.name, "VALUE_4")


class TestBooleanExpression(BaseTestCase):
    """Test constants which are initialized with boolean expressions."""

    def test_valid_boolean_expressions(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
            package P
            typeCollection TC {
                const Boolean b1 = true
                const Boolean b2 = MAX_COUNT > 3
                const Boolean b3 = (a && b) || (foo=="bar")
                const Boolean b4 =  a > b || c > d
                const Boolean b5 =  a || b > c || d
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["b1"]
        self.assertEqual(isinstance(constant.expression, ast.Value), True)
        self.assertEqual(constant.expression.value, True)

        constant = package.typecollections["TC"].constants["b2"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.reference_name, "MAX_COUNT")
        self.assertEqual(isinstance(constant.expression.operand2, ast.Value), True)
        self.assertEqual(constant.expression.operand2.value, 3)
        self.assertEqual(constant.expression.operator, ">")

        constant = package.typecollections["TC"].constants["b3"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.ParentExpression), True)
        self.assertEqual(isinstance(constant.expression.operand1.term, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1.term.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.term.operand1.reference_name, "a")
        self.assertEqual(isinstance(constant.expression.operand1.term.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.term.operand2.reference_name, "b")
        self.assertEqual(constant.expression.operand1.term.operator, "&&")
        self.assertEqual(isinstance(constant.expression.operand2, ast.ParentExpression), True)
        self.assertEqual(isinstance(constant.expression.operand2.term, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.term.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.term.operand1.reference_name, "foo")
        self.assertEqual(isinstance(constant.expression.operand1.term.operand2, ast.Value), True)
        self.assertEqual(constant.expression.operand2.term.operand2.value, "bar")
        self.assertEqual(constant.expression.operand2.term.operator, "==")

        constant = package.typecollections["TC"].constants["b4"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand1.reference_name, "a")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand2.reference_name, "b")
        self.assertEqual(constant.expression.operand1.operator, ">")

        self.assertEqual(isinstance(constant.expression.operand2, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand2.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand1.reference_name, "c")
        self.assertEqual(isinstance(constant.expression.operand2.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.operand2.reference_name, "d")
        self.assertEqual(constant.expression.operand2.operator, ">")

        constant = package.typecollections["TC"].constants["b5"]
        self.assertEqual(isinstance(constant.expression, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1, ast.Term), True)
        self.assertEqual(isinstance(constant.expression.operand1.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand1.reference_name, "a")
        self.assertEqual(isinstance(constant.expression.operand1.operand2, ast.Term), True)

        self.assertEqual(isinstance(constant.expression.operand1.operand2.operand1, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand2.operand1.reference_name, "b")
        self.assertEqual(isinstance(constant.expression.operand1.operand2.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand1.operand2.operand2.reference_name, "c")
        self.assertEqual(constant.expression.operand1.operand2.operator, ">")
        self.assertEqual(isinstance(constant.expression.operand2, ast.ValueReference), True)
        self.assertEqual(constant.expression.operand2.reference_name, "d")
        self.assertEqual(constant.expression.operator, "||")


class TestArrayExpression(BaseTestCase):
    """Test constants of type array which are initialized with a list"""

    def test_valid_list_expressions(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
            package P
            typeCollection TC {
               array Array1 of UInt16
               const Array1 empty = []
               const Array1 one = [ 123 ] 
               const Array1 full = [ 1, 2, 2+3, 100*100+100 ] 
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["empty"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionArray), True)
        self.assertEqual(len(constant.expression.elements), 0)

        constant = package.typecollections["TC"].constants["one"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionArray), True)
        self.assertEqual(len(constant.expression.elements), 1)
        self.assertEqual(isinstance(constant.expression.elements[0], ast.Value), True)
        self.assertEqual(constant.expression.elements[0].value, 123)

        constant = package.typecollections["TC"].constants["full"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionArray), True)
        self.assertEqual(len(constant.expression.elements), 4)
        self.assertEqual(isinstance(constant.expression.elements[0], ast.Value), True)
        self.assertEqual(constant.expression.elements[0].value, 1)
        self.assertEqual(isinstance(constant.expression.elements[1], ast.Value), True)
        self.assertEqual(constant.expression.elements[1].value, 2)
        # i do not check all sub elements of the terms. terms are testded in other test routines.
        self.assertEqual(isinstance(constant.expression.elements[2], ast.Term), True)
        self.assertEqual(constant.expression.elements[2].operator, "+")
        self.assertEqual(isinstance(constant.expression.elements[3], ast.Term), True)
        self.assertEqual(constant.expression.elements[3].operator, "+")

    def test_valid_list_expressions_struct(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
            package P
            typeCollection TC {
               struct Struct1 
                {
                    Boolean e1
                    UInt16 e2
                    String e3
                }
                array Array1 of Struct1
                const Array1 a1 =  [ { e1: true, e2: 1, e3: "foo" }, 
                                     { e1: false, e2:2, e3: "bar" }]
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["a1"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionArray), True)
        self.assertEqual(len(constant.expression.elements), 2)
        self.assertEqual(isinstance(constant.expression.elements[0], ast.InitializerExpressionStruct), True)
        self.assertEqual(constant.expression.elements[0].elements["e1"].value, True)
        self.assertEqual(constant.expression.elements[0].elements["e2"].value, 1)
        self.assertEqual(constant.expression.elements[0].elements["e3"].value, "foo")

        self.assertEqual(isinstance(constant.expression.elements[1], ast.InitializerExpressionStruct), True)
        self.assertEqual(constant.expression.elements[1].elements["e1"].value, False)
        self.assertEqual(constant.expression.elements[1].elements["e2"].value, 2)
        self.assertEqual(constant.expression.elements[1].elements["e3"].value, "bar")

    def test_valid_list_expressions_map(self):
        """Franca 0.9.2, section 5.2.1"""
        package = self._assertParse("""
            package P
            typeCollection TC {
               struct Struct1 
                {
                    Boolean e1
                    UInt16 e2
                    String e3
                }
                map Map1 { String to Struct1 }
                const Map1 m1 = [ "foo" => { e1: true, e2: 1, e3: "foo" }, "bar"  => { e1: false, e2:2, e3: "bar" } ]
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)

        constant = package.typecollections["TC"].constants["m1"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionMap), True)
        self.assertEqual(len(constant.expression.elements), 2)
        self.assertEqual(isinstance(constant.expression.elements[0][0], ast.Value), True)
        self.assertEqual(constant.expression.elements[0][0].value, "foo")
        self.assertEqual(isinstance(constant.expression.elements[0][1], ast.InitializerExpressionStruct), True)
        self.assertEqual(constant.expression.elements[0][1].elements["e1"].value, True)
        self.assertEqual(constant.expression.elements[0][1].elements["e2"].value, 1)
        self.assertEqual(constant.expression.elements[0][1].elements["e3"].value, "foo")

        self.assertEqual(isinstance(constant.expression.elements[1][0], ast.Value), True)
        self.assertEqual(constant.expression.elements[1][0].value, "bar")
        self.assertEqual(isinstance(constant.expression.elements[1][1], ast.InitializerExpressionStruct), True)
        self.assertEqual(constant.expression.elements[1][1].elements["e1"].value, False)
        self.assertEqual(constant.expression.elements[1][1].elements["e2"].value, 2)
        self.assertEqual(constant.expression.elements[1][1].elements["e3"].value, "bar")


class TestStructExpression(BaseTestCase):
    """Test constant of type struct that are initialized with an expression"""

    def test_valid_struct_expressions(self):
        """Franca 0.9.2, section 5.2.2"""
        package = self._assertParse("""
            package P
            typeCollection TC {
                struct Struct1 
                {
                    Boolean e1
                    UInt16 e2
                    String e3
                }
                const Struct1 s1 = { e1: true, e2: 1, e3: "foo" }
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)
        constant = package.typecollections["TC"].constants["s1"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionStruct), True)
        self.assertEqual(constant.expression.elements["e1"].value, True)
        self.assertEqual(constant.expression.elements["e2"].value, 1)
        self.assertEqual(constant.expression.elements["e3"].value, "foo")

    def test_valid_struct_expressions_complex(self):
        """Franca 0.9.2, section 5.2.2"""
        package = self._assertParse("""
            package P
            typeCollection TC {
                struct Struct1 
                {
                    Boolean e1
                    UInt16 e2
                    String e3
                }
                const Struct1 s1 = { e1: 24>42, e2: 1+2*3, e3: "foo" }
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)
        constant = package.typecollections["TC"].constants["s1"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionStruct), True)
        self.assertEqual(isinstance(constant.expression.elements["e1"], ast.Term), True)
        self.assertEqual(isinstance(constant.expression.elements["e2"], ast.Term), True)
        self.assertEqual(constant.expression.elements["e3"].value, "foo")

    def test_duplicated_initializer(self):
        """Franca 0.9.2, section 5.2.2"""

        with self.assertRaises(ParserException) as context:
            self._parse("""
            package P
            typeCollection TC {
                struct Struct1 
                {
                    Boolean e1
                    UInt16 e2
                    String e3
                }
                const Struct1 s1 = { e1: true, e1: 1, e3: "foo" }
            }
         """)
        self.assertEqual(str(context.exception),
                         "Duplicate initializer 'e1'.")


class TestMapExpression(BaseTestCase):
    """Test constant of type struct that are initialized with an expression"""

    def test_valid_map_expressions(self):
        """Franca 0.9.2, section 5.2.2"""
        package = self._assertParse("""
            package P
            typeCollection TC {
                map Map1 { UInt16 to String }
                const Map1 m1 = [ 1 => "one", 2 => "two" ]
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)
        constant = package.typecollections["TC"].constants["m1"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionMap), True)
        self.assertEqual(len(constant.expression.elements), 2)
        self.assertEqual(isinstance(constant.expression.elements[0][0], ast.Value), True)
        self.assertEqual(constant.expression.elements[0][0].value, 1)
        self.assertEqual(isinstance(constant.expression.elements[0][1], ast.Value), True)
        self.assertEqual(constant.expression.elements[0][1].value, "one")
        self.assertEqual(isinstance(constant.expression.elements[1][0], ast.Value), True)
        self.assertEqual(constant.expression.elements[1][0].value, 2)
        self.assertEqual(isinstance(constant.expression.elements[1][1], ast.Value), True)
        self.assertEqual(constant.expression.elements[1][1].value, "two")

    def test_valid_map_expressions_complex(self):
        """Franca 0.9.2, section 5.2.2"""
        package = self._assertParse("""
            package P
            typeCollection TC {
                map Map1 { UInt16 to String }
                const Map1 m1 = [ 1+2*3 => a>b, 3+2*1 => a<b ]
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)
        constant = package.typecollections["TC"].constants["m1"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionMap), True)
        self.assertEqual(len(constant.expression.elements), 2)
        self.assertEqual(isinstance(constant.expression.elements[0][0], ast.Term), True)
        self.assertEqual(isinstance(constant.expression.elements[0][1], ast.Term), True)
        self.assertEqual(isinstance(constant.expression.elements[1][0], ast.Term), True)
        self.assertEqual(isinstance(constant.expression.elements[1][1], ast.Term), True)


class TestUnionExpression(BaseTestCase):
    """Test constant of type struct that are initialized with an expression"""

    def test_valid_map_expressions(self):
        """Franca 0.9.2, section 5.2.2"""
        package = self._assertParse("""
            package P
            typeCollection TC {
                union Union1 
                {
                    UInt16 e1
                    Boolean e2
                    String e3
                }
                const Union1 uni1 = { e1: 1 }
                const Union1 uni2 = { e3: "foo" }
            }
        """)

        self.assertEqual(package.name, "P")
        self.assertEqual(len(package.typecollections), 1)
        constant = package.typecollections["TC"].constants["uni1"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionStruct), True)
        self.assertEqual(len(constant.expression.elements), 1)
        self.assertEqual(constant.expression.elements["e1"].value, 1)

        constant = package.typecollections["TC"].constants["uni2"]
        self.assertEqual(isinstance(constant.expression, ast.InitializerExpressionStruct), True)
        self.assertEqual(len(constant.expression.elements), 1)
        self.assertEqual(constant.expression.elements["e3"].value, "foo")
