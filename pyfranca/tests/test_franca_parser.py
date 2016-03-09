
import unittest

from pyfranca.franca_parser import Parser, ParserException
from pyfranca.franca_lexer import LexerException
from pyfranca.ast import Package


class BaseTestCase(unittest.TestCase):

    def _parse(self, data):
        parser = Parser()
        package = parser.parse(data)
        return package

    def _assertParse(self, data):
        package = self._parse(data)
        self.assertIsInstance(package, Package)
        return package


class TestTopLevel(BaseTestCase):
    """Test parsing top-level Franca elements."""

    def test_empty(self):
        """A package statement is expected as a minimum."""
        with self.assertRaises(ParserException) as context:
            self._parse("")
        self.assertEqual(str(context.exception),
                         "Reached unexpected end of file.")

    def test_garbage(self):
        """Invalid input."""
        with self.assertRaises(LexerException) as context:
            self._parse("%!@#")
        self.assertEqual(str(context.exception),
                         "Illegal character '%' at line 1.")

    def test_single_line_comments(self):
        self._assertParse("""
            // Package P
            package P   // This is P
            // EOF
        """)

    def test_multiline_comments(self):
        self._assertParse("""
            /* Package P
            */
            package P   /* This is P */
            /* EOF
            */
        """)

    def test_structured_comments(self):
        self._assertParse("""
            <** @description: Package P
            **>
            package P
        """)

    def test_empty_package(self):
        package = self._assertParse("package P")
        self.assertEqual(package.name, "P")
        self.assertIsNone(package.file)
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 0)

    def test_multiple_package_definitions(self):
        with self.assertRaises(ParserException) as context:
            self._parse("""
                package P
                package P2
            """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 3 near 'package'.")

    def test_import_namespace(self):
        package = self._assertParse("package P import NS from \"test.fidl\"")
        self.assertEqual(package.name, "P")
        self.assertIsNone(package.file)
        self.assertEqual(len(package.imports), 1)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 0)
        imp = package.imports[0]
        self.assertEqual(imp.namespace, "NS")
        self.assertEqual(imp.file, "test.fidl")

    def test_import_model(self):
        package = self._assertParse("package P import model \"test.fidl\"")
        self.assertEqual(package.name, "P")
        self.assertIsNone(package.file)
        self.assertEqual(len(package.imports), 1)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 0)
        imp = package.imports[0]
        self.assertIsNone(imp.namespace)
        self.assertEqual(imp.file, "test.fidl")

    def test_import_two_namespaces(self):
        package = self._assertParse("""
            package P
            import NS1 from \"test1.fidl\"
            import NS2 from \"test2.fidl\"
        """)
        self.assertEqual(package.name, "P")
        self.assertIsNone(package.file)
        self.assertEqual(len(package.imports), 2)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 0)
        imp = package.imports[0]
        self.assertEqual(imp.namespace, "NS1")
        self.assertEqual(imp.file, "test1.fidl")
        imp = package.imports[1]
        self.assertEqual(imp.namespace, "NS2")
        self.assertEqual(imp.file, "test2.fidl")

    def test_empty_typecollection(self):
        package = self._assertParse("package P typeCollection TC {}")
        self.assertEqual(package.name, "P")
        self.assertIsNone(package.file)
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 1)
        self.assertEqual(len(package.interfaces), 0)
        self.assertTrue("TC" in package.typecollections)
        typecollection = package.typecollections["TC"]
        self.assertEqual(typecollection.package, package)
        self.assertEqual(typecollection.name, "TC")
        self.assertListEqual(typecollection.flags, [])
        self.assertIsNone(typecollection.version)
        self.assertEqual(len(typecollection.typedefs), 0)
        self.assertEqual(len(typecollection.enumerations), 0)
        self.assertEqual(len(typecollection.structs), 0)
        self.assertEqual(len(typecollection.arrays), 0)
        self.assertEqual(len(typecollection.maps), 0)

    def test_two_empty_typecollections(self):
        package = self._assertParse("""
            package P
            typeCollection TC1 {}
            typeCollection TC2 {}
        """)
        self.assertEqual(package.name, "P")
        self.assertIsNone(package.file)
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 2)
        self.assertEqual(len(package.interfaces), 0)
        self.assertTrue("TC1" in package.typecollections)
        typecollection = package.typecollections["TC1"]
        self.assertEqual(typecollection.package, package)
        self.assertEqual(typecollection.name, "TC1")
        self.assertListEqual(typecollection.flags, [])
        self.assertIsNone(typecollection.version)
        self.assertEqual(len(typecollection.typedefs), 0)
        self.assertEqual(len(typecollection.enumerations), 0)
        self.assertEqual(len(typecollection.structs), 0)
        self.assertEqual(len(typecollection.arrays), 0)
        self.assertEqual(len(typecollection.maps), 0)
        self.assertTrue("TC2" in package.typecollections)
        typecollection = package.typecollections["TC2"]
        self.assertEqual(typecollection.package, package)
        self.assertEqual(typecollection.name, "TC2")
        self.assertListEqual(typecollection.flags, [])
        self.assertIsNone(typecollection.version)
        self.assertEqual(len(typecollection.typedefs), 0)
        self.assertEqual(len(typecollection.enumerations), 0)
        self.assertEqual(len(typecollection.structs), 0)
        self.assertEqual(len(typecollection.arrays), 0)
        self.assertEqual(len(typecollection.maps), 0)

    def test_empty_interface(self):
        package = self._assertParse("package P interface I {}")
        self.assertEqual(package.name, "P")
        self.assertIsNone(package.file)
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 1)
        self.assertTrue("I" in package.interfaces)
        interface = package.interfaces["I"]
        self.assertEqual(interface.package, package)
        self.assertEqual(interface.name, "I")
        self.assertListEqual(interface.flags, [])
        self.assertIsNone(interface.version)
        self.assertEqual(len(interface.typedefs), 0)
        self.assertEqual(len(interface.enumerations), 0)
        self.assertEqual(len(interface.structs), 0)
        self.assertEqual(len(interface.arrays), 0)
        self.assertEqual(len(interface.maps), 0)
        self.assertEqual(len(interface.attributes), 0)
        self.assertEqual(len(interface.methods), 0)
        self.assertEqual(len(interface.broadcasts), 0)

    def test_two_empty_interfaces(self):
        package = self._assertParse("""
            package P
            interface I1 {}
            interface I2 {}
        """)
        self.assertEqual(package.name, "P")
        self.assertIsNone(package.file)
        self.assertEqual(len(package.imports), 0)
        self.assertEqual(len(package.typecollections), 0)
        self.assertEqual(len(package.interfaces), 2)
        self.assertTrue("I1" in package.interfaces)
        interface = package.interfaces["I1"]
        self.assertEqual(interface.package, package)
        self.assertEqual(interface.name, "I1")
        self.assertListEqual(interface.flags, [])
        self.assertIsNone(interface.version)
        self.assertEqual(len(interface.typedefs), 0)
        self.assertEqual(len(interface.enumerations), 0)
        self.assertEqual(len(interface.structs), 0)
        self.assertEqual(len(interface.arrays), 0)
        self.assertEqual(len(interface.maps), 0)
        self.assertEqual(len(interface.attributes), 0)
        self.assertEqual(len(interface.methods), 0)
        self.assertEqual(len(interface.broadcasts), 0)
        self.assertTrue("I2" in package.interfaces)
        interface = package.interfaces["I2"]
        self.assertEqual(interface.package, package)
        self.assertEqual(interface.name, "I2")
        self.assertListEqual(interface.flags, [])
        self.assertIsNone(interface.version)
        self.assertEqual(len(interface.typedefs), 0)
        self.assertEqual(len(interface.enumerations), 0)
        self.assertEqual(len(interface.structs), 0)
        self.assertEqual(len(interface.arrays), 0)
        self.assertEqual(len(interface.maps), 0)
        self.assertEqual(len(interface.attributes), 0)
        self.assertEqual(len(interface.methods), 0)
        self.assertEqual(len(interface.broadcasts), 0)


class TestFrancaUserManualExamples(BaseTestCase):
    """Test parsing various examples from the Franca user manual."""

    def test_calculator_api(self):
        self._assertParse("""
            package P
            interface CalculatorAPI {
                method add {
                    in {
                        Float a
                        Float b
                    }
                    out {
                        Float sum
                    }
                }
            }
        """)

    def test_example_interface(self):
        self._assertParse("""
            package P
            interface ExampleInterface {
                attribute Double temperature readonly noSubscriptions
                attribute Boolean overheated
            }
        """)

    def test_calculator_divide(self):
        """Method "error extends ..." statements are not supported."""
        with self.assertRaises(ParserException) as context:
            self._parse("""
            package P
            interface Calculator {
                method divide {
                    in {
                        UInt32 dividend
                        UInt32 divisor
                    }
                    out {
                        UInt32 quotient
                        UInt32 remainder
                    }
                    error extends GenericErrors {
                        DIVISION_BY_ZERO
                        OVERFLOW
                        UNDERFLOW
                    }
                }
                enumeration GenericErrors {
                    INVALID_PARAMATERS
                    // ...
                }
            }
        """)
        self.assertEqual(str(context.exception),
                         "Syntax error at line 13 near 'extends'.")

    def test_calculator_divide2(self):
        self._assertParse("""
            package P
            interface Calculator {
                method divide {
                    in {
                        UInt32 dividend
                        UInt32 divisor
                    }
                    out {
                        UInt32 quotient
                        UInt32 remainder
                    }
                    error CalcErrors
                }
                enumeration CalcErrors {
                    DIVISION_BY_ZERO
                    OVERFLOW
                    UNDERFLOW
                }
            }
        """)

    def test_broadcast(self):
        self._assertParse("""
            package P
            interface ExampleInterface {
                broadcast buttonClicked {
                    out {
                        ButtonId id
                        Boolean isLongPress
                    }
                }
            }
        """)


class TestMisc(BaseTestCase):
    """Test parsing various FIDL examples."""

    def test_all_supported(self):
        self._assertParse("""
            package P

            import m1.* from "m1.fidl"
            import model "m2.fidl"

            typeCollection TC {
                version { major 1 minor 0 }

                typedef MyInt8 is Int8
                typedef MyInt16 is Int16
                typedef MyInt32 is Int32
                typedef MyInt64 is Int64
                typedef MyUInt8 is UInt8
                typedef MyUInt16 is UInt16
                typedef MyUInt32 is UInt32
                typedef MyUInt64 is UInt64
                typedef MyBoolean is Boolean
                typedef MyFloat is Float
                typedef MyDouble is Double
                typedef MyString is String
                typedef MyByteBuffer is ByteBuffer

                typedef MyInt32Array is Int32[]
                typedef MyThis is MyThat

                enumeration E {
                    FALSE = 0
                    TRUE
                }
                enumeration E2 extends E {}

                struct S {
                    Int32 a
                    Int32[] b
                }
                struct S2 extends S {}
                struct S3 polymorphic {}

                array A of UInt8

                map M {
                    String to Int32
                }
                map M2 {
                    Key to Value
                }
            }

            interface I {
                version { major 1 minor 0 }

                attribute Int32 A
                attribute Int32 A2 readonly
                attribute Int32 A3 noSubscriptions

                method M {
                    in {
                        Float a
                        Float[] b
                    }
                    out {
                        Float result
                    }
                    error {
                        FAILURE = 0
                        SUCCESS
                    }
                }
                method M2 fireAndForget {}

                broadcast B {
                    out {
                        Int32 x
                    }
                }
                broadcast B2 selective {}

                typedef ITD is String

                enumeration IE {
                    FALSE = 0
                    TRUE
                }

                struct IS {
                    Int32 a
                    Int32[] b
                }

                array IA of UInt8

                map IM {
                    String to Int32
                }
            }

            interface I2 extends I {
            }
        """)
