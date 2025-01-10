from typing import Callable

from svdsuite.model.process import Device
from svdsuite.model.types import (
    AccessType,
    ProtectionStringType,
)


def test_default_register_properties_on_device_level(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "application_of_default_values/default_register_properties_on_device_level.svd"
    )

    assert device.size == 32
    assert device.access == AccessType.READ_WRITE
    assert device.protection == ProtectionStringType.ANY
    assert device.reset_value == 0x0
    assert device.reset_mask == 0xFFFFFFFF


def test_custom_register_properties_on_device_level(get_processed_device_from_testfile: Callable[[str], Device]):
    device = get_processed_device_from_testfile(
        "application_of_default_values/custom_register_properties_on_device_level.svd"
    )

    assert device.size == 16
    assert device.access == AccessType.WRITE_ONLY
    assert device.protection == ProtectionStringType.SECURE
    assert device.reset_value == 0xDEADBEEF
    assert device.reset_mask == 0xDEADC0DE
