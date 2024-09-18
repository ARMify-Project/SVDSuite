import tempfile
from unittest.mock import Mock
from typing import Callable, TypeAlias
import pytest

from svdsuite.serialize import Serializer
from svdsuite.model.parse import SVDDevice, SVDPeripheral, SVDCluster, SVDRegister, SVDField
from svdsuite.model.process import Device, Peripheral, Cluster, Register, Field
from svdsuite.process import Process, _ProcessRegister, _RegisterClusterMap  # type: ignore
from svdsuite.model.types import AccessType, ProtectionStringType

TestDataTuple: TypeAlias = tuple[
    Device,
    Peripheral,
    Register,
    Register,
    Register,
    Register,
    Register,
    Register,
    Register,
    Register,
    Register,
    Cluster,
    Cluster,
    Cluster,
]


class TestProcessRegisterDeriveFields:
    @pytest.fixture(name="derive_fields_caller", scope="function")
    def fixture_derive_fields_caller(self) -> Callable[[list[Field], list[Field]], list[Field]]:
        def _(processed_fields: list[Field], base_fields: list[Field]) -> list[Field]:
            mock_self = Mock(spec=_ProcessRegister)
            mock_self._process_field = Mock()  # pylint: disable=protected-access
            mock_self._process_field.get_processed_field.return_value = (  # pylint: disable=protected-access
                processed_fields
            )
            base_element = Register(
                name="r",
                address_offset=0x0,
                size=32,
                access=AccessType.READ_WRITE,
                protection=ProtectionStringType.SECURE,
                reset_value=0,
                reset_mask=0xFFFFFFFF,
                fields=base_fields,
                parsed=SVDRegister(name="r", address_offset=0x0),
            )
            return _ProcessRegister._derive_fields(  # type: ignore pylint: disable=protected-access
                mock_self, "", base_element
            )

        return _

    def test_simple_overwrite(self, derive_fields_caller: Callable[[list[Field], list[Field]], list[Field]]) -> None:
        processed_fields = [
            Field(name="processed", lsb=0, msb=2, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]
        base_fields = [
            Field(name="base", lsb=0, msb=2, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]

        result = derive_fields_caller(processed_fields, base_fields)
        assert len(result) == 1
        assert result[0].name == "processed"

    def test_simple_merge(self, derive_fields_caller: Callable[[list[Field], list[Field]], list[Field]]) -> None:
        processed_fields = [
            Field(name="processed", lsb=0, msb=2, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]
        base_fields = [
            Field(name="base", lsb=3, msb=5, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]

        result = derive_fields_caller(processed_fields, base_fields)
        assert len(result) == 2
        assert result[0].name == "processed"
        assert result[1].name == "base"

    def test_overlap_overwrite(self, derive_fields_caller: Callable[[list[Field], list[Field]], list[Field]]) -> None:
        processed_fields = [
            Field(name="processed", lsb=0, msb=3, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]
        base_fields = [
            Field(name="base", lsb=2, msb=5, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]

        result = derive_fields_caller(processed_fields, base_fields)
        assert len(result) == 1
        assert result[0].name == "processed"

    def test_overlap_overwrite_multiple(
        self, derive_fields_caller: Callable[[list[Field], list[Field]], list[Field]]
    ) -> None:
        processed_fields = [
            Field(name="processed", lsb=1, msb=5, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]
        base_fields = [
            Field(name="base1", lsb=0, msb=2, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="base2", lsb=3, msb=4, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="base3", lsb=5, msb=6, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]

        result = derive_fields_caller(processed_fields, base_fields)
        assert len(result) == 1
        assert result[0].name == "processed"

    def test_overlap_overwrite_multiple2(
        self, derive_fields_caller: Callable[[list[Field], list[Field]], list[Field]]
    ) -> None:
        processed_fields = [
            Field(name="processed", lsb=3, msb=4, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]
        base_fields = [
            Field(name="base1", lsb=0, msb=2, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="base2", lsb=3, msb=4, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="base3", lsb=5, msb=6, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]

        result = derive_fields_caller(processed_fields, base_fields)
        assert len(result) == 3
        assert result[0].name == "base1"
        assert result[1].name == "processed"
        assert result[2].name == "base3"

    def test_merge2(self, derive_fields_caller: Callable[[list[Field], list[Field]], list[Field]]) -> None:
        processed_fields = [
            Field(name="processed1", lsb=0, msb=2, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="processed2", lsb=7, msb=8, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]
        base_fields = [
            Field(name="base1", lsb=3, msb=4, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="base2", lsb=5, msb=6, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]

        result = derive_fields_caller(processed_fields, base_fields)
        assert len(result) == 4
        assert result[0].name == "processed1"
        assert result[1].name == "base1"
        assert result[2].name == "base2"
        assert result[3].name == "processed2"

    def test_merge_and_overwrite(self, derive_fields_caller: Callable[[list[Field], list[Field]], list[Field]]) -> None:
        processed_fields = [
            Field(name="processed1", lsb=0, msb=2, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="processed2", lsb=7, msb=8, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="processed3", lsb=9, msb=11, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]
        base_fields = [
            Field(name="base1", lsb=3, msb=4, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="base2", lsb=5, msb=6, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
            Field(name="base3", lsb=10, msb=10, access=AccessType.READ_WRITE, parsed=SVDField(name="")),
        ]

        result = derive_fields_caller(processed_fields, base_fields)
        assert len(result) == 5
        assert result[0].name == "processed1"
        assert result[1].name == "base1"
        assert result[2].name == "base2"
        assert result[3].name == "processed2"
        assert result[4].name == "processed3"


class TestRegistersClustersMap:
    @pytest.fixture(name="create_testdata", scope="function")
    def fixture_create_testdata(self) -> TestDataTuple:
        r1 = Register(
            name="r1",
            address_offset=0x0,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )
        r2 = Register(
            name="r2",
            address_offset=0x10,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )
        r3 = Register(
            name="r3",
            address_offset=0x0,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )
        r4 = Register(
            name="r4",
            address_offset=0x4,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )
        r5 = Register(
            name="r5",
            address_offset=0x8,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )
        r6 = Register(
            name="r6",
            address_offset=0x0,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )
        r7 = Register(
            name="r7",
            address_offset=0x0,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )
        r8 = Register(
            name="r8",
            address_offset=0x4,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )
        r9 = Register(
            name="r9",
            address_offset=0x8,
            size=32,
            access=None,  # type: ignore
            protection=None,  # type: ignore
            reset_value=0,
            reset_mask=0,
            parsed=None,  # type: ignore
        )

        cl3 = Cluster(name="cl3", address_offset=0x4, registers_clusters=[r7, r8, r9], parsed=None)  # type: ignore
        cl2 = Cluster(name="cl2", address_offset=0x14, registers_clusters=[r6, cl3], parsed=None)  # type: ignore
        cl1 = Cluster(name="cl1", address_offset=0x4, registers_clusters=[r3, r4, r5], parsed=None)  # type: ignore

        peripheral = Peripheral(
            name="peripheral",
            base_address=0x0,
            registers_clusters=[r1, cl1, r2, cl2],
            parsed=None,  # type: ignore
        )

        device = Device(
            name="device",
            version="1.0",
            description="Test Device",
            address_unit_bits=8,
            width=32,
            peripherals=[peripheral],
            parsed=None,  # type: ignore
        )

        return (device, peripheral, r1, r2, r3, r4, r5, r6, r7, r8, r9, cl1, cl2, cl3)

    def test_registers_clusters_map_simple(self, create_testdata: TestDataTuple):
        device, peripheral, r1, r2, r3, r4, r5, r6, r7, r8, r9, cl1, cl2, cl3 = create_testdata  # type: ignore

        registers_clusters_map = _RegisterClusterMap.build_map_from_registers_clusters([r1, cl1, r2, cl2])

        expected = [(0, 3, "r1"), (4, 15, "cl1"), (16, 19, "r2"), (20, 35, "cl2")]
        for start, end, reference in registers_clusters_map.regions:
            expected_start, expected_end, expected_name = expected.pop(0)
            assert start == expected_start
            assert end == expected_end
            assert reference.name == expected_name

    def test_registers_clusters_map_changed_order(self, create_testdata: TestDataTuple):
        device, peripheral, r1, r2, r3, r4, r5, r6, r7, r8, r9, cl1, cl2, cl3 = create_testdata  # type: ignore

        registers_clusters_map = _RegisterClusterMap.build_map_from_registers_clusters([r2, cl2, cl1, r1])

        expected = [(0, 3, "r1"), (4, 15, "cl1"), (16, 19, "r2"), (20, 35, "cl2")]
        for start, end, reference in registers_clusters_map.regions:
            expected_start, expected_end, expected_name = expected.pop(0)
            assert start == expected_start
            assert end == expected_end
            assert reference.name == expected_name

    def test_registers_clusters_map_changed_size(self, create_testdata: TestDataTuple):
        device, peripheral, r1, r2, r3, r4, r5, r6, r7, r8, r9, cl1, cl2, cl3 = create_testdata  # type: ignore

        r1.size = 16
        cl1.address_offset = 0x2
        r3.size = 8
        r4.address_offset = 0x1
        r5.size = 16
        r5.address_offset = 0x5
        r2.address_offset = 0x9
        r2.size = 64
        cl2.address_offset = 0x11
        cl3.address_offset = 0x0
        r8.size = 16
        r8.address_offset = 0x0
        r9.size = 8
        r9.address_offset = 0x2
        r7.size = 24
        r7.address_offset = 0x3
        r6.size = 64
        r6.address_offset = 0x6

        registers_clusters_map = _RegisterClusterMap.build_map_from_registers_clusters([r1, cl1, r2, cl2])

        expected = [(0, 1, "r1"), (2, 8, "cl1"), (9, 16, "r2"), (17, 30, "cl2")]
        for start, end, reference in registers_clusters_map.regions:
            expected_start, expected_end, expected_name = expected.pop(0)
            assert start == expected_start
            assert end == expected_end
            assert reference.name == expected_name

    def test_registers_clusters_map_changed_size_gaps(self, create_testdata: TestDataTuple):
        device, peripheral, r1, r2, r3, r4, r5, r6, r7, r8, r9, cl1, cl2, cl3 = create_testdata  # type: ignore

        r1.size = 16
        r1.address_offset = 0x4
        cl1.address_offset = 0x8
        r3.address_offset = 0x0
        r3.size = 8
        r4.address_offset = 0x4
        r4.size = 24
        r5.address_offset = 0x9
        r5.size = 16
        r2.address_offset = 0x13
        r2.size = 64
        cl2.address_offset = 0x1B
        r7.size = 24
        r8.address_offset = 0x7
        r8.size = 8
        r9.address_offset = 0x8
        r9.size = 16

        registers_clusters_map = _RegisterClusterMap.build_map_from_registers_clusters([r1, cl1, r2, cl2])

        expected = [(4, 5, "r1"), (8, 18, "cl1"), (19, 26, "r2"), (27, 40, "cl2")]
        for start, end, reference in registers_clusters_map.regions:
            expected_start, expected_end, expected_name = expected.pop(0)
            assert start == expected_start
            assert end == expected_end
            assert reference.name == expected_name

    def test_registers_clusters_map_r1_r2_overlapping(self, create_testdata: TestDataTuple):
        device, peripheral, r1, r2, r3, r4, r5, r6, r7, r8, r9, cl1, cl2, cl3 = create_testdata  # type: ignore

        r2.address_offset = 0x0

        registers_clusters_map = _RegisterClusterMap.build_map_from_registers_clusters([r1, cl1, r2, cl2])

        expected = [(0, 3, "r1"), (0, 3, "r2"), (4, 15, "cl1"), (20, 35, "cl2")]
        for start, end, reference in registers_clusters_map.regions:
            expected_start, expected_end, expected_name = expected.pop(0)
            assert start == expected_start
            assert end == expected_end
            assert reference.name == expected_name


class TestProcess:
    @pytest.fixture(name="parsed_device", scope="function")
    def fixture_parsed_device(self) -> SVDDevice:
        f1 = SVDField(name="f1", derived_from="p2.r5.f7", lsb=0, msb=2)
        f2 = SVDField(name="f2", derived_from="f3", lsb=0, msb=2)
        f3 = SVDField(name="f3", lsb=3, msb=4)
        f4 = SVDField(name="f4", derived_from="p%s.cl4.r6.f%s", lsb=0, msb=2)
        f5 = SVDField(name="f5", derived_from="p5.cl4.r6.f11", lsb=8, msb=10)
        f6 = SVDField(name="f6", derived_from="p1.cl1.r1.f1", lsb=0, msb=2)
        f7_f8_dim = SVDField(name="f%s", dim=2, dim_increment=2, dim_index="7,8", lsb=3, msb=4, description="test")
        f9 = SVDField(name="f9", derived_from="f8", lsb=7, msb=7)
        f10_f11_dim = SVDField(name="f%s", dim=2, dim_increment=4, dim_index="10-11", lsb=0, msb=3)

        r1 = SVDRegister(name="r1", derived_from="p2.r5", address_offset=0x0, fields=[f1])
        f1.parent = r1

        r2 = SVDRegister(name="r2", derived_from="p1.r8", address_offset=0x4, fields=[f2, f3])
        f2.parent = r2
        f3.parent = r2

        r3 = SVDRegister(name="r3", address_offset=0x0, fields=[])

        r4 = SVDRegister(name="r4", address_offset=0x0, fields=[f4, f5])
        f4.parent = r4
        f5.parent = r4

        r5 = SVDRegister(name="r5", address_offset=0x0, size=192, fields=[f6, f7_f8_dim, f9])
        f6.parent = r5
        f7_f8_dim.parent = r5
        f9.parent = r5

        r6 = SVDRegister(name="r6", derived_from="p1.cl2.cl3.r4", address_offset=0x0, fields=[f10_f11_dim])
        f10_f11_dim.parent = r6

        r7 = SVDRegister(name="r7", derived_from="p1.cl1.r1", address_offset=0x0, fields=[])
        r8 = SVDRegister(name="r8", address_offset=0xC, fields=[])
        r9 = SVDRegister(name="r9", address_offset=0x14, fields=[])

        cl1 = SVDCluster(name="cl1", description="test", address_offset=0x4, registers_clusters=[r1, r2])
        r1.parent = cl1
        r2.parent = cl1

        cl2 = SVDCluster(name="cl2", description="test", address_offset=0x10, registers_clusters=[r3])
        r3.parent = cl2

        cl3 = SVDCluster(name="cl3", description="test", address_offset=0x0, parent=cl2, registers_clusters=[r4])
        cl2.registers_clusters.append(cl3)
        r4.parent = cl3

        cl4_cl5_dim = SVDCluster(
            name="cl%s",
            description="test",
            dim=2,
            dim_increment=1,
            dim_index="4-5",
            address_offset=0x0,
            registers_clusters=[r6],
        )
        r6.parent = cl4_cl5_dim

        p1 = SVDPeripheral(name="p1", base_address=0x0, registers_clusters=[r7, cl1, r8, cl2, r9])
        r7.parent = p1
        cl1.parent = p1
        r8.parent = p1
        cl2.parent = p1
        r9.parent = p1

        p2 = SVDPeripheral(name="p2", derived_from="p1", base_address=0x0, registers_clusters=[r5])
        r5.parent = p2

        p3 = SVDPeripheral(name="p3", derived_from="p2", base_address=0x0, registers_clusters=[])

        p4_p5_dim = SVDPeripheral(
            name="p%s", dim=2, dim_increment=1, dim_index="4-5", base_address=0x0, registers_clusters=[cl4_cl5_dim]
        )
        cl4_cl5_dim.parent = p4_p5_dim

        return SVDDevice(
            name="d",
            xs_no_namespace_schema_location="",
            schema_version="",
            version="1",
            description="test description",
            address_unit_bits=8,
            width=32,
            peripherals=[p1, p2, p3, p4_p5_dim],
            access=AccessType.READ_WRITE,
            size=32,
            protection=ProtectionStringType.SECURE,
            reset_value=0,
            reset_mask=0xFFFFFFFF,
        )

    def test_basic(self, parsed_device: SVDDevice) -> None:
        device = Process(parsed_device).get_processed_device()

        assert len(device.peripherals) == 5
        assert device.peripherals[0].name == "p1"
        assert device.peripherals[1].name == "p2"
        assert device.peripherals[2].name == "p3"
        assert device.peripherals[3].name == "p4"
        assert device.peripherals[4].name == "p5"
        p1 = device.peripherals[0]
        p2 = device.peripherals[1]
        p3 = device.peripherals[2]
        p4 = device.peripherals[3]
        p5 = device.peripherals[4]

        assert len(p1.registers_clusters) == 5
        assert p1.registers_clusters[0].name == "r7"
        assert p1.registers_clusters[1].name == "cl1"
        assert p1.registers_clusters[2].name == "r8"
        assert p1.registers_clusters[3].name == "cl2"
        assert p1.registers_clusters[4].name == "r9"
        cl1 = p1.registers_clusters[1]
        cl2 = p1.registers_clusters[3]

        assert isinstance(cl1, Cluster)
        assert len(cl1.registers_clusters) == 2
        assert cl1.registers_clusters[0].name == "r1"
        assert cl1.registers_clusters[1].name == "r2"
        r1 = cl1.registers_clusters[0]
        r2 = cl1.registers_clusters[1]

        assert isinstance(r1, Register)
        assert len(r1.fields) == 4
        assert r1.fields[0].name == "f1"
        assert r1.fields[1].name == "f7"
        assert r1.fields[2].name == "f8"
        assert r1.fields[3].name == "f9"

        assert isinstance(r2, Register)
        assert len(r2.fields) == 2
        assert r2.fields[0].name == "f2"
        assert r2.fields[1].name == "f3"

        assert isinstance(cl2, Cluster)
        assert len(cl2.registers_clusters) == 2
        assert cl2.registers_clusters[0].name == "r3"
        assert cl2.registers_clusters[1].name == "cl3"
        cl3 = cl2.registers_clusters[1]

        assert isinstance(cl3, Cluster)
        assert len(cl3.registers_clusters) == 1
        assert cl3.registers_clusters[0].name == "r4"
        r4 = cl3.registers_clusters[0]

        assert isinstance(r4, Register)
        assert len(r4.fields) == 2
        assert r4.fields[0].name == "f4"
        assert r4.fields[1].name == "f5"

        assert len(p2.registers_clusters) == 1
        assert p2.registers_clusters[0].name == "r5"
        r5 = p2.registers_clusters[0]

        assert isinstance(r5, Register)
        assert len(r5.fields) == 4
        assert r5.fields[0].name == "f6"
        assert r5.fields[1].name == "f7"
        assert r5.fields[2].name == "f8"
        assert r5.fields[3].name == "f9"
        f6 = r5.fields[0]
        f7 = r5.fields[1]
        f8 = r5.fields[2]
        f9 = r5.fields[3]
        assert f6.lsb == 0
        assert f6.msb == 2
        assert f7.lsb == 3
        assert f7.msb == 4
        assert f8.lsb == 5
        assert f8.msb == 6
        assert f9.lsb == 7
        assert f9.msb == 7
        assert f9.description == "test"

        assert len(p3.registers_clusters) == 1
        assert p3.registers_clusters[0].name == "r5"
        assert isinstance(p3.registers_clusters[0], Register)
        assert len(p3.registers_clusters[0].fields) == 4
        assert p3.registers_clusters[0].fields[0].name == "f6"
        assert p3.registers_clusters[0].fields[1].name == "f7"
        assert p3.registers_clusters[0].fields[2].name == "f8"
        assert p3.registers_clusters[0].fields[3].name == "f9"

        assert len(p4.registers_clusters) == 2
        assert p4.registers_clusters[0].name == "cl4"
        assert p4.registers_clusters[1].name == "cl5"
        cl4_p4 = p4.registers_clusters[0]
        cl5_p4 = p4.registers_clusters[1]

        assert isinstance(cl4_p4, Cluster)
        assert len(cl4_p4.registers_clusters) == 1
        assert cl4_p4.registers_clusters[0].name == "r6"
        r6_cl4_p4 = cl4_p4.registers_clusters[0]

        assert isinstance(r6_cl4_p4, Register)
        assert len(r6_cl4_p4.fields) == 3
        assert r6_cl4_p4.fields[0].name == "f10"
        assert r6_cl4_p4.fields[1].name == "f11"
        assert r6_cl4_p4.fields[2].name == "f5"

        assert isinstance(cl5_p4, Cluster)
        assert len(cl5_p4.registers_clusters) == 1
        assert cl5_p4.registers_clusters[0].name == "r6"
        r6_cl5_p4 = cl5_p4.registers_clusters[0]

        assert isinstance(r6_cl5_p4, Register)
        assert len(r6_cl5_p4.fields) == 3
        assert r6_cl5_p4.fields[0].name == "f10"
        assert r6_cl5_p4.fields[1].name == "f11"
        assert r6_cl5_p4.fields[2].name == "f5"

        assert len(p5.registers_clusters) == 2
        assert p5.registers_clusters[0].name == "cl4"
        assert p5.registers_clusters[1].name == "cl5"
        cl4_p5 = p5.registers_clusters[0]
        cl5_p5 = p5.registers_clusters[1]

        assert isinstance(cl4_p5, Cluster)
        assert len(cl4_p5.registers_clusters) == 1
        assert cl4_p5.registers_clusters[0].name == "r6"
        r6_cl4_p5 = cl4_p5.registers_clusters[0]

        assert isinstance(r6_cl4_p5, Register)
        assert len(r6_cl4_p5.fields) == 3
        assert r6_cl4_p5.fields[0].name == "f10"
        assert r6_cl4_p5.fields[1].name == "f11"
        assert r6_cl4_p5.fields[2].name == "f5"

        assert isinstance(cl5_p5, Cluster)
        assert len(cl5_p5.registers_clusters) == 1
        assert cl5_p5.registers_clusters[0].name == "r6"
        r6_cl5_p5 = cl5_p5.registers_clusters[0]

        assert isinstance(r6_cl5_p5, Register)
        assert len(r6_cl5_p5.fields) == 3
        assert r6_cl5_p5.fields[0].name == "f10"
        assert r6_cl5_p5.fields[1].name == "f11"
        assert r6_cl5_p5.fields[2].name == "f5"

    def test_r5_normal_size(self, parsed_device: SVDDevice) -> None:
        r5 = parsed_device.peripherals[1].registers_clusters[0]
        assert r5.name == "r5"
        r5.size = 32

        device = Process(parsed_device).get_processed_device()
        assert len(device.peripherals) == 5
        assert device.peripherals[1].name == "p2"
        p2 = device.peripherals[1]
        assert len(p2.registers_clusters) == 5
        assert p2.registers_clusters[0].name == "r5"
        assert p2.registers_clusters[1].name == "cl1"
        assert p2.registers_clusters[2].name == "r8"
        assert p2.registers_clusters[3].name == "cl2"
        assert p2.registers_clusters[4].name == "r9"

    def test_r5_offset_deriving(self, parsed_device: SVDDevice) -> None:
        r5 = parsed_device.peripherals[1].registers_clusters[0]
        assert r5.name == "r5"
        r5.address_offset = 0x30

        device = Process(parsed_device).get_processed_device()
        assert len(device.peripherals) == 5
        assert device.peripherals[1].name == "p2"
        p2 = device.peripherals[1]
        assert len(p2.registers_clusters) == 6
        assert p2.registers_clusters[0].name == "r7"
        assert p2.registers_clusters[1].name == "cl1"
        assert p2.registers_clusters[2].name == "r8"
        assert p2.registers_clusters[3].name == "cl2"
        assert p2.registers_clusters[4].name == "r9"
        assert p2.registers_clusters[5].name == "r5"

    def test_to_xml(self, parsed_device: SVDDevice, get_test_svd_file_content: Callable[[str], bytes]) -> None:
        svd_device = Process(parsed_device).convert_processed_device_to_svd_device()

        with tempfile.TemporaryDirectory() as temp_dir:
            Serializer.device_to_svd_file(temp_dir + "/test.svd", svd_device, pretty_print=True)

            with open(temp_dir + "/test.svd", "rb") as f:
                test_content = f.read()

        expected_content = get_test_svd_file_content("process_to_xml_expected.svd")

        assert expected_content == test_content
