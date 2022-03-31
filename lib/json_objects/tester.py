#!/usr/bin/env python3

from json_objs import json_obj

from dataclasses import dataclass

@json_obj
class TestClass:
    foo: int
    bar: str
    fun: None

    def test_method(self):
        pass


# @json_obj
class PrevInit:
    foo: int
    bar: str
    fun: None

    def __init__(self):
        print("haha cherade you are")


def main():
    test1 = TestClass(10, "hi", None)
    test1_json = test1.to_json()

    test2 = TestClass.from_json_str(test1_json)
    print(repr(test2))

    print(test2)


if __name__ == "__main__":
    main()