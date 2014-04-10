#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../")
    
from common import AutoInitObject

class ExecutionHandler(object):
    __metaclass__ = AutoInitObject
    name = ""
    handler = None
    order = 0

class HandlerCollection(object):
    _handlers = None
    
    def __init__(self, *args, **kwargs):
        self._handlers = []
    
    def add(self, name, handler, order=0):
        self._handlers.append(ExecutionHandler(
            name=name,
            handler=handler,
            order=order
        ))
    
    def get(self, name):
        fmtname = lambda t: t.lower() \
            .replace(" ", "").replace("-", "").replace("_", "")
        return self.select(select=lambda h: fmtname(h.name) == fmtname(name))
    
    def get_by_order(self, order):
        return self.select(select=lambda h: h.order == order)
    
    def select(self, select):
        return [h for h in self._handlers if select(h)]

    def orders(self):
        return set(h.order for h in self._handlers)


class HandlerModule(object):
    __metaclass__ = AutoInitObject
    _attributes = None
    _handlers = None
    
    def __init__(self, *args, **kwargs):
        self._attributes = HandlerCollection()
        self._handlers = HandlerCollection()
        
    def add_attribute(self, name, handler, order=0):
        self._attributes.add(
            name=name,
            handler=handler,
            order=order
        )
        
    def add_handler(self, name, handler, order=0):
        self._handlers.add(
            name=name,
            handler=handler,
            order=order
        )
        
    def get_attribute(self, name):
        return self._attributes.get(name)
    
    def get_entity(self, name):
        return self._handlers.get(name)
    
    def get_default_attribute(self):
        return self._attributes.get("$default$")[0]
    
    def get_default_handler(self):
        return self._handlers.get("$default$")[0]
    
    def set_default_attribute(self, handler):
        return self._attributes.add(
            name="$default$",
            handler=handler,
            order=0
        )
    
    def set_default_handler(self, handler):
        return self._handlers.add(
            name="$default$",
            handler=handler,
            order=0
        )
    
    
    def get_attribute_by_order(self, order):
        return self._attributes.get_by_order(order)
    
    def get_entity_by_order(self, order):
        return self._handlers.get_by_order(order)
    
    def select_attribute(self, select):
        return self._attributes.select(select)
    
    def select_handler(self, select):
        return self._handlers.select(select)
    
    def get_entity_orders(self):
        return self._handlers.orders()
    
    def get_attribute_orders(self):
        return self._attributes.orders()
