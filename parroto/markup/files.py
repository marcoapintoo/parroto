#!/usr/bin/python
import os
import sys
import re
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../")
    
from common import AutoInitObject, Message
from .entities import Entity

class StructureFile(object):
    __metaclass__ = AutoInitObject
    _rootnode = None
    _controllers = None
    
    def set_node(self, node):
        self._rootnode = node
    
    def set_module(self, module):
        self._controllers = module
        self._rootnode.set_controllers(module)
    
    def set_modified(self, modified=True):
        self._rootnode.set_modified(modified)
        
    def is_modified(self):
        return self._rootnode.is_modified()
    
    def beautifier(self, text):
        text = text.replace("\r\n", "\n")
        #return text
        text = re.sub(r"\n[ \t]*%[ \t]*\n", "\n%\n", text)
        text = re.sub(r"([ \t]*\n[ \t]*\n)+", "\n\n", text)
        text = re.sub(r"([ \t]*\n[ \t]*\n[ \t]*\n)+", "\n\n", text)
        #text = re.sub(r"\n[ \t]*\n", "\n\n", text)
        #text = re.sub(r"(\n\n)+", "\n\n", text)
        text = re.sub(r"(%+\n)+", "%\n", text)
        return text
        while True:
            text0 = text
            text = re.sub(r"\n[ \t]*%[ \t]*\n", "%\n", text0)
            #text = re.sub(r"([ \t]*\n[ \t]*\n)+", "\n\n", text)
            text = re.sub(r"([ \t]*\n[ \t]*\n[ \t]*\n)+", "\n\n", text)
            if text0 == text:
                break
        return text
    
    def execute(self):
        execute_node_flag = True
        cycle = 1
        while execute_node_flag or self.is_modified():
            Message.message("Starting cycle {0}".format(cycle), header="PROCESS", prefix_space=1)
            cycle += 1
            execute_node_flag = False
            self._rootnode.execute()
        Message.message("Starting last cycle {0}".format(cycle), header="PROCESS", prefix_space=1)
        Entity.order_activated = False
        self._rootnode.execute(order=None)
        return self.beautifier(self._rootnode.translated_value())
        
