from typing import List

from k8s_audit_filter.abstract_classes import Factory, Field, FieldException


class ResourceGroupSubField(Field):
    def __init__(self, value: str):
        self.name = "group"
        self.value: str = value

    def check_match(self, target: dict) -> bool:
        if not self.value:
            return True
        if target["objectRef"].get("apiGroup") and target["objectRef"]["apiGroup"] == self.value:
            return True
        return False


class ResourceResourseSubField(Field):
    def __init__(self, value: List[str]):
        self.name = "resources"
        self.value: List[str] = value

    def check_match(self, target: dict) -> bool:
        for resource in self.value:
            if target["objectRef"].get("resource") and target["objectRef"]["resource"] == resource:
                return True
        return False


class ResourceNamesSubField(Field):
    def __init__(self, value: List[str]):
        self.name = "resourceNames"
        self.value: List[str] = value

    def check_match(self, target: dict) -> bool:
        for name in self.value:
            if target["objectRef"].get("name") and target["objectRef"]["name"] == name:
                return True
        return False


class ResourcesFieldsFactory(Factory):
    mapping = {
        "group": ResourceGroupSubField,
        "resources": ResourceResourseSubField,
        "resourceNames": ResourceNamesSubField,
    }

    @classmethod
    def create(cls, entities: dict):
        fields = []
        for key, value in entities.items():
            if key in cls.mapping:
                fields.append(cls.mapping[key](value))
                continue
            raise FieldException(f"Invalid subfield {key} for Resource field")
        return fields


class ResourceField(Field):
    def __init__(self, value: List[dict]):
        self.name = "resources"
        self.value = [ResourcesFieldsFactory.create(v) for v in value]

    def check_match(self, target: dict) -> bool:
        for subfield in self.value:  # type: ignore
            if all([s.check_match(target) for s in subfield]):  # type: ignore
                return True
        return False
