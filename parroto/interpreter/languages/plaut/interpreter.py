# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../../"))

from parroto.interpreter.languages.meta.interpreter import BaseInterpreter
import compiler


class Interpreter(BaseInterpreter):
    compiler = compiler


if __name__ == "__main__":
    interpreter = Interpreter()
    element = interpreter.process(r"""
@example{
    content
}
@start:example
    content2
@stop
""")
    print element.xml_string

