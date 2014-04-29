# -------------------------------------------------------------------------
#Parser.py -- ATG file parser
#Compiler Generator Coco/R,
#Copyright (c) 1990, 2004 Hanspeter Moessenboeck, University of Linz
#extended by M. Loeberbauer & A. Woess, Univ. of Linz
#ported from Java to Python by Ronald Longo
#
#This program is free software; you can redistribute it and/or modify it
#under the terms of the GNU General Public License as published by the
#Free Software Foundation; either version 2, or (at your option) any
#later version.
#
#This program is distributed in the hope that it will be useful, but
#WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#for more details.
#
#You should have received a copy of the GNU General Public License along
#with this program; if not, write to the Free Software Foundation, Inc.,
#59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
#As an exception, it is allowed to write an extension of Coco/R that is
#used as a plugin in non-free software.
#
#If not otherwise stated, any source code generated by Coco/R (other than
#Coco/R itself) does not fall under the GNU General Public License.
#-------------------------------------------------------------------------*/

import sys

from parroto.interpreter.languages.meta import Element


class Token(object):
    def __init__(self):
        self.kind = 0  # token kind
        self.pos = 0  # token position in the source text (starting at 0)
        self.col = 0  # token column (starting at 0)
        self.line = 0  # token line (starting at 1)
        self.val = u''  # token value
        self.next = None  # AW 2003-03-07 Tokens are kept in linked list


class Position(object):  # position of source code stretch (e.g. semantic action, resolver expressions)
    def __init__(self, buf, beg, len, col):
        assert isinstance(buf, Buffer)
        assert isinstance(beg, int)
        assert isinstance(len, int)
        assert isinstance(col, int)

        self.buf = buf
        self.beg = beg  # start relative to the beginning of the file
        self.len = len  # length of stretch
        self.col = col  # column number of start position

    def getSubstring(self):
        return self.buf.readPosition(self)


class Buffer(object):
    EOF = u'\u0100'  # 256

    def __init__(self, s):
        self.buf = s
        self.bufLen = len(s)
        self.pos = 0
        self.lines = s.splitlines(True)

    def Read(self):
        if self.pos < self.bufLen:
            result = self.buf[self.pos]
            self.pos += 1
            return result
        else:
            return Buffer.EOF

    def ReadChars(self, numBytes=1):
        result = self.buf[self.pos: self.pos + numBytes]
        self.pos += numBytes
        return result

    def Peek(self):
        if self.pos < self.bufLen:
            return self.buf[self.pos]
        else:
            return self.buffer.EOF

    def getString(self, beg, end):
        s = ''
        oldPos = self.getPos()
        self.setPos(beg)
        while beg < end:
            s += self.Read()
            beg += 1
        self.setPos(oldPos)
        return s

    def getPos(self):
        return self.pos

    def setPos(self, value):
        if value < 0:
            self.pos = 0
        elif value >= self.bufLen:
            self.pos = self.bufLen
        else:
            self.pos = value

    def readPosition(self, pos):
        assert isinstance(pos, Position)
        self.setPos(pos.beg)
        return self.ReadChars(pos.len)

    def __iter__(self):
        return iter(self.lines)


class Scanner(object):
    EOL = u'\n'
    eofSym = 0

    charSetSize = 256
    maxT = 27
    noSym = 27
    start = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 4, 4, 4, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        4, 1, 7, 1, 1, 1, 1, 5, 1, 1, 1, 0, 1, 1, 1, 1,
        9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 1, 1, 0, 16, 0, 1,
        0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 21, 1, 0, 2,
        0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 17, 1, 18, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        -1]


    def __init__(self, s):
        self.buffer = Buffer(unicode(s))  # the buffer instance

        self.ch = u'\0'  # current input character
        self.pos = -1  # column number of current character
        self.line = 1  # line number of current character
        self.lineStart = 0  # start position of current line
        self.oldEols = 0  # EOLs that appeared in a comment;
        self.NextCh()
        self.ignore = set()  # set of characters to be ignored by the scanner
        #self.ignore.add( ord(' ') )  # blanks are always white space

        # fill token list
        self.tokens = Token()  # the complete input token stream
        node = self.tokens

        node.next = self.NextToken()
        node = node.next
        while node.kind != Scanner.eofSym:
            node.next = self.NextToken()
            node = node.next

        node.next = node
        node.val = u'EOF'
        self.t = self.tokens  # current token
        self.pt = self.tokens  # current peek token

    def NextCh(self):
        if self.oldEols > 0:
            self.ch = Scanner.EOL
            self.oldEols -= 1
        else:
            self.ch = self.buffer.Read()
            self.pos += 1
            # replace isolated '\r' by '\n' in order to make
            # eol handling uniform across Windows, Unix and Mac
            if (self.ch == u'\r') and (self.buffer.Peek() != u'\n'):
                self.ch = Scanner.EOL
            if self.ch == Scanner.EOL:
                self.line += 1
                self.lineStart = self.pos + 1


    def Comment0(self):
        level = 1
        line0 = self.line
        lineStart0 = self.lineStart
        self.NextCh()
        if self.ch == '*':
            self.NextCh()
            while True:
                if self.ch == '*':
                    self.NextCh()
                    if self.ch == '%':
                        level -= 1
                        if level == 0:
                            self.oldEols = self.line - line0
                            self.NextCh()
                            return True
                        self.NextCh()
                elif self.ch == Buffer.EOF:
                    return False
                else:
                    self.NextCh()
        else:
            if self.ch == Scanner.EOL:
                self.line -= 1
                self.lineStart = lineStart0
            self.pos = self.pos - 2
            self.buffer.setPos(self.pos + 1)
            self.NextCh()
        return False

    def Comment1(self):
        level = 1
        line0 = self.line
        lineStart0 = self.lineStart
        self.NextCh()
        while True:
            if ord(self.ch) == 10:
                level -= 1
                if level == 0:
                    self.oldEols = self.line - line0
                    self.NextCh()
                    return True
                self.NextCh()
            elif self.ch == Buffer.EOF:
                return False
            else:
                self.NextCh()

    def Comment2(self):
        level = 1
        line0 = self.line
        lineStart0 = self.lineStart
        self.NextCh()
        if self.ch == '#':
            self.NextCh()
            while True:
                if ord(self.ch) == 10:
                    level -= 1
                    if level == 0:
                        self.oldEols = self.line - line0
                        self.NextCh()
                        return True
                    self.NextCh()
                elif self.ch == Buffer.EOF:
                    return False
                else:
                    self.NextCh()
        else:
            if self.ch == Scanner.EOL:
                self.line -= 1
                self.lineStart = lineStart0
            self.pos = self.pos - 2
            self.buffer.setPos(self.pos + 1)
            self.NextCh()
        return False


    def CheckLiteral(self):
        lit = self.t.val
        if lit == "[":
            self.t.kind = 10
        elif lit == "]":
            self.t.kind = 11
        elif lit == ",":
            self.t.kind = 12
        elif lit == ":":
            self.t.kind = 14
        elif lit == "start":
            self.t.kind = 18
        elif lit == "Start":
            self.t.kind = 19
        elif lit == "START":
            self.t.kind = 20
        elif lit == "-":
            self.t.kind = 21
        elif lit == "stop":
            self.t.kind = 22
        elif lit == "Stop":
            self.t.kind = 23
        elif lit == "STOP":
            self.t.kind = 24
        elif lit == ".":
            self.t.kind = 25


    def NextToken(self):
        while ord(self.ch) in self.ignore:
            self.NextCh()
        if (self.ch == '%' and self.Comment0() or self.ch == '%' and self.Comment1() or ord(
                self.ch) == 92 and self.Comment2()):
            return self.NextToken()

        self.t = Token()
        self.t.pos = self.pos
        self.t.col = self.pos - self.lineStart + 1
        self.t.line = self.line
        if ord(self.ch) < len(self.start):
            state = self.start[ord(self.ch)]
        else:
            state = 0
        buf = u''
        buf += unicode(self.ch)
        self.NextCh()

        done = False
        while not done:
            if state == -1:
                self.t.kind = Scanner.eofSym  # NextCh already done
                done = True
            elif state == 0:
                self.t.kind = Scanner.noSym  # NextCh already done
                done = True
            elif state == 1:
                if (self.ch == '!'
                    or self.ch >= '#' and self.ch <= '&'
                    or self.ch >= '(' and self.ch <= '*'
                    or self.ch >= ',' and self.ch <= '/'
                    or self.ch >= ':' and self.ch <= ';'
                    or self.ch == '?'
                    or self.ch == '['
                    or self.ch == ']'
                    or self.ch == '|'):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 1
                else:
                    self.t.kind = 1
                    self.t.val = buf
                    self.CheckLiteral()
                    return self.t
            elif state == 2:
                if (self.ch >= '0' and self.ch <= '9'
                    or self.ch >= 'A' and self.ch <= 'Z'
                    or self.ch == '_'
                    or self.ch >= 'a' and self.ch <= 'z'):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 2
                else:
                    self.t.kind = 2
                    self.t.val = buf
                    self.CheckLiteral()
                    return self.t
            elif state == 3:
                if (self.ch >= '0' and self.ch <= '9'
                    or self.ch >= 'A' and self.ch <= 'Z'
                    or self.ch == '_'
                    or self.ch >= 'a' and self.ch <= 'z'):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 3
                else:
                    self.t.kind = 4
                    done = True
            elif state == 4:
                if (ord(self.ch) >= 9 and ord(self.ch) <= 12
                    or self.ch == ' '):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 4
                else:
                    self.t.kind = 5
                    done = True
            elif state == 5:
                if (self.ch <= '&'
                    or self.ch >= '(' and self.ch <= '['
                    or self.ch >= ']' and ord(self.ch) <= 255 or ord(self.ch) > 256):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 5
                elif ord(self.ch) == 39:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 6
                elif ord(self.ch) == 92:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 10
                else:
                    self.t.kind = Scanner.noSym
                    done = True
            elif state == 6:
                self.t.kind = 6
                done = True
            elif state == 7:
                if (self.ch <= '!'
                    or self.ch >= '#' and self.ch <= '['
                    or self.ch >= ']' and ord(self.ch) <= 255 or ord(self.ch) > 256):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 7
                elif self.ch == '"':
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 8
                elif ord(self.ch) == 92:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 11
                else:
                    self.t.kind = Scanner.noSym
                    done = True
            elif state == 8:
                self.t.kind = 7
                done = True
            elif state == 9:
                if (self.ch >= '0' and self.ch <= '9'):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 9
                elif (self.ch >= 'A' and self.ch <= 'Z'
                      or self.ch == '_'
                      or self.ch >= 'a' and self.ch <= 'z'):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 3
                elif self.ch == '.':
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 12
                else:
                    self.t.kind = 3
                    done = True
            elif state == 10:
                if (self.ch <= '&'
                    or self.ch >= '(' and self.ch <= '['
                    or self.ch >= ']' and ord(self.ch) <= 255 or ord(self.ch) > 256):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 5
                elif ord(self.ch) == 39:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 13
                elif ord(self.ch) == 92:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 10
                else:
                    self.t.kind = Scanner.noSym
                    done = True
            elif state == 11:
                if (self.ch <= '!'
                    or self.ch >= '#' and self.ch <= '['
                    or self.ch >= ']' and ord(self.ch) <= 255 or ord(self.ch) > 256):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 7
                elif self.ch == '"':
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 14
                elif ord(self.ch) == 92:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 11
                else:
                    self.t.kind = Scanner.noSym
                    done = True
            elif state == 12:
                if (self.ch >= '0' and self.ch <= '9'):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 12
                elif (self.ch >= 'A' and self.ch <= 'Z'
                      or self.ch == '_'
                      or self.ch >= 'a' and self.ch <= 'z'):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 3
                else:
                    self.t.kind = 3
                    done = True
            elif state == 13:
                if (self.ch <= '&'
                    or self.ch >= '(' and self.ch <= '['
                    or self.ch >= ']' and ord(self.ch) <= 255 or ord(self.ch) > 256):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 5
                elif ord(self.ch) == 39:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 6
                elif ord(self.ch) == 92:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 10
                else:
                    self.t.kind = 6
                    done = True
            elif state == 14:
                if (self.ch <= '!'
                    or self.ch >= '#' and self.ch <= '['
                    or self.ch >= ']' and ord(self.ch) <= 255 or ord(self.ch) > 256):
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 7
                elif self.ch == '"':
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 8
                elif ord(self.ch) == 92:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 11
                else:
                    self.t.kind = 7
                    done = True
            elif state == 15:
                self.t.kind = 9
                done = True
            elif state == 16:
                self.t.kind = 13
                done = True
            elif state == 17:
                self.t.kind = 15
                done = True
            elif state == 18:
                self.t.kind = 16
                done = True
            elif state == 19:
                self.t.kind = 17
                done = True
            elif state == 20:
                self.t.kind = 26
                done = True
            elif state == 21:
                if ord(self.ch) == 92:
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 15
                elif self.ch == '}':
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 19
                elif self.ch == '%':
                    buf += unicode(self.ch)
                    self.NextCh()
                    state = 20
                else:
                    self.t.kind = 8
                    done = True

        self.t.val = buf
        return self.t

    def Scan(self):
        self.t = self.t.next
        self.pt = self.t.next
        return self.t

    def Peek(self):
        self.pt = self.pt.next
        while self.pt.kind > self.maxT:
            self.pt = self.pt.next

        return self.pt

    def ResetPeek(self):
        self.pt = self.t


class ErrorRec(object):
    def __init__(self, l, c, s):
        self.line = l
        self.col = c
        self.num = 0
        self.str = s


class Errors(object):
    errMsgFormat = "file %(file)s : (%(line)d, %(col)d) %(text)s\n"
    eof = False
    count = 0  # number of errors detected
    fileName = ''
    listName = ''
    mergeErrors = False
    mergedList = None  # PrintWriter
    errors = []
    minErrDist = 2
    errDist = minErrDist
    # A function with prototype: f( errorNum=None ) where errorNum is a
    # predefined error number.  f returns a tuple, ( line, column, message )
    # such that line and column refer to the location in the
    # source file most recently parsed.  message is the error
    # message corresponging to errorNum.

    @staticmethod
    def Init(fn, dir, merge, getParsingPos, errorMessages):
        Errors.theErrors = []
        Errors.getParsingPos = getParsingPos
        Errors.errorMessages = errorMessages
        Errors.fileName = fn
        listName = dir + 'listing.txt'
        Errors.mergeErrors = merge
        if Errors.mergeErrors:
            try:
                Errors.mergedList = open(listName, 'w')
            except IOError:
                raise RuntimeError('-- Compiler Error: could not open ' + listName)

    @staticmethod
    def storeError(line, col, s):
        if Errors.mergeErrors:
            Errors.errors.append(ErrorRec(line, col, s))
        else:
            Errors.printMsg(Errors.fileName, line, col, s)

    @staticmethod
    def SynErr(errNum, errPos=None):
        line, col = errPos if errPos else Errors.getParsingPos()
        msg = Errors.errorMessages[errNum]
        Errors.storeError(line, col, msg)
        Errors.count += 1

    @staticmethod
    def SemErr(errMsg, errPos=None):
        line, col = errPos if errPos else Errors.getParsingPos()
        Errors.storeError(line, col, errMsg)
        Errors.count += 1

    @staticmethod
    def Warn(errMsg, errPos=None):
        line, col = errPos if errPos else Errors.getParsingPos()
        Errors.storeError(line, col, errMsg)

    @staticmethod
    def Exception(errMsg):
        print errMsg
        sys.exit(1)

    @staticmethod
    def printMsg(fileName, line, column, msg):
        vals = {'file': fileName, 'line': line, 'col': column, 'text': msg}
        sys.stdout.write(Errors.errMsgFormat % vals)

    @staticmethod
    def display(s, e):
        Errors.mergedList.write('**** ')
        for c in xrange(1, e.col):
            if s[c - 1] == '\t':
                Errors.mergedList.write('\t')
            else:
                Errors.mergedList.write(' ')
        Errors.mergedList.write('^ ' + e.str + '\n')

    @staticmethod
    def Summarize(sourceBuffer):
        if Errors.mergeErrors:
            # Initialize the line iterator
            srcLineIter = iter(sourceBuffer)
            srcLineStr = srcLineIter.next()
            srcLineNum = 1

            try:
                # Initialize the error iterator
                errIter = iter(Errors.errors)
                errRec = errIter.next()

                # Advance to the source line of the next error
                while srcLineNum < errRec.line:
                    Errors.mergedList.write('%4d %s\n' % (srcLineNum, srcLineStr))

                    srcLineStr = srcLineIter.next()
                    srcLineNum += 1

                # Write out all errors for the current source line
                while errRec.line == srcLineNum:
                    Errors.display(srcLineStr, errRec)

                    errRec = errIter.next()
            except:
                pass

            # No more errors to report
            try:
                # Advance to end of source file
                while True:
                    Errors.mergedList.write('%4d %s\n' % (srcLineNum, srcLineStr))

                    srcLineStr = srcLineIter.next()
                    srcLineNum += 1
            except:
                pass

            Errors.mergedList.write('\n')
            Errors.mergedList.write('%d errors detected\n' % Errors.count)
            Errors.mergedList.close()

        sys.stdout.write('%d errors detected\n' % Errors.count)
        if (Errors.count > 0) and Errors.mergeErrors:
            sys.stdout.write('see ' + Errors.listName + '\n')


class Parser(object):
    _EOF = 0
    _symbols = 1
    _identifier = 2
    _number = 3
    _numunit = 4
    _spaces = 5
    _string1 = 6
    _string2 = 7
    maxT = 27

    T = True
    x = False
    minErrDist = 2

    document = None
    positions_mark = []

    def mark_line(self):
        self.positions_mark.append(self.token.pos + len(self.token.val))

    def clear_marks(self):
        self.positions_mark = []

    def is_command_token(self):
        token = self.token.next
        post_token = self.token.next.next
        return token.val == "\\" and post_token.val not in ["stop", "Stop", "STOP"]

    def add_command(self, element, cmd, txt):
        self.add_text(element, txt)
        element.children.append(cmd)

    def add_text(self, element, txt):
        if txt != "":
            element.children.append(txt)

    def add_code(self, cmd):
        self.mark_line()
        formatter = lambda portion: "" if not portion else (portion[1:] if portion[0].isalnum() else portion)
        position_end = self.token.pos + len(self.token.val)
        portions = [self.scanner.buffer.buf[self.positions_mark[i]: self.positions_mark[i + 1]] for i in
                    range(0, len(self.positions_mark) - 1)]
        if len(portions) == 1:
            cmd["__code__"] = formatter(repr(portions[0]))
        else:
            cmd["__code__"] = ""
            for portion in portions:
                cmd["__code__"].children.append(formatter(repr(portion)))


    def __init__(self):
        self.scanner = None
        self.token = None  # last recognized token
        self.la = None  # lookahead token
        self.genScanner = False
        self.tokenString = ''  # used in declarations of literal tokens
        self.noString = '-none-'  # used in declarations of literal tokens
        self.errDist = Parser.minErrDist

    def getParsingPos(self):
        return self.la.line, self.la.col

    def SynErr(self, errNum):
        if self.errDist >= Parser.minErrDist:
            Errors.SynErr(errNum)

        self.errDist = 0

    def SemErr(self, msg):
        if self.errDist >= Parser.minErrDist:
            Errors.SemErr(msg)

        self.errDist = 0

    def Warning(self, msg):
        if self.errDist >= Parser.minErrDist:
            Errors.Warn(msg)

        self.errDist = 0

    def Successful(self):
        return Errors.count == 0;

    def LexString(self):
        return self.token.val

    def LookAheadString(self):
        return self.la.val

    def Get(self):
        while True:
            self.token = self.la
            self.la = self.scanner.Scan()
            if self.la.kind <= Parser.maxT:
                self.errDist += 1
                break

            self.la = self.token

    def Expect(self, n):
        if self.la.kind == n:
            self.Get()
        else:
            self.SynErr(n)

    def StartOf(self, s):
        return self.set[s][self.la.kind]

    def ExpectWeak(self, n, follow):
        if self.la.kind == n:
            self.Get()
        else:
            self.SynErr(n)
            while not self.StartOf(follow):
                self.Get()

    def WeakSeparator(self, n, syFol, repFol):
        s = [False for i in xrange(Parser.maxT + 1)]
        if self.la.kind == n:
            self.Get()
            return True
        elif self.StartOf(repFol):
            return False
        else:
            for i in xrange(Parser.maxT):
                s[i] = self.set[syFol][i] or self.set[repFol][i] or self.set[0][i]
            self.SynErr(n)
            while not s[self.la.kind]:
                self.Get()
            return self.StartOf(syFol)

    def Syntax(self):
        element = Element(name=u"document-file");
        cmd = u"";
        txt = u"";
        while self.StartOf(1):
            if self.la.kind == 8:
                cmd = self.Command()
                self.add_command(element, cmd, txt);
                txt = u"";
            elif self.la.kind == 5:
                self.Get()
                txt += self.token.val;
            elif self.la.kind == 9:
                self.CommandEscapeMark()
                txt += self.token.val[1:];
            else:
                self.Get()
                txt += self.token.val;

        self.Expect(0)
        self.add_text(element, txt)
        self.document = element;

    def Command(self):
        self.clear_marks();
        self.mark_line();
        self.CommandMark()
        while not (self.StartOf(2)):
            self.SynErr(28)
            self.Get()
        if (self.la.kind == 5):
            self.Get()
        if self.la.kind == 2 or self.la.kind == 15:
            cmd = self.SimpleCommand()
        elif self.la.kind == 18 or self.la.kind == 19 or self.la.kind == 20:
            cmd = self.ExtendedCommand()
        else:
            self.SynErr(29)
        return cmd

    def CommandEscapeMark(self):
        self.Expect(9)

    def CommandMark(self):
        self.Expect(8)

    def SimpleCommand(self):
        cmd = Element();
        content = u"";
        spaceval = "";
        name = self.CommandName()
        cmd.name = name.replace("_", "").lower()
        if (self.la.kind == 5):
            self.Get()
            spaceval = self.token.val;
        self.mark_line();
        if (self.la.kind == 10):
            self.ArgumentExpression(cmd)
            spaceval = u""
        if (self.la.kind == 5):
            self.Get()
            spaceval = self.token.val;
        self.mark_line();
        if (self.la.kind == 15):
            content = self.TextArguments()
            self.add_text(cmd, content);
            spaceval = u"";
        self.mark_line();
        self.add_code(cmd)
        cmd.children.append(spaceval)
        return cmd

    def ExtendedCommand(self):
        cmd = Element();
        name = u"";
        args = u"";
        content = u"";
        self.BeginToken()
        if (self.la.kind == 5):
            self.Get()
        name = self.CommandName()
        cmd.name = name.replace("_", "").lower()
        if (self.la.kind == 5):
            self.Get()
            content = self.token.val;
        self.mark_line();
        if (self.la.kind == 10):
            self.ArgumentExpression(cmd)
            content = u""
        self.mark_line();
        while self.StartOf(1):
            if self.StartOf(3):
                self.Get()
                content += self.token.val;
            elif self.la.kind == 5:
                self.Get()
                content += self.token.val;
            elif self.la.kind == 9:
                self.CommandEscapeMark()
                content += self.token.val[1:];
            else:
                if not self.is_command_token(): break
                cmd = self.Command()
                self.add_command(element, cmd, txt);
                content = u"";

        self.mark_line();
        self.CommandMark()
        if (self.la.kind == 5):
            self.Get()
        self.EndToken()
        self.add_text(cmd, content)
        self.add_code(cmd)
        #cmd.children.append(content) 
        return cmd

    def CommandName(self):
        if self.la.kind == 2:
            value = self.Identifier()
        elif self.la.kind == 15:
            self.IdentifierStartMark()
            value = self.Identifier()
            self.IdentifierEndMark()
        else:
            self.SynErr(30)
        return value

    def ArgumentExpression(self, cmd):
        self.ArgumentStartMark()
        if (self.la.kind == 5):
            self.Get()
        if (self.StartOf(4)):
            self.ArgumentParameters(cmd)
        if (self.la.kind == 5):
            self.Get()
        self.ArgumentEndMark()

    def TextArguments(self):
        txt = u""
        self.TextArgumentStartMark()
        while self.StartOf(5):
            if self.StartOf(6):
                if self.StartOf(7):
                    self.Get()
                elif self.la.kind == 5:
                    self.Get()
                else:
                    self.SynErr(31)
                txt += self.token.val
            elif self.la.kind == 9 or self.la.kind == 17 or self.la.kind == 26:
                if self.la.kind == 17:
                    self.TextArgumentEndEscapeMark()
                elif self.la.kind == 9:
                    self.CommandEscapeMark()
                elif self.la.kind == 26:
                    self.Get()
                else:
                    self.SynErr(32)
                txt += self.token.val[1:]
            else:
                cmd = self.Command()
                txt += cmd

        self.TextArgumentEndMark()
        return txt

    def BeginToken(self):
        if self.la.kind == 18:
            self.Get()
        elif self.la.kind == 19:
            self.Get()
        elif self.la.kind == 20:
            self.Get()
        else:
            self.SynErr(33)
        if (self.la.kind == 5):
            self.Get()
        self.Expect(21)

    def EndToken(self):
        if self.la.kind == 22:
            self.Get()
        elif self.la.kind == 23:
            self.Get()
        elif self.la.kind == 24:
            self.Get()
        else:
            self.SynErr(34)

    def ArgumentStartMark(self):
        self.Expect(10)

    def ArgumentParameters(self, cmd):
        index = 0;
        self.ArgumentParameter(cmd, index)
        index += (1 if arg.startswith("argument-") else 0)
        if (self.la.kind == 5):
            self.Get()
        while self.StartOf(8):
            while self.la.kind == 12:
                self.ArgumentSeparatorMark()

            if (self.la.kind == 5):
                self.Get()
            self.ArgumentParameter(cmd, index)
            index += (1 if arg.startswith("argument-") else 0)
            if (self.la.kind == 5):
                self.Get()

        if (self.la.kind == 5):
            self.Get()

    def ArgumentEndMark(self):
        self.Expect(11)

    def ArgumentParameter(self, cmd, index):
        args = u"";
        temp = u"";
        name = u"argument-{0}".format(index);
        args = self.TextString()
        if (self.la.kind == 5):
            self.Get()
        if (self.la.kind == 13 or self.la.kind == 14):
            self.ArgumentKeyMark()
            if (self.la.kind == 5):
                self.Get()
            temp = self.TextString()
            name, args = args, temp;
            if not name.replace("-", "").isalnum(): raise Exception("Invalid parameter name " + name);
        cmd[name] = args

    def ArgumentSeparatorMark(self):
        self.Expect(12)

    def TextString(self):
        value = u""
        if self.la.kind == 6 or self.la.kind == 7:
            value = self.CommonString()
        elif self.la.kind == 15:
            value = self.KeyString()
        elif self.la.kind == 1 or self.la.kind == 2 or self.la.kind == 3:
            value = self.AnyTextString()
        else:
            self.SynErr(35)
        return value

    def ArgumentKeyMark(self):
        if self.la.kind == 13:
            self.Get()
        elif self.la.kind == 14:
            self.Get()
        else:
            self.SynErr(36)

    def IdentifierStartMark(self):
        self.Expect(15)

    def IdentifierEndMark(self):
        self.Expect(16)

    def TextArgumentStartMark(self):
        self.Expect(15)

    def TextArgumentEndMark(self):
        self.Expect(16)

    def TextArgumentEndEscapeMark(self):
        self.Expect(17)

    def KeyStringStartMark(self):
        self.Expect(15)

    def KeyStringEndMark(self):
        self.Expect(16)

    def KeyStringEndEscapeMark(self):
        self.Expect(17)

    def Identifier(self):
        self.Expect(2)
        value = self.token.val
        while self.la.kind == 2 or self.la.kind == 21 or self.la.kind == 25:
            if self.la.kind == 21:
                self.Get()
            elif self.la.kind == 25:
                self.Get()
            else:
                self.Get()
            value += self.token.val

        return value

    def CommonString(self):
        value = u""
        if self.la.kind == 6:
            self.Get()
        elif self.la.kind == 7:
            self.Get()
        else:
            self.SynErr(37)
        value += eval("u" + self.token.val);
        return value

    def KeyString(self):
        value = u""
        self.KeyStringStartMark()
        while self.StartOf(5):
            if self.StartOf(9):
                if self.StartOf(10):
                    self.Get()
                elif self.la.kind == 5:
                    self.Get()
                else:
                    self.SynErr(38)
                value += self.token.val
            else:
                if self.la.kind == 17:
                    self.KeyStringEndEscapeMark()
                elif self.la.kind == 26:
                    self.Get()
                else:
                    self.SynErr(39)
                value += self.token.val[1:]

        self.KeyStringEndMark()
        return value

    def AnyTextString(self):
        value = u""
        value = self.AnyTextChar()
        v = u"";
        while self.la.kind == 1 or self.la.kind == 2 or self.la.kind == 3:
            v = self.AnyTextChar()
            value += v;

        return value

    def AnyTextChar(self):
        if self.la.kind == 2:
            self.Get()
        elif self.la.kind == 3:
            self.Get()
        elif self.la.kind == 1:
            self.Get()
        else:
            self.SynErr(40)
        value = self.token.val
        return value


    def Parse(self, scanner):
        self.scanner = scanner
        self.la = Token()
        self.la.val = u''
        self.Get()
        self.Syntax()
        self.Expect(0)


    set = [
        [T, x, T, x, x, T, x, x, x, x, x, x, x, x, x, T, x, x, T, T, T, x, x, x, x, x, x, x, x],
        [x, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, x],
        [T, x, T, x, x, T, x, x, x, x, x, x, x, x, x, T, x, x, T, T, T, x, x, x, x, x, x, x, x],
        [x, T, T, T, T, x, T, T, x, x, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, x],
        [x, T, T, T, x, x, T, T, x, x, x, x, x, x, x, T, x, x, x, x, x, x, x, x, x, x, x, x, x],
        [x, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, x, T, T, T, T, T, T, T, T, T, T, T, x],
        [x, T, T, T, T, T, T, T, x, x, T, T, T, T, T, T, x, x, T, T, T, T, T, T, T, T, x, T, x],
        [x, T, T, T, T, x, T, T, x, x, T, T, T, T, T, T, x, x, T, T, T, T, T, T, T, T, x, T, x],
        [x, T, T, T, x, T, T, T, x, x, x, x, T, x, x, T, x, x, x, x, x, x, x, x, x, x, x, x, x],
        [x, T, T, T, T, T, T, T, T, T, T, T, T, T, T, T, x, x, T, T, T, T, T, T, T, T, x, T, x],
        [x, T, T, T, T, x, T, T, T, T, T, T, T, T, T, T, x, x, T, T, T, T, T, T, T, T, x, T, x]

    ]

    errorMessages = {

        0: "EOF expected",
        1: "symbols expected",
        2: "identifier expected",
        3: "number expected",
        4: "numunit expected",
        5: "spaces expected",
        6: "string1 expected",
        7: "string2 expected",
        8: "\"\\\\\" expected",
        9: "\"\\\\\\\\\" expected",
        10: "\"[\" expected",
        11: "\"]\" expected",
        12: "\",\" expected",
        13: "\"=\" expected",
        14: "\":\" expected",
        15: "\"{\" expected",
        16: "\"}\" expected",
        17: "\"\\\\}\" expected",
        18: "\"start\" expected",
        19: "\"Start\" expected",
        20: "\"START\" expected",
        21: "\"-\" expected",
        22: "\"stop\" expected",
        23: "\"Stop\" expected",
        24: "\"STOP\" expected",
        25: "\".\" expected",
        26: "\"\\\\%\" expected",
        27: "??? expected",
        28: "this symbol not expected in Command",
        29: "invalid Command",
        30: "invalid CommandName",
        31: "invalid TextArguments",
        32: "invalid TextArguments",
        33: "invalid BeginToken",
        34: "invalid EndToken",
        35: "invalid TextString",
        36: "invalid ArgumentKeyMark",
        37: "invalid CommonString",
        38: "invalid KeyString",
        39: "invalid KeyString",
        40: "invalid AnyTextChar",
    }


