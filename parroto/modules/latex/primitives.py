#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

from common import AutoInitObject, accepts, returns

# LATEX SYNTAX

class LatexBase(object):
    def __init__(self, require=[], content=""):
        self.content = content
        if not isinstance(require, (list, tuple)):
            require = [require]
        self.require = require

    @staticmethod
    @returns(str)
    @accepts(params=(list, tuple, set), named_params=dict)
    def format_command_params(params, named_params):
        params = ",".join(params + LatexBase.named_params_to_array(named_params))
        return "[%s]" % params if params else ""
    
    @staticmethod
    @returns(str)
    @accepts(params=(list, tuple, set))
    def format_params(params):
        return ",".join(params)

    @staticmethod
    @returns(list)
    @accepts(params=dict)
    def named_params_to_array(params):
        return ["{k}={v}".format(k=key, v=params[key]) for key in params]

    @staticmethod    
    @returns(str)
    @accepts(params=dict)
    def format_named_params(params):
        return LatexBase.named_params(LatexBase.named_params_to_array(params))

    @staticmethod
    @returns(str)
    @accepts(text=(tuple, list, set, str, None))
    def format_text_params(text):
        if isinstance(text, (tuple, list, set)):
            text = "".join(("{%s}" % t) for t in text)
        else:
            text = ("{%s}" % text) if text is not None else ""
        return text

    @staticmethod
    @returns(str)
    @accepts(name=str, text=(str, tuple, list, set, None), params=(list, tuple, set, None), named_params=(dict, None))
    def single_command(name, text=None, params=[], named_params={}):
        return r"\{name}{param}{text}".format(name=name, param=LatexBase.format_command_params(params, named_params), text=LatexBase.format_text_params(text))
    
    @staticmethod
    @returns(str)
    def empty_text_argument():
        return r"{}"
        
    @staticmethod
    @returns(str)
    def start_text_argument():
        return r"{"
    
    @staticmethod
    @returns(str)
    def close_text_argument():
        return r"}"
    
    @staticmethod
    @returns(str)
    @accepts(params=(list, tuple, set, None), named_params=(dict, None))
    def environment_command(name, text=None, text_params=None, params=[], named_params={}):
        return LatexBase.begin_environment(name, text_params, params, named_params) + text + LatexBase.end_environment(name)

    @staticmethod
    @returns(str)
    @accepts(name=str, text_param=(str, tuple, list, set, None), params=(list, tuple, set, None), named_params=(dict, None))
    def begin_environment(name, text_param=None, params=[], named_params={}):
        return r"\begin{param}{{{name}}}{text}".format(name=name, param=LatexBase.format_command_params(params, named_params), text=LatexBase.format_text_params(text_param)) + "%\n"

    @staticmethod
    @returns(str)
    @accepts(name=str)
    def end_environment(name):
        return "%\n" + r"\end{{{name}}}".format(name=name)


class Dash(object):
    @staticmethod
    @returns(str)
    def hyphen_dash():
        return "-"  # inter-word

    @staticmethod
    @returns(str)
    def en_dash():
        return "--"  # page range

    @staticmethod
    @returns(str)
    def em_dash():
        return "---"  # punctuation dash -- like this

class Counters(object):
    @staticmethod
    @returns(str)
    @accepts(counter=str, value=str)
    def change_counter_value(counter, value):
        return LatexBase.single_command("setcounter", text=[counter, value])

    @staticmethod
    @returns(str)
    @accepts(counter=str, value=str)
    def change_length_value(counter, value):
        return LatexBase.single_command("setlength", text=[counter, value])
        

class Dimensions(object):
    @staticmethod
    @returns(str)
    @accepts(name=str)
    def create_dimension(name):
        return LatexBase.single_command("newdimen") + LatexBase.single_command(name)

    @staticmethod
    @returns(str)
    @accepts(counter=str, value=str)
    def change_dimension_value(counter, value):
        return "{name}={value}".format(
            name=LatexBase.single_command(counter),
            value=value)
            
    
class Quotes(object):
    quotes_start = ("`", "``", "``", ",,", "<<")
    quotes_end = ("'", "''", '"', "''", ">>")
    
    @staticmethod
    @returns(str)
    @accepts(text=str, quote_type=int)
    def quote_mark(text, quote_type=1):
        return Quotes.quotes_start[quote_type] + text + LatexBase.quotes_end[quote_type]
    
    @staticmethod
    @returns(LatexBase)
    @accepts(text=str)
    def short(text):
        return LatexBase(
            content=LatexBase.environment_command("quote", text=text)
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(text=str)
    def long(text):
        return LatexBase(
            content=LatexBase.environment_command("quotation", text=text)
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(text=str)
    def verse(text):
        return LatexBase(
            content=LatexBase.environment_command("verse", text=text)
        )

class Fonts(object):
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def WeightBold():
        return LatexBase(
            content=LatexBase.single_command("bfseries", text=""),
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def WeightRegular():
        return LatexBase(
            content=LatexBase.single_command("mdseries", text=""),
        )
    
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def StyleSlanted():
        return LatexBase(
            content=LatexBase.single_command("slshape", text=""),
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def StyleOblique():
        return Fonts.StyleSlanted()
        
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def StyleItalics():
        return LatexBase(
            content=LatexBase.single_command("itshape", text=""),
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def StyleNormal():
        return LatexBase(
            content=LatexBase.single_command("upshape", text=""),
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def VariantSmallCaps():
        return LatexBase(
            content=LatexBase.single_command("scshape", text=""),
            require=LatexRequire(
                name="smallcap"
            )
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def VariantNormal():
        return LatexBase(
            content=LatexBase.single_command("upshape", text=""),
        )
    
    @staticmethod
    @returns(LatexBase)
    @accepts(text=str)
    def LineUnderline(text):
        return LatexBase(
            content=LatexBase.single_command("Underline", text=text),
            require=LatexRequire(
                name="umoline",
            )
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(text=str)
    def LineMidline(text):
        return LatexBase(
            content=LatexBase.single_command("Midline", text=text),
            require=LatexRequire(
                name="umoline",
            )
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(text=str)
    def LineOverline(text):
        return LatexBase(
            content=LatexBase.single_command("Overline", text=text),
            require=LatexRequire(
                name="umoline",
            )
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(color=str)
    def LineAnyline(height, text):
        return LatexBase(
            content=LatexBase.single_command("UMOline", text=[height, text]),
            require=LatexRequire(
                name="umoline",
            )
        )
            
    @staticmethod
    @returns(LatexBase)
    @accepts(angle=str, text=str)
    def rotating_text(angle, text):
        return LatexBase(
            content=LatexBase.single_command("rotatebox", text=[angle, text], named_params={"origin": "c"}),
            # content=LatexBase.environment_command("rotate", text=text, text_params=[angle]),
            require=LatexRequire(
                name="rotating",
            )
        )
        
        
class TextColor(object):    
    @staticmethod
    @returns(LatexBase)
    @accepts()
    def textcolor_unnamed(colortype, color, text):
        return LatexBase(
            content=LatexBase.single_command("textcolor", text=[color, text], params=[colortype]),
            require=LatexRequire(
                name="xcolor",
                arguments=["usenames", "dvipsnames", "svgnames", "table", "x11names"]
            )
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts()
    def color_unnamed(colortype, color):
        return LatexBase(
            content=LatexBase.single_command("color", text=[color], params=[colortype]),
            require=LatexRequire(
                name="xcolor",
                arguments=["usenames", "dvipsnames", "svgnames", "table", "x11names"]
            )
        )

class DocumentStructure(object):    
    @staticmethod
    @returns(str)
    @accepts(name=str, params=(list, tuple, set, None), named_params=(dict, None))
    def use_package(name, params=[], named_params={}):
        return LatexBase.single_command("usepackage", text=name, params=params, named_params=named_params)

    @staticmethod
    @returns(str)
    @accepts(doctype=str, params=(list, tuple, set, None), named_params=(dict, None))
    def document_class(doctype, params=[], named_params={}):
        return LatexBase.single_command("documentclass", text=doctype, params=params, named_params=named_params)
    
    @staticmethod
    @returns(str)
    @accepts(author=str, params=(list, tuple, set, None), named_params=(dict, None))
    def author(author, params=[], named_params={}):
        return LatexBase.single_command("author", text=author, params=params, named_params=named_params)
        
    @staticmethod
    @returns(str)
    @accepts(title=str, params=(list, tuple, set, None), named_params=(dict, None))
    def title(title, params=[], named_params={}):
        return LatexBase.single_command("title", text=title, params=params, named_params=named_params)
        
    @staticmethod
    @returns(str)
    @accepts(date=str, params=(list, tuple, set, None), named_params=(dict, None))
    def date(date, params=[], named_params={}):
        return LatexBase.single_command("date", text=date, params=params, named_params=named_params)

    @staticmethod    
    @returns(str)
    @accepts(text_param=str, params=(list, tuple, set, None), named_params=(dict, None))
    def begin_document(text_param="", params=[], named_params={}):
        return LatexBase.begin_environment("document", params=params, named_params=named_params, text_param=text_param)
        
    @staticmethod
    @returns(str)
    def end_document():
        return LatexBase.end_environment("document")

    @staticmethod
    @returns(str)
    def make_title():
        return LatexBase.single_command("maketitle")

    @staticmethod
    @returns(str)
    @accepts(zone=str, title=str, numbered=bool, short_title=str, params=(list, tuple, set, None), named_params=(dict, None))
    def text_region_definition(zone, title, numbered=True, short_title="", params=[], named_params={}):
        if short_title: params.insert(0, short_title)
        if numbered:
            cmd = LatexBase.single_command(zone, title, params, named_params)
        else:
            cmd = LatexBase.single_command(zone + "*", title, params, named_params)
            cmd = LatexBase.single_command("phantomsection")
            cmd += TableOfContents.AddToTOC(zone, short_title if short_title else title)
        return cmd


class LatexRequire(object):
    __metaclass__ = AutoInitObject
    name = ""
    arguments = []
    named_arguments = {}
    
    @returns(str)
    def use_package(self):
        return DocumentStructure.use_package(name=self.name, params=self.arguments, named_params=self.named_arguments)
    
    def command_params(self):
        return LatexBase.format_command_params(self.arguments, self.named_arguments)
    
    @staticmethod
    @returns(str)
    @accepts(list_packages=list)
    def merge_packages_declaration(list_packages):
        return "\n".join(package.use_package() for package in LatexRequire.merge_packages(list_packages))
        
    @staticmethod
    @returns(list)
    @accepts(list_packages=list)
    def merge_packages(list_packages):
        def review_all_packages(lst):
            for ele in lst:
                if isinstance(ele, (list, tuple, set)):
                    for i in review_all_packages(ele): yield i
                else:
                    yield ele
        def merge_in_pool(pkg, listpkg):
            if pkg.name in listpkg:
                otherpkg = listpkg[pkg.name]
                arguments = list(set(pkg.arguments + otherpkg.arguments))
                named_arguments = otherpkg.named_arguments.copy()
                for key, value in pkg.named_arguments.viewvalues():
                    named_arguments[key] = value
            else:
                arguments = pkg.arguments
                named_arguments = pkg.named_arguments.copy()
            listpkg[pkg.name] = LatexRequire(
                name=pkg.name,
                arguments=arguments,
                named_arguments=named_arguments
            )    
        packages = {}
        for package in review_all_packages(list_packages):
            merge_in_pool(package, packages)
        return packages.values()
    

class TableOfContents(object):
    @staticmethod    
    @returns(LatexBase)
    @accepts(level=str, title=str)
    def AddToTOC(level, title):
        return LatexBase.single_command("addcontentsline", text=["toc", level, title])
    
    @staticmethod
    @returns(LatexBase)
    @accepts(level=str)
    def SectionNumberingDepth(level):
        return LatexBase(
            content=LatexBase.change_counter_value("secnumdepth", level)
        )


@returns(LatexBase)
@accepts(color=str)
def ColorDeclaration(color):
    return LatexBase(
        content=LatexBase.single_command("color", text=color),
        require=LatexRequire(
            name="xcolor",
            arguments=["usenames", "dvipsnames", "svgnames", "table", "x11names"]
        )
    )
    
    
class Equation(object):
    __metaclass__ = AutoInitObject
    use_dollar_sign = True
    numbered = True
    type = "inline"
    
    @returns(str)
    def command(self):
        return Equation.select_command(self.numbered, self.type)
    
    @returns(str)
    def start_command(self):
        cmd = self.command()
        if self.use_dollar_sign and cmd == "math": return "$"
        if cmd == "*subequations":
            return LatexBase.begin_environment("subequations") + "\n" + LatexBase.begin_environment("align") + "\n"
        elif cmd == "*subequations*":
            return LatexBase.begin_environment("subequations") + "\n" + LatexBase.begin_environment("align*") + "\n"
        return LatexBase.begin_environment(cmd) + "\n"
        
    @returns(str)
    def end_command(self):
        cmd = self.command()
        if self.use_dollar_sign and cmd == "math": return "$"
        if cmd == "*subequations":
            return LatexBase.end_environment("align") + "\n" + LatexBase.end_environment("subequations") + "\n"
        elif cmd == "*subequations*":
            return LatexBase.end_environment("align*") + "\n" + LatexBase.end_environment("subequations") + "\n"
        return "\n" + LatexBase.end_environment(cmd)
    
    @staticmethod
    @returns(str)
    @accepts(numbered=bool, equation_type=str)
    def select_command(numbered, equation_type):
        equation_type = equation_type.strip().lower()
        if equation_type in ("inline", ""):
            command = "math"
        elif equation_type in ("displayed", "display"):
            command = "equation"
        elif equation_type in ("multiline", "align"):
            command = "align"
        elif equation_type in ("subequations", "subequation"):
            command = "*subequations"
        else:
            print "ERROR", "not a equation type:", equation_type
        return (command + "*") if not numbered and command != "math" else command
    
    @returns(LatexBase)
    def start_declaration(self):
        return LatexBase(
            content=self.start_command(),
            require=LatexRequire(name="mathtools") 
        )
        
    @returns(LatexBase)
    def close_declaration(self):
        return LatexBase(
            content=self.end_command(),
            require=LatexRequire(name="mathtools")
        )


#########################################################################
class References(object):
    @staticmethod
    @returns(LatexBase)
    @accepts(name=str)
    def define_label(name):
        return LatexBase(
            content=LatexBase.single_command("label", text=name),
            # require=LatexRequire(name="mathtoolsxxx")
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(link=str)
    def reference_to(link):
        return LatexBase(
            content=LatexBase.single_command("ref", text=link)
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(link=str)
    def equation_reference_to(link):
        return LatexBase(
            content=LatexBase.single_command("eqref", text=link)
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(link=str)
    def page_reference_to(link):
        return LatexBase(
            content=LatexBase.single_command("pageref", text=link)
        )
#########################################################################


class Alignment(object):
    @staticmethod
    @returns(LatexBase)
    def left_ragged():
        return LatexBase(
            content=LatexBase.single_command("raggedleft")
        )

    @staticmethod            
    @returns(LatexBase)
    def right_ragged():
        return LatexBase(
            content=LatexBase.single_command("raggedright")
        )
        
    @staticmethod
    @returns(LatexBase)
    def justified():
        return LatexBase(
            content=LatexBase.single_command("justifying"),
            require=LatexRequire(
                name="ragged2e"
             )   
        )
        
    @staticmethod    
    @returns(LatexBase)
    def center():
        return LatexBase(
            content=LatexBase.single_command("centering")
        )
#########################################################################



class TextSpace(object):
    @staticmethod
    @returns(LatexBase)
    def no_break_space(self):
        return LatexBase(
            content="~"
        )

    @staticmethod
    @returns(LatexBase)
    def horizontal_fill_space(self):
        return LatexBase(
            content=LatexBase.single_command("hfill")
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(size=str)
    def horizontal_space(self, size):
        return LatexBase(
            content=LatexBase.single_command("hspace", text=size)
        )

    @staticmethod
    @returns(LatexBase)
    def vertical_fill_space(self):
        return LatexBase(
            content=LatexBase.single_command("hfill")
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(size=str)
    def vertical_space(self, size):
        return LatexBase(
            content=LatexBase.single_command("vspace", text=size)
        )

    @staticmethod
    @returns(LatexBase)
    def clear_page(self):
        return LatexBase(
            content=LatexBase.single_command("clearpage")
        )
            

# http://en.wikibooks.org/wiki/LaTeX/Document_Structure
# http://en.wikibooks.org/wiki/LaTeX/Text_Formatting


    

@returns(str)
@accepts(text=str)
def TextWithLargeWords(text):
    return LatexBase(
        content=LatexBase.environment_command("sloppypar", text=text)
    )

@returns(str)
@accepts(text=str)
def SuperScriptText(text):
    return LatexBase(
        content=LatexBase.single_command("textsuperscript", text=text)
    )

@returns(str)
@accepts(text=str)
def SubScriptText(text):
    return LatexBase(
        content=LatexBase.single_command("textsubscript", text=text),
        require=LatexRequire(
            name="mhchem"
        )
    )

@returns(str)
@accepts(formula=str)
def ChemicalFormula(formula):
    return LatexBase(
        content=LatexBase.single_command("ce", text=formula),
        require=LatexRequire(
            name="fixltx2e",
            named_arguments={"version": "3"}
        )
    )


    
# http://en.wikibooks.org/wiki/LaTeX/Paragraph_Formatting

class Paragraph(object):
    @staticmethod
    @returns(LatexBase)
    @accepts(size=str)
    def paragraph_indent(size):
        return LatexBase(
            content=LatexBase.change_length_value("parindent", size)
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(proportion=str)
    def line_spacing(proportion):
        return LatexBase(
            content=LatexBase.single_command("setstretch", text=proportion),
            require=LatexRequire(
                name="setspace"
            )
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(size=str)
    def paragraph_skip(size):
        return LatexBase(
            content=LatexBase.change_length_value("parskip", size),
            require=LatexRequire(
                name="parskip",
            )
        )

    @staticmethod
    @returns(LatexBase)
    def use_indentation():
        return LatexBase(
            content=LatexBase.single_command("indent")
        )

    @staticmethod
    @returns(LatexBase)
    def dont_use_indentation():
        return LatexBase(
            content=LatexBase.single_command("noindent")
        )
    
@returns(LatexBase)
@accepts(size=str, allow_page_break=bool)
def new_line(size, allow_page_break=True):
    return LatexBase(
        content=TextSpace.HorizontalSpace("0pt") + "\\" + ("" if allow_page_break else "*") + LatexBase.format_command_params([size], {})
    )

class WordSpacing(object):
    default_stretch_name = "originwordstretch"
    default_expand_name = "originwordspace"
    @staticmethod
    @returns(str)
    @accepts()
    def prepare_dimensions():
        result = WordSpacing.create_dimensions()
        result += "%\n"
        result += WordSpacing.base_dimensions()
        result += "%\n" 
        return result
    
    @staticmethod
    @returns(str)
    @accepts()
    def base_dimensions():
        result = Dimensions.change_dimension_value(WordSpacing.default_stretch_name, LatexBase.single_command("fontdimen2") + LatexBase.single_command("font"))
        result += "%\n"
        result += Dimensions.change_dimension_value(WordSpacing.default_expand_name, LatexBase.single_command("fontdimen2") + LatexBase.single_command("font"))
        return result
    
    @staticmethod
    @returns(str)
    @accepts()
    def create_dimensions():
        result = Dimensions.create_dimension(WordSpacing.default_stretch_name)
        result += "%\n"
        result += Dimensions.create_dimension(WordSpacing.default_expand_name)
        return result
        
    @staticmethod
    @returns(str)
    @accepts(proportion=str)
    def code_stretch(proportion):
        result = Dimensions.change_dimension_value(r"fontdimen2\font", LatexBase.single_command(WordSpacing.default_expand_name))
        result += "%\n"
        result += Dimensions.change_dimension_value(r"fontdimen3\font", proportion)
        result += "%\n"
        return result
    
    @staticmethod
    @returns(str)
    @accepts(proportion=str)
    def code_expand(proportion):
        result = Dimensions.change_dimension_value(r"fontdimen3\font", LatexBase.single_command(WordSpacing.default_stretch_name))
        result += "%\n"
        result += Dimensions.change_dimension_value(r"fontdimen2\font", proportion)
        result += "%\n"
        return result
    
    @staticmethod
    @returns(str)
    @accepts(proportion=str)
    def text_space(proportion=None, expand=True, create=False):
        if proportion:
            return LatexBase(
                content=WordSpacing.code_expand(proportion) if expand else WordSpacing.code_stretch(proportion)
            )
        return LatexBase(
            content=WordSpacing.prepare_dimensions() if create else WordSpacing.code_expand("\\" + WordSpacing.default_expand_name) 
        )
    
    

@returns(LatexBase)
@accepts(text=str)
def VerbatimText(text):
    return LatexBase(
        content=LatexBase.environment_command("verbatim", text=text),
        require=LatexRequire(
            name="verbatim",
        )
    )

@returns(LatexBase)
@accepts(url=str)
def UrlText(url):
    return LatexBase(
        content=LatexBase.single_command("url", text=url)
    )



@returns(LatexBase)
@accepts(text=str)
def Abstract(text):
    return LatexBase(
        content=LatexBase.environment_command("abstract", text=text)
    )



# http://en.wikibooks.org/wiki/LaTeX/Colors

class Tips(object):
    @staticmethod
    @returns(LatexBase)
    @accepts(name=str, level=str)
    def NumberingElementBy(name="equation", level="section"):
        return LatexBase(
            content=LatexBase.single_command("numberwithin", text=[name, level]),
            require=LatexRequire(
                name="amsmath",
            )
        )
        
    @staticmethod
    @returns(LatexBase)
    @accepts(level=str)
    def NumberingFigureBy(level="section"):
        return LatexBase(
            content=LatexBase.Tip_NumberingElementBy("figure", level)
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(level=str)
    def NumberingEquationBy(level="section"):
        return LatexBase(
            content=LatexBase.Tip_NumberingElementBy("equation", level)
        )

    @staticmethod
    @returns(LatexBase)
    @accepts(filename=str)
    def IncludeSourceCode(filename="section"):
        return LatexBase(
            content=LatexBase.environment_command("verbatim", text=LatexBase.single_command("verbatiminput", text=filename)),
            require=LatexRequire(
                name="verbatim",
            )
        )






""""
\ref{label-name}
\eqref{label-name}
\pageref{label-name}

\begin{environmentname}
text to be influenced
\end{environmentname}

\commandname[option1,option2,...]{argument1}{argument2}


Grouping Figure/Equation Numbering by Section[edit]

For long documents the numbering can become cumbersome as the numbers reach into double and triple digits. To reset the counters at the start of each section and prefix the numbers by the section number, include the following in the preamble.
\use_package{amsmath}
\numberwithin{equation}{section}
\numberwithin{figure}{section}


Dynamically Including Program Listings

You have written the perfect program wonderful.cc and want to include it your report. Well you could do

\begin{verbatim}
-- Copy and paste your program to here --
\end{verbatim}
However what happens when you suddenly find that your program has a bug or would be even better with some tweak. Then you would have to delete the copy from your report and repaste the new version. In preference you can use the verbatim package. This allows you to have a file printed in verbatim format (ie. looking like a typewriter) at the chosen point of your report.

At the head of your document (somewhere before

\begin{document}
put the line
\use_package{verbatim}
Then in the relevant location put

\verbatiminput{/hame/perfect/wonderful.cc}

\protect 
Latex complains when you put citations in table captions (and when you put footnotes in arguments of \section commands). Fix this by putting a \protect command in front:
  \caption{Data taken from \protect \citeauthor{Efron79t}
  \protect \shortcite{Efron79t}}
  
  
Latex in Powerpoint 
To typeset Latex within MS Powerpoint, use TexPoint. Note that a grouped figure can be saved as PNG, which can be converted to postscript using (e.g.) the Gimp.
No page numbers 
To suppress the page number on a page, use
\thispagestyle{empty}
A basic preamble 
Here's the blank document I usually start with:
\documentclass{article}
\use_package{amsmath}
\use_package{amsfonts}
\use_package{latexsym}
\use_package{graphicx}
\newcommand{\comment}[1]{}
\newcommand{\field}[1]{\mathbb{#1}} % requires amsfonts
\newcommand{\pd}[2]{\frac{\partial#1}{\partial#2}}
\begin{document}
\bibliographystyle{abbrv}
\bibliography{refs}
\end{document}
An alternative to xdvi 
After trying dvilx, it didn't take me long to switch. What took me some time is figuring out how to get Emacs/Auctex/Latex-mode to default to using dvilx for viewing. Eventually, I figured it out. Here's the magic (add to your ~/.emacs file):
  (defcustom TeX-view-style `(("." "dvilx %d")) "")
[2/16/05] Note: this doesn't seem to work anymore...
Postscript 
Some programs create postscript files without a bounding box. Latex doesn't like this. To fix the problem, add a line like this to the top of the postscript file:
%%BoundingBox: 50 150 550 650
A4 Paper 
When someone sends me an A4-formatted postscript document, it prints badly. "pstops" can be used to shift the document down to print correctly. Here's the magic for an A4 postscript:
pstops '(0cm,-2cm)' in.ps out.ps
Side-by-side tables 
Normally a tablular environment stretches the entire width of the text area (whether it looks like it should or not!). You can restrict the width with a minipage. This allows you to put two tables side-by-side:
  \begin{minipage}{2in}
    \begin{tabular}{c}
      Table1
    \end{tabular}
  \end{minipage}
  \begin{minipage}{2in}
    \begin{tabular}{c}
      Table2
    \end{tabular}
  \end{minipage}
Derivatives 
If you write partial derivatives a lot, it's useful to make a macro:
  \newcommand{\pd}[2]{\frac{\partial #1}{\partial #2}}
Then, writing a partial is as simple as $\pd{J}{x}$.
Save Trees 
Do you hate the fact that Latex uses white space a little too freely sometimes? Or, do you have a strict page limit that you have to adhear to? If so, the savetrees package is for you.
AUC TeX 
The Emacs latex mode is okay, but nowhere near as useful as AUC TeX. AUC TeX incorporates many useful features into the mode, including intelligent indentation/formatting (Meta-q), inserting environments (Ctrl-c Ctrl-e), inserting sections (Ctrl-c Ctrl-s) and more! See the AUC TeX documentation for the lowdown.
The Reals 
Latex doesn't have a special math symbol for the set of reals, but the symbol that we all know and love can be found in the AMS fonts package:
  \use_package{amsfonts}
  \newcommand{\field}[1]{\mathbb{#1}}
  ...
  A metric space is a set $S$ together with a metric
  $\rho:S \times S \rightarrow \field{R}$
This works for other fields such as the integers (\field{Z}) and complex numbers (\field{C}).
Citations 
I use the named bibliography style because it allows for more fine-tuned citing. Commands include \cite, \citeauthor, \citeyear and \shortcite (for after you've already used \citeauthor). You'll need named.sty and named.bst. Use it like this:
  \use_package{named}
  ...
  \citeauthor{Efron79t} introduced the bootstrap \shortcite{Efron79t}.
  ...
  \bibliographystyle{named}
  \bibliography{/foo/bar/baz/refs}
The above assumes that your bibliography file is "/foo/bar/baz/refs.bib".
BibTeX 
BibTeX makes citations a breeze. I keep a local copy of the database entry types to help remind me of the fields that go with the different types. Take a look at my refs.bib.
Processing the Bibliography 
Let "main.tex" be the name of your Latex file. Run
  latex main
  bibtex main
  latex main
  latex main
(in that order) to have Latex and Bibtex work together to process the bibliography.
\protect 
Latex complains when you put citations in table captions (and when you put footnotes in arguments of \section commands). Fix this by putting a \protect command in front:
  \caption{Data taken from \protect \citeauthor{Efron79t}
  \protect \shortcite{Efron79t}}
In general, any fragile command that appears in a moving argument must be preceded by a \protect command. See Help with Latex for more information.
xdvi 
"k" or "K" (depending on your version of xdvi) will toggle holding your scrolling position when changing pages. This is good for reading papers with large margins. 
Alternatively, add the following line to your ~/.Xresources file:
xdvi.keepPosition:    true
\rightarrow 
Use \to instead of \rightarrow to save your fingers from excess typing.
Aligning Images 
By default, images align according to their "reference point," which is never what you want it to be. Put a minipage around an image to make it align properly (according to its center):
  \use_package{graphicx}
  \begin{minipage}{2in}
    \includegraphics[width=2in,angle=-90]{foo}
  \end{minipage}
2-Column Images 
When in 2-column mode (using either \twocolumn or the multicols environment (package multicol)), use \begin{figure*} and \begin{table*} to create figures and tables that span the entire width of the page. \begin{figure} and \begin{table} span only one column.
"""

