#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
   Created on 12-03-2022
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"
import pathlib
import glob
from pprint import pprint
import itertools

from markdown import Markdown, markdown

from ._generate import Markdownify

from .._objectify import Namespace, Reference, Documentation 

def page_namespace(markdownify : Markdownify, namespace : Namespace):
    markdownify.title(1,f"Namespace {markdownify.markdownify_name(namespace.obj)}")
    markdownify.write(markdownify.markdownify(namespace.obj.docstring))
    if len(namespace.obj.namespaces) > 0:
        markdownify.title(3,"Namespaces")
        markdownify.list(sorted(namespace.obj.namespaces, key=lambda x: x.obj.name))
    if len(namespace.obj.classes) > 0:
        markdownify.title(3,"Classes")
        markdownify.list(sorted(namespace.obj.classes, key=lambda x: x.obj.name))

def page_class(markdownify : Markdownify, cls : Reference):
    markdownify.title(1, f"{cls.obj.kind.capitalize()} {markdownify.markdownify_name(cls.obj)}") 
    
    markdownify.newline()
    markdownify.write(markdownify.markdownify(cls.obj.docstring))
    markdownify.newline()
    markdownify.hline()

    for key, group in itertools.groupby(cls.obj.members, key=lambda x: x.kind):
        markdownify.title(4, key.capitalize())
        markdownify.list(list(group))
        markdownify.hline()

    if len(cls.obj.inherit_from) > 0:
        markdownify.title(4, "Inherits")
        markdownify.list(cls.obj.inherit_from)

    if len(cls.obj.inherit_by) > 0:
        markdownify.title(4, "Derived")
        markdownify.list(cls.obj.inherit_by)

    markdownify.title(4, f"Namespace: {markdownify.markdownify(cls.obj.namespace)}")    
    markdownify.write(f"Source: {cls.obj.path}\n")

def markdownify(data, root_path="./docs", path="./docs", **kwargs):
    Markdownify.set_base_path(path)
    Markdownify.set_root_path(root_path)

    print("-----------------------------------")
    index = data['index']
    # MARKDOWNIFY NAMESPACES
    namespaces = index.__dict__['namespace']
    with Markdownify(f"Namespace/index.md") as m:
        m.title(1, "Namespaces")
        m.list(namespaces) # TODO could nest them...
    for namespace in namespaces:
        with Markdownify(f"Namespace/{namespace.id}.md", navigation_title=namespace.obj.name) as m:
            page_namespace(m, namespace)

    # MARKDOWNIFY CLASSES
    classes = index.__dict__.get('class', [])
    with Markdownify("Class/index.md") as m:
        m.title(1, "Classes")
        m.list(classes)
    for cls in sorted(classes, key = lambda x: x.obj.name):
        with Markdownify(f"Class/{cls.id}.md", navigation_title=cls.obj.name) as m:
            page_class(m, cls)

    classes = index.__dict__.get('interface', [])
    with Markdownify("Interface/index.md") as m:
        m.title(1, "Interfaces")
        m.list(classes)
    
    for cls in sorted(classes, key = lambda x: x.obj.name):
        #print(cls.obj.name)
        with Markdownify(f"Interface/{cls.id}.md", navigation_title=cls.obj.name) as m:
            page_class(m, cls)

    # order navigation...
    pages_path = pathlib.Path(path, kwargs.get('navigation_file', '.pages'))
    with pages_path.open("a") as pages:
        pages.write("nav: \n")
        pages.write("    - Namespace\n")
        pages.write("    - Class\n")
        pages.write("    - Interface\n")
        



    










