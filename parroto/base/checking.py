# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
from functools import wraps

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from parroto.base import is_iterable


class TypeVerifier(object):
    ThisClass = "types.ThisClass"
    type_list = None
    target = None
    function_name = ""
    variable_names = None
    default_variables = None

    def __init__(self, **type_list):
        self.type_list = type_list

    def __call__(self, func):
        self.settings(func)

        @wraps(func)
        def analyze(*args, **kwargs):
            return self.target(*args, **kwargs)

        return analyze

    def settings(self, func):
        code = func.func_code
        self.target = func
        self.function_name = func.func_name
        self.variable_names = code.co_varnames[:code.co_argcount]
        defaults = func.func_defaults or []
        self.default_variables = dict(zip(self.variable_names[-len(defaults):], defaults))

    def verify_types(self, type_list, this_class):
        if not is_iterable(type_list):
            type_list = (type_list,)
        type_list = list(type_list)
        if str in type_list:
            type_list.append(unicode)
        change = {
            self.ThisClass: this_class,
            None: type(None)
        }
        return tuple([change[c] if c in change else c for c in type_list])

    def analyze(self, *args, **kwargs):
        return self.target(*args, **kwargs)

    def warning_message(self, expected_type, actual_value, value_name="", is_args=True):
        format_message = lambda types: ', '.join(
            unicode(t).split("'")[1] for t in (types if type(types) == tuple else (types,)))
        actual_type = type(actual_value)
        expected, actual = format_message(expected_type), format_message(actual_type)
        if is_args:
            msg = "'{function_name} method accepts '{argname}' argument with type in ({types})," \
                " but was given '{value}' ({value_type})".format(
                    function_name=self.function_name,
                    argname=value_name,
                    value=actual_type,
                    types=expected,
                    value_type=actual
                )
        else:
            msg = "'{function_name} method returns value with type in ({types})," \
                " but result was '{value}' ({value_type})".format(
                    function_name=self.function_name,
                    value=actual_type,
                    types=expected,
                    value_type=actual
                )
        return msg


class ParametersTypeVerifier(TypeVerifier):
    def __init__(self, **type_list):
        super(ParametersTypeVerifier, self).__init__(**type_list)

    def analyze(self, *args, **kwargs):
        error_message = ""
        for argument_name, argtype in self.type_list.viewitems():
            try:
                argument_value = args[self.variable_names.index(argument_name)]
            except (ValueError, IndexError):
                if argument_name in kwargs:
                    argument_value = kwargs.get(argument_name)
                else:
                    argument_value = self.default_variables.get(argument_name)
            argument_types = self.verify_types(argtype,
                                               type(args[0]) if len(args) > 0 else None)
            if not isinstance(argument_value, argument_types):
                error_message += ("" if error_message == "" else "\n")
                error_message += self.warning_message(argument_types, argument_value,
                                                      argument_name, is_args=True)
        if error_message != "":
            raise TypeError(error_message)
        return self.target(*args, **kwargs)


accepts = ParametersTypeVerifier


class OutputTypeVerifier(TypeVerifier):
    return_type = None

    def __init__(self, return_type):
        self.return_type = return_type
        super(OutputTypeVerifier, self).__init__()

    def analyze(self, *args, **kwargs):
        result = self.target(*args, **kwargs)
        required_types = self.verify_types(self.return_type, type(args[0]) if len(args) > 0 else None)
        if not isinstance(result, required_types):
            msg = self.warning_message(required_types, result, is_args=False)
            raise TypeError(msg)
        return result


returns = OutputTypeVerifier
