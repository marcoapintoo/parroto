#!/usr/bin/python
from __future__ import print_function
import os
import sys
from termcolor import colored

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from classbase import AutoInitObject

class Message(object):
    __metaclass__ = AutoInitObject
    content = ""
    prefix_space = 0
    
    def show(self):
        print(" " * self.prefix_space + self.content, file=sys.stderr)
    
    @staticmethod
    def meta_advise(message, line, header_message, message_attr={}, prefix_space=4):
        w_message = colored(*header_message)
        w_message += colored(
            message.format(
                line=colored("line {0}".format(line),
                color="white",
                on_color="on_grey",
                attrs=['bold'])
            ), **message_attr
        )
        obj = Message(
            content=w_message,
            prefix_space=prefix_space
        )
        obj.show()
        return obj
        
    @staticmethod
    def warning(message, line="", prefix_space=4):
        return Message.meta_advise(message, line, ("WARNING: ", "blue"), prefix_space=prefix_space)
        
    @staticmethod
    def ignoredLineWarning(line, prefix_space=4):
        return Message.meta_advise("Invalid command in {line} was ignored.",
                            line, ("WARNING: ", "blue"), prefix_space=prefix_space)
        
    @staticmethod
    def error(message, line="", prefix_space=4):
        return Message.meta_advise(message, line, ("ERROR: ", "red"), prefix_space=prefix_space)
        
    @staticmethod
    def message(message, line=0, header="MESSAGE", prefix_space=4, **message_attr):
        return Message.meta_advise(
            message, line,
            header_message=("{0}: ".format(header), "cyan"),
            message_attr=message_attr,
            prefix_space=prefix_space
        )
        
    @staticmethod
    def important_advice(message="", line=0, color="green", prefix_space=4, **message_attr):
        return Message.meta_advise(
            message="",
            line=line,
            header_message=("{0}".format(message), color, None, ["bold"]),
            message_attr=message_attr,
            prefix_space=prefix_space
        )
    

