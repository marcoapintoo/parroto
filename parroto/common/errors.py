#!/usr/bin/python
import os
import sys
import inspect

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from consolemsg import Message
#from classbase import AutoInitObject

class Error(Exception):
    #__metaclass__ = AutoInitObject
    
    def __init__(self, message = ""):
        return super(Error, self).__init__(message)
    
    @staticmethod
    def warning(message, line=0):
        msg = Message.warning(message, line)
        return Error(msg.content)
        
    @staticmethod
    def error(message, line=0):
        msg = Message.error(message, line)
        return Error(msg.content)
        
    @staticmethod
    def information(message, line=0, header="MESSAGE", **message_attr):
        msg = Message.message(
            content=message,
            line=line,
            header=header,
            **message_attr
        )
        return Error(msg.message)

    @staticmethod
    def not_implemented():
        filename, current_line, function_name = inspect.stack()[1][1:4]
        return Error.error(
            "Method {name} is not implemented at line {line} in {filename}" \
            .format(
                name=function_name,
                line=current_line,
                filename=filename
            )
        )
    
    @staticmethod
    def bad_argument_type(name, vartype, value, expected_type):
        filename, current_line, function_name = inspect.stack()[1][1:4]
        message_error = ("Expected variable {varname} " \
             "with type {expected_type}, " \
             "but received {value} with type {vartype}.").format(
                varname=name,
                vartype=vartype,
                expected_type=expected_type,
                value=value
            )
        message_exception = ("In method {name}, at line " \
            "{line} in {filename}. {error}").format(
                name=function_name,
                line=current_line,
                filename=filename,
                error=message_error,
            )
        return TypeError(Error.error(
            message_exception
        ))
    
    
    @staticmethod
    def bad_attribute_value(attribute, valid_values, value):
        message = ("Attribute 'attribute' only allows values: {values}" \
            " and '{value}' was setted").format(
                values = valid_values,
                value = value
            )
        return ValueError(Error.error(message))
