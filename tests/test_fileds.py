import pytest

from k8s_audit_filter.fields import (  # noqa isort:skip
    FieldException,
    FieldFactory,
    LevelField,
    NamespacesField,
    UserGroupsField,
    UsersField,
    VerbsField,
    ResourceField,
)


@pytest.mark.parametrize(
    "field, data, result",
    [
        (LevelField("Request"), {"level": "Request"}, True),
        (LevelField("Request"), {"level": "Metadata"}, False),
        (VerbsField(["get"]), {"verb": "get"}, True),
        (VerbsField(["get"]), {"verb": "watch"}, False),
        (UsersField(["admin"]), {"user": {"username": "admin"}}, True),
        (UsersField(["admin"]), {"user": {"username": "user"}}, False),
        (UserGroupsField(["system:admins"]), {"user": {"groups": ["system:admins"]}}, True),
        (UserGroupsField(["system:admins"]), {"user": {"groups": ["system:users"]}}, False),
        (NamespacesField(["kube-system"]), {"objectRef": {"namespace": "kube-system"}}, True),
        (NamespacesField(["kube-system"]), {"objectRef": {"namespace": "default"}}, False),
        (ResourceField([{"group": ""}]), {"objectRef": {"apiGroup": "apiextensions.k8s.io"}}, True),
        (ResourceField([{"group": "apps"}]), {"objectRef": {"apiGroup": "apiextensions.k8s.io"}}, False),
        (ResourceField([{"group": "apps"}]), {"objectRef": {"apiGroup": "apps"}}, True),
        (
            ResourceField([{"group": "apps", "resources": ["configmaps"]}]),
            {"objectRef": {"resource": "configmaps", "apiGroup": "apps"}},
            True,
        ),
        (
            ResourceField([{"group": "apps", "resources": ["configmaps"]}]),
            {"objectRef": {"resource": "configmaps", "apiGroup": "apps"}},
            True,
        ),
        (
            ResourceField([{"group": "apps", "resources": ["configmaps"]}]),
            {"objectRef": {"resource": "leases", "apiGroup": "apps"}},
            False,
        ),
        (
            ResourceField([{"group": "apps", "resources": ["leases"], "resourceNames": ["test"]}]),
            {"objectRef": {"resource": "leases", "apiGroup": "apps", "name": "test"}},
            True,
        ),
    ],
)
def test_filed(field, data, result):
    assert field.check_match(data) is result


def test_level_field_none():
    with pytest.raises(ValueError):
        LevelField(None)


def test_fields_are_equal():
    field1 = LevelField("Request")
    field2 = LevelField("Request")
    assert field1 == field2


def test_field_factory():
    fields = FieldFactory.create({"level": "Request"})
    assert len(fields) == 1
    assert isinstance(fields[0], LevelField)


def test_field_factory_invalid_field():
    with pytest.raises(FieldException):
        FieldFactory.create({"Some": "data"})
