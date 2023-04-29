import logging
from copy import deepcopy

import yaml

from k8s_audit_filter.rules import RuleFactory

from typing import Any, List, Union  # noqa isort:skip


from .abstract_classes import Factory, Rule  # noqa isort:skip

logger = logging.getLogger(__name__)


class AuditFilterException(Exception):
    pass


class AuditFilter:
    def __init__(self, config: Union[dict, str, None] = None):
        self.config = {
            "apiVersion": "audit.k8s.io/v1",
            "kind": "Policy",
            "rules": [],
        }
        self.rules = PolicyFactory.create(config)
        self.config["rules"] = [rule.as_dict for rule in self.rules]

    def filter(self, log_line: dict) -> bool:
        if not self.rules:
            return True  # no rules, no filter
        for rule in self.rules:
            try:
                if rule.check_rule(log_line):
                    return True
            except Exception as e:
                logger.warning(
                    f"Exception: {e}, Type: {e.__class__.__qualname__} "
                    f"Traceback: {e.__traceback__} Rule: {rule} with log line: {log_line}"
                )
                raise e  # if rule check fails, we assume it should not be filtered
        return False

    def add_rule(self, rule: dict):
        internal_rule = RuleFactory.create(rule)
        self.rules.append(internal_rule)
        self.config["rules"].append(internal_rule.as_dict)  # type: ignore

    def add_rules(self, rules: list):
        for rule in rules:
            self.add_rule(rule)

    def remove_rule(self, rule: dict):
        internal_rule = RuleFactory.create(rule)
        self.rules.remove(internal_rule)
        self.config["rules"].remove(internal_rule.as_dict)  # type: ignore

    def remove_rules(self, rules: list):
        for rule in rules:
            self.remove_rule(rule)

    def dump_config(self, path_to_config, k8s_standard: bool = True):
        config = deepcopy(self.config)
        if k8s_standard:
            for rule in config["rules"]:
                if "codes" in rule:  # there is no codes field in k8s standard
                    del rule["codes"]  # type: ignore
        with open(path_to_config, "w") as f:
            yaml.dump(config, f, indent=4)

    @staticmethod
    def filter_with_rule(log_line: dict, rule: dict) -> bool:
        internal_rule: Rule = RuleFactory.create(rule)
        return internal_rule.check_rule(log_line)


def from_yaml(config: str) -> List[Rule]:
    if not ("yaml" in config or "yml" in config):
        raise AuditFilterException("Invalid config, must be yaml")
    with open(config) as f:
        policy = yaml.safe_load(f)
    if "apiVersion" not in policy or policy["apiVersion"] != "audit.k8s.io/v1":
        raise AuditFilterException("Invalid policy, missing version or version does not match 'audit.k8s.io/v1'")
    if "kind" not in policy or policy["kind"] != "Policy":
        raise AuditFilterException("Invalid policy, missing kind or kind does not match 'Policy'")
    return [RuleFactory.create(rule) for rule in policy["rules"]]


def from_dict(config: dict) -> List[Rule]:
    return [RuleFactory.create(rule) for rule in config["rules"]]


def empty_config(config: None) -> list:
    return []


class PolicyFactory(Factory):
    mapping = {
        str: from_yaml,
        dict: from_dict,
        None: empty_config,
    }

    @classmethod
    def create(cls, entity: Any):
        if type(entity) in cls.mapping:
            return cls.mapping[type(entity)](entity)
        if entity is None:
            return cls.mapping[None](entity)
        raise AuditFilterException(f"Invalid config type {type(entity)}")
