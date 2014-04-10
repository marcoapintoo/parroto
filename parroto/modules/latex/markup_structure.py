#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from common import AutoInitObject
from markup import RootDocument
from .primitives import LatexRequire, LatexBase, DocumentStructure
from .base import LatexEntity as Entity

class Root(RootDocument):
    # packages = []
    def translate(self, node):
        # self.get_native_attribute(node, "packages_data", [])
        # content += LatexRequire.merge_packages_declaration(Root.packages)

        content = RootDocument.translate(self, node)
        
        # packages = Entity.get_attribute(node, "packages", [])
        node.prepare_native_property("packages", [])
        packages = node.packages
        content_packages = LatexRequire.merge_packages_declaration(packages) + "\n"
        # print content_packages
        
        infonode = node.find("document-information")[0]
        infocontent = infonode.handler().translate_node(infonode)
        content = infocontent + content_packages + content
        # print 10101010101, node._element[0]
        # print 1111111111, packages
        return content 
    

class DocumentInformation(Entity):
    def translate(self, node):
        return ""
    
    def translate_node(self, node):
        attributes = self.get_attributes(node)
        content = ""
        content += DocumentStructure.document_class(
            unicode(attributes.get("type", "")),
            params = self.split_argument(attributes, "type-params"))+"%\n"
        content += DocumentStructure.title(unicode(attributes.get("title", ""))) + "\n"
        content += DocumentStructure.author(unicode(attributes.get("author", ""))) + "\n"
        content += DocumentStructure.date(unicode(attributes.get("date", ""))) + "\n"
        return content  # self.traverse_subnodes(node)

    def split_argument(self, attributes, name, separator=";"):
        return self._split_unescape(unicode(attributes.get(name, "")), separator=";", escape="\\")

    def _split_unescape(self, s, separator=";", escape='\\', unescape=True):
        """
        >>> split_unescape('foo,bar', ',')
        ['foo', 'bar']
        >>> split_unescape('foo$,bar', ',', '$')
        ['foo,bar']
        >>> split_unescape('foo$$,bar', ',', '$', unescape=True)
        ['foo$', 'bar']
        >>> split_unescape('foo$$,bar', ',', '$', unescape=False)
        ['foo$$', 'bar']
        >>> split_unescape('foo$', ',', '$', unescape=True)
        ['foo$']
        """
        ret = []
        current = []
        itr = iter(s)
        for ch in itr:
            if ch == escape:
                try:
                    # skip the next character; it has been escaped!
                    if not unescape:
                        current.append(escape)
                    current.append(next(itr))
                except StopIteration:
                    if unescape:
                        current.append(escape)
            elif ch == separator:
                # split! (add current to the list and reset it)
                ret.append(''.join(current))
                current = []
            else:
                current.append(ch)
        ret.append(''.join(current))
        return ret

class DocumentStyle(Entity):
    def translate(self, node):
        attributes = self.get_attributes(node)
        targetname = unicode(attributes.get("apply-to", "document"))
        # print "TARGET", targetname, attributes
        target = node.root().find(targetname)  # or []
        for obj in target:
            for key, value in attributes.items():
                if key == "apply-to": continue
                obj.set_attribute(name=key, content=unicode(value))
                # print 1, key, value
        return "\n"

class HeadingDocument(Entity):
    __metaclass__ = AutoInitObject
    level = 0
    labels = {"document":-1, "part":0, "chapter":1, "section":2, "subsection":3, "subsubsection":4, "paragraph":4, "subparagraph":5}
    label = ""
    is_switch = True
    def translate(self, node):
        if self.label == "":
            self.label = [label for label, level in HeadingDocument.labels.items() if level == self.level][0]
        for child in node.nextAll():
            if not child.is_(self.label):
                child.appendTo(node)
            else:
                break
        attributes = self.get_attributes(node)
        subnode_content = self.traverse_subnodes(node)
        content = ""
        if self.is_switch:
            content = LatexBase.single_command(name=self.label, text=unicode(attributes.get("title", ""))) + "%\n"
            content += subnode_content
        else:
            content = LatexBase.environment_command(
                name=self.label,
                text=subnode_content
            )
        # node.set_translated_value(content)
        # for _, attr in attributes.items():
        #    newcontent = attr.apply(node)
        #    #node.set_translated_value(attr.apply(node))
        #    if content != newcontent:
        #        newcontent += "%\n"
        #        node.set_translated_value(newcontent)
        #        content = newcontent
        #    #content = node.translated_value()
        # return node.translated_value()
        return self.traverse_attributes(node, attributes, content)
