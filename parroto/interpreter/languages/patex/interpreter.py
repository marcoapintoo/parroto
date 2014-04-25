# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../../"))

from parroto.compiler import CompilerErrorHandler
import compiler


class Interpreter(object):
    scanner = None
    parser = None

    def filter_bash(self, text):
        pos = text.find("#!")
        if pos == -1 or text[0:pos].strip() != "":
            return text
        end_pos = text.find("\n", pos)
        return text[0:pos] + "\n" + text[end_pos + 1:]

    def process_text(self, text, filename="stdin"):
        text = text.decode("utf-8")
        text = self.filter_bash(text)
        self.scanner = compiler.Scanner(text)
        self.parser = compiler.Parser()
        compiler.Errors = CompilerErrorHandler(
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
        compiler.Errors.Summarize(self.scanner.buffer)
        sys.stdout = stdout
        return self.parser.document

    def process_file(self, filename):
        text = ""
        with open(filename, "r") as f:
            text += "".join(f.readlines())
        return self.process_text(text, filename)


if __name__ == "__main__":
    interpreter = Interpreter()
    element = interpreter.process_text(r"""
\example{
    content
}
""")
    print element.xml_string

