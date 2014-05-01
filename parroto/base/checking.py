# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
import inspect
import types
from functools import wraps

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from parroto.base import is_iterable, neutral

class ParameterCondition(dict):
    ThisClass = "<<this>>"
    MethodType = types.MethodType
    UnboundMethodType = types.UnboundMethodType
    condition_keyword = "when"
    enable_condition_keyword = False

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def has_condition(self):
        return self.condition_keyword in self

    def match(self, parameters, this_class=None, strict=True, raise_error=False, messages=None):
        """
        Verify if signature matches with parameters sent.
        :param parameters: arguments sent to method.
        :param this_class: Class of "self" argument.
        :param strict: if False subclasses will be considered valid too.
        :param raise_error: if True an exception will be raised.
        :param messages: list that will store the message results: (message, semantic_message)
        :return:
        """
        if messages is None:
            messages = []
        message = ""
        semantic_message = ""
        for parameter, expected_types in self.items():
            if parameter == self.condition_keyword and self.enable_condition_keyword:
                result = eval(expected_types, globals(), parameters)
                if not result:
                    semantic_message = "Semantic predicate '{expected_types}' " \
                                       "with result '{result}' is not valid.".format(**locals())
                continue
            expected_types = self.get_types(expected_types, this_class)
            value = parameters[parameter]
            value_type = type(value)
            # is_type = isinstance(value, expected_types) if strict else issubclass(value_type, expected_types)
            is_type = value_type in expected_types if strict else issubclass(value_type, expected_types)
            if not is_type:
                message += "Parameter '{parameter}' with type {expected_types} " \
                           "expected. Value '{value}' ({value_type}) is not valid.".format(**locals())
        if (message + semantic_message) != "" and raise_error:
            raise TypeError(message + semantic_message)
        messages.extend((message, semantic_message))
        return not message and not semantic_message

    def get_types(self, type_list, this_class):
        """
        Returns a list with types. It replaces special symbols with types,
        and does some fixings on this list: adding unicode when str is found.
        :param type_list: types that would be analyzed
        :param this_class: class that represent current "self" parameter
        :return:
        """
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


class TypeVerifier(object):
    # ThisClass = "types.ThisClass"
    type_list = None
    target = None
    function_name = ""
    variable_names = None
    default_variables = None
    caller_name = ""

    def __init__(self, **type_list):
        self.type_list = ParameterCondition(type_list)

    def __call__(self, func):
        """
        Defines the decorator
        :param func:
        :return:
        """
        self.settings(func)

        @wraps(func)
        def analyze(*args, **kwargs):
            return self.analyze(*args, **kwargs)

        return analyze

    def settings(self, func):
        """
        Obtain parameters from a function: name, variable names, default parameters, and so on.
        :param func:
        :return:
        """
        code = func.func_code
        self.target = func
        self.function_name = func.func_name
        self.variable_names = code.co_varnames[:code.co_argcount]
        defaults = func.func_defaults or []
        self.default_variables = dict(zip(self.variable_names[-len(defaults):], defaults))
        current_frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(current_frame, 2)
        # self.caller_name = caller_frame[1][3]
        self.caller_name = caller_frame[2][3]

    def analyze(self, *args, **kwargs):
        """
        Default caller
        :param args:
        :param kwargs:
        :return:
        """
        return self.target(*args, **kwargs)

    def warning_message(self, expected_type, actual_value, value_name="", is_args=True):
        """
        Returns a warning message when method signature is failed or returns type is failed
        :param expected_type:
        :param actual_value:
        :param value_name:
        :param is_args: defined if message corresponds to return type (False) or accepted types (True)
        :return:
        """
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
                value_type=actual)
        else:
            msg = "'{function_name} method returns value with type in ({types})," \
                " but result was '{value}' ({value_type})".format(
                function_name=self.function_name,
                value=actual_type,
                types=expected,
                value_type=actual)
        return msg

    def call_method(self, obj, args, kwargs):
        """
        Call a method with only parameters defined in its signature.
        :param obj:
        :param args:
        :param kwargs:
        :return:
        """
        names, varargs, keywords, defaults = inspect.getargspec(self.target)
        if keywords:
            named_args = dict((k, v) for k, v in kwargs.items() if k in names)
            self.target(obj, *args, **named_args)
        else:
            self.target(obj, *args)

    def call_parameters(self, args, kwargs):
        """
        Obtain signature and values of the stored target method.
        :param args:
        :param kwargs:
        :return:
        """
        return TypeVerifier.get_call_parameters(self.target, args, kwargs)

    @staticmethod
    def get_call_parameters(target, args, kwargs, strict=True):
        """
        Obtain signature and values of a target method.
        :param target: method to verify
        :param args:
        :param kwargs:
        :param strict:
        :return:
        """
        function_name = target.func_name
        names, varargs, keywords, defaults = inspect.getargspec(target)
        len_args = min(len(names), len(args))
        named_args = list(args[:len_args])
        unnamed_args = args[len_args + 1:]
        default_parameters = list(defaults[len_args - len(names):]) if defaults else []
        fill_none = [neutral] * (len(names) - len_args - len(default_parameters))
        parameters = dict(zip(names, named_args + fill_none + default_parameters)
                          + [(k, v) for k, v in kwargs.items() if k in names])
        keyword_args = [(k, v) for k, v in kwargs.items() if k not in names]
        if keywords:
            parameters[keywords] = keyword_args
        elif keyword_args and strict:
            raise TypeError("{name}() got an unexpected keyword argument '{names}' ".format(
                name=function_name,
                names="', '".join(kwargs.keys())))
        elif keyword_args:
            return {}
        if varargs:
            parameters[varargs] = unnamed_args
        elif unnamed_args or any(o == neutral for o in parameters.values()):
            if strict:
                raise TypeError("{name}() takes exactly {number} arguments ({total} given) ".format(
                    name=function_name,
                    number=len(names),
                    total=len(args)))
            return {}
        return parameters


class ParametersTypeVerifier(TypeVerifier):
    def __init__(self, **type_list):
        super(ParametersTypeVerifier, self).__init__(**type_list)

    def analyze(self, *args, **kwargs):
        """
        Verify signature, and raise an error if does not exist an method that matches.
        :param args:
        :param kwargs:
        :return:
        """
        messages = []
        match = self.type_list.match(self.call_parameters(args, kwargs),
                                     this_class=type(args[0]) if args else None,
                                     strict=False,
                                     messages=messages)
        if not match:
            raise TypeError(messages[0])
        return self.target(*args, **kwargs)


accepts = ParametersTypeVerifier


class OutputTypeVerifier(TypeVerifier):
    return_type = None

    def __init__(self, return_type):
        self.return_type = return_type
        super(OutputTypeVerifier, self).__init__()

    def analyze(self, *args, **kwargs):
        """
        Verify output type result.
        :param args:
        :param kwargs:
        :return:
        """
        result = self.target(*args, **kwargs)
        required_types = self.type_list.get_types(self.return_type, this_class=type(args[0]) if args else None)
        if not isinstance(result, required_types):
            msg = self.warning_message(required_types, result, is_args=False)
            raise TypeError(msg)
        return result

returns = OutputTypeVerifier
ThisClass = ParameterCondition.ThisClass


if __name__ == "__main__":
    class Foo(object):
        b = 122

        @returns(None)
        @accepts(a=(int, str, ThisClass))
        def param1(self, a):
            print self.b, a, type(a)

    f = Foo()
    f.param1(12)
    f.param1("s--s")
    f.param1(f)