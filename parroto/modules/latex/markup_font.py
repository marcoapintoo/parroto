#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

#from markup import  OneShotAttribute, AttributeEntity
from .primitives import Fonts
from .base import SimpleSelectableAttribute
#from .base import LatexEntity as Entity

class FontWeightAttribute(SimpleSelectableAttribute):
    def apply(self, attr, attribute_owner):
        valid_types = {
            "bold": Fonts.WeightBold(),
            "normal":Fonts.WeightRegular(),
            "regular":Fonts.WeightRegular(),
        }
        return self.simple_apply(attr, attribute_owner, valid_types)

    
class FontStyleAttribute(SimpleSelectableAttribute):
    def apply(self, attr, attribute_owner):
        valid_types = {
            "italics": Fonts.StyleItalics(),
            "normal":Fonts.StyleNormal(),
            "regular":Fonts.StyleNormal(),
            "oblique":Fonts.StyleOblique(),
            "slanted":Fonts.StyleSlanted(),
        }
        return self.simple_apply(attr, attribute_owner, valid_types)
    

class FontVariantAttribute(SimpleSelectableAttribute):
    def apply(self, attr, attribute_owner):
        valid_types = {
            "normal": Fonts.VariantNormal(),
            "regular": Fonts.VariantNormal(),
            "smallcaps":Fonts.VariantSmallCaps(),
            "small-caps":Fonts.VariantSmallCaps(),
            "small_caps":Fonts.VariantSmallCaps(),
        }
        return self.simple_apply(attr, attribute_owner, valid_types)
    

class FontLineAttribute(SimpleSelectableAttribute):
    def apply(self, attr, attribute_owner):
        valid_types = {
            "over-line": Fonts.LineOverline(),
            "overline": Fonts.LineOverline(),
            "overlined": Fonts.LineOverline(),
            "under-line":Fonts.LineUnderline(),
            "underline":Fonts.LineUnderline(),
            "underlined":Fonts.LineUnderline(),
            "mid-line": Fonts.LineMidline(),
            "midline": Fonts.LineMidline(),
            "midlined": Fonts.LineMidline(),
        }
        return self.simple_apply(attr, attribute_owner, valid_types)
    
