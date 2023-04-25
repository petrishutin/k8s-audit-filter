from abc import ABC
from typing import List, Union


class Field(ABC):
    __slots__ = ("name", "value")

    def __init__(self, value: Union[str, List[str], None]):
        self.name: Union[str, None] = None
        self.value: Union[str, List[str], List[dict], List[Field], None] = value

    def __eq__(self, other):
        return self.name == other.name and self.value == other.value

    def __str__(self):
        return f"{self.__class__.__qualname__}: {self.name}={self.value}"

    __repr__ = __str__

    def check_match(self, target: dict) -> bool:
        raise NotImplementedError


class FieldException(Exception):
    pass


class Rule(ABC):
    __slots__ = ("fields", "as_dict")

    def __str__(self):
        return f"{self.__class__.__qualname__}: {self.as_dict}"

    def __eq__(self, other):
        return self.fields == other.fields

    def check_rule(self, instance: dict) -> bool:
        raise NotImplementedError


class RuleException(Exception):
    pass


class Factory(ABC):
    mapping: dict = {}

    @classmethod
    def create(cls, entity: dict):
        raise NotImplementedError
