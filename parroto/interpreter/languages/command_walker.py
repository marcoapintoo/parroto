# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
import re
from functools import wraps
from pyquery import PyQuery

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "../../../"))

from parroto.base import AutoObject, is_a, Message, multimethod
from parroto.interpreter.languages.meta.element import Element
from command_interpreter import BaseSelector


class CommandStructure(PyQuery):
    def __init__(self, *args, **kwargs):
        super(CommandStructure, self).__init__(*args, **kwargs)

    def _raw_sub_nodes(self):
        result = []
        sub_nodes = self.children()
        for raw_child in sub_nodes:
            child = PyQuery(raw_child)
            child_name = self.first_tag_name(child)
            result.append((child, "." in child_name))
        return result

    def sub_nodes(self):
        if self.is_attribute:
            return []
        return [CommandStructure(child)
                for child, is_attr in self._raw_sub_nodes() if not is_attr]

    def properties(self):
        if self.is_attribute:
            return []
        return [CommandStructure(child)
                for child, is_attr in self._raw_sub_nodes() if is_attr]

    def first_tag_name(self, element=None):
        if not element:
            element = self
        return element[0].tag if len(element) else ""

    @property
    def is_attribute(self):
        return "." in self.first_tag_name()


class EventCollection(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)

    def add(self, handler, condition):
        condition_code = condition
        if condition_code.strip() == "*":
            condition = lambda command: True
        else:
            try:
                code = compile(condition_code, "<<", "eval")
                condition = lambda command: eval(code, {}, {"command": command})
            except Exception, e:
                condition = lambda command: command.name.lower().strip() == condition_code.lower().strip()
        self.append((handler, condition))

    def execute(self, command, *args, **kwargs):
        for handler, condition in self:
            if condition(command):
                handler(command, *args, **kwargs)


class DocumentContextData(object):
    __metaclass__ = AutoObject
    pool = None
    events = None
    filename = "<stdin>"

    def __init__(self):
        self.pool = CommandPool()
        self.events = {}

    def __str__(self):
        return str(self.__dict__)

    @multimethod()
    def raise_event(self, event, command):
        self.events.setdefault(event, EventCollection())
        self.events[event].execute(command)

    @multimethod(event=(list, tuple, set))
    def raise_event(self, event, command):
        for e in event:
            self.raise_event(e, command)

    def find_tag(self, tag_name):
        return self.pool.find_tag(tag_name)

    def exists_tag(self, tag_name):
        return self.pool.exists_tag(tag_name)

    def execute(self, tag_name, *args, **kwargs):
        return self.pool.execute(tag_name, *args, **kwargs)

    def fill_callable(self, target, document):
        return self.pool.fill_callable(target, document)


class DocumentFlag(dict):
    def __init__(self, *args, **kwargs):
        super(DocumentFlag, self).__init__(*args, **kwargs)

    def __getitem__(self, item):
        return super(DocumentFlag, self).__getitem__(item.lower())

    def __setitem__(self, key, value):
        super(DocumentFlag, self).__setitem__(key.lower(), value)

    def __missing__(self, key):
        # self.disable(key)
        self.enable(key)
        return self[key]

    def enable(self, key):
        self[key] = True

    def disable(self, key):
        self[key] = False


class DocumentData(DocumentContextData):
    scopes = None
    flags = None

    def __init__(self):
        super(DocumentData, self).__init__()
        self.scopes = []
        self.flags = DocumentFlag()

    def create_context(self, filename="<stdin>"):
        self.scopes.append(DocumentContextData(filename=filename))

    def last_context(self):
        return self.scopes[-1]

    def __scopes(self):
        results = [self.pool]
        results.extend(self.scopes)
        return results

    def __scope_find_tag(self, tag_name):
        results = [pool.find_tag(tag_name) for pool in self.__scopes()]
        for pos, result in enumerate(results):
            if result is not None:
                return pos, result
        return -1, None

    def find_tag(self, tag_name):
        return self.__scope_find_tag(tag_name)[1]

    def exists_tag(self, tag_name):
        return self.find_tag(tag_name) is not None

    def execute(self, tag_name, *args, **kwargs):
        pos, result = self.__scope_find_tag(tag_name)
        if pos == -1:
            return ""
        return self.__scopes()[pos].execute(tag_name, *args, **kwargs)

    def fill_callable(self, target, document):
        for pool in self.__scopes():
            pool.fill_callable(target, document)


class CommandData(object):
    __metaclass__ = AutoObject
    __line = 0
    __column = 0
    __name = ""
    __structure = None
    __content = None
    document = None

    def __init__(self, line=0, column=0, name="", structure=None):
        self.__line = line
        self.__column = column
        # self.__filename = filename
        self.__name = name
        self.__structure = structure
        # self.__content = content

    @property
    def line(self):
        return self.__line

    @property
    def column(self):
        return self.__column

    @property
    def filename(self):
        # return self.__filename
        return self.document.filename

    @property
    def name(self):
        return self.__name

    @property
    def structure(self):
        return self.__structure

    @property
    def arguments(self):
        return {k: (CommandWalker(root=v, document=self.document).walk() if is_a(v, Element) else v) for k, v in
                self.raw_arguments.items()}

    @property
    def raw_arguments(self):
        forbidden = ("__line__", "__column__", "__code__")
        if not self.structure:
            return {}
        return {k: v for k, v in self.structure.attributes.items() if k not in forbidden}

    @property
    def content(self):
        text = ""
        for node in self.__structure.children:
            walker = CommandWalker(root=node, document=self.document)
            text += walker.walk()
        return text


class CommandPool(dict):
    def __init__(self, *args, **kwargs):
        super(CommandPool, self).__init__(*args, **kwargs)

    def find_tag(self, tag_name):
        return self.get(tag_name, None)

    def exists_tag(self, tag_name):
        return self.find_tag(tag_name) is not None

    def execute(self, tag_name, *args, **kwargs):
        handler = self.find_tag(tag_name)
        return handler(*args, **kwargs) if handler else "[{}]".format(tag_name)

    def fill_callable(self, target, document):
        def create_handler(handler, key):
            def call_wrapper(*args, **kwargs):
                return handler(CommandData(document=document), *args, **kwargs)

            return call_wrapper

        for key, handler in self.items():
            target[key] = create_handler(handler, key)


class AutoDict(dict):
    def __missing__(self, key):
        return key


class StringCode(object):
    code = ""
    var_name = "<name>"
    arguments = {}

    def __init__(self, code, name, arguments):
        self.code = code
        self.var_name = name
        self.arguments = arguments

    def drain(self):
        base_code = self.clean_base_code()
        base_code = self.indent_text(0, base_code)
        if self.is_inline_sentence(base_code):
            base_code = "return {}".format(base_code.strip())
        elif not self.is_group_sentence(base_code):
            base_code = "return {}".format(repr(base_code))
        if base_code.strip() == "":
            base_code = "pass"
        code = """
def string_code({params}):
    {code}
            """.format(
            params=",".join("{}={}".format(k, repr(str(v))) for k, v in self.arguments.items()),
            code=base_code.replace("\n", "\n    ").strip()
        ).strip()
        return code

    def clean_base_code(self):
        code = self.code
        if code.startswith("'") and code.endswith("'") or \
                        code.startswith('"') and code.endswith('"'):
            code = eval(code)
        code = "\n".join(line[:line.find("#")] if line.find("#") >= 0 else line for line in code.split("\n"))
        return code

    def is_inline_sentence(self, code):
        try:
            compile(code, "<command:{}>".format(self.var_name), "eval")
            return True
        except (IndentationError, SyntaxError):
            return False

    def is_group_sentence(self, code):
        try:
            compile(code, "<command:{}>".format(self.var_name), "exec")
            return True
        except (IndentationError, SyntaxError), e:
            if "'return'" in e.msg:
                return True
            return False

    def indent_text(self, indent_base=0, code=None):
        if not code:
            code = self.code
        lines = code.split("\n")
        first_indent = -1
        indent_list = [re.search(r"[^\s]", line).start() \
                       for line in lines \
                       if line.strip() != "" and \
                       (line.find("#") < 0 or line[:line.find("#")].strip() != "")]
        indent = min(indent_list) if indent_list else 0
        for index, line in enumerate(lines):
            if first_indent < 0 and line.strip() != "":
                first_indent = re.search(r"[^\s]", line).start()
            if line.strip() != "":
                lines[index] = re.sub("^" + r"\s" * indent, "", line)
                while True:
                    fline = lines[index]
                    lines[index] = re.sub(r"^(\t*?)\t([^\t])", r"\1    \2", fline)
                    if lines[index] == fline:
                        break
        return ("\n" + " " * (4 * indent_base)).join(lines)


class StringCommand(object):
    __metaclass__ = AutoObject
    __name__ = ""
    __command = None
    __arguments = None

    def __init__(self, command, arguments={}):
        self.__command = command
        self.arguments = arguments

    @property
    def arguments(self):
        return self.__arguments

    @arguments.setter
    @multimethod(value=dict)
    def arguments(self, value):
        self.__arguments = value


    @arguments.setter
    @multimethod(value=str)
    def arguments(self, value):
        self.arguments = StringCommand.format_arguments(value)

    def codename(self):
        return self.__command.name.replace("-", "_")

    def get_code(self):
        code = self.__command["__code__"][2].value
        exec_code = StringCode(code=code, name=self.codename(), arguments=self.arguments)
        return exec_code.drain()

    def join_arguments(self, reference, *new_values):
        result = reference.copy()
        for collection in new_values:
            for key, value in collection.items():
                if key in result:
                    result[key] = value
        return result

    def unsecure_call(self, command, *args, **kwargs):
        code = compile(self.get_code(), "<command:{}>{}".format(self.codename(), self.get_code()), "exec")
        # exec code in globals(), locals()
        variables = {}
        # !command.document.private_pool.fill_callable(variables, command.document)
        # !command.document.pool.fill_callable(variables, command.document)
        command.document.fill_callable(variables, command.document)
        variables["document"] = command.document
        variables["command"] = command
        function_locals = {}
        exec code in variables, function_locals
        handler = function_locals["string_code"]
        arguments = self.join_arguments(self.arguments, command.arguments, kwargs)  # WHY??
        return handler(**arguments)

    def call(self, command, *args, **kwargs):
        try:
            return self.unsecure_call(command, *args, **kwargs)
        except Exception, e:
            Message.error("Executing {}: {}. {}".format(self.codename(), str(e), command.name))
            raise e

    def __call__(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    @staticmethod
    def format_arguments(__argument_text):
        try:
            arguments = dict(eval(__argument_text, {}, AutoDict(locals())))
        except:
            try:
                arguments = eval("[{}]".format(__argument_text), {}, AutoDict(locals()))
                arguments = {key: "" for key in arguments}
            except:
                try:
                    arguments = eval("{{{}}}".format(__argument_text), {}, AutoDict(locals()))
                except:
                    Message.error("Invalid arguments format: {}".format(arguments))
                    arguments = {}
        return arguments


class LoadFile(object):
    __metaclass__ = AutoObject
    filename = ""
    document = None
    extension = ".parroto"

    def __init__(self):
        pass

    def load(self):
        self.document.create_context(self.filename)
        interpreter = BaseSelector()
        element = interpreter.process_file(self.filename)
        walker = CommandWalker(root=element, document=self.document)
        return walker.walk()


def add_events(handler):
    @wraps(handler)
    def handler_with_event(command, *args, **kwargs):
        events_enabled = command.document.flags["events"]
        if events_enabled:
            command.document.raise_event("enter", command)
        return_value = handler(command, *args, **kwargs)
        if events_enabled:
            command.document.raise_event(("leave", "exit"), command)
        return return_value

    return handler_with_event


class CommandWalker(object):
    __metaclass__ = AutoObject
    root = None
    document = None

    def __init__(self):
        self.default_pool()

    @property
    def pool(self):
        return self.document.pool

    @property
    def private_pools(self):
        return self.document.__scopes()

    def default_pool(self):
        self.pool.setdefault("document-file", self.walk_command)
        self.pool.setdefault("text", self.walk_command)
        self.pool.setdefault("define", self.define_command)
        self.pool.setdefault("execute", self.execute_command)
        self.pool.setdefault("event", self.event_command)
        self.pool.setdefault("include", self.include_command)
        self.pool.setdefault("document-flag", self.document_flag_command)
        self.pool.setdefault("document-flags", self.document_flag_command)

    @staticmethod
    def __get_argument(command, name, default):
        value = command.structure.get(name, default)
        if is_a(value, Element):
            return CommandWalker(root=value, document=command.document).walk()
        return value

    @staticmethod
    def document_flag_command(command, *args, **kwargs):
        enabled = CommandWalker.__get_argument(command, "enabled", "")
        disabled = CommandWalker.__get_argument(command, "disabled", "")
        for name in enabled.split(","):
            command.document.flags.enable(name.strip())
        for name in disabled.split(","):
            command.document.flags.disable(name.strip())
        return ""

    @staticmethod
    @add_events
    def include_command(command, *args, **kwargs):
        filename = command.content
        return LoadFile(filename=filename, document=command.document).load()

    @staticmethod
    @add_events
    def execute_command(command, *args, **kwargs):
        string_command = StringCommand(command=command.structure)
        return string_command(command, *args, **kwargs) or ""

    @staticmethod
    @add_events
    def walk_command(command, *args, **kwargs):
        return command.structure.value if command.structure.value else command.content

    @staticmethod
    @add_events
    def define_command(command, *args, **kwargs):
        command_name = command.structure.get("argument-0") or command.structure.get("name")
        arguments = command.structure.get("arguments", "{}")
        if is_a(arguments, Element):
            arguments = CommandWalker(root=arguments, document=command.document).walk()
        if is_a(command_name, Element):
            command_name = CommandWalker(root=command_name, document=command.document).walk()
        string_command = StringCommand(command=command.structure, arguments=arguments)
        command.document.pool[command_name] = add_events(string_command)
        return ""

    @staticmethod
    def event_command(command, *args, **kwargs):
        event_name = command.structure.get("argument-0") or command.structure.get("at")
        apply_to = command.structure.get("apply-to", "*")
        if is_a(apply_to, Element):
            apply_to = CommandWalker(root=apply_to, document=command.document).walk()
        if is_a(event_name, Element):
            event_name = CommandWalker(root=event_name, document=command.document).walk()
        string_command = StringCommand(command=command.structure)
        command.document.events.setdefault(event_name, EventCollection())
        command.document.events[event_name].add(handler=string_command, condition=apply_to)
        return ""

    def command_sentence(self, **kwargs):
        return CommandData(structure=self.root, name=self.root.name, document=self.document, **kwargs)

    def walk(self):
        parameters = {}
        specials = {}
        for property_name, node_value in self.root.attributes.items():
            command_node = CommandWalker(root=node_value, document=self.document).walk()
            self.assign_special_properties(parameters, specials, property_name, command_node)
        command_data = self.command_sentence(**specials)
        parameters["command"] = command_data
        parameters["document"] = self.document
        return unicode(self.pool.execute(self.root.name, **parameters))

    @staticmethod
    def assign_special_properties(parameters, specials, name, value):
        if name == "__line__":
            specials["line"] = value
        elif name == "__column__":
            specials["column"] = value
        elif name == "__code__":
            pass
        else:
            parameters[name] = value


if __name__ == "__main__":
    loader = LoadFile(
        # filename="example01.parroto",
        filename="tex-base.parroto",
        document=DocumentData()
    )
    print loader.load()

