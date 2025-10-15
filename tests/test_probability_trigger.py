import random

import pytest

from src.models.interface_model import (
    Interface,
    InterfaceType,
    InterfaceDirection,
    InterfaceFailureMode,
    FailureMode,
    TriggerCondition,
)


def _make_interface_with_prob_condition(params: dict) -> Interface:
    itf = Interface("概率接口", "", InterfaceType.ALGORITHM_HARDWARE, InterfaceDirection.BIDIRECTIONAL)
    fm = InterfaceFailureMode(FailureMode.TIMEOUT, "超时")
    fm.enabled = True
    cond = TriggerCondition("prob", "probability")
    cond.parameters = params.copy()
    fm.add_trigger_condition(cond)
    itf.add_failure_mode(fm)
    itf.reset_runtime_state()
    return itf


def test_probability_trigger_p_one_triggers():
    interface = _make_interface_with_prob_condition({"p": 1.0})
    normal = interface.normal_state_id
    assert interface.current_state_id == normal
    rng = random.Random(0)
    result = interface.step_state_machine({"random": rng})
    assert interface.current_state_id != normal
    assert result["state_id"] == interface.current_state_id


def test_probability_trigger_p_zero_not_trigger():
    interface = _make_interface_with_prob_condition({"p": 0.0})
    normal = interface.normal_state_id
    rng = random.Random(0)
    result = interface.step_state_machine({"random": rng})
    assert interface.current_state_id == normal
    assert result["state_id"] == normal


def test_probability_trigger_lambda_dt_converts_to_near_one():
    # λ=1000 / h, dt=3600 s => p_step ~ 1 - exp(-1000) ~ 1.0
    interface = _make_interface_with_prob_condition({"lambda_per_hour": 1000.0, "dt": 3600.0})
    normal = interface.normal_state_id
    rng = random.Random(0)
    result = interface.step_state_machine({"random": rng})
    assert interface.current_state_id != normal
    assert result["state_id"] == interface.current_state_id

