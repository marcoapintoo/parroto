# !/usr/bin/python
# coding=utf-8
__author__ = 'Marco Antonio Pinto Orellana'
import os
import sys
import re
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


class DocumentData(object):
    __metaclass__ = AutoObject
    pool = None
    private_pool = None

    def __init__(self):
        self.pool = CommandPool()
        self.private_pool = CommandPool()

    def __str__(self):
        return str(self.__dict__)


class CommandData(object):
    __metaclass__ = AutoObject
    __line = 0
    __column = 0
    __filename = ""
    __name = ""
    __structure = None
    __content = None
    document = None

    def __init__(self, line=0, column=0, filename="", name="", structure=None):
        self.__line = line
        self.__column = column
        self.__filename = filename
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
        return self.__filename

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

            call_wrapper.handler = handler
            call_wrapper.key = key
            return call_wrapper

        for key, handler in self.items():
            target[key] = create_handler(handler, key)


class AutoDict(dict):
    def __missing__(self, key):
        return key


class StringCode(object):
    __metaclass__ = AutoObject
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
        return code

    # def is_runnable(self):
    # conditions = [
    # "return" in self.code,
    #         "+=" in self.code,
    #         re.search(r"\.\s*append\s*\(", self.code) is not None,
    #         re.search(r"\bresult\b", self.code) is not None,
    #         re.search(r"\b{0}\b".format(self.var_name), self.code) is not None,
    #         ]
    #     return any(conditions)

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
        indent = min(re.search(r"[^\s]", line).start() for line in lines if line.strip() != "")
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

    def join_arguments(self, reference, *newvalues):
        result = reference.copy()
        for collection in newvalues:
            for key, value in collection.items():
                if key in result:
                    result[key] = value
        return result

    def call(self, command, *args, **kwargs):
        try:
            code = compile(self.get_code(), "<command:{}>{}".format(self.codename(), self.get_code()), "exec")
            # exec code in globals(), locals()
            variables = {}
            command.document.private_pool.fill_callable(variables, command.document)
            command.document.pool.fill_callable(variables, command.document)
            variables["document"] = command.document
            variables["command"] = command
            function_locals = {}
            exec code in variables, function_locals
            handler = function_locals["string_code"]
            arguments = self.join_arguments(self.arguments, command.arguments, kwargs)  #WHY??
            return handler(**arguments)
        except Exception, e:
            Message.error("Executing {}: {}".format(self.codename(), str(e)))
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
    def private_pool(self):
        return self.document.private_pool

    def default_pool(self):
        self.pool.setdefault("document-file", self.walk_command)
        self.pool.setdefault("text", self.walk_command)
        self.pool.setdefault("define", self.define_command)

    @staticmethod
    def walk_command(command, *args, **kwargs):
        return command.structure.value if command.structure.value else command.content

    @staticmethod
    def define_command(command, *args, **kwargs):
        command_name = command.structure.get("argument-0") or command.structure.get("name")
        arguments = command.structure.get("arguments", "{}")
        if is_a(arguments, Element):
            arguments = CommandWalker(root=arguments, document=command.document).walk()
        if is_a(command_name, Element):
            command_name = CommandWalker(root=command_name, document=command.document).walk()
        # command.document.pool[command_name] = lambda *arg, **a: "3"
        string_command = StringCommand(command=command.structure, arguments=arguments)
        command.document.pool[command_name] = string_command
        return ""

    def command_sentence(self, **kwargs):
        return CommandData(structure=self.root, name=self.root.name, document=self.document, **kwargs)

    def walk(self):
        parameters = {}
        specials = {}
        for property_name, node_value in self.root.attributes.items():
            command_node = CommandWalker(root=node_value, document=self.document).walk()
            self.assign_special_properties(parameters, specials, property_name, command_node)
            # if is_a(node<-node_value)
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
    interpreter = BaseSelector()
    element = interpreter.process(r"""
#!compiler: patex
#!/usr/bin/parroto
#!compiler: patex

\start-define[message,arguments={text: "default",}]
    print 11111111111, text
    return text*4
\stop
\start-define[my-command,arguments={text: "default", text2: "33"}]
    return 3*text, 54, message.key, message.handler.get_code(), message(text=text2)
\stop
\start-execute[named, arguments={}]
    document.language = "english"
    document.call_stack = []
    document.counter = {}
    document.packages = set()
    print "COMMAND:", command
    return ""
\stop
\my-command{}
aa
\my-command[text="aaa "]
\my-command[text2="p"]
""")
    # print element.xml_string
    # print interpreter.instructions
    walker = CommandWalker(root=element, document=DocumentData())
    print walker.walk()
    print walker.document

