import pytest

from k8s_audit_filter.rules import ExcludeRule, IncludeRule, RuleException, RuleFactory

include_rules_data = [
    [{"level": "Request"}, {"level": "Request"}, True],
    [{"level": "Request"}, {"level": "Request", "other": "field"}, True],
    [{"level": "Request"}, {"level": "Metadata"}, False],
    [{"level": "Request", "verbs": ["get"]}, {"level": "Request", "verb": "get"}, True],
    [{"level": "Request", "verbs": ["get"]}, {"level": "Metadata", "verb": "get"}, False],
    [{"level": "Request", "users": ["admin"]}, {"level": "Request", "user": {"username": "admin"}}, True],
    [
        {"level": "Request", "userGroups": ["system:admins"]},
        {"level": "Request", "user": {"groups": ["system:admins"]}},
        True,
    ],
    [
        {"level": "Request", "namespaces": ["kube-system"]},
        {"level": "Request", "objectRef": {"namespace": "kube-system"}},
        True,
    ],
    [
        {"level": "Request", "namespaces": ["kube-system"]},
        {"level": "Request", "objectRef": {"namespace": "default"}},
        False,
    ],
    [
        {"level": "Request", "resources": [{"group": ""}]},
        {"level": "Request", "objectRef": {"apiGroup": "apps"}},
        True,
    ],
    [
        {"level": "Request", "resources": [{"group": "apps"}]},
        {"level": "Request", "objectRef": {"apiGroup": "apps"}},
        True,
    ],
    [
        {"level": "Request", "resources": [{"group": "apps", "resources": ["deployments"]}]},
        {"level": "Request", "objectRef": {"apiGroup": "apps", "resource": "deployments"}},
        True,
    ],
    [
        {"level": "Request", "resources": [{"group": "apps", "resources": ["deployments"], "resourceNames": ["test"]}]},
        {"level": "Request", "objectRef": {"apiGroup": "apps", "resource": "deployments", "name": "app"}},
        False,
    ],
    [
        {"level": "Request", "codes": [200]},
        {"level": "Request", "responseStatus": {"code": 200}},
        True,
    ],
    [
        {"level": "Request", "codes": [200]},
        {"level": "Request", "responseStatus": {"code": 500}},
        False,
    ],
]


@pytest.mark.parametrize("fields, instance, result", include_rules_data)
def test_include_rules(fields, instance, result):
    rule = IncludeRule(fields)
    assert rule.check_rule(instance) is result


exclude_rules_data = [
    [{"verbs": ["get"]}, {"level": "Request", "verb": "get"}, False],
    [{"verbs": ["get"]}, {"level": "Metadata", "verb": "watch"}, True],
]


@pytest.mark.parametrize("fields, instance, result", exclude_rules_data)
def test_exclude_rules(fields, instance, result):
    rule = ExcludeRule(fields)
    assert rule.check_rule(instance) is result


def test_rules_are_equal():
    rule1 = IncludeRule({"level": "Request"})
    rule2 = IncludeRule({"level": "Request"})
    assert rule1 == rule2


def test_rule_str():
    rule = IncludeRule({"level": "Request"})
    assert str(rule) == "IncludeRule: {'level': 'Request'}"


@pytest.mark.parametrize(
    "fields, result",
    [
        ({"level": "Request"}, IncludeRule),
        ({"level": None}, ExcludeRule),
    ],
)
def test_rule_factory(fields, result):
    rule = RuleFactory.create(fields)
    assert isinstance(rule, result)


def test_rule_factory_missing_level():
    with pytest.raises(RuleException):
        RuleFactory.create({"verbs": "get"})
