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


from .objectify import Compound, Namespace, Reference

class Markdownify:

    def __init__(self, path):
        path = pathlib.Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True) # make them if not already made...
        self.path = path
        
    def __enter__(self):
        self.file = open(str(self.path), "a")
        return self

    def write(self, x):
        self.file.write(x)

    def title(self, level, x):
        self.write(f"{'#' * level} {x}")

    def __exit__(self, *args):
        self.file.close()


def markdownify_Compound(x, m):
    m.title(1, x.name)

def markdownify_Namespace(x, m):
    m.title(1, x.name)



MARKDOWNIFY = {
    Compound : markdownify_Compound,
}

def markdownify(index, objects):
   
    print("-----------------------------------")

    # make directory structure by namespace
    namespaces = index.__dict__.get('namespace', [])
    for n in namespaces:
        path = pathlib.Path("docs", *n.obj.name.split("::"))
        path.mkdir(parents=True, exist_ok=True)
        print(path)
        # markdownify namespaces
        with Markdownify(pathlib.Path(path, n.obj.name).with_suffix(".md")) as m:
            markdownify_Namespace(n.obj, m)


        #for cls in n.classes:
        #    DIRECTORY_STRUCTURE[path]




    #for name, obj in objects.items():
    #    path = pathlib.Path(name).with_suffix(".md")
    #    print(path)
        
        #with Markdownify(path) as m:
        #    MARKDOWNIFY.get(type(obj), lambda *args: None)(obj, m)
            

    
    """
    print("-----------------------------------")

    for k,v in Reference.__reference__.items():
        print("REFERENCE", k, v.obj)

    print("-----------------------------------")

    for p, o in objects.items():
        print("OBJECT", p, o.id, o.id.obj)
    """
    """

   
    """











