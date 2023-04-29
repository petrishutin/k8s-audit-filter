from abc import ABC

from k8s_audit_filter.abstract_classes import Factory


class CountRuleException(Exception):
    pass


class CountRule(ABC):
    def __str__(self):
        return f"{self.__class__.__qualname__}"

    def get(self, instance: dict) -> list:
        raise NotImplementedError


class LevelCountRule(CountRule):
    def get(self, instance: dict):
        return [instance["level"]]


class UserCountRule(CountRule):
    def get(self, instance: dict):
        return [instance["user"]["username"]]


class GroupCountRule(CountRule):
    def get(self, instance: dict):
        return instance["user"]["groups"]


class CodesCountRule(CountRule):
    def get(self, instance: dict):
        return [instance["responseStatus"]["code"]]


class CountRuleFactory(Factory):
    mapping = {
        "level": LevelCountRule,
        "users": UserCountRule,
        "groups": GroupCountRule,
        "codes": CodesCountRule,
    }

    @classmethod
    def create(cls, entity: str) -> CountRule:
        if entity not in cls.mapping:
            raise CountRuleException(
                f"Invalid count rule. Unknown key {entity}. Must be one of {list(cls.mapping.keys())}"
            )
        return cls.mapping[entity]()
