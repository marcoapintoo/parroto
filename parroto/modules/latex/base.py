#!/usr/bin/python
import os
import sys
import re

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from common import is_str, accepts, returns, Message, Error, AutoInitObject, is_a
from markup import Entity, AttributeEntity
from .primitives import LatexBase

class LatexEntity(Entity):
    def translate(self, node, unordered=False):
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
        # WORKS, WHY??
        # return u"%\n\n{{\n{command}%\n{value}\n\n}}\n".format(command=command, value=value)
        return u"%\n{{\n{command}%\n{value}\n}}\n".format(command=command, value=value)
    
    @returns(str)
    @accepts(cmd=(str, LatexBase, tuple, list, set))
    def command(self, node, cmd):
        if is_str(cmd):
            return cmd
        elif is_a(cmd, tuple, list, set):
            return "".join(self.command(node, subcmd) for subcmd in cmd)
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
            if "__default__" not in valid_types:
                raise Error.bad_attribute_value(type(self).__name__, valid_types.keys(), aligntype)
            aligntype = "__default__"
        
        # command = self.command(attribute_owner, valid_types[aligntype]())
        command = self.command(attribute_owner, valid_types[aligntype])
        if command != "":
            # value = u"%\n\n{{\n{command}%\n{value}\n\n}}\n".format(command=command, value=value)
            value = self.wrap_switch(command, value) 
        # print 111111,value,111111*3
        attribute_owner.set_translated_value(value)
        return value


class SimpleContentAttribute(LatexAttributeEntity):
    def simple_apply(self, attr, attribute_owner, valid_types):
        # attribute_owner.prepend("<label>{name}</label>".format(name=self.value(attr)))
        value = attribute_owner.translated_value()
        
        attrtype = attr.handler().traverse_subnodes(attr) or attr.text() or ""
        
        if attrtype not in valid_types:
            if "__default__" not in valid_types:
                raise Error.bad_attribute_value(type(self).__name__, valid_types.keys(), attrtype)
            attrtype = "__default__" 
        
        # command = self.command(attribute_owner, valid_types[aligntype]())
        command = self.command(attribute_owner, valid_types[attrtype](value or attrtype))
        if command != "":
            # value = u"%\n\n{{\n{command}%\n{value}\n\n}}\n".format(command=command, value=value)
            value = command 
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
    
class SimpleRestorableValue(object):
    __metaclass__ = AutoInitObject
    name = ""
    command_after = None
    command_before = None
    values = []
    
    def execute_after(self, value):
        return self.command_after(value, self.values)
    
    def execute_before(self, value):
        return self.command_before(value, self.values)
    
class SimpleRestorableEntity(LatexEntity):
    nodes = []
    commands = {}
    def translate(self, node, unordered=False):
        if not unordered:
            return ""
        classname = type(self).__name__
        value = node.translated_value()
        node.prepare_native_property("__has_" + classname, False)
        has = getattr(node, "__has_" + classname)
        if has: return ""
        setattr(node, "__has_" + classname, True)
        command = self.commands[node.name().replace("_after", "").replace("_before", "")]
        text = self.traverse_subnodes(node) or node.text()
        self.nodes.append(node)
        if node.name().endswith("_after"):
            command.values.pop()
            cmd = command.execute_after(text)
        else:
            cmd = command.execute_before(text)
            command.values.append(text)
        cmd = self.command(node, cmd)
        return cmd or ""
        # return self.as_inline(node, cmd or "")

class SimpleRestorableAttribute(LatexAttributeEntity):
    def __init__(self, module):
        self.module = module
        self._counter = -1
        self.entity = SimpleRestorableEntity()
        
    def is_valid(self, attr, attribute_owner, value):
        return True
    
    def latex_command(self, value, othervalues):
        return None
    
    def latex_restore_command(self, value, othervalues):
        return None
    
    def get_default_value(self, attr, attribute_owner):
        return ""
    
    def simple_apply(self, attr, attribute_owner):
        classname = type(self).__name__
        
        value = attribute_owner.translated_value()
        attrvalue = attr.handler().traverse_subnodes(attr) or attr.text() or ""
        # print attrvalue, self._counter
        attribute_owner.prepare_native_property("__has_" + classname, False)
        has = getattr(attribute_owner, "__has_" + classname)
        if has: return value
        self._counter += 1
        setattr(attribute_owner, "__has_" + classname, True)
        
        # print attribute_owner._element, "\n"*4
        attribute_owner.before(Entity.create(name=classname + "_before", content=attrvalue, attributes={"__id": self._counter}))
        attribute_owner.after(Entity.create(name=classname + "_after", content=attrvalue, attributes={"__id": self._counter}))
        
        # print attribute_owner.parent()._element, "\n"*4
        
        if not self.is_valid(attr, attribute_owner, attrvalue):
            raise TypeError(Error.error("Invalid value in {classname}: '{value}'".format(classname=type(self).__name__, value=attrvalue)))
        
        self.module.add_handler(classname + "_before", self.entity, order=1000)
        self.module.add_handler(classname + "_after", self.entity, order=1000)
        
        self.entity.commands.setdefault(classname, SimpleRestorableValue(
            name=classname,
            command_before=self.latex_command,
            command_after=self.latex_restore_command,
            values=[self.get_default_value(attr, attribute_owner)],
        ))
         
        # self.entity.commands[classname].stackvalues.append(attrvalue)
        self.entity.commands[classname].command_before = self.latex_command
        self.entity.commands[classname].command_after = self.latex_restore_command 
        
        # command = self.command(attribute_owner, self.latex_command(attrvalue))
        # restore_command = self.command(attribute_owner, self.latex_restore_command(attrvalue))
        # value = "%\n" + command + "%\n" + value + "%\n" + restore_command  
        # attribute_owner.set_translated_value(value)
        return value


class TextDocument(Entity):
    def translate(self, node, unordered=False):
        text = self.traverse_subnodes(node)
        if text == u"":
            text = node.text(raw=True)
        
        #if node.rawtext().strip() == "":
        #    print node.rawtext() == text, ">>%s<<" % node.rawtext(), ">>%s<<" % text, "\n"
            # print node.prev().rawtext() if node.prev() else "...", ">>%s<<" % node.rawtext()
        content = self.traverse_attributes(node, self.get_attributes(node), text)
        # if "return" in text: print content == text, node.text(raw=True) == text
        basetext = re.sub(text, r"[ \t]+", " ")
        rawtext = re.sub(node.text(raw=True), r"[ \t]+", " ")
        contenttext = re.sub(content, r"[ \t]+", " ")
        return content if contenttext == basetext and rawtext == basetext else u"{{{0}}}".format(content)
        # return content if content == text and node.text(raw=True) == text else u"{{{0}}}".format(content)







