#!/usr/bin/python
import os
import sys
import re

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from common import AutoInitObject, Error, is_a, is_str
from markup import RootDocument, MetaElement
from .primitives import LatexRequire, LatexBase, DocumentStructure
from .base import LatexEntity as Entity

class MacroDefinedResult(list):
    @staticmethod
    def wrap_content(content):
        return Entity.create("text", content)
    
    def append(self, content):
        list.append(self, MacroDefinedResult.wrap_content(content))
    
    def add(self, content):
        return self.append(content)
    
    def value(self):
        return "".join(self)
    
    def __iadd__(self, content):
        self.append(content)
        return self
    
    def __add__(self, othervalue):
        if is_str(othervalue):
            othervalue = MacroDefinedResult.wrap_content(othervalue)
            res = MacroDefinedResult()
            res.extend(self)
            res.append(othervalue)
            return res
        elif is_a(othervalue, MacroDefinedResult):
            res = MacroDefinedResult()
            res.extend(self)
            res.extend(othervalue)
            return res
        else:
            raise TypeError(Error.error("Invalid operation between {0} and {1}".format(type(self), type(othervalue))))
    
    def __str__(self):
        return str(self.value())
    
    def __unicode__(self):
        return unicode(self.value())
    

class MacroHandler(object):
    __metaclass__ = AutoInitObject
    name = ""
    handler = None
    raw_code = ""
    defaults = {}
    
    def codename(self):
        return "".join(c if c.isalnum() else "_" for c in self.name)
    
    def prepare_handler(self, after_code="", before_code=""):
        try:
            # code = self.code.format(before_code=before_code, after_code=after_code)
            if not self._is_code(self.raw_code):
                code = u"def macro_translation(): #inline-value" \
                    u"\n    {before_code} " \
                    u"\n    return '''{code}''' ".format(code=self.raw_code, before_code=before_code) + \
                    u"\n    {after_code} ".format(after_code=after_code)
            else:
                code = u"def macro_translation(): #code" \
                    u"\n    {before_code} " \
                    u"\n    ".format(before_code=before_code) + self._reindent(self.raw_code) + \
                    u"\n    {after_code} " \
                    u"\n    return '' ".format(after_code=after_code)
            exec compile(code, self.name, "exec") in globals(), locals()
            self.handler = locals()["macro_translation"]
            self.handler.func_globals["code_text"] = self.raw_code
            self.handler.func_globals["default_attributes"] = self.defaults 
        except (IndentationError, SyntaxError), e:
            print "*"*10, "ERROR:", e
            print "*"*10, "CODE", "*"*10
            print code
            print "*"*26
            # raise e
    
    def _is_code(self, code):
        conditions = [
            "return" in code,
            "+=" in code,
            re.search(r"\.\s*append\s*\(", code) is not None,
            re.search(r"\bresult\b", code) is not None,
            re.search(r"\b{0}\b".format(self.codename()), code) is not None,
        ]
        return any(conditions)
        
    def _reindent(self, text):
        lines = text.split("\n")
        first_indent = -1
        indent = min(re.search(r"[^\s]", line).start() for line in lines if line.strip() != "")
        for index, line in enumerate(lines):
            if first_indent < 0 and line.strip() != "":
                first_indent = re.search(r"[^\s]", line).start()
            if line.strip() != "":
                lines[index] = re.sub("^" + r"\s"*indent, "", line)
                while True:
                    fline = lines[index]
                    lines[index] = re.sub(r"^(\t*?)\t([^\t])", r"\1    \2", fline)
                    # print "---%s--%s"%(fline,lines[index])
                    if lines[index] == fline:
                        break
        return "\n    ".join(lines)
        

class DefinedMacro(Entity):
    handlers = {}
    def __init__(self):
        self.handlers = {}
    
    def add(self, name, macro_handler):
        self.handlers[name] = macro_handler
    
    def translate(self, node, unordered=False):
        node.prepare_native_property("_executed", False)
        if node._executed:
            return node.translated_value()
        node._executed = True
        text = self.traverse_subnodes(node) or node.text() or ""
        name = node.name()
        # attributes = dict((key, str(value)) for key, value in self.get_attributes(node).items())
        attributes = dict((key, unicode(value)) for key, value in self.get_attributes(node).items())
        attributes.setdefault("text", text)
        attributes.setdefault("node", node)
        macro_handler = self.handlers[name]
        self._set_default_vars(node, macro_handler, attributes)
        try:
            handlerret = macro_handler.handler()
            if handlerret is not None:
                ret = unicode(handlerret)
                DefinedMacro.create_and_add(node, name="text", content=ret)
            return ""
        except Exception, e:
            Error.error("Error executing macro " + node.name() + ": " + e.message)
            return ""
    
    def _set_default_vars(self, node, macro_handler, attributes):
        before_code = "result = globals()['result']; {0} = globals()['result'];".format(macro_handler.codename())
        after_code = "return unicode(result)"
        macro_handler.prepare_handler(before_code=before_code, after_code=after_code)
        for key, value in macro_handler.defaults.items():
            macro_handler.handler.func_globals[key] = value
        
        macro_handler.handler.func_globals["result"] = MacroDefinedResult()
        macro_handler.handler.func_globals["macro"] = DefinedMacro.create
        macro_handler.handler.func_globals["create"] = DefinedMacro.create
        macro_handler.handler.func_globals["macro_text"] = DefinedMacro.create_text
        macro_handler.handler.func_globals["create_text"] = DefinedMacro.create_text
        macro_handler.handler.func_globals["attributes"] = attributes
        macro_handler.handler.func_globals["self"] = self
        macro_handler.handler.func_globals["this"] = self
        macro_handler.handler.func_globals["node"] = node
        for key, value in attributes.items():
            macro_handler.handler.func_globals[key] = value
            
    @staticmethod
    def create(name, content="", attributes=None):
        entity = Entity.create(name, content, attributes)
        return entity
    
    @staticmethod
    def create_text(content="", attributes=None):
        entity = Entity.create("text", content, attributes)
        return entity
    
    @staticmethod
    def create_and_add(node, name, content="", attributes=None):
        entity = Entity.create(name, content, attributes)
        xmlentity = MetaElement(entity, base=node)
        xmlentity.insertAfter(node)
        return xmlentity

class Define(Entity):
    def __init__(self, module):
        self.module = module
        self.macro_manager = DefinedMacro()
        
    def translate(self, node, unordered=False):
        # DANGEROUS:
        code_text = self.traverse_subnodes(node)
        # code_text = "".join(subnode.text() for subnode in node.subnodes())
        # attributes = dict((key, str(value)) for key, value in self.get_attributes(node).items())
        attributes = dict((key, unicode(value)) for key, value in self.get_attributes(node).items())
        if "macro" not in attributes:
            raise Error.error("macro with no name")
        # print "##%s##\n" % code_text
        self.create_macro(code_text, attributes)
        return ""

    def create_macro(self, code_text, attributes):
        self.module.add_handler(attributes["macro"], self.macro_manager, order=0)
        self.macro_manager.add(attributes["macro"], MacroHandler(
            name=attributes["macro"],
            raw_code=code_text,
            defaults=attributes
        ))
        
