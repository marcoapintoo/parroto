# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
import copy
import inspect

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../../"))
from parroto.base import is_method, is_property


class AutoObject(type):
    """
    Object with auto-initialition.
    """

    def __new__(mcs, name, bases, dct):
        mcs.__default_init = dct.get("__init__", None)
        dct["__init__"] = AutoObject.auto_constructor(dct)
        return super(AutoObject, mcs).__new__(mcs, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(AutoObject, cls).__init__(name, bases, dct)

    @staticmethod
    def auto_constructor(default_values):
        """
        Define an default constructor establishing default members.
        """
        default_init = default_values.get("__init__", None)

        def base_init(obj, *args, **kwargs):
            AutoObject.set_members(obj, default_values,
                                   omit_special_names=True,
                                   omit_property=True,
                                   override=True,
                                   deep_copy=True)
            AutoObject.set_members(obj, kwargs,
                                   omit_special_names=False,
                                   omit_property=True,
                                   # override=False,
                                   override=True,
                                   deep_copy=False)
            if default_init:
                AutoObject.call_base_constructor(default_init, obj, args, kwargs)

        return base_init

    @staticmethod
    def set_members(obj, values, omit_special_names=True,
                    omit_property=True, deep_copy=True, override=True):
        """
        Set dictionary values as members in an object,
        omitting properties and special names (starting with underscore),
        copying deepen and overriding if these options are activated.
        """
        for name, value in values.iteritems():
            if is_method(value) or \
                    (name.startswith("_") and not omit_special_names) or \
                    (is_property(value) and not omit_property):
                continue
            try:
                #if is_property(getattr(type(obj), name, None)): continue #FIX:
                oldvalue = getattr(obj, name, None)
                if oldvalue is None or override:
                    setattr(obj, name, copy.deepcopy(value) if deep_copy else value)
            except:
                pass

    @staticmethod
    def call_base_constructor(init, obj, args, kwargs):
        """
        Call constructor in object sending only parameters defined in it.
        Only if there are keyword parameters, they are sending.
        """
        names, varargs, keywords, defaults = inspect.getargspec(init)
        if keywords:
            init(obj, *args, **kwargs)
        else:
            named_args = dict((k, v) for k, v in kwargs.items() if k in names)
            init(obj, *args, **named_args)


class NeutralObject(object):
    """
    Neutral object for comparisons.
    It is an alternative to None at checking process.
    """
    pass


neutral = NeutralObject()
del NeutralObject


class NativeAttribute(object):
    """
    Attribute member for native objects, like lxml objects.
    """
    __metaclass__ = AutoObject
    __temporal_ref__ = []
    repository = lambda self, o: o.handler()
    key = lambda self, o: o
    name = u"native_attribute"
    default = None

    def __get__(self, instance, owner):
        handler = self.repository(instance)
        id_key = self.__create__(instance)
        return getattr(handler, "__native_" + self.name).setdefault(id_key, self.default)

    def __set__(self, instance, value):
        handler = self.repository(instance)
        id_key = self.__create__(instance)
        getattr(handler, "__native_" + self.name)[id_key] = value

    def __delete__(self, instance):
        raise Exception("Not implemented")

    def __create__(self, instance):
        handler = self.repository(instance)
        attr = getattr(handler, "__native_" + self.name, {})
        setattr(handler, "__native_" + self.name, attr)
        obj = self.key(instance)
        # Trick with Python's garbage collector:
        NativeAttribute.__temporal_ref__.append(obj)
        return id(obj)


class NativeAutoAttributeObject(object):
    _native_key = lambda self, o: o

    def __init_native_attribute(self, name, default):
        obj = getattr(type(self), name, neutral)
        if obj == neutral:
            setattr(type(self), name, NativeAttribute(name=name, default=default, key=type(self)._native_key))

    def __setattr__(self, name, value):
        self.__init_native_attribute(name, None)
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        self.__init_native_attribute(name, None)
        return object.__getattribute__(self, name)

