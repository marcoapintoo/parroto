#!/usr/bin/python
import os
import sys
import codecs

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../")
    
from common import AutoInitObject, accepts, returns
from .files import StructureFile
from .core import MetaElement
from .handler import HandlerModule

class Interpreter(object):
    __metaclass__ = AutoInitObject
    _document = None
    _module = None
    
    @accepts(data_string=str)
    def load_string(self, data_string):
        data_string = data_string.encode("utf-8")
        self._document = StructureFile() 
        # self._document.set_node(NodeElement.create(data_string, normalize=True))
        self._document.set_node(MetaElement(data_string, normalize=True))
        
    @accepts(filename=str)
    def load_file(self, filename):
        text = ""
        with codecs.open(filename, "rt", encoding="utf-8") as fileobj:
            text += "".join(fileobj.readlines())
        self.load_string(text)
        
    @accepts(module=HandlerModule)
    def set_module(self, module):
        self._module = module
        self._document.set_module(module)
        
    @returns(str)
    def execute(self):
        return self._document.execute()
    
    @accepts(filename=str)
    def execute_to_file(self, filename):
        text = self._document.execute()
        with codecs.open(filename, "wt", encoding="utf-8") as fileobj:
            fileobj.write(text)

