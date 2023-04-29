import json
import sys
from collections import Counter
from typing import List, Union

from k8s_audit_filter.audit_filter import AuditFilter
from k8s_audit_filter.count_rules import CountRuleFactory


class AuditDataException(Exception):
    pass


class AuditData(list):
    """AuditData is a list of dicts like object.
    Can be filtered with k8s audit rules and counted with count rules"""

    def __init__(self, audit_data: Union[List[dict], None] = None):
        self.audit_data: List[dict] = audit_data if audit_data else []
        self.audit_filter = AuditFilter()

    def append(self, item):
        if not isinstance(item, dict):
            raise AuditDataException(f"Item {item} is not a dict")
        self.audit_data.append(item)

    def clear(self):
        self.audit_data.clear()

    def copy(self):
        return AuditData(self.audit_data.copy())

    def count(self, count_rule) -> Counter:  # type: ignore
        rule = CountRuleFactory.create(count_rule)
        result = []
        for data in self.audit_data:
            if self.audit_filter.filter(data):
                result.extend(rule.get(data))
        return Counter(result)

    def extend(self, iterable):
        if isinstance(iterable, AuditData):
            self.audit_data.extend(iterable.audit_data)
            return
        raise AuditDataException(f"Cant extend AuditData with {type(iterable)}")

    def index(self, *args, **kwargs):
        raise NotImplementedError

    def insert(self, *args, **kwargs):
        raise NotImplementedError

    def pop(self, index=-1):
        return self.audit_data.pop(index)

    def remove(self, item):
        self.audit_data.remove(item)

    def reverse(self):
        raise NotImplementedError

    def sort(self, key=None, reverse=False):
        self.audit_data.sort(key=key, reverse=reverse)

    def _filter(self, rule: dict) -> "AuditData":
        self.audit_data = [data for data in self.audit_data if self.audit_filter.filter_with_rule(data, rule)]  # noqa
        return self

    def filter(self, rules: List[dict]) -> "AuditData":
        for rule in rules:
            self._filter(rule)
        return self

    def result(self) -> List[dict]:
        return self.audit_data

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.audit_data, f)

    def __add__(self, other):
        if isinstance(other, AuditData):
            return AuditData(self.audit_data + other.audit_data)
        raise AuditDataException(f"Can't add {type(other)} to AuditData")

    def __contains__(self, item):
        return item in self.audit_data

    def __delitem__(self, key):
        del self.audit_data[key]

    def __eq__(self, other):
        if isinstance(other, AuditData):
            return self.audit_data == other.audit_data
        raise AuditDataException(f"Can't compare {type(other)} to AuditData")

    def __getitem__(self, item):
        return self.audit_data[item]

    def __ge__(self, other):
        raise NotImplementedError

    def __gt__(self, other):
        raise NotImplementedError

    def __iadd__(self, other):
        if isinstance(other, AuditData):
            self.audit_data += other.audit_data
        else:
            raise AuditDataException(f"Can't add {type(other)} to AuditData")
        return self

    def __imul__(self, other):
        raise NotImplementedError

    def __iter__(self):
        return iter(self.audit_data)

    def __len__(self):
        return len(self.audit_data)

    def __le__(self, other):
        raise NotImplementedError

    def __lt__(self, other):
        raise NotImplementedError

    def __mul__(self, other):
        raise NotImplementedError

    def __ne__(self, other):
        if isinstance(other, AuditData):
            return self.audit_data != other.audit_data
        raise AuditDataException(f"Invalid type {type(other)}")

    def __repr__(self):
        return repr(self.audit_data)

    def __reversed__(self):
        raise NotImplementedError

    def __rmul__(self, other):
        raise NotImplementedError

    def __setitem__(self, key, value):
        self.audit_data[key] = value

    def __sizeof__(self):
        return sys.getsizeof(self)

    def __next__(self):
        return next(self.audit_data)

    def __str__(self):
        return str(self.audit_data)

    def __copy__(self):
        return self.copy()
