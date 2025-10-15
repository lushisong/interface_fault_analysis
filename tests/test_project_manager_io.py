import os
import json

import pytest

from src.core.project_manager import ProjectManager
from src.models.system_model import SystemStructure
from src.models.module_model import Module
from src.models.interface_model import Interface, InterfaceDirection, InterfaceType


def test_project_manager_save_load_roundtrip(tmp_path):
    pm = ProjectManager()
    system = SystemStructure("测试系统", "保存与加载往返测试")
    pm.set_current_system(system)

    # Populate with a module and an interface and a simple connection-free state
    module = Module("通信模块", "测试模块")
    module.python_code = "outputs['ok'] = True"
    system.add_module(module)

    interface = Interface(
        name="链路接口",
        description="用于链路通信",
        interface_type=InterfaceType.ALGORITHM_APPLICATION,
        direction=InterfaceDirection.BIDIRECTIONAL,
    )
    system.add_interface(interface)

    # Save
    out_file = tmp_path / "project.json"
    ok = pm.save_project_as(str(out_file))
    assert ok is True
    assert out_file.exists()

    # Tamper minimally to ensure file content is sane JSON
    with out_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    assert "modules" in data and "interfaces" in data

    # Load back
    loaded_system = pm.load_project(str(out_file))
    assert isinstance(loaded_system, SystemStructure)
    assert pm.current_file_path == str(out_file)
    assert pm.has_unsaved_changes() is False

    # Verify round-trip integrity
    assert len(loaded_system.modules) == 1
    restored_module = next(iter(loaded_system.modules.values()))
    assert restored_module.name == module.name
    assert restored_module.python_code == module.python_code

    assert len(loaded_system.interfaces) == 1
    restored_interface = next(iter(loaded_system.interfaces.values()))
    assert restored_interface.name == interface.name
    assert restored_interface.direction == interface.direction
    assert restored_interface.interface_type == interface.interface_type

