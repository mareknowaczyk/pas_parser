# -*- encoding: utf-8 -*-
"""
    This module contains classes that helps in collecting
informations about definitions/ variables/ classes/ interfaces
gathered in pascal files (Delphi).
"""

from json import JSONEncoder


def get_function_arg(kwargs, key, default_value ):
    """Shortcut for retrieving dictionary (:kwargs:) value if dictionary key :key: exists,
    or :default_value: otherwise."""
    return kwargs[key] if key in kwargs else default_value


def set_default_values(obj, args, kwargs):
    """Add all arguments from :args: into :obj: as a fields ,
    with names stored in :args: with '_' prefix, and 
    with values stored in :kwargs: or None if they are not 
    exists in :kwargs:.

    I.e
        obj = MyClass()
        set_default_values(
            obj, 
            ['name', 'comment'], 
            {'name': 'name_of_my_object'})
        ...
        The code above add two new fields to 'obj'
        - '_name', with value 'name_of_my_object', and
        - '_comment', with 'None' value.
    """    
    for arg in args:
        setattr(obj, '_%s' % arg, get_function_arg(kwargs, arg, None), )


class PascalDefinition(object):
    """Pascal definition object - base class for all pascal classes"""
    
    def __init__(self, namespace, fields=[],  **kwargs):
        """
        :namespace: pascal namespace
        :**kwargs: additional info
           'documentation':     documentation for class
           'filename':          pascal file that contains class
           'line_number':       line number in filename, where class is defined
        """r"(\w+) *= *interface *(.*)"
        self._args = fields + [            
                'documentation',
                'filename',
                'line_number',
                'namespace',
                'kind',
            ]
        set_default_values(self, self._args, kwargs)
        self._namespace = namespace
        self._kind = "pascal_definition"

    @property 
    def kind(self):
        return self._kind

    def set_namespace(self, value):
        self._namespace = value

    def get_namespace(self):
        return self._namespace

    def set_filename(self, value):
        self._filename = value
    
    def get_filename(self):
        return self._filename

    def set_line_number(self, value):
        self._line_number = value

    def get_line_number(self):
        return self._line_number

    def set_documentation(self, value):
        self._documentation = value

    def get_documentation(self):
        return self._documentation

    namespace = property(get_namespace, set_namespace)
    filename = property(get_filename, set_filename)
    line_number = property(get_line_number, set_line_number)
    documentation = property(get_documentation, set_documentation)

    def __repr__(self):
        return "%s" % (self._namespace)

    def to_dict(self):
        return dict([(f, str(getattr(self, "_%s" % f))) for f in self._args])


    def to_json(self):
        #return "{\n\t"+",\n\t".join(["""\"%s" : "%s\"""" % (f, getattr(self, "_%s" % f)) for f in self._args])+"\n}"
        return JSONEncoder().encode(self.to_dict())


class PascalParentedDefinition(PascalDefinition):
    """Pascal parented definition object - based class for all 
    pascal classes that implements inheritation"""

    def __init__(self, namespace, parent_namespace, fields=[], **kwargs):
        """
            :namespace:         pascal namespace
            :parent_namespace:  namespace for parent
        """
        super(PascalParentedDefinition, self).__init__(namespace, ['parent_namespace', 'parent','childrens']+ fields, **kwargs)
        self._kind = 'parented_definition'
        self._parent_namespace = parent_namespace
        if not self._childrens:
            self._childrens = []

    def set_parent_name(self, value):
        self._parent_namespace = value

    def get_parent_name(self):
        return self._parent_namespace

    def set_parent(self, value):
        self._parent = value

    def get_parent(self):
        return self._parent

    def add_children(self, child):
        if not child in self._childrens:
            self._childrens.append(child)
    
    @property
    def childrens(self):
        return self._childrens

    parent_name = property(get_parent_name, set_parent_name)

    parent = property(get_parent, set_parent)

class PascalClass(PascalParentedDefinition):

    """Pascal class object - gathered information about:
    - class name
    - class inheritance
    - class interfaces
    """
    
    def __init__(self, class_name, class_parent, **kwargs):
        """
        :class_name: pascal class namespace
        :class_parent: pascal class namespace for parent
        :**kwargs: additional info
           'interfaces':        list of interfaces
           'documentation':     documentation for class
           'filename':          pascal file that contains class
           'line_number':       line number in filename, where class is defined
        """
        super(PascalClass, self).__init__(class_name, class_parent, ['interfaces'], **kwargs)
        self._kind = 'class'

    def set_interfaces(self, value):
        self._interfaces = value

    def get_interfaces(self):
        return self._interfaces

    interfaces = property(get_interfaces, set_interfaces)

class PascalInterface(PascalParentedDefinition):

    """Pascal interface deinition - with additional informations """

    def __init__(self, interface_name, interface_parent, **kwargs):
        super(PascalInterface, self).__init__(interface_name, interface_parent, ['guid'], **kwargs)
        self._kind = 'interface'

    def get_guid(self):
        return self._guid

    def set_guid(self, value):
        self._guid = value

    guid = property(get_guid, set_guid)

        

def get_pascal_class_info(pascal_class):
    """Get PascalClass object details:

    :pascal_class: PascalClass object
    :return: string with PascalClass object detailed information 

    """
    return """%s
        - parent: %s
        - interfaces: %s
        - docs: %s
        - filename: %s
        - line no: %s
        """ % (
                pascal_class._namespace,
                pascal_class._parent_namespace,
                ",".join(pascal_class.interfaces) if pascal_class.interfaces else "",
                pascal_class.documentation,
                pascal_class.filename,
                pascal_class.line_number
            )
   
     


