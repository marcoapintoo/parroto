# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../../"))

from parroto.base import AutoObject
from parroto.interpreter.languages.patex.interpreter import Interpreter as PatexInterpreter
from parroto.interpreter.languages.plaut.interpreter import Interpreter as PlautInterpreter


class CompilerInstruction(object):
    __metaclass__ = AutoObject
    value = None
    name = None

    def process(self, text):
        result = text.split(":", 2)
        if len(result) == 0:
            raise Exception("No instruction")
        elif len(result) == 1:
            self.name = result[0].strip()
            self.value = ""
        elif len(result) == 2:
            self.name = result[0].strip()
            self.value = result[1].strip()

    @staticmethod
    def from_string(text):
        instruction = CompilerInstruction()
        instruction.process(text)
        return instruction

    def __repr__(self):
        return "{name}: {value}".format(name=self.name, value=self.value)


class InstructionFinder(object):
    __metaclass__ = AutoObject
    instructions = None

    def __init__(self):
        self.instructions = {}

    def add_instruction(self, instruction):
        self.instructions[instruction.name] = instruction

    def find_instructions(self, text):
        mark = "#!"
        end_pos = 0
        while True:
            pos = text.find(mark, end_pos)
            if pos == -1 or text[end_pos:pos].strip() != "":
                break
            end_pos = text.find("\n", pos)
            self.add_instruction(CompilerInstruction.from_string(text[pos + len(mark):end_pos]))
        return text[end_pos + 1:]


class BaseSelector(InstructionFinder):
    __metaclass__ = AutoObject

    def __init__(self):
        super(BaseSelector, self).__init__()
        self.default_instruction(
            name="compiler",
            value="patex"
        )

    def default_instruction(self, name, value):
        self.add_instruction(CompilerInstruction(
            name=name,
            value=value
        ))

    def process(self, text, filename="stdin"):
        text = text.decode("utf-8")
        text = self.find_instructions(text)
        if self.instructions["compiler"].value == "patex":
            interpreter = PatexInterpreter()
            result = interpreter.process(text, filename)
        elif self.instructions["compiler"].value == "plaut":
            interpreter = PlautInterpreter()
            result = interpreter.process(text, filename)
        else:
            raise Exception("Compiling error")
        return result

    def process_file(self, filename):
        text = ""
        with open(filename, "r") as f:
            text += "".join(f.readlines())
        return self.process(text, filename)


if __name__ == "__main__":
    interpreter = BaseSelector()
    element = interpreter.process(r"""
#!compiler: patex
#!/usr/bin/parroto
#!compiler: patex



\define[name=label,arguments={text: "",}]{
    r"\label{{{text}}}".format(text)
}
\define-set[name=old_label, target=label]{}
\define[name=label,arguments={text: "",}]{
    print label #<- current string response
    return old_label.use(text = text)
}
\oldlabel=\let\label
\def\label#1{
}

\example{
    content
}
@example{
    content
}
\start-example
    content2
\stop

""")
    print element.xml_string
    print interpreter.instructions

