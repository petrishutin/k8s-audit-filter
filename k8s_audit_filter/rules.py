from .abstract_classes import Factory, Rule, RuleException
from .fields import FieldFactory


class RuleInitMixin:
    def __init__(self, fields: dict):
        self.as_dict = fields
        self.fields = FieldFactory.create(fields)


class IncludeRule(Rule, RuleInitMixin):
    def check_rule(self, instance: dict) -> bool:
        for field in self.fields:
            if not field.check_match(instance):
                return False
        return True


class ExcludeRule(Rule, RuleInitMixin):
    def check_rule(self, instance: dict) -> bool:
        for field in self.fields:
            if field.check_match(instance):
                return False
        return True


class RuleFactory(Factory):
    mapping = {
        "include": IncludeRule,
        "exclude": ExcludeRule,
    }

    @classmethod
    def create(cls, entity: dict) -> Rule:
        # check if rule has level field
        if "level" not in entity:
            raise RuleException("Invalid rule, missing level")
        if entity["level"] is None:
            del entity["level"]
            return cls.mapping["exclude"](entity)
        return cls.mapping["include"](entity)
