# !/usr/bin/python
# coding=utf-8
from __future__ import print_function

__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys

try:
    from termcolor import colored
except:
    print("Package 'termcolor' is not installed. Colors disabled", file=sys.stderr)

    def colored(text, *args, **kwargs):
        return text

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from parroto.base import AutoObject


class Message(object):
    __metaclass__ = AutoObject
    content = ""
    prefix_space = 0

    def show(self):
        """
        Show message in stderr.
        :return:
        """
        print(" " * self.prefix_space + self.content, file=sys.stderr)


    @staticmethod
    def meta_advise(message, line, header_message, message_attr={}, prefix_space=4):
        """
        Returns a generic advertisement.
        :param message:
        :param line:
        :param header_message:
        :param message_attr:
        :param prefix_space:
        :return:
        """
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
        """
        Returns a warning message with a certain number of previous spaces
        :param message:
        :param line:
        :param prefix_space:
        :return:
        """
        return Message.meta_advise(message, line, ("WARNING: ", "blue"), prefix_space=prefix_space)

    @staticmethod
    def ignored_line_warning(line, prefix_space=4):
        """
        Returns a ignored line warning message
        :param line:
        :param prefix_space:
        :return:
        """
        return Message.meta_advise("Invalid command in {line} was ignored.",
                                   line, ("WARNING: ", "blue"), prefix_space=prefix_space)

    @staticmethod
    def error(message, line="", prefix_space=4):
        """
        Returns a error message with a certain number of previous spaces
        :param message:
        :param line:
        :param prefix_space:
        :return:
        """
        return Message.meta_advise(message, line, ("ERROR: ", "red"), prefix_space=prefix_space)

    @staticmethod
    def message(message, line=0, header="MESSAGE", prefix_space=4, **message_attr):
        """
        Returns a generic message
        :param message:
        :param line:
        :param header:
        :param prefix_space:
        :param message_attr:
        :return:
        """
        return Message.meta_advise(
            message, line,
            header_message=("{0}: ".format(header), "cyan"),
            message_attr=message_attr,
            prefix_space=prefix_space
        )

    @staticmethod
    def important_advice(message="", line=0, color="green", prefix_space=4, **message_attr):
        """
        Returns an important advertisement message.
        :param message:
        :param line:
        :param color:
        :param prefix_space:
        :param message_attr:
        :return:
        """
        return Message.meta_advise(
            message="",
            line=line,
            header_message=("{0}".format(message), color, None, ["bold"]),
            message_attr=message_attr,
            prefix_space=prefix_space
        )
