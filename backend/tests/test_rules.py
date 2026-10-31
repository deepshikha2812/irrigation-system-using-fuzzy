import pytest

from app.rules import RULES, Rule, validate_rule_base


def test_rule_count_is_reasonable():
    assert 15 <= len(RULES) <= 25


def test_rule_ids_are_unique():
    ids = [rule.id for rule in RULES]
    assert len(ids) == len(set(ids))


def test_every_rule_has_a_reason():
    assert all(rule.reason.strip() for rule in RULES)


def test_no_two_rules_have_identical_conditions():
    keys = [tuple(sorted(rule.conditions().items())) for rule in RULES]
    assert len(keys) == len(set(keys))


def test_rule_description_is_readable():
    text = RULES[1].describe()
    assert text == ("IF soil moisture is DRY AND temperature is HOT AND humidity is LOW "
                    "THEN irrigation is VERY HIGH")


def test_validation_rejects_unknown_set():
    with pytest.raises(ValueError):
        validate_rule_base([Rule(99, "soggy", None, None, "low", "invalid")])


def test_validation_rejects_rule_without_conditions():
    with pytest.raises(ValueError):
        validate_rule_base([Rule(99, None, None, None, "low", "invalid")])
