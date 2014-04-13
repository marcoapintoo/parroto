#!/usr/bin/python
import os
import sys
from lxml import etree

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from markup import HandlerModule, AttributeEntity
from .base import LatexEntity as Entity, TextDocument
from .markup_references import Label, LabelAttribute, Reference
from .markup_alignment import AlignmentAttribute
from .markup_structure import Root, DocumentInformation, DocumentStyle, HeadingDocument
from .markup_font import FontWeightAttribute, FontStyleAttribute, FontVariantAttribute, FontLineAttribute, WordSpacingAttribute, TextRotateAttribute
from .markup_paragraph import LineHeightAttribute
from .markup_color import TextColorAttribute
from .markup_macros import Define

class LatexModule(HandlerModule):
    def __init__(self):
        HandlerModule.__init__(self)
        self.set_default_handler(Entity())
        self.set_default_attribute(AttributeEntity())
        self.add_attribute("label", LabelAttribute(), order=7)
        self.add_attribute("alignment", AlignmentAttribute(), order=1)
        self.add_attribute("align", AlignmentAttribute(), order=1)
        
        
        self.add_handler("define", Define(self), order=0)
        
        self.add_handler("root", Root(), order=1e100)
        self.add_handler("file-document", Root(), order=1e100)
        self.add_handler("document-file", Root(), order=1e100)
        
        self.add_handler("text", TextDocument(), order=0)
        
        self.add_attribute("text-color", TextColorAttribute(), order=0)
        self.add_attribute("text-rotating", TextRotateAttribute(), order=20990)
        self.add_attribute("text-rotate", TextRotateAttribute(), order=20990)
        self.add_attribute("text-rotates", TextRotateAttribute(), order=20990)
        self.add_attribute("word-spacing", WordSpacingAttribute(self), order=20990)
        self.add_attribute("line-height", LineHeightAttribute(), order=0)
        self.add_attribute("paragraph-height", LineHeightAttribute(), order=0)
        self.add_attribute("text-line", FontLineAttribute(), order=0)
        self.add_attribute("font-line", FontLineAttribute(), order=0)
        self.add_attribute("font-weight", FontWeightAttribute(), order=0)
        self.add_attribute("font-variant", FontVariantAttribute(), order=0)
        self.add_attribute("font-style", FontStyleAttribute(), order=0)
        
        self.add_handler("label", Label(), order=0)
        self.add_handler("ref", Reference(), order=0)
        self.add_handler("reference", Reference(), order=0)
        
        self.add_handler("document-information", DocumentInformation(), order=100) 
        self.add_handler("style", DocumentStyle(), order=1000)
        
        self.add_handler("document", HeadingDocument(level=-1, is_switch=False), order=1)
        self.add_handler("part", HeadingDocument(level=0), order=1)
        self.add_handler("chapter", HeadingDocument(level=1), order=2)
        self.add_handler("section", HeadingDocument(level=2), order=3)
        self.add_handler("subsection", HeadingDocument(level=3), order=4)
        self.add_handler("subsubsection", HeadingDocument(level=4), order=5)
        self.add_handler("paragraph", HeadingDocument(level=5), order=6)
        self.add_handler("subparagraph", HeadingDocument(level=6), order=7)

