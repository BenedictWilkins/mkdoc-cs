#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
   Created on 14-03-2022
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import pathlib
import glob
from pprint import pprint
import functools

from markdown import markdown

from .._objectify import Member, Variable, Function, Compound, Namespace, Reference, Documentation

class Markdownify:

    def __init__(self, path, navigation_title=None, navigation_file=".pages"):
        path = pathlib.Path(path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True) # make them if not already made...
        self.path = path
        self.navigation_file = navigation_file
        self.navigation_title = navigation_title
        self._pages()

        self.MARKDOWNIFY = {
            str: lambda *args, **kwargs: args[0],
            Reference:self.markdownify_reference,
            Documentation:self.markdownify_documentation,
            Variable:self.markdownify_variable,
            Function:self.markdownify_function}

    def _pages(self):
        path_pages = pathlib.Path(self.path.parent, self.navigation_file)
        if not path_pages.exists():
            with path_pages.open('w') as f:
                f.write("nav:\n")
        with path_pages.open('a') as f:
            if self.navigation_title is None:
                f.write(f"    - '{self.path.name}'\n")
            else:
                f.write(f"    - '{self.navigation_title}' : '{self.path.name}'\n")
        
    def __enter__(self):
        self.file = open(str(self.path), "a")
        return self

    def __exit__(self, *args):
        self.file.close()

    def write(self, x):
        self.file.write(x)

    def newline(self):
        self.file.write("\n")

    def title(self, level, x):
        assert level > 0
        self.write(f"{'#' * level} {x}\n")

    def list(self, elements, indent=0):
        for x in elements:
            if isinstance(x, (list, tuple)):
                self.list(x, indent=indent+1)
            else:
                self.write(f"{'    '*indent}- {self.markdownify(x)}\n")

    #def link(self, ref : Reference):
    #    assert isinstance(ref, Reference)
    #    self.write(self.markdownify_reference(ref))

    def markdownify(self, x, **kwargs):
        return self.MARKDOWNIFY[type(x)](x, **kwargs)

    def markdownify_reference(self, ref : Reference, text=None, short=False):
        if text is None:
            if not short:
                return self.markdownify_name(ref.obj)
            else:
                text = ref.obj.name.split("::")[-1]
                return f"[{text}]({ref.id}.md)"
        else:
            return f"[{text}]({ref.id}.md)" # this kind of link requires auto link package...
   
    def markdownify_documentation(self, doc : Documentation):
        short = "".join([self.markdownify(x) for x in doc.short])
        long = "".join([self.markdownify(x) for x in doc.long])
        return f"{short}\n\n{long}\n"

    def markdownify_name(self, obj): # get the name with embedded links to namespaces/parent compounds
        parents = list(reversed(obj.get_parents()[:-1])) # ignore global namespace
        names = [*parents, obj.id]
        linked_name = "::".join(self.markdownify_reference(n, short=True) for n in names)
        return linked_name

    def markdownify_variable(self, obj):
        return f"```{obj.definition}```"

    def markdownify_function(self, obj):
        return f"```{obj.definition}```"

