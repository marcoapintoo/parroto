#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from common import Error
from markup import  OneShotAttribute
from .primitives import References
from .base import LatexEntity as Entity

class LabelAttribute(OneShotAttribute):
    def apply_once(self, attr, attribute_owner):
        # attribute_owner.prepend("<label>{name}</label>".format(name=self.value(attr)))
        attribute_owner.prepend(Entity.create(
            name="label",
            content=self.value(attr)
        ))


class Label(Entity):
    def translate(self, node):
        # print node, node._element
        text = self.traverse_subnodes(node)
        # raw_input("..")
        if text == "":
            text = node.text()
        # return LatexDocument.command(node, References.define_label(text))
        # ##return self.command(node, References.define_label(text))
        cmd = self.command(node, References.define_label(text))
        return self.as_inline(node, cmd)


class Reference(Entity):
    def translate(self, node):
        # print node, node._element
        attributes = self.get_attributes(node)
        #reftype = str(attributes.get("type", "reference")).lower()
        reftype = unicode(attributes.get("type", "reference")).lower()
        
        text = self.traverse_subnodes(node)
        if text == "":
            text = node.text()
            
        valid_types = {
            "ref": References.reference_to,
            "reference": References.reference_to,
            "equation": References.equation_reference_to,
            "page": References.page_reference_to,
        }
        
        if reftype not in valid_types:
            raise Error.bad_attribute_value("ref.type", valid_types.keys(), reftype)
            raise Error.error(u"Reference attribute only admits: {values}, but {value} was setted".\
                format(values=valid_types.keys(), value=reftype))
        # return LatexDocument.command(node, References.define_label(text))
        # ##return self.command(node, References.define_label(text))
        cmd = self.command(node, valid_types[reftype](text))
        return self.as_inline(node, cmd)
