import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

from src.models.interface_model import InterfaceFailureMode, FailureMode
from src.models.module_model import Module


def test_interface_failure_mode_rpn_and_rates():
    fm = InterfaceFailureMode(FailureMode.TIMEOUT, "超时")
    fm.severity = 8
    fm.failure_rate = 1e-5
    fm.detection_rate = 0.2
    rpn = fm.rpn()
    assert rpn > 0


def test_module_failure_rate_persistence():
    m = Module("M")
    m.failure_rate = 2.5e-6
    data = m.to_dict()
    assert data["failure_rate"] == 2.5e-6

    m2 = Module()
    m2.from_dict(data)
    assert m2.failure_rate == 2.5e-6

