
import os
from collections import OrderedDict
from pyfranca import franca_parser, ast


class ProcessorException(Exception):

    def __init__(self, message):
        super(ProcessorException, self).__init__()
        self.message = message

    def __str__(self):
        return self.message


class Processor(object):
    """
    Franca IDL processor.
    """

    def __init__(self):
        """
        Constructor.
        """
        # Default package paths.
        self.package_paths = []
        # Maps absolute file specifications to package AST objects.
        self.files = {}
        # Maps package names to package AST objects.
        self.packages = {}
        # List of imported string file specifications
        self._string_files = []

    @staticmethod
    def basename(namespace):
        """
        Extract the type or namespace name from a Franca FQN.
        """
        dot = namespace.rfind(".")
        if dot == -1:
            return namespace
        else:
            return namespace[dot + 1:]

    @staticmethod
    def packagename(namespace):
        """
        Extract the package name from a Franca FQN.
        """
        dot = namespace.rfind(".")
        if dot == -1:
            return None
        else:
            return namespace[0:dot]

    @staticmethod
    def is_fqn(string):
        """
        Defines whether a Franca name is an ID or an FQN.
        """
        return string.count(".") >= 2

    @staticmethod
    def split_fqn(fqn):
        """
        Split a Franca FQN into a tuple - package, namespace, and name.
        """
        parts = fqn.rsplit(".", 2)
        while len(parts) < 3:
            parts.insert(0, None)
        return tuple(parts)

    @staticmethod
    def resolve(namespace, fqn):
        """
        Resolve type references.

        :param namespace: context ast.Namespace object.
        :param fqn: FQN or ID string.
        :return: Dereferenced ast.Type object.
        """
        if not isinstance(namespace, ast.Namespace) or \
                not isinstance(fqn, str):
            raise ValueError("Unexpected input.")
        pkg, ns, name = Processor.split_fqn(fqn)

        resolved_namespace = None
        count = 0 # number of matches, 0 not found, 1 ok, >1 ambiguous
        package_fqn = ""

        if pkg is not None:
            package_fqn += namespace.package.name + "."

        if ns is not None:
            package_fqn += namespace.name + "."

        package_fqn += name

        if package_fqn == fqn:
            # fqn is with within this namespace
            if name in namespace:
                resolved_namespace = namespace[name]
                count += 1

        # lock into visible namespaces
        for ns_ref in namespace.namespace_references:
            if pkg is not None:
                if pkg != ns_ref.package.name:
                    continue
            if ns is not None:
                if ns != ns_ref.name:
                    continue

            if name in ns_ref:
                count += 1
                resolved_namespace = ns_ref[name]

        if count > 1:
            raise ProcessorException(
                "Reference '{}' is ambiguous.".format(fqn))

        if resolved_namespace:
            return resolved_namespace

        # Give up
        raise ProcessorException(
            "Unresolved reference '{}'.".format(fqn))

    @staticmethod
    def resolve_namespace(package, fqn):
        """
        Resolve namespace references.

        :param package: context ast.Package object.
        :param fqn: FQN or ID string.
        :return: Dereferenced ast.Namespace object.
        """
        if not isinstance(package, ast.Package) or not isinstance(fqn, str):
            raise ValueError("Unexpected input.")
        if fqn.count(".") > 0:
            pkg, name = fqn.rsplit(".", 2)
        else:
            pkg, name = (None, fqn)
        if pkg is None:
            # This is an ID
            # Look for other namespaces in the package
            if name in package:
                return package[name]
            # Look in model imports
            for package_import in package.imports:
                if not package_import.namespace:
                    if name in package_import.package_reference:
                        return package_import.package_reference[name]
        else:
            # This is an FQN
            if pkg == package.name:
                # Check in the current package
                if name in package:
                    return package[name]
            else:
                # Look in model imports
                for package_import in package.imports:
                    if not package_import.namespace:
                        if name in package_import.package_reference:
                            return package_import.package_reference[name]
        # Give up
        raise ProcessorException(
            "Unresolved namespace reference '{}'.".format(fqn))

    def _update_complextype_references(self, name):
        """
        Update type references in a complex type.

        :param name: ast.ComplexType object.
        """
        if isinstance(name, ast.Enumeration):
            if name.extends:
                name.reference = self.resolve(name.namespace, name.extends)
                if not isinstance(name.reference, ast.Enumeration):
                    raise ProcessorException(
                        "Invalid enumeration reference '{}'.".format(
                            name.extends))
        elif isinstance(name, ast.Struct):
            for field in name.fields.values():
                self._update_type_references(name.namespace, field.type)
            if name.extends:
                name.reference = self.resolve(name.namespace, name.extends)
                if not isinstance(name.reference, ast.Struct):
                    raise ProcessorException(
                        "Invalid struct reference '{}'.".format(
                            name.extends))
        elif isinstance(name, ast.Union):
            for field in name.fields.values():
                self._update_type_references(name.namespace, field.type)
            if name.extends:
                name.reference = self.resolve(name.namespace, name.extends)
                if not isinstance(name.reference, ast.Union):
                    raise ProcessorException(
                        "Invalid union reference '{}'.".format(
                            name.extends))
        elif isinstance(name, ast.Array):
            self._update_type_references(name.namespace, name.type)
        elif isinstance(name, ast.Map):
            self._update_type_references(name.namespace, name.key_type)
            self._update_type_references(name.namespace, name.value_type)
        elif isinstance(name, ast.Constant):
            self._update_type_references(name.namespace, name.type)
        else:
            assert False

    def _update_type_references(self, namespace, name):
        """
        Update type references in a type.

        :param namespace: ast.Namespace context.
        :param name: ast.Type object.
        """
        if isinstance(name, ast.Typedef):
            self._update_type_references(name.namespace, name.type)
        elif isinstance(name, ast.PrimitiveType):
            pass
        elif isinstance(name, ast.ComplexType):
            self._update_complextype_references(name)
        elif isinstance(name, ast.Reference):
            if not name.reference:
                resolved_name = self.resolve(namespace, name.name)
                name.reference = resolved_name
                name.namespace = resolved_name.namespace

                # remove package and namespace from fqn.
                # it is not necessary anymore -> information is preserved in the reference
                pkg, ns, type_name = Processor.split_fqn(name.name)
                name.name = type_name
        elif isinstance(name, ast.Attribute):
            self._update_type_references(name.namespace, name.type)
        elif isinstance(name, ast.Method):
            for arg in name.in_args.values():
                self._update_type_references(name.namespace, arg.type)
            for arg in name.out_args.values():
                self._update_type_references(name.namespace, arg.type)
            if isinstance(name.errors, OrderedDict):
                pass
            elif isinstance(name.errors, ast.Reference):
                # Errors can be a reference to an enumeration
                self._update_type_references(name.namespace, name.errors)
                if not isinstance(name.errors.reference, ast.Enumeration):
                    raise ProcessorException(
                        "Invalid error reference '{}'.".format(
                            name.errors.name))
            else:
                assert False
        elif isinstance(name, ast.Broadcast):
            for arg in name.out_args.values():
                self._update_type_references(name.namespace, arg.type)
        else:
            assert False

    def _update_namespace_references(self, namespace):
        """
        Update type references in a namespace.

        :param namespace: ast.Namespace object.
        """
        for name in namespace.typedefs.values():
            self._update_type_references(namespace, name)
        for name in namespace.enumerations.values():
            self._update_type_references(namespace, name)
        for name in namespace.structs.values():
            self._update_type_references(namespace, name)
        for name in namespace.unions.values():
            self._update_type_references(namespace, name)
        for name in namespace.arrays.values():
            self._update_type_references(namespace, name)
        for name in namespace.maps.values():
            self._update_type_references(namespace, name)
        for name in namespace.constants.values():
            self._update_type_references(namespace, name)

    def _update_interface_references(self, namespace):
        """
        Update type references in an interface.

        :param namespace: ast.Interface object.
        """
        self._update_namespace_references(namespace)
        for name in namespace.attributes.values():
            self._update_type_references(namespace, name)
        for name in namespace.methods.values():
            self._update_type_references(namespace, name)
        for name in namespace.broadcasts.values():
            self._update_type_references(namespace, name)
        if namespace.extends:
            namespace.reference = self.resolve_namespace(
                namespace.package, namespace.extends)
            if not isinstance(namespace.reference, ast.Interface):
                raise ProcessorException(
                    "Invalid interface reference '{}'.".format(
                        namespace.extends))

    def _update_imported_namespaces_references(self, package, imported_namespace):
        for package_namespace in package.typecollections.values():
            package_namespace.namespace_references.append(imported_namespace)

        for package_namespace in package.interfaces.values():
            package_namespace.namespace_references.append(imported_namespace)

    def _update_namespaces_references(self, package):
        # add all other namespaces in this package as reference to a namespace
        for ns1 in package.typecollections.values():
            for ns2 in package.typecollections.values():
                if ns1 != ns2:
                    ns1.namespace_references.append(ns2)
                for ns3 in package.interfaces.values():
                    ns1.namespace_references.append(ns3)

        for ns1 in package.interfaces.values():
            for ns2 in package.interfaces.values():
                if ns1 != ns2:
                    ns1.namespace_references.append(ns2)
            for ns3 in package.typecollections.values():
                ns1.namespace_references.append(ns3)


    def _update_package_references(self, package, imported_package, package_import):
        """
        Update type references in a package.

        :param package: ast.Package object.
        """

        # Update import reference  but not for itself
        package_import.package_reference = imported_package

        do_import = False
        if package_import.namespace:
            # import only the specified namespace
            if not package_import.namespace.endswith(".*"):
                raise ProcessorException(
                    "Invalid namespace import {}.".format(
                        package_import.namespace))

            fqn = package_import.namespace[:-2]
            ns = self.basename(fqn)
            p = self.packagename(fqn)
            found = False
            for imported_namespace in imported_package.typecollections.values():
                do_update = False
                if (imported_namespace.name == ns) and (imported_namespace.package.name == p):
                    do_update = True
                elif fqn == imported_namespace.package.name:
                    do_update = True

                if do_update:
                    found = True
                    package_import.namespace_reference = imported_namespace

                    # reference namespace from imported package to all namespaces in this package
                    self._update_imported_namespaces_references(package, imported_namespace)

            for imported_namespace in imported_package.interfaces.values():
                do_update = False
                if (imported_namespace.name == ns) and (imported_namespace.package.name == p):
                    do_update = True
                elif fqn == imported_namespace.package.name:
                    do_update = True

                if do_update:
                    found = True
                    package_import.namespace_reference = imported_namespace

                    # reference namespace from imported package to all namespaces in this package
                    self._update_imported_namespaces_references(package, imported_namespace)

            if not found:
                raise ProcessorException(
                    "Namespace '{}' not found.".format(
                        package_import.namespace))
        else:
            # model import -> import all namespaces
            for imported_namespace in imported_package.typecollections.values():
                self._update_imported_namespaces_references(package, imported_namespace)
            for imported_namespace in imported_package.interfaces.values():
                self._update_imported_namespaces_references(package, imported_namespace)

    def import_package(self, fspec, package, references=None):
        """
        Import an ast.Package into the processor.

        If the package has already been imported it will be silently ignored.

        :param fspec: File specification of the package.
        :param package: ast.Package object.
        :param references: A list of package references.
        """
        # Check whether package is already imported
        abs_fspec = os.path.abspath(fspec)

        if not isinstance(package, ast.Package):
            ValueError("Expected ast.Package as input.")
        if not references:
            references = []
        elif abs_fspec in references:
            # todo maybe raise an exception, interrupt circular dependency
            return

        # Process package imports before merging the packages. Otherwise the package import are processed multiple times
        # it is important here to use abs_fspec as reference, not the pacakge
        # in order to determine which fspec is already processed.
        fspec_dir = os.path.dirname(abs_fspec)
        for package_import in package.imports:
            imported_package = self.import_file(
                package_import.file, references + [abs_fspec], fspec_dir)
            self._update_package_references(package, imported_package, package_import)

        self._update_namespaces_references(package)

        for namespace in package.typecollections:
            self._update_namespace_references(
                package.typecollections[namespace])
        for namespace in package.interfaces:
            self._update_interface_references(
                package.interfaces[namespace])

        if package.name in self.packages:
            if abs_fspec not in self.packages[package.name].files:
                # Merge the new package into the already existing one.
                self.packages[package.name] += package
                # Register the package file in the processor.
                self.files[abs_fspec] = self.packages[package.name]
                package = self.packages[package.name]
            else:
                return
        else:
            # Register the package in the processor.
            self.packages[package.name] = package
            # Register the package file in the processor.
            self.files[abs_fspec] = package


    def _exists(self, fspec):
        """
        Tests whether a file specification exists.
            The list of imported string files is checked first, followed by the real file-system.

        :param fspec: File specification.
        :return: Boolean.
        """
        if fspec in self._string_files:
            exists = True
        else:
            exists = os.path.exists(fspec)
        return exists

    def import_file(self, fspec, references=None, package_path=None):
        """
        Parse an FIDL file and import it into the processor as package.

        If a file has already been imported, the corresponding package will be returned.

        :param fspec: File specification.
        :param references: A list of package references.
        :param package_path: Additional model path to search for imports.
        :return: The parsed ast.Package.
        """
        abs_fspec = os.path.abspath(fspec)
        if not self._exists(abs_fspec):
            if os.path.isabs(fspec):
                # Absolute specification
                raise ProcessorException(
                    "Model '{}' not found.".format(fspec))
            else:
                # Relative specification.
                package_paths = list(self.package_paths)
                if package_path:
                    package_paths.insert(0, package_path)
                # Check in the package path list.
                for path in package_paths:
                    temp_fspec = os.path.abspath(os.path.join(path, fspec))
                    if self._exists(temp_fspec):
                        abs_fspec = temp_fspec
                        break
                else:
                    raise ProcessorException(
                        "Model '{}' not found.".format(fspec))

        if abs_fspec in self.files:
            # File already loaded.
            return self.files[abs_fspec]

        # Parse the file.
        parser = franca_parser.Parser()
        package = parser.parse_file(abs_fspec)
        # Import the package in the processor.
        self.import_package(abs_fspec, package, references)
        return package
