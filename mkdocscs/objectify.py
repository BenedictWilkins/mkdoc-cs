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
from os import get_blocking
import pathlib
from pprint import pprint
from re import I
from types import SimpleNamespace
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Dict, Tuple

class DocList:

    def __init__(self):
        self.doc = []

    def append(self, x):
        #print("APPEND", x)
        if x is not None and x != '':
            self.doc.append(x)

    def __repr__(self):
        return str(self) 

    def __str__(self):
        return str(self.doc) # TODO convert to markdown



ID = "id"
NAME = "compoundname"
NAMESPACE = "namespace"
FILE = "innerfile"
PROTECTION = "prot"
KIND = "kind"
CLASS = "class"
DOC_LONG = "detaileddescription"
DOC_SHORT = "briefdescription"
DIRECTORY = "dir"
FILE = "file"


def get_id(x):
    return Reference(x.attrib[ID], None)

def get_name(x):
    return x.find(NAME).text

def get_kind(x):
    return x.attrib[KIND]

def get_protection(x):
    return x.attrib[PROTECTION]

def get_documentation(x):
    return (parse_documentation(x.find(DOC_SHORT)), parse_documentation(x.find(DOC_LONG)))

def get_path(x):
    return x.find('location').attrib[FILE]


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
class Object:
    
    id : Reference

    def __post_init__(self):
        self.id.obj = self

@dataclass
class Member(Object):

    name: str
    protection: str
    docstring: str

@dataclass
class Compound(Object): 
    
    name: str
    kind: str
    protection: str
    docstring: Tuple[str, str]
    path: str

    def parse(x):
        return Compound(get_id(x), get_name(x), get_kind(x), get_protection(x), get_documentation(x), get_path(x))

@dataclass
class Class(Compound): 
  
    variables: List[Member]
    methods: List[Member]

    def parse(x):
        assert x.attrib[KIND] == CLASS
        
@dataclass
class Namespace(Object): 

    name: str
    docstring: str
    namespaces: List['Namespace']
    classes: List[Class]
    

    def parse(x):
        assert x.attrib[KIND] == NAMESPACE
        classes = [Reference(str(c.attrib['refid']), None) for c in x.findall('innerclass')]
        namespaces = [Reference(str(c.attrib['refid']), None) for c in x.findall('innernamespace')]
        return Namespace(get_id(x), get_name(x), get_documentation(x), namespaces, classes)

@dataclass 
class Directory(Object):

    path: str
    docstring: str
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
    doc = DocList()
    if p is not None:  
        for y in p.iter():
            parsers[y.tag](y, doc)
    #print(x, doc)
    return doc

def parse(file):
    print("PARSING:", file)
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
    print(f"PARSING: {path}")
    result = {}
    for file in files(path):
        result[pathlib.Path(file).with_suffix('').name] = parse(file)
    index_file = "index"
    index = result[index_file]
    del result[index_file]
    return index, result

