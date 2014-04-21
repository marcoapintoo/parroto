# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
import types

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../../"))


def is_a(obj, *object_types):
    """
    Checking íf an object is an instance of any of types.
    """
    return issubclass(type(obj), tuple(object_types))


def is_str(obj):
    """
    Checking íf an object is a string: str or unicode.
    """
    return is_a(obj, str, unicode)


def is_iterable(obj):
    """
    Checking íf an object is a tuple, list, or set.
    """
    return is_a(obj, tuple, list, set)


def is_callable(obj):
    """
    Checking íf an object has a __call__ method.
    """
    return hasattr(obj, "__call__")


def is_method(obj, strict=False):
    """
    Checking íf an object is a method: function or class/static/object method.
    """
    if strict:
        return is_a(obj, types.MethodType)
    return is_a(obj, types.FunctionType, types.MethodType, staticmethod, classmethod)


def is_lambda(obj):
    """
    Checking íf an object is a lambda.
    """
    return is_a(obj, types.LambdaType)


def is_generator(obj):
    """
    Checking íf an object is a generator.
    """
    return is_a(obj, types.GeneratorType)


def is_property(obj):
    """
    Checking íf an object is a property object. In other words, if it has __get__ and __set__ methods.
    """
    return all(hasattr(obj, method) for method in ("__get__", "__set__"))


