#!/usr/bin/python
import os
import sys
import re

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from common import Error
#from markup import  OneShotAttribute, AttributeEntity
from .primitives import Paragraph
from .base import SimpleAttribute
#from .base import LatexEntity as Entity

class LineHeightAttribute(SimpleAttribute):
    line_types = {
        u"simple": 1,
        u"single": 1,
        u"litle": 1.3,
        u"common": 1.5,
        u"one-half": 1.5,
        u"onehalf": 1.5,
        u"one-and-half": 1.5,
        u"double": 2
    }
    def is_valid(self, attr, attribute_owner, value):
        value = value.strip().lower()
        return re.match(r"\d*(\.\d+)?", value) is not None or value in self.line_types.keys()
    
    def latex_command(self, value):
        value = value.strip().lower()
        if value in self.line_types.keys():
            value = unicode(self.line_types[value])
        return Paragraph.line_spacing(value)
    
    def apply(self, attr, attribute_owner):
        return self.simple_apply(attr, attribute_owner)
    