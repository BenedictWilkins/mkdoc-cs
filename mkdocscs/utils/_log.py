#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
   Created on 15-03-2022
"""
__author__ = "Benedict Wilkins"
__email__ = "benrjw@gmail.com"
__status__ = "Development"

import warnings

class MkdocscsWarning(Warning):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return f"[WARNING]: {self.message}"


def _log(fun):
    def log(*args, **kwargs):
        if not Log.get_logger().silent:
            return fun(Log.get_logger(), *args, **kwargs)
    return log

class Log:

    _LOGGER = None

    def __new__(cls, *args, **kwargs):
        if Log._LOGGER is None:
            _LOGGER = super().__new__(cls)
            #_LOGGER.__init___(*args, **kwargs)
        return _LOGGER

    def __init__(self, silent=False):
        self.silent = silent
    
    @_log
    def warn(self, message):
        print(MkdocscsWarning(message))

    @_log
    def log(self, message):
        print(f"[INFO]: {message}")

    @classmethod
    def get_logger(cls):
        return Log()

Log.get_logger()