#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
   Created on 12-03-2022
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import mkdocscs
import pathlib
import glob

from pprint import pprint

def clean(path):
    import shutil
    shutil.rmtree(path)

if __name__ == "__main__":
    path = pathlib.Path(__file__).parent
    path_xml = pathlib.Path(path, "xml")
    clean(pathlib.Path(path, "docs"))
    index, result = mkdocscs.objectify(path_xml)
    
    mkdocscs.markdownify(index, result)

    
    
