# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
from pyquery import PyQuery
from lxml import etree

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from parroto.base import AutoObject, NativeAttribute, is_a, is_str, neutral


class MetaElement(object):
    _element = None
    _native_key = lambda self, o: o._element[0]
    _value = NativeAttribute(name="_value", default="", key=_native_key)
    _normalized = False
    _modified = NativeAttribute(name="_modified", default=True, key=_native_key)
    _handler_cache = None
    controllers = None
    is_attribute = False
    _text_node_tag = u"text"
    __metaclass__ = AutoObject

    @staticmethod
    def create(content, *args, **kwargs):
        if is_a(content, PyQuery) and len(content) == 0:
            return None
        elif is_str(content) and content.strip() == u"":
            return None
        elif content is None:
            return None
        return MetaElement(content, *args, **kwargs)

    def __init__(self, content, *args, **kwargs):
        if is_a(content, PyQuery):
            element_content = content[0] if len(content) > 0 else unicode(content)
        elif is_a(content, MetaElement):
            element_content = content._element
            self._handler_cache = content._handler_cache
        elif is_a(content, etree._Element):
            element_content = content
        else:
            try:
                element_content = unicode(content)
            except UnicodeEncodeError:
                element_content = unicode(content.encode("utf-8"))
            except UnicodeDecodeError:
                element_content = unicode(content.decode("utf-8"))
        if "base" in kwargs and kwargs["base"]:
            base = kwargs["base"]
            self.controllers = base.controllers
            self._element = PyQuery(element_content, parent=base._element)
            del kwargs["base"]
        else:
            self._element = PyQuery(element_content)
        if "normalize" in kwargs and kwargs["normalize"]:
            self.normalize()
        attrs = ["id", "class"]
        for attr_name in attrs:
            attr = self.get_attribute(attr_name)
            if attr:
                self.attr(attr_name, attr.text())

    def __init_native_attribute(self, name, default):
        obj = getattr(type(self), name, neutral)
        if obj == neutral:
            setattr(type(self), name, NativeAttribute(name=name, default=default, key=MetaElement._native_key))

    def __setattr__(self, name, value):
        self.__init_native_attribute(name, None)
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        self.__init_native_attribute(name, None)
        return object.__getattribute__(self, name)

    def set_controllers(self, controllers):
        self.controllers = controllers

    @property
    def elements(self):
        return self._element

    @elements.setter
    def elements(self, value):
        if self._element is None:
            self._element = PyQuery()
        self._element.html(unicode(value))

    def translated_value(self):
        return self._value

    def set_translated_value(self, value):
        self._value = value

    def is_modified(self):
        # return Entity.get_attribute(self, "_is_modified", True)
        return self._modified

    def set_modified(self, modified=True, propagate=True):
        old_state = self._modified
        self._modified = modified
        if propagate and modified != old_state:
            parent = self.parent()
            if parent:
                parent.set_modified(modified=modified, propagate=True)

    @staticmethod
    def normalize_as_string(node, include_root=True):
        node = PyQuery(node)
        tagname = node[0].tag
        tree = u"<{0}>\n".format(tagname) if include_root else ""
        for attr_name, attr_value in node[0].attrib.iteritems():
            tree += u"<{tag}.{name}>{text}</{tag}.{name}>\n".format(
                text=attr_value,
                tag=tagname,
                name=attr_name)
        for element in node.contents():
            if isinstance(element, (str, unicode)):
                tree += u"<{tag}>{text}</{tag}>\n".format(
                    text=element,
                    tag=MetaElement._text_node_tag)
            else:
                tree += MetaElement.normalize_as_string(element)
        tree += ("</{0}>\n".format(tagname) if include_root else "")
        return tree

    def normalize(self, forced=False):
        if self._normalized and not forced:
            return
        self._normalized = True
        node = self._element
        tagname = node[0].tag
        if tagname == u"text" and (self.html().strip() == u"" or
                                       all(child.name() == u"text" for child in self.subnodes())):
            return
        tree = MetaElement.normalize_as_string(node, include_root=False)
        self._element.html(tree)

    def execute(self, order=1e100):
        handler_information = self.handler(get_info=True)
        handler = handler_information.handler
        if handler:
            if order >= handler_information.order and self.is_modified() or order is None:
                self.set_modified(False, propagate=False)
                self.set_translated_value(handler.translate(self, unordered=order is None))
        return self.translated_value()

    def name(self):
        basename = self.tag_name()
        if not self.is_attribute:
            return basename
        return basename[basename.index(".") + 1:]

    def element_name(self):
        basename = self.tag_name()
        if not self.is_attribute:
            return basename
        return basename[:basename.index(".")]

    def _raw_sub_nodes(self):
        result = []
        sub_nodes = self._element.children()
        for raw_child in sub_nodes:
            child = PyQuery(raw_child)
            child_name = self.get_tag_name(child)
            result.append((child, "." in child_name))
        return result

    def subnodes(self, ordered=False):
        if ordered:
            sub_nodes = self.subnodes(ordered=False)
            return sorted(sub_nodes, key=lambda c: c.handler(get_info=True).order)
        if self.is_attribute:
            return []
        return [MetaElement(child, base=self)
                for child, is_attr in self._raw_sub_nodes() if not is_attr]

    def attributes(self, ordered=False):
        if ordered:
            attributes = self.attributes(ordered=False)
            return sorted(attributes, key=lambda c: c.handler(get_info=True).order)
        if self.is_attribute:
            return []
        return [MetaElement(child, base=self, is_attribute=True)
                for child, is_attr in self._raw_sub_nodes() if is_attr]

    def get_attribute(self, name, default=None):
        children = self.children(u"{name}\\.{attr}".format(name=self.name(), attr=name))
        if children and len(children) > 0:
            return MetaElement(children[0], base=self, is_attribute=True)
        return default

    def has_attribute(self, name):
        return self.get_attribute(name) is None

    def set_attribute(self, name, content):
        attr = self.get_attribute(name)
        if attr:
            attr.html(content)
            return
        attr_value = u"<{tag}.{attr}>{value}</{tag}.{attr}>".format(
            tag=self.tag_name(),
            attr=name,
            value=content)
        self.prepend(attr_value)

    def handler(self, get_info=False, forced=False):
        if self._handler_cache and not forced:
            return self._handler_cache.handler if not get_info else self._handler_cache
        if self.is_attribute:
            self._handler_cache = self._handler_attributes()
        else:
            self._handler_cache = self._handler_entities()
        return self._handler_cache.handler if not get_info else self._handler_cache

    def _handler_entities(self):
        for execute_handler in self.controllers.get_entity(self.name()):
            return execute_handler
        return self.controllers.get_default_handler()

    def _handler_attributes(self):
        for execute_handler in self.controllers.get_attribute(self.name()):
            return execute_handler
        return self.controllers.get_default_attribute()

    def children(self, selector=None):
        children = self._element.children(selector=selector)
        if children:
            return [MetaElement(o, base=self) for o in children]
        return []

    def extend(self, other):
        return self._element.extend(other)

    def items(self, selector=None):
        return self._element.items(selector)

    def remove_namespaces(self):
        return self._element.remove_namespaces()

    def root(self):
        pseudo_parent = self.parent()
        parent = None
        while pseudo_parent is not None:
            parent = pseudo_parent
            pseudo_parent = pseudo_parent.parent()
        return parent
        # return MetaElement.create(self._element.root, base=self)

    def encoding(self):
        return self._element.encoding()

    def parent(self, selector=None):
        return MetaElement.create(self._element.parent(selector), base=self)

    def prev(self, selector=None):
        return MetaElement.create(self._element.prev(selector), base=self)

    def next(self, selector=None):
        return MetaElement.create(self._element.next(selector), base=self)

    def nextAll(self, selector=None, ordered=False):
        source = [MetaElement.create(o, base=self) for o in self._element.nextAll(selector)]
        if ordered:
            source = sorted(source, key=lambda q: q.handler(get_info=True).order)
        return source
        # for ele in source:
        # yield MetaElement(ele, base=self)

    def prevAll(self, selector=None):
        return [MetaElement(o, base=self) for o in self._element.prevAll(selector)]

    def siblings(self, selector=None):
        return self._element.siblings(selector)

    def parents(self, selector=None):
        return [MetaElement(o, base=self) for o in self._element.parents(selector)]

    def closest(self, selector=None):
        return [MetaElement(o, base=self) for o in self._element.closest(selector)]

    def contents(self):
        return self._element.contents()

    def filter(self, selector):
        return [MetaElement(o, base=self) for o in self._element.filter(selector)]

    def not_(self, selector):
        return self._element.not_(selector)

    def is_(self, selector):
        return self._element.is_(selector)

    def find(self, selector):
        return [MetaElement(o, base=self) for o in self._element.find(selector)]

    def eq(self, index):
        return self._element.eq(index)

    # def each(self, func):
    # return self._element.each(func)
    def map(self, func):
        return self._element.map(func)

    def length(self):
        return self._element.length()

    def size(self):
        return self._element.size()

    def end(self):
        return self._element.end()

    def attr(self, *args, **kwargs):
        return self._element.attr(*args, **kwargs)

    def removeAttr(self, name):
        return self._element.removeAttr(name)

    def height(self, value=None):
        return self._element.height(value) if value else self._element.height()

    def width(self, value=None):
        return self._element.width(value) if value else self._element.width()

    def val(self, value=None):
        return self._element.val(value) if value else self._element.val()

    def html(self, value=None, **kwargs):
        return self._element.html(value, **kwargs) if value else self._element.html()

    def outerHtml(self):
        return self._element.outerHtml()

    def text(self, value=None, raw=False):
        return self._element.text(value) if value else (self.raw_text() if raw else self._element.text())

    def append(self, value):
        self.set_modified()
        return self._element.append(value)

    def appendTo(self, value):
        self.set_modified()
        value.set_modified()
        return self._element.appendTo(value)

    def prepend(self, value):
        self.set_modified()
        return self._element.prepend(value)

    def prependTo(self, value):
        value.set_modified()
        self.set_modified()
        return self._element.prependTo(value)

    def after(self, value):
        self.set_modified()
        return self._element.after(value)

    def insertAfter(self, value):
        self.set_modified()
        return self._element.insertAfter(value)

    def before(self, value):
        self.set_modified()
        return self._element.before(value)
        self.set_modified()

    def insertBefore(self, value):
        return self._element.insertBefore(value)

    def wrap(self, value):
        self.set_modified()
        return self._element.wrap(value)

    def wrapAll(self, value):
        self.set_modified()
        return self._element.wrapAll(value)

    def replaceWith(self, value):
        self.set_modified()
        return self._element.replaceWith(value)

    def replaceAll(self, expr):
        self.set_modified()
        return self._element.replaceAll(expr)

    def empty(self):
        return self._element.empty()

    def remove(self, expr=None):
        self.set_modified()
        return self._element.remove(expr) if expr else self._element.remove()

    def base_url(self):
        return self._element.base_url()

    def make_links_absolute(self, base_url=None):
        return self._element.make_links_absolute(base_url)

    @staticmethod
    def get_tag_name(query_element):
        return query_element[0].tag if len(query_element) > 0 else ""

    def tag_name(self):
        return self._element[0].tag if len(self._element) > 0 else ""

    def raw_text(self):
        if not self._element:
            return ''
        text = []

        def add_text(tag, no_tail=False):
            if tag.text and not isinstance(tag, etree._Comment):
                text.append(tag.text)
            for child in tag.getchildren():
                add_text(child)
            if not no_tail and tag.tail:
                text.append(tag.tail)

        for tag_element in (self._element[0] if len(self._element) else []):
            add_text(tag_element, no_tail=True)
        return ' '.join([t for t in text if t])


if __name__ == "__main__":
    element = MetaElement("abc<tag>abc</tag>def", normalize=True)
    print element
    print element.elements
    # element.find("tag")[0].othervalue = 12
    print element.tag_name(), element.raw_text(), element.text()
