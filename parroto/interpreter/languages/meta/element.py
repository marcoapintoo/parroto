# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
from lxml import etree

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from parroto.base import multimethod, ThisClass


class Element(object):
    __attributes = None
    __children = None
    __xml = None
    __xml_string = None
    __name = ""
    __changed = False
    value = ""
    parent = None


    def __init__(self, name="", value="", parent=None):
        self.__attributes = {}
        self.__children = ElementChildren(self)
        self.name = name
        self.value = value
        self.parent = parent

    def notify_change(self):
        self.__changed = True

    def __contains__(self, item):
        return item in self.__attributes or item in self.__children

    @multimethod()
    def __getitem__(self, item):
        raise Exception("{} is not a valid item.".format(item))

    @multimethod(item=int)
    def __getitem__(self, item):
        return self.__children[item]

    @multimethod(item=str, when="item in self.attributes")
    def __getitem__(self, item):
        return self.__attributes[item]

    @multimethod()
    def __setitem__(self, item, value):
        raise Exception("{} is not a valid item.".format(item))

    @multimethod(item=int)
    def __setitem__(self, item, value):
        self.__children[item] = value

    @multimethod(item=str, when="'.' in item")
    def __setitem__(self, item, value):
        print "{} is not a valid attribute. It was ignored.".format(item)
        self.__children.append(Element(name=item, value=value))

    @multimethod(item=str)
    def __setitem__(self, item, value):
        self.__attributes[item] = Element(name="text", value=unicode(value))
        self.notify_change()

    @multimethod(item=str, value=ThisClass)
    def __setitem__(self, item, value):
        self.__attributes[item.strip()] = value
        self.notify_change()

    @property
    def children(self):
        return self.__children

    @property
    def attributes(self):
        return self.__attributes

    def copy_children(self, other):
        for child in other.children:
            self.children.append(child)

    def __xml_representation(self):
        root = etree.Element(self.name)
        document = etree.ElementTree(root)
        for attribute_name, value in self.attributes.items():
            attribute_document = etree.SubElement(root, "{}.{}".format(self.name, attribute_name))
            attribute_document.append(value.xml)
        for child in self.children:
            child_document = child.xml
            root.append(child_document)
        if self.value:
            if self.name != "text":
                value = etree.SubElement(root, "text")
                value.text = self.value
            else:
                root.text = self.value
        return root

    def __str__(self):
        return u"[{}]".format(self.name)

    def __unicode__(self):
        return u"[{}]".format(self.name)

    @property
    def xml_string(self):
        if not self.__xml_string or self.__changed:
            self.__xml_string = unicode(etree.tostring(self.xml, pretty_print=True))
        return self.__xml_string

    @property
    def xml(self):
        if self.__xml is None or self.__changed:
            self.__xml = self.__xml_representation()
        return self.__xml

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value
        self.notify_change()


class ElementChildren(list):
    parent = None

    def __init__(self, parent=None, *args, **kwargs):
        self.parent = parent
        super(ElementChildren, self).__init__(*args, **kwargs)

    @multimethod()
    def append(self, element):
        raise Exception("{} is not a valid.".format(element))

    @multimethod(element=str)
    def append(self, element):
        self.parent.notify_change()
        return self.append(Element(name="text", value=element))

    @multimethod(element=Element)
    def append(self, element):
        self.parent.notify_change()
        element.parent = self.parent
        sub_names = element.name.split(".")
        if len(sub_names) == 1:
            return super(ElementChildren, self).append(element)
        elif len(sub_names) > 2:
            print "{name} is not a valid attribute. It is not matching <node>.<attribute> format. It was ignored.".format(
                name=element.name)
            return
        parent_name = sub_names[-2]
        parent = self.parent
        while parent.name != parent_name:
            parent = parent.parent
            if not parent:
                print "{name} is not a valid attribute. There is no parent. It was ignored.".format(name=element.name)
                return
        children = element.children
        if len(children) == 0:
            child = ""
        elif len(children) == 1:
            child = children
        else:
            child = Element("text")
            child.copy_children(element)
        parent[sub_names[-1]] = child


if __name__ == "__main__":
    element = Element()
    element.name = "node_main"
    element["attributes"] = 12
    element["a"] = -1
    subnode2 = Element(name="subnode2")
    element.children.append(Element(name="subnode"))
    element.children.append("text")
    element.children.append(subnode2)
    subnode2["node_main.other"] = "this"
    element.children.append(Element(name="node_main.b"))
    print element[0]
    print element["a"]
    # print element.children
    # print element.attributes
    print element
    print element.xml_string
    # print etree.tostring(element.representation(), pretty_print=True)