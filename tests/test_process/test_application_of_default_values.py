"""
This feature includes tests that verify the parser correctly applies default values to properties not explicitly defined
in the SVD file. It ensures the parser adheres to the SVD standard by assigning the appropriate predefined defaults.
"""

from typing import Callable
import pytest

from svdsuite.model.process import Device
from svdsuite.model.types import (
    AccessType,
    ProtectionStringType,
)


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_default_register_properties_on_device_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    Although not stated in the SVD specification, `svdconv` assigns default values to size (32), access (read-
    write), resetValue (0x0), and resetMask (0xFFFFFFFF). This test ensures that the default values are set if
    they are not specified in a processed SVD file.

    **Expected Outcome:** The device is processed correctly, with default register properties applied at the device
    level. The register size is set to 32 bits, the access type is `READ_WRITE`, the protection type is `ANY`, the
    reset value is `0x0`, and the reset mask is `0xFFFFFFFF`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile(
        "application_of_default_values/default_register_properties_on_device_level.svd"
    )

    assert device.size == 32
    assert device.access == AccessType.READ_WRITE
    assert device.protection == ProtectionStringType.ANY
    assert device.reset_value == 0x0
    assert device.reset_mask == 0xFFFFFFFF


@pytest.mark.filterwarnings("error::svdsuite.process.ProcessWarning")
def test_custom_register_properties_on_device_level(get_processed_device_from_testfile: Callable[[str], Device]):
    """
    This test ensures that the default values are overwritten if custom values are specified in a processed SVD
    file on device level.

    **Expected Outcome:** The device is processed correctly, with custom register properties specified at the device
    level overriding the default values. The register size is set to 16 bits, the access type is `WRITE_ONLY`, the
    protection type is `SECURE`, the reset value is `0xDEADBEEF`, and the reset mask is `0xDEADC0DE`.

    **Processable with svdconv:** yes
    """

    device = get_processed_device_from_testfile(
        "application_of_default_values/custom_register_properties_on_device_level.svd"
    )

    assert device.size == 16
    assert device.access == AccessType.WRITE_ONLY
    assert device.protection == ProtectionStringType.SECURE
    assert device.reset_value == 0xDEADBEEF
    assert device.reset_mask == 0xDEADC0DE
