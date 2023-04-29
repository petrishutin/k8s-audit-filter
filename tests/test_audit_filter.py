import os

import pytest
import yaml

from k8s_audit_filter.audit_filter import AuditFilter, AuditFilterException


def test_audit_filter():
    rules = {
        "rules": [
            {"level": "Request"},
            {"level": "Metadata", "verbs": ["get"]},
        ]
    }
    filter_audit = AuditFilter(config=rules)
    assert filter_audit.filter({"level": "Request", "verb": "get"}) is True


def test_audit_filter_with_no_rules():
    filter_audit = AuditFilter()
    assert filter_audit.filter({"level": "Request", "verb": "get"}) is True


def test_audit_filter_with_invalid_instance():
    with pytest.raises(AuditFilterException):
        AuditFilter(config=("rules", []))  # type: ignore


@pytest.mark.parametrize(
    "data, result",
    [
        ({"level": "Metadata", "verb": "get", "user": {"username": "admin"}}, True),
        ({"level": "Request", "verb": "get", "user": {"username": "admin"}}, True),
        ({"level": "Request", "verb": "create", "user": {"username": "admin"}}, True),
        ({"level": "Request", "verb": "get", "user": {"username": "user", "groups": ["system:users"]}}, False),
        ({"level": "Request", "verb": "put", "user": {"username": "admin2", "groups": ["system:admins"]}}, True),
        ({"level": "Request", "verb": "create", "user": {"username": "admin3", "groups": ["system:masters"]}}, False),
        (
            {
                "level": "Request",
                "user": {"username": "admin", "groups": ["system:admins"]},
                "objectRef": {"namespace": "kube-system"},
            },
            True,
        ),
        (
            {
                "level": "RequestResponse",
                "objectRef": {"namespace": "default", "resource": "flowschemas", "apiGroup": "apps", "name": "test1"},
            },
            False,
        ),
        (
            {"level": "RequestResponse", "objectRef": {"resource": "deployments", "apiGroup": "tests", "name": "pods"}},
            True,
        ),
        (
            {"level": "RequestResponse", "objectRef": {"resource": "leases", "apiGroup": "apps", "name": "test"}},
            True,
        ),
        (
            {"level": "RequestResponse", "objectRef": {"resource": "leases", "apiGroup": "apps", "name": "test1"}},
            False,
        ),
        (
            {"level": "RequestResponse", "responseStatus": {"code": 200}},
            True,
        ),
        (
            {"level": "RequestResponse", "responseStatus": {"code": 201}},
            False,
        ),
    ],
)
def test_audit_filter_load_config_from_yaml(data, result):
    filter_audit = AuditFilter("audit-policy.yaml")
    assert filter_audit.filter(data) is result


def test_audit_filter_load_invalid_policy():
    with pytest.raises(AuditFilterException):
        AuditFilter("invalid-audit-policy.yaml")


def test_audit_filter_add_and_remove_rules():
    filter_audit = AuditFilter()
    filter_audit.add_rule({"level": "Request"})
    assert filter_audit.filter({"level": "Request", "verb": "get"}) is True
    filter_audit.add_rule({"level": "Metadata"})
    assert filter_audit.filter({"level": "Metadata", "verb": "get"}) is True
    filter_audit.remove_rule({"level": "Request"})
    assert filter_audit.filter({"level": "Request", "verb": "get"}) is False


def test_audit_filter_with_rule():
    assert AuditFilter.filter_with_rule({"level": "Request", "verb": "get"}, {"level": "Request"}) is True
    assert AuditFilter.filter_with_rule({"level": "Request", "verb": "get"}, {"level": "Metadata"}) is False


def test_audit_filter_dump_config():
    filter_audit = AuditFilter()
    filter_audit.add_rule({"level": "Request"})
    filter_audit.add_rule({"level": "Metadata", "codes": [200, 201]})
    filter_audit.dump_config("test.yaml")
    assert os.path.exists("test.yaml")
    with open("test.yaml") as f:
        file = yaml.safe_load(f)
    assert file["rules"] == [{"level": "Request"}, {"level": "Metadata"}]
    os.remove("test.yaml")
    filter_audit.dump_config("test1.yaml", k8s_standard=False)
    with open("test1.yaml") as f:
        file = yaml.safe_load(f)
    assert file["rules"] == [{"level": "Request"}, {"level": "Metadata", "codes": [200, 201]}]
    os.remove("test1.yaml")
