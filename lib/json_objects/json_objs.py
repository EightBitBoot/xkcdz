
import json

all = [
    "json_obj"
]

# TODO(Adin): recursive json object building and serialization

def _create_init_func(member_names):
    # TODO(Adin): type annotations on parameters
    # TODO(Adin): type checking

    self_name = "__self_instance__" if "self" in member_names else "self"

    param_list = ", ".join([self_name] + list(member_names))
    body = "\n".join(["    {}.{} = {}".format(self_name, member, member) for member in member_names])

    exec_str = "def __init__({}):\n{}".format(param_list, body)

    ns = {}
    exec(exec_str, None, ns)

    return ns["__init__"]


def _create_from_json_dict_func(member_names):
    body_statements = ["    {} = json_dict['{}'] if '{}' in json_dict else None".format(member, member, member) for member in member_names]
    body_statements.append("    return cls({})".format(", ".join(member_names)))
    body = "\n".join(body_statements)
    
    exec_str = "def from_json_dict(cls, json_dict):\n{}".format(body)

    ns = {}
    exec(exec_str, None, ns)

    return classmethod(ns["from_json_dict"])


def _create_from_json_str_func():
    def from_json_str(cls, json_str):
        json_dict = json.loads(json_str)

        return cls.from_json_dict(json_dict)

    return classmethod(from_json_str)


def _create_to_json_dict_func(member_names):
    body_statements = ["    json_dict = {}"]
    body_statements.extend(["    json_dict['{}'] = {}".format(member, "self." + member) for member in member_names])
    body_statements.append("    return json_dict")

    body = "\n".join(body_statements)

    exec_str = "def to_json_dict(self):\n{}".format(body)

    ns = {}
    exec(exec_str, None, ns)
    
    return ns["to_json_dict"]


def _create_to_json_func():
    def to_json(self):
        return json.dumps(self.to_json_dict())

    return to_json


def _create_repr_func(class_name, member_names):
    in_str_list = ", ".join(["{}={{}}".format(member) for member in member_names])
    format_arg_list =  ", ".join("self." + member for member in member_names)

    body = "    return '{}({})'.format({})".format(class_name, in_str_list, format_arg_list)

    exec_str = "def __repr__(self):\n{}".format(body)

    ns = {}
    exec(exec_str, None, ns)

    return ns["__repr__"]


def _create_str_func():
    def __str__(self):
        return json.dumps(self.to_json_dict(), indent=4)

    return __str__


def json_obj(cls):
    if "__annotations__" not in cls.__dict__:
        raise AttributeError("{} has no annotated class variables".format(cls.__name__))

    member_names = cls.__dict__["__annotations__"].keys()

    if "__init__" not in cls.__dict__:
        setattr(cls, "__init__", _create_init_func(member_names))

    if "from_json_dict" not in cls.__dict__:
        setattr(cls, "from_json_dict", _create_from_json_dict_func(member_names))

    if "from_json_str" not in cls.__dict__:
        setattr(cls, "from_json_str", _create_from_json_str_func())

    if "to_json_dict" not in cls.__dict__:
        setattr(cls, "to_json_dict", _create_to_json_dict_func(member_names))

    if "to_json" not in cls.__dict__:
        setattr(cls, "to_json", _create_to_json_func())

    if "__repr__" not in cls.__dict__:
        setattr(cls, "__repr__", _create_repr_func(cls.__name__, member_names))

    if "__str__" not in cls.__dict__:
        setattr(cls, "__str__", _create_str_func())

    return cls
    