"""Tests for envault.policy."""

import pytest

from envault.policy import PolicyViolation, PolicyResult, check_policy


SECRETS = {
    "API_KEY": "supersecretvalue",
    "DB_PASSWORD": "hunter2",
    "SHORT": "x",
}


# ---------------------------------------------------------------------------
# PolicyResult helpers
# ---------------------------------------------------------------------------

def test_policy_result_ok_when_no_violations():
    result = PolicyResult()
    assert result.ok is True


def test_policy_result_not_ok_when_violations():
    v = PolicyViolation(key="K", rule="P001", message="missing")
    result = PolicyResult(violations=[v])
    assert result.ok is False


# ---------------------------------------------------------------------------
# required_keys
# ---------------------------------------------------------------------------

def test_required_key_present_no_violation():
    result = check_policy(SECRETS, required_keys=["API_KEY"])
    assert result.ok


def test_required_key_missing_raises_violation():
    result = check_policy(SECRETS, required_keys=["MISSING_KEY"])
    assert not result.ok
    assert any(v.rule == "P001" for v in result.violations)


# ---------------------------------------------------------------------------
# key_pattern
# ---------------------------------------------------------------------------

def test_key_pattern_all_match():
    result = check_policy(SECRETS, key_pattern=r"^[A-Z_]+$")
    assert result.ok


def test_key_pattern_mismatch_triggers_p002():
    secrets = {"lowercase_key": "value"}
    result = check_policy(secrets, key_pattern=r"^[A-Z_]+$")
    assert not result.ok
    assert any(v.rule == "P002" for v in result.violations)


# ---------------------------------------------------------------------------
# min_length
# ---------------------------------------------------------------------------

def test_min_length_satisfied_no_violation():
    result = check_policy({"KEY": "longenough"}, min_length=5)
    assert result.ok


def test_min_length_too_short_triggers_p003():
    result = check_policy(SECRETS, min_length=10)
    violations = [v for v in result.violations if v.rule == "P003"]
    # "hunter2" (7) and "x" (1) are below 10
    assert len(violations) >= 2
    keys_flagged = {v.key for v in violations}
    assert "DB_PASSWORD" in keys_flagged
    assert "SHORT" in keys_flagged


# ---------------------------------------------------------------------------
# forbidden_pattern
# ---------------------------------------------------------------------------

def test_forbidden_pattern_no_match_no_violation():
    result = check_policy(SECRETS, forbidden_pattern=r"^NOPE")
    assert result.ok


def test_forbidden_pattern_match_triggers_p004():
    secrets = {"KEY": "password123"}
    result = check_policy(secrets, forbidden_pattern=r"password")
    assert not result.ok
    assert any(v.rule == "P004" for v in result.violations)


# ---------------------------------------------------------------------------
# multiple rules combined
# ---------------------------------------------------------------------------

def test_multiple_violations_collected():
    secrets = {"bad key": "x"}
    result = check_policy(
        secrets,
        required_keys=["MUST_EXIST"],
        key_pattern=r"^[A-Z_]+$",
        min_length=5,
    )
    rules = {v.rule for v in result.violations}
    assert "P001" in rules  # missing required key
    assert "P002" in rules  # key pattern mismatch
    assert "P003" in rules  # value too short


def test_empty_secrets_with_required_keys():
    result = check_policy({}, required_keys=["A", "B"])
    assert len(result.violations) == 2
