# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from parroto.compiler import CompilerErrorHandler
from colors import Color as BaseColor
import compiler


class ColorInterpreter(object):
    scanner = None
    parser = None
    cache = {}

    def process_text(self, text, filename="<<stdin>>"):
        """
        Process a text string.
        :param text:
        :param filename: by default it is <<stdin>>
        :return:
        """
        if text in ColorInterpreter.cache:
            return ColorInterpreter.cache[text]
        text = text.decode("utf-8")
        self.scanner = compiler.Scanner(text)
        self.parser = compiler.Parser()
        compiler.Errors = CompilerErrorHandler(
            filename=filename,
            lines_after_msg=1,
            lines_before_msg=1,
            list_filename='color-listing.txt',
            is_merged=True,
            parser=self.parser,
        )
        stdout, sys.stdout = sys.stdout, sys.stderr
        self.parser.Parse(self.scanner)
        compiler.Errors.Summarize(self.scanner.buffer)
        sys.stdout = stdout
        color = self.parser.color.apply_modifiers()
        ColorInterpreter.cache[text] = color
        return color

    def process_file(self, filename):
        """
        Open a text file and process it.
        :param filename:
        :return:
        """
        text = ""
        with open(filename, "r") as f:
            text += "".join(f.readlines())
        return self.process_text(text, filename)


class Color(BaseColor):
    @staticmethod
    def from_format(text):
        return ColorInterpreter().process_text(text)

    def format(self, text):
        color_value = Color.from_format(text)
        self.rgb = color_value.rgb
        self.alpha = color_value.alpha


if __name__ == "__main__":
    interpreter = ColorInterpreter()
    color = interpreter.process_text("rgb(100, 49, 30)")
    print color, color.rgb
    color = interpreter.process_text("linear-rgb(0.392, 0.192, 0.118)")
    print color, color.rgb
    color = interpreter.process_text("[old rose]")
    print color, color.rgb
    color = interpreter.process_text("30%[old rose] alpha = 0.3")
    print color, color.rgb
    print "-" * 40
    color = Color()
    color.named_color("[red munsell]")
    print color, color.rgb
    color.format("([red munsell] alpha = 0.3)")
    print color, color.rgb
    color.format("30%[old rose] alpha = 0.3")
    print color, color.rgb

