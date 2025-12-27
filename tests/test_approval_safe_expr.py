import pytest
from app.approval_engine import ApprovalEngine


def test_simple_arithmetic():
    assert ApprovalEngine._evaluate_condition_expr('1 + 2 == 3', {}) is True


def test_amount_comparison():
    ctx = {'amount': 150}
    assert ApprovalEngine._evaluate_condition_expr('amount > 100', ctx) is True
    assert ApprovalEngine._evaluate_condition_expr('amount <= 200', ctx) is True


def test_form_data_access():
    ctx = {'form_data': {'urgent': True}}
    assert ApprovalEngine._evaluate_condition_expr("form_data['urgent'] == True", ctx) is True


def test_disallowed_name():
    with pytest.raises(ValueError):
        ApprovalEngine._evaluate_condition_expr('__import__("os").system("ls")', {})


def test_attribute_access_rejected():
    with pytest.raises(ValueError):
        ApprovalEngine._evaluate_condition_expr('().__class__', {})
