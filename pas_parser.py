# -*- encoding: utf-8 -*-
"""
Delphi pascal files parsers
"""

from text_parsers import lines_iterator, LineParser, LineToStringParser 
from pascal import PascalClass, PascalInterface

        

class DocumentationParser(LineToStringParser):
    """Parsing of pascal documentation lines, that starts with ///"""

    def __init__(self):
        LineToStringParser.__init__(self, r"(.*\/\/\/.*)")


class ImplementationDetector(LineToStringParser):
    """Detect implementation line"""

    def __init__(self):
        LineToStringParser.__init__(self, r"(.*implementation.*)")

    def detect(self, line, callback=None):
        parse_res = self.parse(line)        
        res = True if parse_res else False
        self._call_callback(callback, res)
        return res


class ClassNamespaceParser(LineToStringParser):
    """Parsing parent class name from class definition line"""

    def __init__(self):
        LineToStringParser.__init__(self, r"(\w+) *= *class")


class ClassParentClassParser(LineToStringParser):
    """Parsing parent class from class definition line"""

    def __init__(self):
        LineToStringParser.__init__(self, r"= *class *\( *(\w+)")

class ClassInterfacesParser(LineToStringParser):
    """Parsing implemented class interfaces from pascal class definition line"""
    def __init__(self):
        LineToStringParser.__init__(self, r"= *class *\([^,]+, *([^)]+) *\)")

    def parse(self, line, callback=None):
        res = super(ClassInterfacesParser, self).parse(line)
        res2 = None
        if res:
            res2 = [interface.strip() for interface in res.split(',')]
            self._call_callback(callback, res2)
        return res2


class ClassParser(LineToStringParser):
    """Parsing of pascal class definition line """

    def __init__(self):
        LineToStringParser.__init__(self, r"([^=]+= *class.*)")
        self._name_parser = ClassNamespaceParser()
        self._parent_parser = ClassParentClassParser()
        self._interface_parser = ClassInterfacesParser()

    def parse(self, line, callback=None):
        """Parses class definition line
        :returns PascalClass object or None if there is no class definition
        
        """
        res = super(ClassParser, self).parse(line)
        res2 = None
        if res:            
            res2 = PascalClass(
                        self._name_parser.parse(line),
                        self._parent_parser.parse(line),
                        interfaces = self._interface_parser.parse(line)
                    )
        self._call_callback(callback, res2)
        return res2

class InterfaceParentParser(LineToStringParser):

    """Parsing interface ancestor interface"""

    def __init__(self):
        LineToStringParser.__init__(self, r"= *interface *\( *(\w+) *\)")

        

class InterfaceParser(LineParser):

    """Parsing pascal interface declaration line"""
    def __init__(self):
        """TODO: to be defined1. """
        LineParser.__init__(self,r"(\w+) *= *interface *(.*)")
        self._interface_detail_parser = InterfaceParentParser()

    def parse(self, line, callback=None):
        """Parses inteface declaration line

        :line: line to parse
        :callback: callback function to call with parameters
        :returns: PascalInterface or None if there is no interface definition

        """
        res = super(InterfaceParser, self).parse(line)
        interface = None
        if res:
            ancestor = self._interface_detail_parser.parse(res[0][1])
            interface = PascalInterface(
                    res[0][0], 
                    ancestor
                )
        self._call_callback(callback, interface)
        return interface
        

class PascalParser(object):

    """Pascal files class parser
    - retrieving class definitions
    - retrieving class inheritance info
    - retrieving class interface    
    - parsing ends on impementation keyword
    - creating trees of inheritance
    """

    def __init__(self):
        """Pas parser initializator
        """
        self._classes = []
        self._class_dict = {}
        self._roots = {}
        self._class_parser = ClassParser()
        self._doc_parser = DocumentationParser()
        self._implementation_detector = ImplementationDetector()
        self._interface_parser = InterfaceParser()

    def _collect_roots(self):
        """Constructs self._roots list"""
        self._roots = {}
        self._class_dict = {}
        self._class_dict = dict([(c.namespace, c) for c in self._classes])
        for c in self._classes[:]:
            if c.parent_name:
                if not c.parent_name in self._class_dict:
                    c.parent = PascalClass(c.parent_name, "")
                    self._class_dict[c.parent_name] = c.parent
                    self._classes.append(c.parent)                    
                else:
                    c.parent = self._class_dict[c.parent_name]
                c.parent.add_children(c)
        self._roots = dict([(c.namespace, c) for c in self._classes if not c.parent ])       
        

    def parse(self, filename, content):
        """Parsing the pascal lines

        :filename: pascal file of content
        :content: content of pascal file
        :returns: list of root classes

        """

        def append_if_not_none(variable, content):
            return variable +"\n"+ content if content else "" 
        docs = ''
        for i,line in lines_iterator(content):
            if self._implementation_detector.detect(line):
                break
            pascal_object = self._class_parser.parse(line) or self._interface_parser.parse(line)
            if pascal_object:
                pascal_object.documentation = docs
                pascal_object.filename = filename
                pascal_object.line_number = i
                self._classes.append(pascal_object)
            docs = append_if_not_none(docs, self._doc_parser.parse(line))

        self._collect_roots()
        return self._roots

    @property 
    def roots(self):
        """Get dictionary of root classes - classes that has no parent class,
        or parent classes are not defined in file scopes"""
        return self._roots

    @property
    def classes(self):
        """List of defined classes"""
        return self._classes
        
    @property
    def classes_dict(self):
        """Dictionary of defined class"""
        return self._class_dict


if __name__ == "__main__":
    from sys import argv
    if len(argv) > 1:
        parser = PascalParser()
        for iarg in range(1, len(argv)):
            #try:
            filename = argv[iarg]
            with file(filename, 'r') as f:
                content = f.read()
            parser.parse(filename, content)
            #except Exception as e:
            #    print "Excepttion: %s" % e
        defs = [parser.classes_dict[c].to_json() for c in parser.classes_dict]
        #print "[\n" + ",\t\n".join(defs) + "\n]"
        print "\n".join([str(parser.classes_dict[c].interfaces) for c in parser.classes_dict if hasattr(parser.classes_dict[c],'interfaces')])
