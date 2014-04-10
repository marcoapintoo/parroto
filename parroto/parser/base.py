#!/usr/bin/python
import os
import sys
import codecs

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])) + "/../")

from common import AutoInitObject

class ErrorRecorder(object):
    __metaclass__ = AutoInitObject
    line = ""
    col = 0
    num = 0
    str = ""


class CompilerErrorHandler(object):
    __metaclass__ = AutoInitObject
    header = ""
    lines_after_msg = 2
    lines_before_msg = 2
    code_filename = ''
    list_filename = 'listing.txt'
    is_merged = False
    parsing_position_handler = None
    error_messages = None
    # protected
    merged_file = None  # PrintWriter
    errors = [ ]
    # external_use
    minErrDist = 2
    errDist = minErrDist
    count = 0  # number of errors detected
        # A function with prototype: f(errorNum=None) where errorNum is a
        # predefined error number.  f returns a tuple, (line, column, message)
        # such that line and column refer to the location in the
        # source file most recently parsed.  message is the error
        # message corresponging to errorNum.

    def __init__(self, parser=None, *arg, **kwargs):
        if parser is not None:
            self.parsing_position_handler = parser.getParsingPos
            self.error_messages = parser.errorMessages
        if self.is_merged:
            try:
                self.merged_file = codecs.open(self.list_filename, 'w', encoding="utf-8")
            except IOError:
                raise RuntimeError('-- Compiler Error: could not open ' + self.list_filename)

    def StoreError(self, line, col, s):
        if self.is_merged:
            self.errors.append(ErrorRecorder(line=line, col=col, str=s))
        else:
            self.ShowMessage(self.code_filename, line, col, s)

    def SynErr(self, errNum, errPos=None):
        line, col = errPos if errPos else (self.parsing_position_handler() if self.parsing_position_handler else ("", 0))
        msg = self.error_messages[ errNum ]
        self.StoreError(line, col, msg)
        self.count += 1

    def SemErr(self, errMsg, errPos=None):
        line, col = errPos if errPos else (self.parsing_position_handler() if self.parsing_position_handler else ("", 0))
        self.StoreError(line, col, errMsg)
        self.count += 1

    def Warn(self, errMsg, errPos=None):
        line, col = errPos if errPos else (self.parsing_position_handler() if self.parsing_position_handler else ("", 0))
        self.StoreError(line, col, errMsg)

    def Exception(self, errMsg):
        print errMsg
        sys.exit(1)

    def ShowMessage(self, code_filename, line, column, msg):
        val = { 'file':code_filename, 'line':line, 'col':column, 'text':msg }
        if line == 1:
            msg = u"Malformed selector in position {col}: {text}\n"
        else:
            msg = u"Malformed selector in position {col} at line {line}: {text}\n"
        sys.stdout.write(msg.format(**val))

    def DisplayFormat(self, s, e):
        msg = u'**ERROR** '
        for c in xrange(1, e.col):
            msg += '\t' if s[c - 1] == '\t' else ' '
        msg += '^' + e.str + '\n'
        return msg
        
    def Display(self, s, e):
        self.merged_file.write(self.DisplayFormat(s, e))

    def CountErrorFormat(self, see_log=True):
        msg = ""
        if self.count == 1:
            msg = u'One error detected'
        elif self.count > 1:
            msg = u'%d errors detected' % self.count
        if see_log and self.count > 0 and self.is_merged:
            msg += u'. See: ' + self.list_filename
        msg += '\n' if self.count > 0 else ""
        return msg
            
    def TextAroundErrors(self, lines, lines_before=-1, lines_after=-1):
        if self.count == 0: return ""
        msg = "" if self.header.strip() == "" else self.header + "\n"
        fmt = lambda num, line: u'  %4d  |%s' % (num, line)
        last_line = 0
        end_line = len(lines)
        for rec in self.errors:
            if lines_before > 0:
                prev = rec.line - lines_before - 1
                if prev < 0: last_line = 0
                elif prev > last_line: last_line = prev
            for linenum, line in enumerate(lines[last_line:rec.line]):
                msg += fmt(linenum + last_line + 1, line)
            msg += self.DisplayFormat((lines + [""])[rec.line - 1], rec)
            last_line = rec.line - 1
        if lines_after > 0 and last_line + lines_after + 1 < end_line:
            end_line = last_line + lines_after + 1
        for linenum, line in enumerate(lines[last_line + 1:end_line]):
            msg += fmt(linenum + last_line + 2, line)
        return msg
            
    def Summarize(self, sourceBuffer):
        # fmt = lambda num, line: '  %4d  |%s' % (num, line)
        # fmt = lambda num, line: self.merged_file.write('  %4d  |%s' % (num, line if line.endswith("\n") else (line+"\n")))
        if self.is_merged:
            self.merged_file.write(self.TextAroundErrors(sourceBuffer.lines))
            self.merged_file.write(self.CountErrorFormat(see_log=False))
            self.merged_file.close()
        sys.stdout.write(self.TextAroundErrors(sourceBuffer.lines, lines_before=self.lines_before_msg, lines_after=self.lines_after_msg))
        sys.stdout.write(self.CountErrorFormat())
        if self.count > 0: sys.exit(1)

