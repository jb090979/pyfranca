"""
Pyfranca parser tests.
"""

import unittest
import os
import errno
import shutil

from pyfranca import LexerException, ParserException, Parser, ast, ProcessorException, Processor
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


class TestMisc(BaseTestCase):
    """Test parsing various FIDL examples."""

    @unittest.skip("Currently not checked.")
    def test_all_supported(self):
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
        print("Stop here for debugging!")

    @unittest.skip("Currently not checked.")
    def test_print_expressions(self):
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
                      const Double c = 1e-40
                      
                     
               }
           """)

    def test_bad_array_range(self):
        with self.assertRaises(ProcessorException) as context:
            fspec = self.tmp_fidl("tmp.fidl", """
                           package P
                           typeCollection T1 {
                              array Array1 of UInt8
                              const Array1 full = [ 1, 2, 2+3, 100*100+100 ] 
                           }
                       """)
            self.processor.import_file(fspec)

        self.assertEqual(str(context.exception),
                         "Value of type 'String' cannot  assigned to a value of type Boolean.")
        self.processor.import_file(fspec)
        print("Stop here for debugging!")
