from typing import List, Union

from .abstract_classes import Factory, Field, FieldException
from .resourses_field import ResourceField


class LevelField(Field):
    def __init__(self, value: Union[str, None]):
        super().__init__(value)
        self.name: Union[str, None] = "level"
        if value is None:
            raise ValueError("Invalid value for level field")
        self.value = value

    def check_match(self, target: dict) -> bool:
        if target[self.name] == self.value:
            return True
        return False


class VerbsField(Field):
    def __init__(self, value: List[str]):
        self.name = "verb"
        self.value: List[str] = value

    def check_match(self, target: dict) -> bool:
        if target[self.name] in self.value:
            return True
        return False


class UsersField(Field):
    def __init__(self, value: List[str]):
        self.name = "user"
        self.value: List[str] = value

    def check_match(self, target: dict) -> bool:
        if target[self.name]["username"] in self.value:
            return True
        return False


class UserGroupsField(Field):
    def __init__(self, value: List[str]):
        self.name = "userGroups"
        self.value: List[str] = value

    def check_match(self, target: dict) -> bool:
        for group in target["user"]["groups"]:
            if group in self.value:
                return True
        return False


class NamespacesField(Field):
    def __init__(self, value: List[str]):
        self.name = "namespace"
        self.value: List[str] = value

    def check_match(self, target: dict) -> bool:
        for space in self.value:
            if target.get("objectRef") and target["objectRef"].get("namespace") == space:
                return True
        return False


class FieldFactory(Factory):
    mapping = {
        "level": LevelField,
        "verbs": VerbsField,
        "users": UsersField,
        "userGroups": UserGroupsField,
        "namespaces": NamespacesField,
        "resources": ResourceField,
    }

    @classmethod
    def create(cls, entities: dict):
        result = []
        for key, vale in entities.items():
            if key in cls.mapping:
                result.append(cls.mapping[key](vale))
                continue
            raise FieldException(f"Invalid field {key} for Rule")
        return result
