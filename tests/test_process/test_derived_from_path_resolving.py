from typing import Callable
import pytest

from svdsuite.process import Process, ProcessException
from svdsuite.model.process import IRegister, ICluster


@pytest.mark.parametrize(
    "path",
    [
        "PeripheralA.ClusterA.ClusterB.RegisterA",
        "ClusterA.ClusterB.RegisterA",
        pytest.param(
            "PeripheralAA.ClusterA.ClusterB.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralA.ClusterAA.ClusterB.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralA.ClusterA.ClusterBB.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralA.ClusterA.ClusterB.RegisterAA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralA.ClusterB.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralA.ClusterA.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralA.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "ClusterB.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "ClusterA.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_1(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_1.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], ICluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], ICluster)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "ClusterB"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters) == 1

    registera = device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters[0]
    assert isinstance(registera, IRegister)
    assert registera.name == "RegisterA"
    assert registera.address_offset == 0x0
    assert registera.size == 32
    assert len(registera.fields) == 1

    assert registera.fields[0].name == "FieldA"
    assert registera.fields[0].lsb == 0
    assert registera.fields[0].msb == 0

    assert isinstance(device.peripherals[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1

    assert device.peripherals[0].registers_clusters[1].fields[0].name == "FieldA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 0


@pytest.mark.parametrize(
    "path",
    [
        "SameA.SameA.SameA.SameA",  # can't be processed with svdconv
        "SameA.SameA.SameA",  # can't be processed with svdconv
        pytest.param(
            "SameA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "SameA.SameA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "SameA.SameA.SameA.SameA.SameA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_2(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_2.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert device.peripherals[0].name == "SameA"
    assert len(device.peripherals[0].registers_clusters) == 2

    assert isinstance(device.peripherals[0].registers_clusters[0], ICluster)
    assert device.peripherals[0].registers_clusters[0].name == "SameA"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1

    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], ICluster)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "SameA"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters) == 1

    registera = device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters[0]
    assert isinstance(registera, IRegister)
    assert registera.name == "SameA"
    assert registera.address_offset == 0x0
    assert registera.size == 32
    assert len(registera.fields) == 1

    assert registera.fields[0].name == "SameA"
    assert registera.fields[0].lsb == 0
    assert registera.fields[0].msb == 0

    assert isinstance(device.peripherals[0].registers_clusters[1], IRegister)
    assert device.peripherals[0].registers_clusters[1].name == "RegisterB"
    assert device.peripherals[0].registers_clusters[1].address_offset == 0x4
    assert device.peripherals[0].registers_clusters[1].size == 32
    assert len(device.peripherals[0].registers_clusters[1].fields) == 1

    assert device.peripherals[0].registers_clusters[1].fields[0].name == "SameA"
    assert device.peripherals[0].registers_clusters[1].fields[0].lsb == 0
    assert device.peripherals[0].registers_clusters[1].fields[0].msb == 0


@pytest.mark.parametrize(
    "path",
    [
        "ElementA.RegisterA",
        pytest.param(
            "ElementA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_3(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_3.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 2

    assert device.peripherals[1].name == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 2

    assert isinstance(device.peripherals[1].registers_clusters[1], IRegister)
    assert device.peripherals[1].registers_clusters[1].name == "RegisterB"
    assert len(device.peripherals[1].registers_clusters[1].fields) == 1
    assert device.peripherals[1].registers_clusters[1].fields[0].name == "FieldB"


@pytest.mark.parametrize(
    "path",
    [
        "ElementA.RegisterA",
        "ElementB.RegisterA",
        pytest.param(
            "ElementA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_4(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_4.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 2

    assert device.peripherals[1].name == "PeripheralA"
    assert len(device.peripherals[1].registers_clusters) == 3

    assert isinstance(device.peripherals[1].registers_clusters[2], IRegister)
    assert device.peripherals[1].registers_clusters[2].name == "RegisterB"
    assert len(device.peripherals[1].registers_clusters[2].fields) == 1
    assert device.peripherals[1].registers_clusters[2].fields[0].name == "FieldB"


@pytest.mark.parametrize(
    "path",
    [
        "PeripheralA.Cluster%s.RegisterA",
        "PeripheralA.ClusterA.RegisterA",
        "PeripheralA.ClusterB.RegisterA",
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_5(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_5.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 2

    assert device.peripherals[1].name == "PeripheralB"
    assert len(device.peripherals[1].registers_clusters) == 1
    assert isinstance(device.peripherals[1].registers_clusters[0], IRegister)
    assert device.peripherals[1].registers_clusters[0].name == "RegisterA"
    assert len(device.peripherals[1].registers_clusters[0].fields) == 1
    assert device.peripherals[1].registers_clusters[0].fields[0].name == "FieldA"


@pytest.mark.parametrize(
    "path",
    [
        "PeripheralA.ClusterA.ClusterB.RegisterA.FieldA.FieldAEnumeratedValue",
        pytest.param(
            "ClusterA.ClusterB.RegisterA.FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "ClusterB.RegisterA.FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA.FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "FieldA.FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "FieldAEnumeratedValue",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_6(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_6.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0], ICluster)
    assert device.peripherals[0].registers_clusters[0].name == "ClusterA"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 1
    assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], ICluster)
    assert device.peripherals[0].registers_clusters[0].registers_clusters[0].name == "ClusterB"
    assert len(device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters) == 1
    registera = device.peripherals[0].registers_clusters[0].registers_clusters[0].registers_clusters[0]
    assert isinstance(registera, IRegister)
    assert registera.name == "RegisterA"
    assert len(registera.fields) == 2

    assert registera.fields[0].name == "FieldA"
    assert len(registera.fields[0].enumerated_value_containers) == 1
    assert registera.fields[0].enumerated_value_containers[0].name == "FieldAEnumeratedValue"
    assert len(registera.fields[0].enumerated_value_containers[0].enumerated_values) == 2

    assert registera.fields[1].name == "FieldB"
    assert len(registera.fields[1].enumerated_value_containers) == 1
    assert registera.fields[1].enumerated_value_containers[0].name == "FieldAEnumeratedValue"
    assert len(registera.fields[1].enumerated_value_containers[0].enumerated_values) == 2


@pytest.mark.parametrize(
    "path",
    [
        "PeripheralA.RegisterA",
        "PeripheralB.RegisterA",
        "PeripheralB.RegisterA_RegisterX",
        pytest.param(
            "PeripheralC.RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralA.RegisterB",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
        pytest.param(
            "PeripheralB.RegisterB",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_7(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_7.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 3

    assert device.peripherals[2].name == "PeripheralC"
    assert len(device.peripherals[2].registers_clusters) == 1
    assert isinstance(device.peripherals[2].registers_clusters[0], IRegister)
    assert device.peripherals[2].registers_clusters[0].name == "RegisterA"

    if "_RegisterX" in path:
        assert device.peripherals[2].registers_clusters[0].description == "PeripheralB_RegisterA"
    else:
        assert device.peripherals[2].registers_clusters[0].description == "PeripheralA_RegisterA"


@pytest.mark.parametrize(
    "path",
    [
        "ClusterA.RegisterA",
        "ClusterB.RegisterA",
        "PeripheralA.ClusterA.RegisterA",
        "PeripheralA.ClusterB.RegisterA",
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_8(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_8.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert device.peripherals[0].registers_clusters[2].name == "RegisterC"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0xC
    assert device.peripherals[0].registers_clusters[2].size == 32


@pytest.mark.parametrize(
    "path",
    [
        "ClusterA.RegisterA",
        "ClusterB.RegisterA",
        "PeripheralA.ClusterA.RegisterA",
        "PeripheralA.ClusterB.RegisterA",
        pytest.param(
            "RegisterA",
            marks=pytest.mark.xfail(strict=True, raises=ProcessException),
        ),
    ],
)
def test_test_setup_9(path: str, get_test_svd_file_content: Callable[[str], bytes]):
    file_name = "derivedfrom_path_resolving/test_setup_9.svd"

    file_content = get_test_svd_file_content(file_name)
    file_content = file_content.replace(b"PATH", path.encode())

    device = Process.from_xml_content(file_content).get_processed_device()

    assert len(device.peripherals) == 1
    assert len(device.peripherals[0].registers_clusters) == 3

    assert device.peripherals[0].registers_clusters[2].name == "RegisterC"
    assert device.peripherals[0].registers_clusters[2].description == "RegisterA description"
    assert device.peripherals[0].registers_clusters[2].address_offset == 0xC
    assert device.peripherals[0].registers_clusters[2].size == 32
