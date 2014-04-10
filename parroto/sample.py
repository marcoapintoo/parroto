import codecs
from common import Message
from modules.latex import LatexModule
from markup import Interpreter as MarkupInterpreter
from parser.latex import Interpreter as DocInterpreter

xml_content = """
<document-file>
<document-information>
    <document-information.title>Dummy Text</document-information.title>
    <document-information.author>Undefined Author</document-information.author>
</document-information>
<style>
    <style.apply-to>#zz</style.apply-to>
    <style.font-weight>bold</style.font-weight>
    <style.label>bold-label</style.label>
</style>
<style2>
    <style.apply-to>#zz</style.apply-to>
    <style.font-weight>bold</style.font-weight>
    <style.label>bold-label</style.label>
</style2>
<document/>
<chapter title="First chapter"/>
Starting text - Part A.
<text2 or ="3" argument-1="44" argument-0="ABC">
aaabbb
</text2>
<section title="Section One"/>
Starting text - Part B.
<subsection title="Subsection 1.1" label = "aaa"/>
Starting text - Part C.
<section title="Section Two"/>
Starting text - Part D.
<text id="zz">aaa</text>
External part
<subsection title="Subsection 2.1"/>
Starting text - Part E.
<subsection title="Subsection 2.2"/>
Starting text - Part F.
<subsection title="Subsection 2.3"/>
Starting text - Part G.
<section title="Section Three"/>
Starting text - Part H.
<chapter title="Second chapter"/>
Starting text - Part I.
<section title="Section Second-One"/>
Starting text - Part J.
</document-file>
"""

doc_content222 = r"""
\document-information[title={Dummy Text}, author = {Undefined Author}]{}
\begin-style[apply-yo=#zz]
    \style.font-weight{bold}
    \style.label{bold-label}
\end
\begin-style2[apply-yo=document]
    \style.font-weight{bold}
    \style.label{bold-label}
\end
\document{}
\chapter[title="First chapter"]{}
Starting text - Part A.
\begin-text2[or="3",argument-1="44",argument-0="ABC"]
aaabbb
\end
\section[title="Section One"]{}
Starting text - Part B.
\subsection[title="Subsection 1.1", label = "aaa"]{}
Starting text - Part C.
\section[title="Section Two"]{}
Starting text - Part D.
\text[id="zz"]{aaa}
External part
\subsection[title="Subsection 2.1"]{}
Starting text - Part E.
\subsection[title="Subsection 2.2"]{}
Starting text - Part F.
\subsection[title="Subsection 2.3"]{}
Starting text - Part G.
\section[title="Section Three"]{}
Starting text - Part H.
\chapter[title="Second chapter"]{}
Starting text - Part I.
\section[title="Section Second-One"]{}
Starting text - Part J.
"""


doc_content = r"""
\document-information[title={Dummy Text}, author = {Undefined Author}]
\begin-style[apply-yo=#zz]
    \style.font-weight{bold}
    \style.label{bold-label}
\end
\begin-style2[apply-yo=document]
    \style.font-weight{bold}
    \style.label{bold-label}
\end
\document
\chapter[title="First chapter"]
Starting text - Part A.
\begin-text2[or="3",argument-1="44",argument-0="ABC"]
aaabbb
\end
\section[title="Section One"]
Starting text - Part B.
\subsection[title="Subsection 1.1", label = "aaa"]
Starting text - Part C.
\section[title="Section Two"]
Starting text - Part D.
\text[id="zz"]{aaa}
External part
\subsection[title="Subsection 2.1"]
Starting text - Part E.
\subsection[title="Subsection 2.2"]
Starting text - Part F.
\subsection[title="Subsection 2.3"]
Starting text - Part G.
\section[title="Section Three"]
Starting text - Part H.
\chapter[title="Second chapter"]
Starting text - Part I.
\section[title="Section Second-One"]
Starting text - Part J.
"""



if __name__ == "__main__":
    # with open("start.text", "wt") as f:
    #    print >> f, doc_content
    
    Message.important_advice("Processing:", color="red", prefix_space=0)
    Message.message("Reading input...", header="STEP A", prefix_space=0)
    document = DocInterpreter()
    #xml_content = document.ProcessText(doc_content)
    xml_content = document.ProcessFile("start.tex")
    Message.message("Writing intermediate file...", header="STEP B", prefix_space=0)
    with codecs.open("intermediate.xml", "wt", encoding='utf-8') as f:
        f.write(xml_content)
    Message.message("Loading module {0}...".format("latex"), header="STEP C", prefix_space=0)
    module = LatexModule()
    interpreter = MarkupInterpreter()
    Message.message("Loading intermediate file...", header="STEP D", prefix_space=0)
    interpreter.load_string(xml_content)
    interpreter.set_module(module)
    # print interpreter.execute()
    Message.message("Processing intermediate file...", header="STEP E", prefix_space=0)
    interpreter.execute_to_file("output.tex")
    Message.message("Writing output file...", header="STEP F", prefix_space=0)
    with codecs.open("example.xml", "wt", encoding='utf-8') as f:
        #f.write(str(interpreter._document._rootnode._element))
        f.write(unicode(interpreter._document._rootnode._element))
        #print >> f, interpreter._document._rootnode._element
    Message.important_advice("Process finished.", color="magenta", prefix_space=0)
