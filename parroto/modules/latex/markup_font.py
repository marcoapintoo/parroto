#!/usr/bin/python
import os
import sys
import re

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

# from markup import  OneShotAttribute, AttributeEntity
from .primitives import Fonts, WordSpacing
from .base import SimpleSelectableAttribute, SimpleRestorableAttribute, SimpleContentAttribute
# from .base import LatexEntity as Entity

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

class FontLineAttribute(SimpleContentAttribute):
    def apply(self, attr, attribute_owner):
        valid_types = {
            "over-line": Fonts.LineOverline,
            "overline": Fonts.LineOverline,
            "overlined": Fonts.LineOverline,
            "under-line":Fonts.LineUnderline,
            "underline":Fonts.LineUnderline,
            "underlined":Fonts.LineUnderline,
            "mid-line": Fonts.LineMidline,
            "midline": Fonts.LineMidline,
            "midlined": Fonts.LineMidline,
        }
        return self.simple_apply(attr, attribute_owner, valid_types)


class TextRotateAttribute(SimpleContentAttribute):
    def apply(self, attr, attribute_owner):
        # value = attribute_owner.translated_value() or attr.handler().traverse_subnodes(attr) or attr.text() or ""
        # command = self.command(attribute_owner, Fonts.rotating_text(angle=value, text = value))
        attrtype = attr.handler().traverse_subnodes(attr) or attr.text() or ""
        valid_types = {
            "__default__": lambda v: Fonts.rotating_text(angle=attrtype, text=v),
        }
        return self.simple_apply(attr, attribute_owner, valid_types)

    
class WordSpacingAttribute(SimpleRestorableAttribute):
    def is_valid(self, attr, attribute_owner, value):
        value = value.strip().lower()
        return re.match(r"-?\d*(\.\d+)?\w+", value)
        
    def get_default_value(self, attr, attribute_owner):
        return "\\" + WordSpacing.default_expand_name
        
    def latex_command(self, value, othervalues):
        commands = ["%Word space {value}\n".format(value=value)]
        is_expand = not value.startswith("-")
        value = value[1:] if value.startswith("-") else value
        if len(othervalues) == 1:
            cmd = WordSpacing.text_space(None, create=True)
            commands.append(cmd)
        cmd = WordSpacing.text_space(proportion=value, expand=is_expand)
        commands.append(cmd)
        # print "@1", [cmd.content for cmd in commands]
        return commands
    
    def latex_restore_command(self, value, othervalues):
        commands = ["%Word space: from {value} to {last}\n".format(value=value, last=othervalues[-1])]
        cmd = WordSpacing.text_space(othervalues[-1])
        commands.append(cmd)
        # print "@2", [cmd.content for cmd in commands]
        return commands
        
    def apply(self, attr, attribute_owner):
        return self.simple_apply(attr, attribute_owner)
        from .base import Entity
        classname = type(self).__name__
        attribute_owner.prepare_native_property("__has_" + classname, False)
        has = getattr(attribute_owner, "__has_" + classname)
        if has: return ""
        setattr(attribute_owner, "__has_" + classname, True)
        print 111
        attribute_owner.before(Entity.create(name=classname + "_before", content=""))
        attribute_owner.after(Entity.create(name=classname + "_after", content=""))
        root = attribute_owner.root()
        root.prepare_native_property("initial_code", [])
        code = WordSpacing.prepare_dimensions()
        initial_code = root.initial_code
        if code not in initial_code:
            initial_code.append(code)
        print "  ", attr.handler().traverse_subnodes(attr) or attr.text() or ""
        return ""
        return self.simple_apply(attr, attribute_owner)
    
    

