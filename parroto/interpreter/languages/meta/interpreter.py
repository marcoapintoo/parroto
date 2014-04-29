# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../../"))

from parroto.base import AutoObject
from parroto.compiler import CompilerErrorHandler


class BaseInterpreter(object):
    __metaclass__ = AutoObject
    scanner = None
    parser = None
    compiler = None

    def process(self, text, filename="stdin"):
        text = text.decode("utf-8")
        self.scanner = self.compiler.Scanner(text)
        self.parser = self.compiler.Parser()
        self.compiler.Errors = CompilerErrorHandler(
            header="Error in document:",
            filename=filename,
            lines_after_msg=1,
            lines_before_msg=1,
            list_filename='macro-listing.txt',
            is_merged=True,
            parser=self.parser,
        )
        stdout, sys.stdout = sys.stdout, sys.stderr
        self.parser.Parse(self.scanner)
        self.compiler.Errors.Summarize(self.scanner.buffer)
        sys.stdout = stdout
        return self.parser.document

    def process_file(self, filename):
        text = ""
        with open(filename, "r") as f:
            text += "".join(f.readlines())
        return self.process(text, filename)


if __name__ == "__main__":
    from parroto.interpreter.languages.patex import compiler

    interpreter = BaseInterpreter(compiler=compiler)
    element = interpreter.process(r"""
\example{
    content
}
\start-example
    content2
\stop
""")
    print element.xml_string

