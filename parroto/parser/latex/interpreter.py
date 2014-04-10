#!/usr/bin/python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../../")

import compiler as Compiler
from parser import CompilerErrorHandler


class Interpreter(object):
        
    def ProcessText(self, text, filename = "stdin"):
        text = text.decode("utf-8") 
        self.scanner = Compiler.Scanner(text)
        self.parser = Compiler.Parser()
        Compiler.Errors = CompilerErrorHandler(
            header = "Error in document:", 
            filename = filename, 
            lines_after_msg = 1, 
            lines_before_msg = 1,
            list_filename = 'macro-listing.txt', 
            is_merged = True, 
            parser = self.parser, 
        )
        stdout, sys.stdout = sys.stdout, sys.stderr
        self.parser.Parse(self.scanner)
        Compiler.Errors.Summarize(self.scanner.buffer)
        sys.stdout = stdout
        return self.parser.document
        
    def ProcessFile(self, filename): 
        text = ""
        with open(filename, "r") as f:
            text += "".join(f.readlines())
        return self.ProcessText(text, filename)


