from typing import Union

import yaml

from .abstract_classes import Rule
from .rules import RuleFactory


class AuditFilterException(Exception):
    pass


class AuditFilter:
    def __init__(self, config: Union[dict, str, None] = None):
        if isinstance(config, str) and ("yaml" in config or "yml" in config):
            with open(config) as f:
                policy = yaml.safe_load(f)
            if "apiVersion" not in policy or policy["apiVersion"] != "audit.k8s.io/v1":
                raise AuditFilterException(
                    "Invalid policy, missing version or version does not match 'audit.k8s.io/v1'"
                )
            if "kind" not in policy or policy["kind"] != "Policy":
                raise AuditFilterException("Invalid policy, missing kind or kind does not match 'Policy'")
            self.rules = [RuleFactory.create(rule) for rule in policy["rules"]]
            self.config: list = policy["rules"]
        elif isinstance(config, dict):
            self.rules = [RuleFactory.create(rule) for rule in config["rules"]]
            self.config: list = config["rules"]  # type: ignore
        elif config is None:
            self.rules = []  # type: ignore
            self.config: list = []  # type: ignore
        else:
            raise AuditFilterException("Invalid config")

    def filter(self, log_line: dict) -> bool:
        if not self.rules:
            return True  # no rules, no filter
        for rule in self.rules:
            if rule.check_rule(log_line):
                return True
        return False

    def add_rule(self, rule: dict):
        internal_rule = RuleFactory.create(rule)
        self.rules.append(internal_rule)
        self.config.append(internal_rule.as_dict)  # type: ignore

    def add_rules(self, rules: list):
        for rule in rules:
            self.add_rule(rule)

    def remove_rule(self, rule: dict):
        internal_rule = RuleFactory.create(rule)
        self.rules.remove(internal_rule)
        self.config.remove(internal_rule.as_dict)  # type: ignore

    @staticmethod
    def filter_with_rule(log_line: dict, rule: dict) -> bool:
        internal_rule: Rule = RuleFactory.create(rule)
        return internal_rule.check_rule(log_line)
