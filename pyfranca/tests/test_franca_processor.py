"""
Pyfranca processor tests.
"""

import unittest
import os
import errno
import shutil

from pyfranca import ProcessorException, Processor, ast


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        # Create temporary file directory.
        tmp_dir = self.get_spec()
        try:
            os.makedirs(tmp_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            # Delete and try again
            shutil.rmtree(tmp_dir)
            os.makedirs(tmp_dir)
        # Create FIDL processor.
        self.processor = Processor()
        self.processor.package_paths.append(tmp_dir)

    def tearDown(self):
        self.processor = None
        # Remove temporary file directory.
        tmp_dir = self.get_spec()
        shutil.rmtree(tmp_dir)

    @staticmethod
    def get_spec(basedir="tmp", filename=None):
        """
        Get absolute specification a directory or a file under pyfranca/tests/fidl/ .
        :param basedir: Target subdirectory.
        :param filename: File name or None to get a directory specification
        :return: Absolute specification.
        """
        script_dir = os.path.dirname(os.path.realpath(__file__))
        spec = os.path.join(script_dir, "fidl", basedir)
        if filename:
            spec = os.path.join(spec, filename)
        return spec

    def tmp_fidl(self, filename, content):
        fspec = self.get_spec(filename=filename)
        with open(fspec, "w") as f:
            f.write(content)
        return fspec

    def import_tmp_fidl(self, filename, content):
        fspec = self.tmp_fidl(filename, content)
        self.processor.import_file(fspec)


class TestFQNs(BaseTestCase):
    """Test FQN parsing methods."""

    def test_basename(self):
        self.assertEqual(Processor.basename("P.I.A"), "A")
        self.assertEqual(Processor.basename("A"), "A")

    def test_packagename(self):
        self.assertEqual(Processor.packagename("P.I.A"), "P.I")
        self.assertIsNone(Processor.packagename("A"))

    def test_is_fqn(self):
        self.assertTrue(Processor.is_fqn("P.P.I.A"))
        self.assertTrue(Processor.is_fqn("P.I.A"))
        self.assertFalse(Processor.is_fqn("I.A"))
        self.assertFalse(Processor.is_fqn("A"))

    def test_split_fqn(self):
        self.assertEqual(Processor.split_fqn("P.P.I.A"), ("P.P", "I", "A"))
        self.assertEqual(Processor.split_fqn("P.I.A"), ("P", "I", "A"))
        self.assertEqual(Processor.split_fqn("I.A"), (None, "I", "A"))
        self.assertEqual(Processor.split_fqn("A"), (None, None, "A"))


class TestImports(BaseTestCase):
    """Test import related features."""

    def test_basic(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
        """)
        fspec2 = self.tmp_fidl("test2.fidl", """
            package P2
        """)
        self.processor.import_file(fspec)
        self.processor.import_file(fspec2)

        # Verify file access
        self.assertEqual(len(self.processor.files), 2)
        p = self.processor.files[fspec]
        self.assertEqual(p.name, "P")
        p2 = self.processor.files[fspec2]
        self.assertEqual(p2.name, "P2")
        # Verify package access
        self.assertEqual(len(self.processor.packages), 2)
        p = self.processor.packages["P"]
        self.assertEqual(p.name, "P")
        p2 = self.processor.packages["P2"]
        self.assertEqual(p2.name, "P2")

    def test_import_nonexistent_model(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                import model "nosuch.fidl"
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Model 'nosuch.fidl' not found.")

    def test_import_nonexistent_model2(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                import P.Nonexistent.* from "nosuch.fidl"
            """)
            self.processor.import_file(fspec)
        self.assertEqual(str(context.exception),
                         "Model 'nosuch.fidl' not found.")

    def test_import_nonexistent_namespace(self):
        with self.assertRaises(ProcessorException) as context:
            self.tmp_fidl("test.fidl", """
                package P
            """)
            fspec = self.tmp_fidl("test2.fidl", """
                package P2
                import P.Nonexistent.* from "test.fidl"
            """)
            self.processor.import_file(fspec)
            print("Hello")

        self.assertEqual(str(context.exception),
                         "Namespace 'P.Nonexistent.*' not found.")

    def test_circular_dependency(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            import model "test2.fidl"
        """)
        self.tmp_fidl("test2.fidl", """
            package P2
            import model "test.fidl"
        """)
        self.processor.import_file(fspec)
        # FIXME: What is the correct behavior?


class TestPackagesInMultipleFiles(BaseTestCase):
    """Support for packages in multiple files"""

    def test_package_in_multiple_files(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
        """)
        fspec2 = self.tmp_fidl("test2.fidl", """
            package P
        """)
        self.processor.import_file(fspec)
        self.processor.import_file(fspec2)
        p = self.processor.packages["P"]
        self.assertEqual(p.files, [fspec, fspec2])

    def test_package_in_multiple_files_reuse(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        fspec2 = self.tmp_fidl("test2.fidl", """
            package P
            import P.TC.* from "test.fidl"
            interface I {
                typedef B is A
            }
        """)
        self.processor.import_file(fspec)
        self.processor.import_file(fspec2)

        p = self.processor.packages["P"]
        self.assertEqual(p.files, [fspec, fspec2])
        a = p.typecollections["TC"].typedefs["A"]
        self.assertEqual(a.namespace.package, p)
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = p.interfaces["I"].typedefs["B"]
        self.assertEqual(b.namespace.package, p)
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)


class TestReferences(BaseTestCase):
    """Test type references."""

    def test_reference_to_same_namespace(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
                typedef B is A
            }
        """)
        self.processor.import_file(fspec)

        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = self.processor.packages["P"].typecollections["TC"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    def test_fqn_reference(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
                typedef B is P.TC.A
            }
        """)
        self.processor.import_file(fspec)

        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = self.processor.packages["P"].typecollections["TC"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    def test_reference_to_different_namespace(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
            interface I {
                typedef B is A
            }
        """)
        self.processor.import_file(fspec)

        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = self.processor.packages["P"].interfaces["I"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    def test_reference_to_different_model(self):
        self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        fspec = self.tmp_fidl("test2.fidl", """
            package P2
            import P.TC.* from "test.fidl"
            interface I {
                typedef B is A
            }
        """)
        self.processor.import_file(fspec)

        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        b = self.processor.packages["P2"].interfaces["I"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    @unittest.skip("Currently not checked.")
    def test_circular_reference(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                typeCollection TC {
                    typedef A is B
                    typedef B is A
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Circular reference 'B'.")

    def test_reference_priority(self):
        self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        fspec = self.tmp_fidl("test2.fidl", """
            package P2
            import P.TC.* from "test.fidl"
            typeCollection TC {
                typedef A is UInt32
            }
            interface I {
                typedef B is P2.TC.A
                typedef B2 is P.TC.A
            }
        """)
        self.processor.import_file(fspec)

        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        a2 = self.processor.packages["P2"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a2.type, ast.UInt32))
        b = self.processor.packages["P2"].interfaces["I"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a2)
        b2 = self.processor.packages["P2"].interfaces["I"].typedefs["B2"]
        self.assertTrue(isinstance(b2.type, ast.Reference))
        self.assertEqual(b2.type.name, "A")
        self.assertEqual(b2.type.reference, a)

    def test_interface_visibility(self):
        self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                typedef A is Int32
            }
        """)
        fspec = self.tmp_fidl("test2.fidl", """
            package P2
            import P.TC.* from "test.fidl"
            interface I {
                typedef A is UInt32
            }
            typeCollection TC {
                typedef B is TC.A
            }
        """)
        self.processor.import_file(fspec)

        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        a2 = self.processor.packages["P2"].interfaces["I"].typedefs["A"]
        self.assertTrue(isinstance(a2.type, ast.UInt32))
        b = self.processor.packages["P2"].typecollections["TC"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A")
        self.assertEqual(b.type.reference, a)

    def test_unresolved_reference_in_typedef(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                typeCollection TC {
                    typedef TD is Unknown
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_struct(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                typeCollection TC {
                    struct S {
                        Unknown f
                    }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_array(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                typeCollection TC {
                    array A of Unknown
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_map(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                typeCollection TC {
                    map M { Unknown to Int32 }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_map2(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                typeCollection TC {
                    map M { Int32 to Unknown }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_attribute(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                interface I {
                    attribute Unknown A
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                interface I {
                    method M { in { Unknown a } }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method2(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                interface I {
                    method M { out { Unknown a } }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_method3(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                interface I {
                    method M { error Unknown }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_unresolved_reference_in_broadcast(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                interface I {
                    broadcast B { out { Unknown a } }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved reference 'Unknown'.")

    def test_method_error_reference(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            interface I {
                enumeration E { A B C }
                method M { error E }
            }
        """)
        self.processor.import_file(fspec)

        e = self.processor.packages["P"].interfaces["I"].enumerations["E"]
        m = self.processor.packages["P"].interfaces["I"].methods["M"]
        me = m.errors
        self.assertTrue(isinstance(me, ast.Reference))
        self.assertEqual(me.reference, e)

    def test_method_nameless_error(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            interface I {
                method M { error { A B C }  }
            }
        """)
        self.processor.import_file(fspec)

        m = self.processor.packages["P"].interfaces["I"].methods["M"]
        me = m.errors
        self.assertTrue(isinstance(me['A'], ast.Enumerator))
        self.assertTrue(isinstance(me['B'], ast.Enumerator))
        self.assertTrue(isinstance(me['C'], ast.Enumerator))

        self.assertEqual(me['A'].name, "A")
        self.assertEqual(me['B'].name, "B")
        self.assertEqual(me['C'].name, "C")

    def test_invalid_method_error_reference(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                interface I {
                    typedef E is String
                    method M { error E }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Invalid error reference 'E'.")

    def test_enumeration_extension(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            interface I {
                enumeration E { A B C }
                enumeration E2 extends E { D E F }
            }
        """)
        self.processor.import_file(fspec)

        e = self.processor.packages["P"].interfaces["I"].enumerations["E"]
        e2 = self.processor.packages["P"].interfaces["I"].enumerations["E2"]
        self.assertEqual(e2.reference, e)

    def test_invalid_enumeration_extension(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                interface I {
                    typedef E is String
                    enumeration E2 extends E { D E F }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Invalid enumeration reference 'E'.")

    def test_invalid_enumeration_extension2(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            interface I {
                enumeration E { A B C }
                enumeration E2 extends E { A E F }
            }
        """)
        self.processor.import_file(fspec)

        e = self.processor.packages["P"].interfaces["I"].enumerations["E"]
        e2 = self.processor.packages["P"].interfaces["I"].enumerations["E2"]
        self.assertEqual(e2.reference, e)

    def test_struct_extension(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            interface I {
                struct S { Int32 a }
                struct S2 extends S { Int32 b }
            }
        """)
        self.processor.import_file(fspec)

        s = self.processor.packages["P"].interfaces["I"].structs["S"]
        s2 = self.processor.packages["P"].interfaces["I"].structs["S2"]
        self.assertEqual(s2.reference, s)

    def test_invalid_struct_extension(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                interface I {
                    typedef S is String
                    struct S2 extends S { Int32 b }
                }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Invalid struct reference 'S'.")

    def test_interface_extension(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            interface I { }
            interface I2 extends I { }
            interface I3 extends P.I { }
        """)
        self.processor.import_file(fspec)

        i = self.processor.packages["P"].interfaces["I"]
        i2 = self.processor.packages["P"].interfaces["I2"]
        self.assertEqual(i2.reference, i)
        i3 = self.processor.packages["P"].interfaces["I3"]
        self.assertEqual(i3.reference, i)

    def test_interface_extension2(self):
        self.tmp_fidl("test.fidl", """
            package P
            interface I { }
        """)
        fspec = self.tmp_fidl("test2.fidl", """
            package P2
            import model "test.fidl"
            interface I2 extends I { }
            interface I3 extends P.I { }
        """)
        self.processor.import_file(fspec)

        i = self.processor.packages["P"].interfaces["I"]
        i2 = self.processor.packages["P2"].interfaces["I2"]
        self.assertEqual(i2.reference, i)
        i3 = self.processor.packages["P2"].interfaces["I3"]
        self.assertEqual(i3.reference, i)

    def test_invalid_interface_extension(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("test.fidl", """
                package P
                typeCollection TC { typedef I is Int32 }
                interface I2 extends I { }
            """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Unresolved namespace reference 'I'.")

    def test_anonymous_array_references(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                typedef TD is Int32
                typedef TDA is TD[]
                array ATDA of TD[]
                struct S { TD[] tda }
                map M { TD[] to TD[] }
            }
            interface I {
                attribute TD[] A
                method M { in { TD[] tda } out { TD[] tda } }
                broadcast B { out { TD[] tda } }
            }
        """)
        self.processor.import_file(fspec)

        tc = self.processor.packages["P"].typecollections["TC"]
        td = tc.typedefs["TD"]
        tda = tc.typedefs["TDA"]
        self.assertEqual(tda.type.type.reference, td)
        atda = tc.arrays["ATDA"]
        self.assertEqual(atda.type.type.reference, td)
        s = tc.structs["S"]
        self.assertEqual(s.fields["tda"].type.type.reference, td)
        m = tc.maps["M"]
        self.assertEqual(m.key_type.type.reference, td)
        self.assertEqual(m.value_type.type.reference, td)
        i = self.processor.packages["P"].interfaces["I"]
        a = i.attributes["A"]
        self.assertEqual(a.type.type.reference, td)
        m = i.methods["M"]
        self.assertEqual(m.in_args["tda"].type.type.reference, td)
        self.assertEqual(isinstance(m.in_args["tda"].type, ast.Array), True)
        self.assertEqual(m.out_args["tda"].type.type.reference, td)
        b = i.broadcasts["B"]
        self.assertEqual(b.out_args["tda"].type.type.reference, td)

    def test_import_missing_files(self):
        # P.fidl references definitions.fidl but it is not in the package path.
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_file(
                os.path.join(self.get_spec("idl"), "P.fidl"))
            self.processor.import_file(
                os.path.join(self.get_spec("idl2"), "P2.fidl"))
        self.assertEqual(str(context.exception),
                         "Model 'definitions.fidl' not found.")

    def test_import_multiple_files(self):
        fidl_dir = self.get_spec("idl")
        self.processor.package_paths.append(fidl_dir)
        self.processor.import_file(
            os.path.join(fidl_dir, "P.fidl"))
        self.processor.import_file(
            os.path.join(self.get_spec("idl2"), "P2.fidl"))

    def test_import_file_chain(self):
        fspec = self.tmp_fidl("P.fidl", """
            package P
            import P.Type1.* from "Type1.fidl"
            import P.Type2.* from "Type2.fidl"
            interface I {
                version { major 1 minor 0 }
                method getData {
                    out {
                          MyStructType1 outVal
                       }
                    in {
                          MyStructType2 inVal
                       }
                }
            }
        """)
        self.tmp_fidl("Type1.fidl", """
            package P
            import P.Common.* from "common.fidl"
            typeCollection Type1 {
                version { major 1 minor 0 }
                struct MyStructType1 {
                    UInt8 val1
                    MyEnum val2
                    String  msg
                }
            }
        """)
        self.tmp_fidl("Type2.fidl", """
            package P
            import P.Common.* from "common.fidl"
            typeCollection Type2 {
                version { major 1 minor 0 }
                struct MyStructType2 {
                    UInt8 val1
                    MyEnum val2
                    String  msg
                }
            }
        """)
        self.tmp_fidl("common.fidl", """
            package P
            typeCollection Common {
                version { major 1 minor 0 }
                enumeration MyEnum {
                    abc
                    def
                    ghi
                    jkm
                }
            }
        """)
        self.processor.import_file(fspec)
        self.processor.import_file("./Type1.fidl")

        self.assertEqual(self.processor.packages["P"].name, "P")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["outVal"].type.reference.namespace.name, "Type1")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["outVal"].type.reference.namespace.package.name, "P")

        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         in_args["inVal"].type.reference.namespace.name, "Type2")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         in_args["inVal"].type.reference.namespace.package.name, "P")

        self.assertEqual(self.processor.packages['P'].interfaces["I"].namespace_references[0],
                         self.processor.packages['P'].typecollections["Type1"])
        self.assertEqual(self.processor.packages['P'].interfaces["I"].namespace_references[1],
                         self.processor.packages['P'].typecollections["Type2"])

        self.assertEqual(
            self.processor.packages['P'].interfaces["I"].namespace_references[0].namespace_references[0].name, "Common")
        self.assertEqual(
            self.processor.packages['P'].interfaces["I"].namespace_references[1].namespace_references[0].name, "Common")

        # check that interface "I" has no reference to namespace "Common" --> no transitive imports
        self.assertEqual(len(self.processor.packages['P'].interfaces["I"].namespace_references), 2)

    def test_invalid_type_use(self):
        # P.fidl references definitions.fidl but it is not in the package path.
        with self.assertRaises(ProcessorException) as context:
            self.processor.import_file(
                os.path.join(self.get_spec("idl3"), "P1.fidl"))
            self.processor.import_file(
                os.path.join(self.get_spec("idl3"), "P2.fidl"))
        self.assertEqual(str(context.exception),
                         "Unresolved reference 'T1Enum'.")

    # ths test should raise an exception because MyEnum is ambiguous in P.fidl
    def test_ambiguous_types(self):
        with self.assertRaises(ProcessorException) as context:
            self.tmp_fidl("common.fidl", """
                        package P
                        typeCollection T1 {
                            enumeration MyEnum {
                                abc
                            }
                        }

                        typeCollection T2 {
                            enumeration MyEnum {
                                abc
                            }
                        }
                    """)

            fspec = self.tmp_fidl("P.fidl", """
                        package P
                        import model "common.fidl"

                        interface I {
                            version { major 1 minor 0 }
                            method getData {
                                out {
                                      MyEnum outVal
                                   }
                            }
                        }
                    """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Reference 'MyEnum' is ambiguous.")

    def test_model_import(self):
        self.tmp_fidl("common.fidl", """
                    package P
                    typeCollection T1 {
                        enumeration Enum_T1 {
                            abc
                        }
                    }

                    typeCollection T2 {
                        enumeration Enum_T2 {
                            abc
                        }
                    }
                """)

        fspec = self.tmp_fidl("P.fidl", """
                    package P
                    import model "common.fidl"

                    interface I {
                        version { major 1 minor 0 }
                        method getData {
                            out {
                                  Enum_T1 out_t1
                                  Enum_T2 out_t2
                            }
                        }
                    }
                """)
        self.processor.import_file(fspec)
        self.assertEqual(self.processor.packages["P"].name, "P")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["out_t1"].type.reference.namespace.name, "T1")
        self.assertEqual(self.processor.packages['P'].interfaces["I"].methods["getData"].
                         out_args["out_t2"].type.reference.namespace.name, "T2")

    def test_type_notations(self):
        self.tmp_fidl("test.fidl", """
                package P
                typeCollection TC {
                    typedef A is Int32
                }
            """)
        fspec = self.tmp_fidl("test2.fidl", """
                package P2
                import P.TC.* from "test.fidl"
                typeCollection TC2 {
                    typedef A2 is UInt32
                }
                interface I {
                    typedef B is P2.TC2.A2
                    typedef B2 is P.TC.A

                    typedef C is TC2.A2
                    typedef C2 is TC.A

                    typedef D is A2
                    typedef D2 is A
                }
            """)
        self.processor.import_file(fspec)

        a = self.processor.packages["P"].typecollections["TC"].typedefs["A"]
        self.assertTrue(isinstance(a.type, ast.Int32))
        a2 = self.processor.packages["P2"].typecollections["TC2"].typedefs["A2"]
        self.assertTrue(isinstance(a2.type, ast.UInt32))
        b = self.processor.packages["P2"].interfaces["I"].typedefs["B"]
        self.assertTrue(isinstance(b.type, ast.Reference))
        self.assertEqual(b.type.name, "A2")
        self.assertEqual(b.type.reference, a2)
        b2 = self.processor.packages["P2"].interfaces["I"].typedefs["B2"]
        self.assertTrue(isinstance(b2.type, ast.Reference))
        self.assertEqual(b2.type.name, "A")
        self.assertEqual(b2.type.reference, a)

        c = self.processor.packages["P2"].interfaces["I"].typedefs["C"]
        self.assertTrue(isinstance(c.type, ast.Reference))
        self.assertEqual(c.type.name, "A2")
        self.assertEqual(c.type.reference, a2)
        self.assertEqual(c.type.reference.namespace, self.processor.packages["P2"].typecollections["TC2"])

        c2 = self.processor.packages["P2"].interfaces["I"].typedefs["C2"]
        self.assertTrue(isinstance(c2.type, ast.Reference))
        self.assertEqual(c2.type.name, "A")
        self.assertEqual(c2.type.reference, a)

        d = self.processor.packages["P2"].interfaces["I"].typedefs["D"]
        self.assertTrue(isinstance(d.type, ast.Reference))
        self.assertEqual(d.type.name, "A2")
        self.assertEqual(d.type.reference, a2)
        d2 = self.processor.packages["P2"].interfaces["I"].typedefs["D2"]
        self.assertTrue(isinstance(d2.type, ast.Reference))
        self.assertEqual(d2.type.name, "A")
        self.assertEqual(d2.type.reference, a)


class TestExpressions(BaseTestCase):
    """Test type references."""

    def test_print_expressions(self):
        fspec = self.tmp_fidl("test.fidl", """
            package P
            typeCollection TC {
                const UInt32 a = 4
                const UInt32 b = 5
                const UInt32 u3 = (( 3+ 4*5 ) / 3 * (5+-3))
                const Boolean u4 = a+3*b-3 > 23
                
                struct Struct1 
                {
                    Boolean e1
                    UInt16 e2
                    String e3
                }
                const Struct1 s1 = { e1: 24>42, e2: 1+2*3, e3: "foo" }
                
                union Union1 
                {
                    UInt16 e1
                    Boolean e2
                    String e3
                }
                const Union1 uni1 = { e1: 1 }
                const Union1 uni2 = { e3: "foo" }
                
               array Array1 of UInt16
               const Array1 empty = []
               const Array1 one = [ 123 ] 
               const Array1 full = [ 1, 2, 2+3, 100*100+100 ] 
               
               map Map1 { UInt16 to String }
               const Map1 m1 = [ 1 => "one", 2 => "two" ]
            }
        """)
        self.processor.import_file(fspec)
        result_u3 = self.processor.print_constant(self.processor.packages["P"].typecollections["TC"].constants["u3"])
        result_u4 = self.processor.print_constant(self.processor.packages["P"].typecollections["TC"].constants["u4"])
        result_uni1 = self.processor.print_constant(
            self.processor.packages["P"].typecollections["TC"].constants["uni1"])
        result_uni2 = self.processor.print_constant(
            self.processor.packages["P"].typecollections["TC"].constants["uni2"])
        result_s1 = self.processor.print_constant(self.processor.packages["P"].typecollections["TC"].constants["s1"])
        result_empty = self.processor.print_constant(
            self.processor.packages["P"].typecollections["TC"].constants["empty"])
        result_one = self.processor.print_constant(
            self.processor.packages["P"].typecollections["TC"].constants["one"])
        result_full = self.processor.print_constant(
            self.processor.packages["P"].typecollections["TC"].constants["full"])
        result_m1 = self.processor.print_constant(
            self.processor.packages["P"].typecollections["TC"].constants["m1"])
        self.assertEqual(result_u3, "u3 = ( ( 3 + 4 * 5 ) / 3 * ( 5 + -3 ) )")
        self.assertEqual(result_u4, 'u4 = a + 3 * b - 3 > 23')
        self.assertEqual(result_uni1, 'uni1 = { e1: 1 }')
        self.assertEqual(result_uni2, 'uni2 = { e3: foo }')
        self.assertEqual(result_s1, 's1 = { e1: 24 > 42, e2: 1 + 2 * 3, e3: foo }')
        self.assertEqual(result_empty, 'empty = [  ]')
        self.assertEqual(result_one, 'one = [ 123 ]')
        self.assertEqual(result_full, 'full = [ 1, 2, 2 + 3, 100 * 100 + 100 ]')
        self.assertEqual(result_m1, 'm1 = [ 1 => one, 2 => two ]')
        print("Stop here for debugging!")

    def test_resolving_value_refrences(self):
        self.tmp_fidl("test.fidl", """
                       package P
                       typeCollection TC {
                           const UInt32 a = 4
                           const UInt32 b = 5
                           const String s = "hello"
                       }
                   """)

        fspec = self.tmp_fidl("test1.fidl", """
                   package P2
    
                   import P.TC.* from "test.fidl"
    
                   typeCollection TC2 {
                          const UInt32 c = a + b
    
                          struct Struct1 
                                {
                                    Boolean e1
                                    UInt16 e2
                                    String e3
                                }
                          array Array1 of Struct1
                          const Array1 a1 =  [ { e1: true, e2: a, e3: "foo" }, 
                                                     { e1: false, e2:b, e3: "bar" }]
    
                          map Map1 { UInt16 to String }
                          const Map1 m1 = [ a => "one", 2 => s ]
                          
                          const Boolean b1 = a + b < 5
                   }
               """)

        self.processor.import_file(fspec)

        ref_a = self.processor.packages["P"].typecollections["TC"].constants["a"]
        ref_b = self.processor.packages["P"].typecollections["TC"].constants["b"]
        ref_s = self.processor.packages["P"].typecollections["TC"].constants["s"]

        constant = self.processor.packages["P2"].typecollections["TC2"].constants["c"]
        self.assertTrue(isinstance(constant.expression, ast.Term))
        self.assertTrue(isinstance(constant.expression.operand1, ast.ValueReference))
        self.assertEqual(constant.expression.operand1.reference, ref_a)
        self.assertEqual(constant.expression.operand1.value, 4)
        self.assertEqual(constant.expression.operand1.name, "UInt32")
        self.assertTrue(isinstance(constant.expression.operand2, ast.ValueReference))
        self.assertEqual(constant.expression.operand2.reference, ref_b)
        self.assertEqual(constant.expression.operand2.value, 5)
        self.assertEqual(constant.expression.operand2.name, "UInt32")
        self.assertEqual(constant.value, 9)
        self.assertEqual(constant.type.name, "UInt32")

        constant = self.processor.packages["P2"].typecollections["TC2"].constants["a1"]
        self.assertTrue(isinstance(constant.expression, ast.InitializerExpressionArray))
        self.assertTrue(isinstance(constant.expression.elements[0], ast.InitializerExpressionStruct))
        self.assertTrue(isinstance(constant.expression.elements[0].elements["e2"], ast.ValueReference))
        self.assertEqual(constant.expression.elements[0].elements["e2"].reference, ref_a)
        self.assertEqual(constant.expression.elements[0].elements["e2"].name, ref_a.type.name)
        self.assertEqual(constant.expression.elements[0].elements["e2"].value, ref_a.value)
        self.assertEqual(constant.expression.elements[0].elements["e2"].comments, ref_a.comments)

        self.assertTrue(isinstance(constant.expression.elements[1], ast.InitializerExpressionStruct))
        self.assertTrue(isinstance(constant.expression.elements[1].elements["e2"], ast.ValueReference))
        self.assertEqual(constant.expression.elements[1].elements["e2"].reference, ref_b)
        self.assertEqual(constant.expression.elements[1].elements["e2"].reference, ref_b)
        self.assertEqual(constant.expression.elements[1].elements["e2"].name, ref_b.type.name)
        self.assertEqual(constant.expression.elements[1].elements["e2"].value, ref_b.value)
        self.assertEqual(constant.expression.elements[1].elements["e2"].comments, ref_b.comments)

        constant = self.processor.packages["P2"].typecollections["TC2"].constants["m1"]
        self.assertTrue(isinstance(constant.expression, ast.InitializerExpressionMap))
        self.assertTrue(isinstance(constant.expression.elements[0][0], ast.ValueReference))
        self.assertEqual(constant.expression.elements[0][0].reference, ref_a)
        self.assertEqual(constant.expression.elements[0][0].value, 4)
        self.assertEqual(constant.expression.elements[0][0].name, "UInt32")
        self.assertTrue(isinstance(constant.expression.elements[1][1], ast.ValueReference))
        self.assertEqual(constant.expression.elements[1][1].reference, ref_s)
        self.assertEqual(constant.expression.elements[1][1].value, "hello")
        self.assertEqual(constant.expression.elements[1][1].name, "String")
        self.assertEqual(constant.value, None)

        constant = self.processor.packages["P2"].typecollections["TC2"].constants["b1"]
        self.assertEqual(constant.value, False)
        self.assertEqual(constant.type.name, "Boolean")



        #bad cases
        # const Uin8 a = 257
        # const Uint16 b = 70000
        # const Int16 c = -70000
        # const Boolean b1 = 4
        # const String s1 = 4
        # const String s2 ? "Hello" + " " + "Welt!"