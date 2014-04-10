#!/usr/bin/python
import os
import sys
from functools import wraps
from common.typecheck import is_iterable
#from common.errors import Error

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../"))


class type_verification(object):
    ThisClass = "types.ThisClass"
    typelist = None
    target = None
    function_name = ""
    variable_names = None
    default_variables = None
    
    def __init__(self, **typelist):
        self.typelist = typelist
    
    def __call__(self, func):
        self.settings(func)
        #self.analyze.__module__ = #self.__module__
        @wraps(func)
        def analyze(*args, **kwargs):
            return self.target(*args, **kwargs)
        return analyze
        #return wraps(func)(self.analyze)
        #return update_wrapper(self.analyze, func)
    
    def settings(self, func):
        code = func.func_code
        self.target = func
        self.function_name = func.func_name
        self.variable_names = code.co_varnames[:code.co_argcount]
        defaults = func.func_defaults or []
        self.default_variables = dict(zip(self.variable_names[-len(defaults):], defaults))
        
    def _verify_type_lists(self, typelist, thisclass):
        if not is_iterable(typelist):
            typelist = (typelist,)
        typelist = list(typelist)
        if str in typelist:
            typelist.append(unicode)
        change = {
            self.ThisClass: thisclass,
            None: type(None)
        }
        return tuple([change[c] if c in change else c for c in typelist])
    
    def analyze(self, *args, **kwargs):
        return self.target(*args, **kwargs)
    
    def warning_message(self, expected_type, actual_value, value_name="", is_args=True):
        #formatmsg = lambda types: ', '.join(str(t).split("'")[1] for t in (types if type(types) == tuple else (types,)))
        formatmsg = lambda types: ', '.join(unicode(t).split("'")[1] for t in (types if type(types) == tuple else (types,)))
        actual_type = type(actual_value)
        expected, actual = formatmsg(expected_type), formatmsg(actual_type)
        if is_args:
            msg = "'{fname} method accepts '{argname}' argument with type in ({types}), but was given '{value}' ({value_type})".format(
                fname=self.function_name,
                argname=value_name,
                value=actual_type,
                types=expected,
                value_type=actual
            )
        else:
            msg = "'{fname} method returns value with type in ({types}), but result was '{value}' ({value_type})".format(
                fname=self.function_name,
                value=actual_type,
                types=expected,
                value_type=actual
            )
        return msg



class accepts(type_verification):
    def __init__(self, **typelist):
        super(accepts, self).__init__(**typelist)
    
    def analyze(self, *args, **kwargs):
        errormsg = ""
        for argname, argtype in self.typelist.viewitems():
            try:
                argval = args[self.variable_names.index(argname)]
            except (ValueError, IndexError):
                if argname in kwargs:
                    argval = kwargs.get(argname)
                else:
                    argval = self.default_variables.get(argname)
            argtypes = self._verify_type_lists(argtype, type(args[0]) if len(args) > 0 else None)
            if not isinstance(argval, argtypes):
                errormsg += ("" if errormsg == "" else "\n")
                errormsg += self.warning_message(argtypes, argval, argname, is_args=True)
        if errormsg != "":
            raise TypeError(errormsg)
        return self.target(*args, **kwargs)


class returns(type_verification):
    return_type = None
    
    def __init__(self, return_type):
        self.return_type = return_type
        super(returns, self).__init__()
    
    def analyze(self, *args, **kwargs):
        result = self.target(*args, **kwargs)
        required_types = self._verify_type_lists(self.return_type, type(args[0]) if len(args) > 0 else None)
        if not isinstance(result, required_types):
            msg = self.warning_message(required_types, result, is_args=False)
            raise TypeError(msg)
        return result


