#!/usr/bin/python
import os
import sys
import types

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

def is_a(obj, *typelist):
    return issubclass(type(obj), tuple(typelist))

def is_str(obj):
    return is_a(obj, str, unicode)

def is_iterable(obj):
    return is_a(obj, tuple, list, set)

def is_callable(obj):
    return hasattr(obj, "__call__")

def is_method(obj):
    return is_a(obj, types.FunctionType, types.MethodType, staticmethod, classmethod)

def is_lambda(obj):
    return is_a(obj, types.LambdaType)

def is_generator(obj):
    return is_a(obj, types.GeneratorType)




