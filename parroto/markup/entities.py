#!/usr/bin/python
import os
import sys

if __name__ == u"__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../")
    
from common import AutoInitObject

class AttributesEntityDict(dict):
    def value(self, key, default = None):
        val = self.get(key, default)
        return str(val) if val is not None else None
        
class Entity(object):  # (NativeObjectAttr):
    order_activated = True
    def as_inline(self, node, content):
        name = node.parent().name()
        return content + ("" if name == u"text" else "%\n")
    
    def translate(self, node, unordered=False):
        # node.normalize()
        return self.traverse_attributes(node, self.get_attributes(node), self.traverse_subnodes(node)) 
    
    def traverse_subnodes(self, node, separator=""):
        # subnodes = node.subnodes() 
        # if len(subnodes) == 0: return ""
        result = u""
        # orders = node.controllers.get_entity_orders()
        
        orders = sorted(set(child.handler(get_info=True).order for child in node.subnodes()))

        if not Entity.order_activated:
            return self.traverse_sequence_subnodes(node, separator=separator, order=None)
        
        for order in orders:
            result = self.traverse_sequence_subnodes(node, separator=separator, order=order)
        # result = self._traverse_child_iterative(node, separator=separator, order=-1e100)
        # result = self._traverse_child_iterative(node, separator=separator, order=0)
        #UNPREDICTABLE:
        #result = self.traverse_sequence_subnodes(node, separator=separator, order=None)
        
        return result
        
    def traverse_sequence_subnodes(self, node, separator="", order=1e100):
        # r = [(child.html(), child.execute(order=order)) for child in node.subnodes()]
        # o = separator.join(orr[1] for orr in r)
        # o = separator.join(child.execute(order=order) for child in node.subnodes())
        #print " ".join(repr(child._element) for child in node.subnodes())
        # print "--->", o
        return separator.join(child.execute(order=order) for child in node.subnodes())
    
    def traverse_subnodes_unsorted(self, node, separator="", order=1e100):
        # return separator.join(child.execute() for child in node.subnodes())
        subnodes = node.subnodes() 
        if len(subnodes) == 0: return ""
        child = node.subnodes()[0]
        result = u""        

        while child is not None:  # first_child.next() is not None:
            result += child.execute(order=order)
            try:
                child = child.next()
                # child = child.nextAll(ordered=True)[0]
            except IndexError:
                break
        return result
        # return separator.join(child.execute() for child in node.subnodes())

    def get_attributes(self, node):
        attributes = {}
        orders = sorted(set(child.handler(get_info=True).order for child in node.attributes()))

        for order in orders:
            attributes = AttributesEntityDict(
                (child.name().lower(), AttributeEntityValue(
                    value=child.execute(order=order),
                    handler=child.handler(),
                    target=child
                )) for child in node.attributes())
        # print [(attr.value, attr.target.html(), attr.value, repr(attr.target._element), attr.handler) for attr in attributes.values()] 
        return attributes

    def traverse_attributes(self, node, attributes, content):
        node.set_translated_value(content)
        for _, attr in attributes.items():
            newcontent = attr.apply(node)
            # node.set_translated_value(attr.apply(node))
            if content != newcontent:
                newcontent += u"%\n"
                node.set_translated_value(newcontent)
                content = newcontent
            # content = node.translated_value()
        return node.translated_value()
    
    @staticmethod
    def create(name, content, attributes=None):
        rescontent = u"<{0}>".format(name)
        rescontent += u"<text>{0}</text>".format(content)
        if not attributes:
            attributes = {}
        for attr, value in attributes.items():
            if value == u"":
                continue
            rescontent += u"<{tag}.{attr}>{value}</{tag}.{attr}>".format(tag=name, attr=attr, value=value)
        rescontent += u"</{0}>".format(name)
        return rescontent
    
#     @staticmethod
#     def get_attribute(node, name, default):
#         handler = node.handler()
#         Entity._create_native_attribute(node, name)
#         key = id(node._element[0])
#         setattr(handler, "__temporal_ref_element_" + name, node._element[0])
#         # print "KEY", key, id(handler), name,getattr(handler, "__native_" + name)
#         return getattr(handler, "__native_" + name).setdefault(key, default)
#     
#     @staticmethod
#     def set_attribute(node, name, value):
#         handler = node.handler()
#         Entity._create_native_attribute(node, name)
#         key = id(node._element[0])
#         getattr(handler, "__native_" + name)[key] = value
#     @staticmethod
#     def _create_native_attribute(node, name):
#         handler = node.handler()
#         value = getattr(handler, "__native_" + name, None)
#         if value is None:
#             setattr(handler, "__native_" + name, {})
        
class AttributeEntityValue(object):
    __metaclass__ = AutoInitObject
    value = None
    handler = None
    target = None
    
    def apply(self, attribute_owner):
        return self.handler.apply(self.target, attribute_owner)
    
    def __repr__(self):
        return repr(self.value)
    
    def __str__(self):
        return unicode(self.value)


class RootDocument(Entity):
    pass


# class AttributeEntity(object):  # (NativeObjectAttr):
class AttributeEntity(Entity):
    attribute_owner_applied = None
    
    def translate(self, node, unordered=False):
        # node.normalize()
        # print "##", node._element, node.text(), node.html(), ">>"
        # if "bold" in node.html(): raw_input("b")
        return self.value(node)
    
    def value(self, node):
        return node.text()
    
    def apply(self, attr, attribute_owner):
        return attribute_owner.translated_value()
    
    def was_applied(self, attribute_owner):
        attribute_owner.prepare_native_property("attribute_owner_applied", False)
        return attribute_owner.attribute_owner_applied
        # return Entity.get_attribute(attribute_owner, "attribute_owner_applied", False)
        # if self.attribute_owner_applied is None:
        #    self.attribute_owner_applied = {}
        # # V=getattr(self, "aaaaaaaaa", None)
        # key = id(attribute_owner._element[0])
        # # print "T", attribute_owner._element[0]==V, attribute_owner._element[0],V,"::::",
        # setattr(self, "__temporal_ref_element", attribute_owner._element[0])
        # # print attribute_owner._element[0], self.attribute_owner_applied.setdefault(key, False),attribute_owner._element
        # return self.attribute_owner_applied.setdefault(key, False)
        
    def set_applied(self, attribute_owner):
        attribute_owner.prepare_native_property("attribute_owner_applied", False)
        attribute_owner.attribute_owner_applied = True
        # return attribute_owner.attribute_owner_applied
        # return Entity.set_attribute(attribute_owner, "attribute_owner_applied", True)
        # if self.attribute_owner_applied is None:
        #    self.attribute_owner_applied = {}
        # # key = u"__applied" + type(self).__name__
        # key = id(attribute_owner._element[0]) 
        # self.attribute_owner_applied[key] = True
    


class OneShotAttribute(AttributeEntity):
    def apply(self, attr, attribute_owner):
        # self.apply_once(attr, attribute_owner)
        # return attribute_owner.translated_value()
        if not self.was_applied(attribute_owner):
            self.apply_once(attr, attribute_owner)
            self.set_applied(attribute_owner)
        return attribute_owner.translated_value()
        # return "\label{{{name}}}".format(name = self.value(attr)) + attribute_owner.translated_value()
    def apply_once(self, attr, attribute_owner):
        pass
    

class TextDocument(Entity):
    def translate(self, node, unordered=False):
        text = self.traverse_subnodes(node)
        if text == u"":
            text = node.text(raw=True)
            
        content = self.traverse_attributes(node, self.get_attributes(node), text)
        #if "return" in text: print content == text, node.text(raw=True) == text
        return content
        #return content if content == text and node.text(raw=True) == text else u"{{{0}}}".format(content)  


