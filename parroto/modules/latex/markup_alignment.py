#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from common import Error
#from markup import  OneShotAttribute, AttributeEntity
from .primitives import Alignment
from .base import SimpleSelectableAttribute
#from .base import LatexEntity as Entity

class AlignmentAttribute(SimpleSelectableAttribute):
    def apply(self, attr, attribute_owner):
        valid_types = {
            "": lambda: "",
            "justified": Alignment.justified(),
            "right":Alignment.left_ragged(),
            "left": Alignment.right_ragged(),
            "center":Alignment.center(),
        }
        return self.simple_apply(attr, attribute_owner, valid_types)
    
    def apply2(self, attr, attribute_owner):
        # attribute_owner.prepend("<label>{name}</label>".format(name=self.value(attr)))
        value = attribute_owner.translated_value()
        
        aligntype = attr.handler().traverse_subnodes(attr) or attr.text() or ""
            
        valid_types = {
            "": lambda: "",
            "justified": Alignment.justified,
            "right":Alignment.left_ragged,
            "left": Alignment.right_ragged,
            "center":Alignment.center,
        }
        
        if aligntype not in valid_types:
            raise Error.bad_attribute_value("alignment", valid_types.keys(), aligntype)
        
        command = self.command(attribute_owner, valid_types[aligntype]())
        if command != "":
            value = u"%\n\n{{\n{command}%\n{value}\n\n}}\n".format(command=command, value=value)
        #print 111111,value,111111*3
        attribute_owner.set_translated_value(value)
        return value
