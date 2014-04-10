#!/usr/bin/python
import os
import sys
import re

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from common import is_str, accepts, returns, Message, Error
from markup import Entity, AttributeEntity
from .primitives import LatexBase

class LatexEntity(Entity):
    def translate(self, node):
        attributes = self.get_attributes(node)
        parameters = []
        current_name = lambda:"argument-{0}".format(len(parameters))
        current_attr = lambda: attributes.get(current_name(), None)
        attribute = current_attr()
        while attribute is not None:
            attributes.pop(current_name())
            parameters.append(unicode(attribute))
            attribute = current_attr() 
        named_parameters = dict((self.latexify(key, name=True), self.latexify(unicode(value))) for key, value in attributes.items())
        Message.warning("Entity '{name}' has no specific translation to LaTeX.".format(name=node.name()), prefix_space=2)
        return LatexBase.single_command(
            name=node.name(),
            text=self.traverse_subnodes(node),
            params=parameters,
            named_params=named_parameters
        ) + "%\n"
    
    def latexify(self, value, name=False):
        if name:
            return value.replace("-", "_")
        return value.replace("-", r"\-")
        # return self.traverse_attributes(node, self.get_attributes(node), self.traverse_subnodes(node))
    
    def wrap_switch(self, command, value):
        return u"%\n\n{{\n{command}%\n{value}\n\n}}\n".format(command=command, value=value)
    
    @returns(str)
    @accepts(cmd=(str, LatexBase))
    def command(self, node, cmd):
        if is_str(cmd):
            return cmd
        else:
            # node.root().append("<_require_package_>{name}</_require_package_>".format(name=name))
            node.root().prepare_native_property("packages", [])
            packages = node.root().packages
            # packages = Entity.get_attribute(node.root(), "packages", [])
            # print packages
            packages.extend(cmd.require)
            packages = node.root().packages = packages
            # Entity.set_attribute(node.root(), "packages", packages)
            # #for require in cmd.require:
            # #    #print node.root()._element[0]
            # #    node.root().prepend(Entity.create(
            # #        name = "_require_package_",
            # #        content = require.name,
            # #        attributes = {
            # #            "params": require.command_params()
            # #        }
            # #    ))
            # Root.packages.append(cmd.require)
            return cmd.content




class LatexAttributeEntity(AttributeEntity, LatexEntity):
    pass


class SimpleSelectableAttribute(LatexAttributeEntity):
    def simple_apply(self, attr, attribute_owner, valid_types):
        # attribute_owner.prepend("<label>{name}</label>".format(name=self.value(attr)))
        value = attribute_owner.translated_value()
        
        aligntype = attr.handler().traverse_subnodes(attr) or attr.text() or ""
        
        if aligntype not in valid_types:
            raise Error.bad_attribute_value(type(self).__name__, valid_types.keys(), aligntype)
        
        # command = self.command(attribute_owner, valid_types[aligntype]())
        command = self.command(attribute_owner, valid_types[aligntype])
        if command != "":
            # value = u"%\n\n{{\n{command}%\n{value}\n\n}}\n".format(command=command, value=value)
            value = self.wrap_switch(command, value)
        # print 111111,value,111111*3
        attribute_owner.set_translated_value(value)
        return value

class SimpleAttribute(LatexAttributeEntity):
    def is_valid(self, attr, attribute_owner, value):
        return True
    
    def latex_command(self, value):
        return None
    
    def simple_apply(self, attr, attribute_owner):
        value = attribute_owner.translated_value()
        attrvalue = attr.handler().traverse_subnodes(attr) or attr.text() or ""
        if not self.is_valid(attr, attribute_owner, attrvalue):
            raise TypeError(Error.error("Invalid value in {classname}: '{value}'".format(classname=type(self).__name__, value=attrvalue)))
        command = self.command(attribute_owner, self.latex_command(attrvalue))
        value = self.wrap_switch(command, value)
        attribute_owner.set_translated_value(value)
        return value


class TextDocument(Entity):
    def translate(self, node):
        text = self.traverse_subnodes(node)
        if text == u"":
            text = node.text(raw=True)
            
        content = self.traverse_attributes(node, self.get_attributes(node), text)
        # if "return" in text: print content == text, node.text(raw=True) == text
        basetext = re.sub(text, r"[ \t]+", " ")
        rawtext = re.sub(node.text(raw=True), r"[ \t]+", " ")
        contenttext = re.sub(content, r"[ \t]+", " ")
        return content if contenttext == basetext and rawtext == basetext else u"{{{0}}}".format(content)
        # return content if content == text and node.text(raw=True) == text else u"{{{0}}}".format(content)







