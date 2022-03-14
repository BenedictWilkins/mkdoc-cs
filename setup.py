#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created on 11-11-2020 16:33:31
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

from setuptools import setup, find_packages

# last successful build versions  gym-unity-0.28.0 mlagents-envs-0.28.0

setup(name='mkdocscs',
      version='0.0.1',
      description='',
      url='',
      author='Benedict Wilkins',
      author_email='benrjw@gmail.com',
      packages=find_packages(),
      install_requires=['mkdocs-awesome-pages-plugin', 'mkdocs-autolinks-plugin', 'mkdocs-section-index'],
      zip_safe=False)
