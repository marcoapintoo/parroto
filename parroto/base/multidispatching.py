# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
from functools import wraps

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))

from parroto.base import ParameterCondition, TypeVerifier


class MultiMethodPool(object):
    """
    Collects all methods with different signatures
    """
    registry = None

    def __init__(self):
        self.registry = {}

    def assign(self, name, condition, caller):
        """
        Assign a handler for a certain signature.
        :param name: name of method stored
        :param condition: required signature
        :param caller: handler
        :return:
        """
        callers = self.registry.setdefault(name, [])
        callers.append((condition, caller))

    def matches(self, name, args, kwargs, this_class):
        """
        Search a handler that matches with calling parameters.
        :param name: name of method
        :param args: arguments
        :param kwargs: keyword arguments
        :param this_class: replacement of type of self argument
        :return:
        """
        callers = self.registry.get(name, [])
        targets = [caller for condition, caller in callers
                   if condition.match(TypeVerifier.get_call_parameters(caller, args, kwargs, strict=False),
                                      this_class=this_class,
                                      strict=True)]
        if len(targets) != 1:
            targets = [caller for condition, caller in callers
                       if condition.match(TypeVerifier.get_call_parameters(caller, args, kwargs, strict=False),
                                          this_class=this_class,
                                          strict=False)]
        if len(targets) > 0:
            caller = targets[-1]
            return caller
        raise TypeError("No method for that")


class MultiMethodVerifier(TypeVerifier):
    registry = MultiMethodPool()

    @staticmethod
    def add(name, condition, caller):
        """
        Stored a handler with a name and signature
        :param name: method name
        :param condition: signature
        :param caller: handler for method with the defined signature
        :return:
        """
        MultiMethodVerifier.registry.assign(name, condition, caller)

    def __init__(self, **conditions):
        """
        Set signature or conditions for method
        :param conditions:
        :return:
        """
        self.conditions = ParameterCondition(conditions)
        self.conditions.enable_condition_keyword = True
        super(MultiMethodVerifier, self).__init__(**conditions)

    def __call__(self, func):
        """
        Define decorator
        :param func:
        :return:
        """
        self.settings(func)
        name = "{0}.{1}".format(self.caller_name, self.function_name)
        MultiMethodVerifier.add(name, self.conditions, func)

        @wraps(func)
        def decorator(*args, **kwargs):
            this_class = args[0] if args else None
            caller = MultiMethodVerifier.registry.matches(name, args, kwargs, this_class)
            return caller(*args, **kwargs)

        return decorator


multimethod = MultiMethodVerifier

if __name__ == "__main__":
    class A(object):
        b = 10

    class B(A):
        b = 21

    class FooTest(object):
        @multimethod(variable=float)
        def method_name(self, variable, a=12, b=0, c=7, **d):
            print "Calling result:", (variable ** 2)

        @multimethod(variable=str)
        def method_name(self, variable, a=12, b=0, c=7, **d):
            print "Calling result (double string):", (variable * 2)

        @multimethod(variable=B)
        def method_name(self, variable, a=12, b=0, c=7, **d):
            print "Calling result (object children):", variable.b

        @multimethod(variable=A)
        def method_name(self, variable, a=12, b=0, c=7, **d):
            print "Calling result (object parent):", variable.b


    @multimethod(variable=float)
    def func_name(self, variable, a=12, b=0, c=7, **d):
        print "Calling result:", (variable ** 2)


    f = FooTest()
    f.method_name(121.1, 1)  # ,4,6,67,7)
    f.method_name("x", 1)  # ,4,6,67,7)
    f.method_name(B(), 1)  # ,4,6,67,7)
    # f.method_name()
    # f.method_name("+")
    #f.method_name(12.5)