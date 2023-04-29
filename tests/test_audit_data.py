from collections import Counter

from k8s_audit_filter.audit_data import AuditData

test_data = [
    {"level": "Request", "user": {"username": "system:apiserver"}},
    {"level": "Request", "user": {"username": "admin"}},
    {"level": "Metadata", "user": {"username": "system:apiserver"}},
]


def test_audit_data_count():
    audit_data = AuditData(test_data)
    assert audit_data.count("level") == Counter({"Request": 2, "Metadata": 1})
    assert audit_data.count("users") == Counter({"system:apiserver": 2, "admin": 1})


def test_audit_data_filter_count():
    audit_data = AuditData(test_data)
    assert audit_data.filter([{"level": "Request"}]).count("level") == Counter({"Request": 2})
    assert audit_data.filter([{"level": "Request"}]).count("users") == Counter({"system:apiserver": 1, "admin": 1})
