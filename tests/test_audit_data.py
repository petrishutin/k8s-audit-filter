from collections import Counter

import pytest

from k8s_audit_filter.audit_data import AuditData

test_data = [
    {
        "level": "Request",
        "user": {"username": "system:apiserver"},
        "responseStatus": {"code": 201},
    },
    {
        "level": "Request",
        "user": {"username": "admin"},
        "responseStatus": {"code": 200},
    },
    {
        "level": "Metadata",
        "user": {"username": "system:apiserver"},
        "responseStatus": {"code": 403},
    },
    {
        "level": "Request",
        "user": {"username": "system:apiserver"},
        "responseStatus": {"code": 403},
    },
]


@pytest.mark.parametrize(
    "counter, result",
    [
        ("level", Counter({"Request": 3, "Metadata": 1})),
        ("users", Counter({"system:apiserver": 3, "admin": 1})),
        ("codes", Counter({403: 2, 201: 1, 200: 1})),
    ],
)
def test_audit_data_count(counter, result):
    audit_data = AuditData(test_data)
    assert audit_data.count(counter) == result


def test_audit_data_filter_count():
    audit_data = AuditData(test_data)
    assert audit_data.filter([{"level": "Request"}]).count("level") == Counter({"Request": 3})
    assert audit_data.filter([{"level": "Request"}]).count("users") == Counter({"system:apiserver": 2, "admin": 1})
    assert audit_data.filter([{"level": "Request"}]).count("codes") == Counter({201: 1, 200: 1, 403: 1})
