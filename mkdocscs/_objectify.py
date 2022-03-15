#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
   Created on 11-03-2022
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import glob
import itertools
import pathlib
from pickle import GLOBAL
from pprint import pprint
from pydoc import Doc
from re import I
from tkinter.font import names
from types import SimpleNamespace
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Dict, Tuple, Union

from .utils import Log

ID = "id"
NAME = "compoundname"
NAME2 = "name"
MEMEBER = "memberdef"
SECTION = "sectiondef"
NAMESPACE = "namespace"
FILE = "innerfile"
PROTECTION = "prot"
KIND = "kind"
CLASS = "class"
DOC_LONG = "detaileddescription"
DOC_SHORT = "briefdescription"
DIRECTORY = "dir"
FILE = "file"
DEFINITION = "definition"


def get_id(x):
    return Reference(x.attrib[ID], None)

def get_name(x):
    name = x.find(NAME)
    name = name if name is not None else x.find(NAME2)
    return name.text

def get_kind(x):
    return x.attrib[KIND]

def get_protection(x):
    return x.attrib[PROTECTION]

def get_documentation(x):
    return Documentation(parse_documentation(x.find(DOC_SHORT)), parse_documentation(x.find(DOC_LONG)))

def get_path(x):
    return x.find('location').attrib[FILE]

def get_inherit_from(x):
    return [Reference(y.attrib['refid'], None) for y in x.findall('basecompoundref')]

def get_inherit_by(x):
    return [Reference(y.attrib['refid'], None) for y in x.findall('derivedcompoundref')]

def get_template(x):
    ts = x.find('templateparamlist')
    ts = ts if ts is not None else []
    # TODO more complex template doc requires inspecting source xml file...
    ts = [t.find('type').text for t in ts]
    return ts

def get_type(x):
    return x.find('type').text

def get_arguments(x):
    return x.find('argsstring').text # TODO lazy...

def get_members(x):
    def _members():
        for section in x.findall(SECTION):
            for m in section.findall(MEMEBER):
                if get_protection(m) != 'private':
                    yield m
    return [m for m in _members()]

def get_definition(x):
    return x.find(DEFINITION).text

class DocumentationList:

    def __init__(self):
        self.doc = []

    def append(self, x):
        if x is not None and x != '':
            self.doc.append(x)
    
    def __iter__(self):
        return iter(self.doc)

    def __len__(self):
        return len(self.doc)

    def __repr__(self):
        return str(self) 

    def __str__(self):
        return str(self.doc) # TODO convert to markdown

class Reference:

    __reference__ = {}

    def __new__(cls, *args, **kwargs):
        id, obj = args
        if id not in Reference.__reference__:
            instance = super().__new__(cls)
            instance.id, instance.obj = id, obj
            Reference.__reference__[id] = instance
            #print("NEW REF", id, instance.id, instance.obj)
        else:
            instance = Reference.__reference__[id]
            #print("OLD REF", id, instance.id, instance.obj)
        return instance

    ## IMPORTANT that there is no __init__... otherwise things can break!

    def __str__(self):
        return f"<ref {self.id}>"

    def __repr__(self):
        return str(self)

@dataclass
class Documentation:

    long : List[Union[str, Reference]]
    short : List[Union[str, Reference]]

@dataclass
class Object:
    
    id : Reference

    def __post_init__(self):
        self.id.obj = self

@dataclass
class Member(Object):

    name: str
    kind: str
    protection: str
    modifier: List[str] # TODO
    docstring: Documentation

    def parse(x):
        kind = get_kind(x)
        if kind == 'variable':
            return Variable.parse(x)
        elif kind == 'function':
            return Function.parse(x)
        elif kind == 'property':
            return Variable.parse(x)
        else:
            raise NotImplementedError(f"TODO? {kind}")

@dataclass
class Variable(Member): 

    type : str

    def parse(x):
        (*modifiers, type) = get_type(x).split(" ") # hmm...
        return Variable(get_id(x), get_name(x), get_kind(x), get_protection(x), modifiers, 
                get_documentation(x), type)

    @property
    def definition(self):
        return ' '.join([self.protection, *self.modifier, self.name])

@dataclass
class Function(Member):
    
    args : List[Tuple[str, str]]

    def parse(x):
        modifiers = get_type(x).split(" ") # hmm... includes return type...
        return Function(get_id(x), get_name(x), get_kind(x), get_protection(x), modifiers, 
                get_documentation(x), get_arguments(x))

    @property
    def definition(self):
        definition = ' '.join([self.protection, *self.modifier, self.name])
        return f"{definition}{self.args}"

@dataclass
class Compound(Object): 
    
    _name: str
    kind: str
    protection: str
    docstring: Documentation
    path: str
    namespace: Reference
    inherit_from: List[Reference]
    inherit_by: List[Reference]
    template: List[str]
    members: List[Reference]

    @property
    def name(self):
        if len(self.template) > 0:
            return self._name + f"&lt;{','.join(self.template)}&gt;" # this might have to be refactored ...s
        return self._name

    def parse(x):
        members = [Member.parse(m) for m in get_members(x)]
        return Compound(get_id(x), get_name(x), get_kind(x), get_protection(x), get_documentation(x), 
                        get_path(x), GLOBAL_NAMESPACE.id, get_inherit_from(x), get_inherit_by(x), get_template(x),
                        members)

    def get_parents(self):
        return [self.namespace, *self.namespace.obj.get_parents()]

@dataclass
class Namespace(Object): 

    name: str
    docstring: Documentation
    parent: Reference
    namespaces: List[Reference]
    classes: List[Reference]

    def parse(x):
        assert x.attrib[KIND] == NAMESPACE
        classes = [Reference(str(c.attrib['refid']), None) for c in x.findall('innerclass')]
        namespaces = [Reference(str(c.attrib['refid']), None) for c in x.findall('innernamespace')]
        return Namespace(get_id(x), get_name(x), get_documentation(x), GLOBAL_NAMESPACE.id, namespaces, classes)

    def get_compounds(self):
        return self.classes

    def get_parents(self):
        def parents(x):
            while x.obj.parent is not None:
                x = x.obj.parent
                yield x
        return [x for x in parents(self.id)]

GLOBAL_NAMESPACE = Namespace(Reference('namespace__Global', None), "Global", Documentation(["Global namespace."],[]), None, [], [])

@dataclass 
class Directory(Object):

    path: str
    docstring: Documentation
    files: List[str]

    def parse(x):
        assert x.attrib['kind'] == DIRECTORY
        files = [str(f.text) for f in x.findall(FILE)]
        return Directory(get_id(x), get_path(x), get_documentation(x), files)

@dataclass
class File(Object):

    path: str
    
    def parse(x):
        return File(get_id(x), get_path(x)) 

class Index:

    def parse(x):
        results = dict()
        for key, group in itertools.groupby(x.findall('compound'), lambda y : y.attrib[KIND]):
            results[key] = [Reference(y.attrib['refid'], None) for y in group]
        return SimpleNamespace(**results)

def parse_compounddef(x):
    y = PARSERS[x.attrib['kind']](x)
    return y

def parse_documentation(x):
    def parse_ref(x, doc):
        doc.append(Reference(x.attrib['refid'], None))
        doc.append(x.tail)
    def parse_para(x, doc):
        doc.append(x.text)

    parsers = {'para':parse_para, 'ref':parse_ref}
    p = x.find('para')
    doc = DocumentationList()
    if p is not None:  
        for y in p.iter():
            parsers[y.tag](y, doc)
    #print(x, doc)
    return doc

def parse(file):
    Log.log(f"PARSING {file}")
    obj = ET.parse(file).getroot()
    if obj.tag == "doxygen":
        parsed = []
        for child in obj:
            parsed.append(PARSERS[str(child.tag)](child))
        assert len(parsed) == 1 # more than one compounddef found? hmmm
        return parsed[0]
    elif obj.tag == "doxygenindex":
        return Index.parse(obj)
    
PARSERS = {
    "compounddef":parse_compounddef,
    "namespace":Namespace.parse,
    "class": Compound.parse,
    "struct": Compound.parse,
    "union": Compound.parse,
    "interface": Compound.parse,
    "protocol": Compound.parse,
    "category": Compound.parse,
    "exception": Compound.parse,
    "namespace": Namespace.parse,
    #"group": Compound.parse,
    #"page": Compound.parse,
    #"example": Compound.parse,
    "dir": Directory.parse,
    "file": File.parse,
}

def files(path):
    yield from glob.glob(str(pathlib.Path(path, "*.xml")), recursive=True)

def objectify(path):
    path = pathlib.Path(path).resolve()
    Log.log(f"PARSING: {path}")
    result = {}
    for file in files(path):
        result[pathlib.Path(file).with_suffix('').name] = parse(file)

    # post process namespaces
    index = result['index']
    namespaces = index.__dict__.get('namespace', [])
    namespaces = index.__dict__['namespace'] = [GLOBAL_NAMESPACE.id, *sorted(namespaces, key=lambda x: x.obj.name)]

    for namespace in namespaces:
        # set namespace of all compounds in the namespace
        for x in namespace.obj.get_compounds():
            x.obj.namespace = namespace
        for x in namespace.obj.namespaces:
            x.obj.parent = namespace

    # resolve global namespace for all compounds TODO
    GLOBAL_NAMESPACE.namespaces = namespaces[1:]
    for cls in index.__dict__.get('class', []):
        if cls.obj.namespace == GLOBAL_NAMESPACE.id:
            GLOBAL_NAMESPACE.classes.append(cls)
    for cls in index.__dict__.get('interface', []):
        if cls.obj.namespace == GLOBAL_NAMESPACE.id:
            GLOBAL_NAMESPACE.classes.append(cls)

    return result

