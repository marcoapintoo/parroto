#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../")
    
from common import AutoInitObject, Message

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
    
    def execute(self):
        execute_node_flag = True
        cycle = 1
        while execute_node_flag or self.is_modified():
            Message.message("Starting cycle {0}".format(cycle), header="PROCESS", prefix_space=1)
            cycle += 1
            execute_node_flag = False
            self._rootnode.execute()
        return self._rootnode.translated_value()
        