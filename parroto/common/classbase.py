#!/usr/bin/python
import os
import sys
import copy
import lxml.etree
from pyquery import PyQuery

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../")

from .typecheck import is_method, is_a

class AutoInitObject(type):
    def __new__(cls, name, bases, dct):
        dct["__init__"] = AutoInitObject.default_init_handler(dct, dct.setdefault("__init__", None))
        return super(AutoInitObject, cls).__new__(cls, name, bases, dct)
        
    def __init__(cls, name, bases, dct):
        super(AutoInitObject, cls).__init__(name, bases, dct)
    
    @staticmethod
    def default_init_handler(default_values, native_init):
        def default_init(obj, *args, **kwds):
            for name, value in default_values.iteritems():
                #if name.startswith("_") or issubclass(type(value), (types.FunctionType, types.MethodType, staticmethod, classmethod)):
                if name.startswith("_") or is_method(value):
                    continue
                try:
                    setattr(obj, name, copy.deepcopy(value))
                except:
                    pass
            for name, value in kwds.iteritems():
                try:
                    oldvalue = getattr(obj, name, None)
                    #if name == "normalize": print name, "value:", oldvalue, "method:", is_method(oldvalue),
                    if oldvalue is None or not is_method(oldvalue):
                        #if name == "normalize": print "in"
                        setattr(obj, name, value)
                    #elif name == "normalize": print "out"
                except:
                    pass
            if native_init:
                native_init (obj, *args, **kwds)
        return default_init


class PyQuery_NoDefault(object):
    def __repr__(self):
        """clean representation in Sphinx"""
        return '<NoDefault>'
no_default = PyQuery_NoDefault()


class XmlQuery(PyQuery):
    _metas = {}
    _meta = None
    def __init__(self, *args, **kwargs):
        super(XmlQuery, self).__init__(*args, **kwargs)
    
    def tag_name(self):
        return self[0].tag if len(self) > 0 else ""
    
    def rawtext(self, value=no_default):
        if value is no_default:
            if not self:
                return ''
            text = []
            def add_text(tag, no_tail=False):
                if tag.text and not isinstance(tag, lxml.etree._Comment):
                    text.append(tag.text)
                for child in tag.getchildren():
                    add_text(child)
                if not no_tail and tag.tail:
                    text.append(tag.tail)
            for tag in self:
                add_text(tag, no_tail=True)
            return ' '.join([t for t in text if t])
        for tag in self:
            for child in tag.getchildren():
                tag.remove(child)
            tag.text = value
        return self

    def has_meta(self):
        return self.get_meta() is None
        # return self._meta is not None
        
    def set_meta(self, meta):
        if len(self) > 0:
            # setattr(self[0], "_meta", meta)
            XmlQuery._metas[self[0]] = meta
        # self._meta = meta
        
    def get_meta(self):
        # return getattr(self[0], "_meta", None) if len(self) > 0 else None
        return XmlQuery._metas.setdefault(self[0], None) if len(self) > 0 else None
    
    @property
    def root(self):
        """return the xml root element
        """
        if is_a(self._parent, XmlQuery):
            return self._parent.root
        return super(XmlQuery, self).root
