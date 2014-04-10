#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../")

from markup.structure import XmlAttribute, XmlNode
from markup.structure import IEntityHandler, IAttributeHandler
from markup.structure import Interpreter, HandlerModule

class Attribute(IAttributeHandler):
    _node = None
    
    def set_node(self, node):
        self._node = node
    
    def root_node(self):
        return self._node.root()

    def translate(self):
        return ""


class Entity(IEntityHandler):
    _node = None
    
    def set_node(self, node):
        self._node = node
    
    def root_node(self):
        return self._node.root()

    def translate(self):
        return ""

    def readapt_structure(self):
        return ""

