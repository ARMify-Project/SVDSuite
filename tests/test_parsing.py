from typing import Callable, Any
import pytest

from svdsuite.parse import Parser, ParserException, _to_int  # type: ignore
from svdsuite.model.parse import (
    SVDAddressBlock,
    SVDCluster,
    SVDCPU,
    SVDDevice,
    SVDEnumeratedValueContainer,
    SVDEnumeratedValue,
    SVDField,
    SVDInterrupt,
    SVDPeripheral,
    SVDRegister,
    SVDSauRegion,
    SVDSauRegionsConfig,
    SVDWriteConstraint,
    AccessType,
    CPUNameType,
    DataTypeType,
    EndianType,
    EnumeratedTokenType,
    EnumUsageType,
    ModifiedWriteValuesType,
    ProtectionStringType,
    ReadActionType,
    SauAccessType,
)


@pytest.fixture(name="get_device", scope="session")
def fixture_get_device(get_test_svd_file_content: Callable[[str], bytes]) -> Callable[[], SVDDevice]:
    def _():
        file_content = get_test_svd_file_content("parser_testfile.svd")

        parser = Parser.from_xml_content(file_content)
        return parser.get_parsed_device()

    return _


@pytest.fixture(name="get_device_with_element_modification", scope="session")
def fixture_get_device_with_element_modification(
    modify_test_svd_file_and_get_content: Callable[[str, str, None | str, None | str], bytes],
) -> Callable[[str, None | str], SVDDevice]:
    def _(xpath: str, test_input: None | str):
        file_content = modify_test_svd_file_and_get_content("parser_testfile.svd", xpath, None, test_input)

        parser = Parser.from_xml_content(file_content)
        return parser.get_parsed_device()

    return _


@pytest.fixture(name="get_device_with_attribute_modification", scope="session")
def fixture_get_device_with_attribute_modification(
    modify_test_svd_file_and_get_content: Callable[[str, str, None | str, None | str], bytes],
) -> Callable[[str, None | str, None | str], SVDDevice]:
    def _(xpath: str, attribute: None | str, test_input: None | str):
        file_content = modify_test_svd_file_and_get_content("parser_testfile.svd", xpath, attribute, test_input)

        parser = Parser.from_xml_content(file_content)
        return parser.get_parsed_device()

    return _


class TestParserInstantiation:
    def test_cls_for_xml_file(self, get_test_svd_file_path: Callable[[str], str]):
        file_path = get_test_svd_file_path("parser_testfile.svd")
        parser = Parser.from_svd_file(file_path)

        assert isinstance(parser, Parser)

    def test_for_xml_str(self, get_test_svd_file_content: Callable[[str], bytes]):
        file_content = get_test_svd_file_content("parser_testfile.svd")
        file_str = file_content.decode()
        parser = Parser.from_xml_str(file_str)

        assert isinstance(parser, Parser)

    def test_cls_for_xml_content(self, get_test_svd_file_content: Callable[[str], bytes]):
        file_content = get_test_svd_file_content("parser_testfile.svd")
        parser = Parser.from_xml_content(file_content)

        assert isinstance(parser, Parser)


class TestToInt:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("+5", 5),
            ("+0x5", 5),
            ("+0X5", 5),
            ("+0xaAbB", 43707),
            ("+0x9f", 159),
            ("5", 5),
            ("0x5", 5),
            ("0X5", 5),
            ("0xaAbB", 43707),
            ("0x9f", 159),
            ("+#101", 5),
            pytest.param(None, None),
            pytest.param("+!", None, marks=pytest.mark.xfail(strict=True, raises=NotImplementedError)),
        ],
    )
    def test_to_int(self, test_input: str, expected: int):
        assert _to_int(test_input) == expected


class TestDeviceParsing:
    def test_xs_no_namespace_schema_location(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert device.xs_no_namespace_schema_location == "CMSIS-SVD.xsd"

    def test_schema_version(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert device.schema_version == "1.3"

    @pytest.mark.parametrize("test_input,expected", [("ARM Ltd.", "ARM Ltd."), pytest.param(None, None)])
    def test_vendor(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/vendor", test_input)

        assert device.vendor == expected

    @pytest.mark.parametrize("test_input,expected", [("ARM", "ARM"), pytest.param(None, None)])
    def test_vendor_id(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/vendorID", test_input)

        assert device.vendor_id == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("ARM_Example", "ARM_Example"),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/name", test_input)

        assert device.name == expected

    @pytest.mark.parametrize("test_input,expected", [("ARMCM3", "ARMCM3"), pytest.param(None, None)])
    def test_series(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/series", test_input)

        assert device.series == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("1.2", "1.2"), pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException))],
    )
    def test_version(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/version", test_input)

        assert device.version == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("This is a description", "This is a description"), (None, "")],
    )
    def test_description(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/description", test_input)

        assert device.description == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("ARM Limited (ARM) is supplying\n", "ARM Limited (ARM) is supplying\n"), pytest.param(None, None)],
    )
    def test_license_text(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/licenseText", test_input)

        assert device.license_text == expected

    def test_cpu(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert isinstance(device.cpu, SVDCPU)
        assert device.cpu.parent == device

    @pytest.mark.parametrize("test_input,expected", [("asd", "asd"), pytest.param(None, None)])
    def test_header_system_filename(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/headerSystemFilename", test_input)

        assert device.header_system_filename == expected

    @pytest.mark.parametrize("test_input,expected", [("fff", "fff"), pytest.param(None, None)])
    def test_header_definitions_prefix(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/headerDefinitionsPrefix", test_input)

        assert device.header_definitions_prefix == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_address_unit_bits(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/addressUnitBits", test_input)

        assert device.address_unit_bits == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_width(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/width", test_input)

        assert device.width == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_size(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/size", test_input)

        assert device.size == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("read-only", AccessType.READ_ONLY),
            ("write-only", AccessType.WRITE_ONLY),
            ("read-write", AccessType.READ_WRITE),
            ("writeOnce", AccessType.WRITE_ONCE),
            ("read-writeOnce", AccessType.READ_WRITE_ONCE),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/access", test_input)

        assert device.access == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("s", ProtectionStringType.SECURE),
            ("n", ProtectionStringType.NON_SECURE),
            ("p", ProtectionStringType.PRIVILEGED),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/protection", test_input)

        assert device.protection == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_reset_value(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/resetValue", test_input)

        assert device.reset_value == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_reset_mask(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/resetMask", test_input)

        assert device.reset_mask == expected

    def test_peripherals(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert device.peripherals[0].parent == device


class TestCPUParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("CM0", CPUNameType.CM0),
            ("CM0PLUS", CPUNameType.CM0PLUS),
            ("CM0+", CPUNameType.CM0_PLUS),
            ("CM1", CPUNameType.CM1),
            ("CM3", CPUNameType.CM3),
            ("CM4", CPUNameType.CM4),
            ("CM7", CPUNameType.CM7),
            ("CM23", CPUNameType.CM23),
            ("CM33", CPUNameType.CM33),
            ("CM35P", CPUNameType.CM35P),
            ("CM52", CPUNameType.CM52),
            ("CM55", CPUNameType.CM55),
            ("CM85", CPUNameType.CM85),
            ("SC000", CPUNameType.SC000),
            ("SC300", CPUNameType.SC300),
            ("ARMV8MML", CPUNameType.ARMV8MML),
            ("ARMV8MBL", CPUNameType.ARMV8MBL),
            ("ARMV81MML", CPUNameType.ARMV81MML),
            ("CA5", CPUNameType.CA5),
            ("CA7", CPUNameType.CA7),
            ("CA8", CPUNameType.CA8),
            ("CA9", CPUNameType.CA9),
            ("CA15", CPUNameType.CA15),
            ("CA17", CPUNameType.CA17),
            ("CA53", CPUNameType.CA53),
            ("CA57", CPUNameType.CA57),
            ("CA72", CPUNameType.CA72),
            ("SMC1", CPUNameType.SMC1),
            ("other", CPUNameType.OTHER),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/name", test_input)

        assert device.cpu is not None
        assert device.cpu.name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("r1p0", "r1p0"),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_revision(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/revision", test_input)

        assert device.cpu is not None
        assert device.cpu.revision == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("little", EndianType.LITTLE),
            ("big", EndianType.BIG),
            ("selectable", EndianType.SELECTABLE),
            ("other", EndianType.OTHER),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_endian(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/endian", test_input)

        assert device.cpu is not None
        assert device.cpu.endian == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_mpu_present(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/mpuPresent", test_input)

        assert device.cpu is not None
        assert device.cpu.mpu_present == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_fpu_present(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/fpuPresent", test_input)

        assert device.cpu is not None
        assert device.cpu.fpu_present == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_fpu_dp(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/fpuDP", test_input)

        assert device.cpu is not None
        assert device.cpu.fpu_dp == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_dsp_present(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/dspPresent", test_input)

        assert device.cpu is not None
        assert device.cpu.dsp_present == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_icache_present(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/icachePresent", test_input)

        assert device.cpu is not None
        assert device.cpu.icache_present == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_dcache_present(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/dcachePresent", test_input)

        assert device.cpu is not None
        assert device.cpu.dcache_present == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_itcm_present(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/itcmPresent", test_input)

        assert device.cpu is not None
        assert device.cpu.itcm_present == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_dtcm_present(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/dtcmPresent", test_input)

        assert device.cpu is not None
        assert device.cpu.dtcm_present == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_vtor_present(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/vtorPresent", test_input)

        assert device.cpu is not None
        assert device.cpu.vtor_present == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_nvic_prio_bits(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/nvicPrioBits", test_input)

        assert device.cpu is not None
        assert device.cpu.nvic_prio_bits == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_vendor_systick_config(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/vendorSystickConfig", test_input)

        assert device.cpu is not None
        assert device.cpu.vendor_systick_config == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_device_num_interrupts(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/deviceNumInterrupts", test_input)

        assert device.cpu is not None
        assert device.cpu.device_num_interrupts == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_sau_num_regions(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/sauNumRegions", test_input)

        assert device.cpu is not None
        assert device.cpu.sau_num_regions == expected

    def test_sau_regions_config(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert device.cpu is not None
        assert isinstance(device.cpu.sau_regions_config, SVDSauRegionsConfig)
        assert device.cpu.sau_regions_config.parent == device.cpu


class TestSauRegionsConfigParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_enabled(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification("/device/cpu/sauRegionsConfig", "enabled", test_input)

        assert device.cpu is not None
        assert device.cpu.sau_regions_config is not None
        assert device.cpu.sau_regions_config.enabled == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("s", ProtectionStringType.SECURE),
            ("n", ProtectionStringType.NON_SECURE),
            ("p", ProtectionStringType.PRIVILEGED),
            pytest.param(None, None),
        ],
    )
    def test_protection_when_disabled(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification(
            "/device/cpu/sauRegionsConfig", "protectionWhenDisabled", test_input
        )

        assert device.cpu is not None
        assert device.cpu.sau_regions_config is not None
        assert device.cpu.sau_regions_config.protection_when_disabled == expected

    def test_regions(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert device.cpu is not None
        assert device.cpu.sau_regions_config is not None
        assert len(device.cpu.sau_regions_config.regions) == 2
        assert isinstance(device.cpu.sau_regions_config.regions[0], SVDSauRegion)
        assert isinstance(device.cpu.sau_regions_config.regions[1], SVDSauRegion)
        assert device.cpu.sau_regions_config.regions[0].enabled is True
        assert device.cpu.sau_regions_config.regions[0].name == "SAU1"
        assert device.cpu.sau_regions_config.regions[0].base == 0x10001000
        assert device.cpu.sau_regions_config.regions[0].limit == 0x10005000
        assert device.cpu.sau_regions_config.regions[0].access == SauAccessType.NON_SECURE
        assert device.cpu.sau_regions_config.regions[1].enabled is False
        assert device.cpu.sau_regions_config.regions[1].name is None
        assert device.cpu.sau_regions_config.regions[1].base == 0x10005000
        assert device.cpu.sau_regions_config.regions[1].limit == 0x10007000
        assert device.cpu.sau_regions_config.regions[1].access == SauAccessType.NON_SECURE_CALLABLE
        assert device.cpu.sau_regions_config.regions[0].parent == device.cpu.sau_regions_config
        assert device.cpu.sau_regions_config.regions[1].parent == device.cpu.sau_regions_config


class TestSauRegionParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_enabled(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification("/device/cpu/sauRegionsConfig/region", "enabled", test_input)

        assert device.cpu is not None
        assert device.cpu.sau_regions_config is not None
        assert len(device.cpu.sau_regions_config.regions) > 0
        assert device.cpu.sau_regions_config.regions[0].enabled == expected

    @pytest.mark.parametrize("test_input,expected", [("SAU1", "SAU1"), pytest.param(None, None)])
    def test_name(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification("/device/cpu/sauRegionsConfig/region", "name", test_input)

        assert device.cpu is not None
        assert device.cpu.sau_regions_config is not None
        assert len(device.cpu.sau_regions_config.regions) > 0
        assert device.cpu.sau_regions_config.regions[0].name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_base(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/sauRegionsConfig/region/base", test_input)

        assert device.cpu is not None
        assert device.cpu.sau_regions_config is not None
        assert len(device.cpu.sau_regions_config.regions) > 0
        assert device.cpu.sau_regions_config.regions[0].base == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_limit(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/sauRegionsConfig/region/limit", test_input)

        assert device.cpu is not None
        assert device.cpu.sau_regions_config is not None
        assert len(device.cpu.sau_regions_config.regions) > 0
        assert device.cpu.sau_regions_config.regions[0].limit == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("c", SauAccessType.NON_SECURE_CALLABLE),
            ("n", SauAccessType.NON_SECURE),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_access(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/cpu/sauRegionsConfig/region/access", test_input)

        assert device.cpu is not None
        assert device.cpu.sau_regions_config is not None
        assert len(device.cpu.sau_regions_config.regions) > 0
        assert device.cpu.sau_regions_config.regions[0].access == expected


class TestPeripheralParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("teststr", "teststr"),
            pytest.param(None, None),
        ],
    )
    def test_derived_from(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification("/device/peripherals/peripheral", "derivedFrom", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].derived_from == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_dim(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/dim", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_dim_increment(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/dimIncrement", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim_increment == expected

    @pytest.mark.parametrize("test_input,expected", [("Test", "Test"), pytest.param(None, None)])
    def test_dim_index(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/dimIndex", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim_index == expected

    @pytest.mark.parametrize("test_input,expected", [("Test", "Test"), pytest.param(None, None)])
    def test_dim_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/dimName", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim_name == expected

    def test_dim_array_index(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert device.peripherals[0].dim_array_index is not None
        assert device.peripherals[0].dim_array_index.parent == device.peripherals[0]

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("Timer%s", "Timer%s"),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/name", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].name == expected

    @pytest.mark.parametrize("test_input,expected", [("1.0", "1.0"), pytest.param(None, None)])
    def test_version(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/version", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].version == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("Timer 1 is a standard timer ...", "Timer 1 is a standard timer ..."), pytest.param(None, None)],
    )
    def test_description(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/description", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].description == expected

    @pytest.mark.parametrize("test_input,expected", [("TestAlternate", "TestAlternate"), pytest.param(None, None)])
    def test_alternate_peripheral(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/alternatePeripheral", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].alternate_peripheral == expected

    @pytest.mark.parametrize("test_input,expected", [("TestGroupName", "TestGroupName"), pytest.param(None, None)])
    def test_group_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/groupName", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].group_name == expected

    @pytest.mark.parametrize("test_input,expected", [("PreTest", "PreTest"), pytest.param(None, None)])
    def test_prepend_to_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/prependToName", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].prepend_to_name == expected

    @pytest.mark.parametrize("test_input,expected", [("AppendTest", "AppendTest"), pytest.param(None, None)])
    def test_append_to_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/appendToName", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].append_to_name == expected

    @pytest.mark.parametrize("test_input,expected", [("HeadTest", "HeadTest"), pytest.param(None, None)])
    def test_header_struct_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/headerStructName", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].header_struct_name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("(System->ClockControl->apbEnable == 0)", "(System->ClockControl->apbEnable == 0)"),
            pytest.param(None, None),
        ],
    )
    def test_disable_condition(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/disableCondition", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].disable_condition == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_base_address(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/baseAddress", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].base_address == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_size(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/size", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].size == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("read-only", AccessType.READ_ONLY),
            ("write-only", AccessType.WRITE_ONLY),
            ("read-write", AccessType.READ_WRITE),
            ("writeOnce", AccessType.WRITE_ONCE),
            ("read-writeOnce", AccessType.READ_WRITE_ONCE),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/access", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].access == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("s", ProtectionStringType.SECURE),
            ("n", ProtectionStringType.NON_SECURE),
            ("p", ProtectionStringType.PRIVILEGED),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/protection", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].protection == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_reset_value(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/resetValue", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].reset_value == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_reset_mask(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/resetMask", test_input)

        assert len(device.peripherals) > 0
        assert device.peripherals[0].reset_mask == expected

    def test_address_blocks(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert len(device.peripherals[0].address_blocks) == 2
        assert isinstance(device.peripherals[0].address_blocks[0], SVDAddressBlock)
        assert isinstance(device.peripherals[0].address_blocks[1], SVDAddressBlock)
        assert device.peripherals[0].address_blocks[0].offset == 0x0
        assert device.peripherals[0].address_blocks[0].size == 0x400
        assert device.peripherals[0].address_blocks[0].protection == ProtectionStringType.SECURE
        assert device.peripherals[0].address_blocks[1].offset == 0x400
        assert device.peripherals[0].address_blocks[1].size == 0x800
        assert device.peripherals[0].address_blocks[1].protection == ProtectionStringType.NON_SECURE
        assert device.peripherals[0].address_blocks[0].parent == device.peripherals[0]
        assert device.peripherals[0].address_blocks[1].parent == device.peripherals[0]

    def test_interrupts(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert len(device.peripherals[0].interrupts) == 2
        assert isinstance(device.peripherals[0].interrupts[0], SVDInterrupt)
        assert isinstance(device.peripherals[0].interrupts[1], SVDInterrupt)
        assert device.peripherals[0].interrupts[0].name == "TIM0"
        assert device.peripherals[0].interrupts[0].description == "This is a description"
        assert device.peripherals[0].interrupts[0].value == 3
        assert device.peripherals[0].interrupts[1].name == "TIM1"
        assert device.peripherals[0].interrupts[1].description == "This is a second description"
        assert device.peripherals[0].interrupts[1].value == 4
        assert device.peripherals[0].interrupts[0].parent == device.peripherals[0]
        assert device.peripherals[0].interrupts[1].parent == device.peripherals[0]

    def test_registers_clusters(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert len(device.peripherals[0].registers_clusters) == 2
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[0].parent == device.peripherals[0]
        assert device.peripherals[0].registers_clusters[1].parent == device.peripherals[0]


class TestDimArrayIndexParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("FSMC_EnumArray", "FSMC_EnumArray"),
            pytest.param(None, None),
        ],
    )
    def test_header_enum_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/dimArrayIndex/headerEnumName", test_input
        )

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim_array_index is not None
        assert device.peripherals[0].dim_array_index.header_enum_name == expected

    def test_enumerated_values(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert device.peripherals[0].dim_array_index is not None
        assert len(device.peripherals[0].dim_array_index.enumerated_values) == 2
        assert isinstance(device.peripherals[0].dim_array_index.enumerated_values[0], SVDEnumeratedValue)
        assert isinstance(device.peripherals[0].dim_array_index.enumerated_values[1], SVDEnumeratedValue)
        assert device.peripherals[0].dim_array_index.enumerated_values[0].name == "UART0"
        assert device.peripherals[0].dim_array_index.enumerated_values[0].description == "UART0 Peripheral"
        assert device.peripherals[0].dim_array_index.enumerated_values[0].value == "0"
        assert device.peripherals[0].dim_array_index.enumerated_values[0].is_default is None
        assert device.peripherals[0].dim_array_index.enumerated_values[1].name == "UART1"
        assert device.peripherals[0].dim_array_index.enumerated_values[1].description is None
        assert device.peripherals[0].dim_array_index.enumerated_values[1].value is None
        assert device.peripherals[0].dim_array_index.enumerated_values[1].is_default is True

    def test_enumerated_values_parent(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert device.peripherals[0].dim_array_index is not None
        assert len(device.peripherals[0].dim_array_index.enumerated_values) == 2
        assert isinstance(device.peripherals[0].dim_array_index.enumerated_values[0], SVDEnumeratedValue)
        assert isinstance(device.peripherals[0].dim_array_index.enumerated_values[1], SVDEnumeratedValue)

        dim_array_index = device.peripherals[0].dim_array_index

        assert dim_array_index.enumerated_values[0].parent == dim_array_index
        assert dim_array_index.enumerated_values[1].parent == dim_array_index


class TestEnumeratedValueParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("UART0", "UART0"),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/dimArrayIndex/enumeratedValue/name", test_input
        )

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim_array_index is not None
        assert len(device.peripherals[0].dim_array_index.enumerated_values) > 0
        assert device.peripherals[0].dim_array_index.enumerated_values[0].name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("UART0 Peripheral", "UART0 Peripheral"), pytest.param(None, None)],
    )
    def test_description(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/dimArrayIndex/enumeratedValue/description", test_input
        )

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim_array_index is not None
        assert len(device.peripherals[0].dim_array_index.enumerated_values) > 0
        assert device.peripherals[0].dim_array_index.enumerated_values[0].description == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("0", "0"), pytest.param(None, None)],
    )
    def test_value(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/dimArrayIndex/enumeratedValue/value", test_input
        )

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim_array_index is not None
        assert len(device.peripherals[0].dim_array_index.enumerated_values) > 0
        assert device.peripherals[0].dim_array_index.enumerated_values[0].value == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_is_default(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/dimArrayIndex/enumeratedValue/isDefault", test_input
        )

        assert len(device.peripherals) > 0
        assert device.peripherals[0].dim_array_index is not None
        assert len(device.peripherals[0].dim_array_index.enumerated_values) > 0
        assert device.peripherals[0].dim_array_index.enumerated_values[0].is_default == expected


class TestAddressBlockParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            (None, 0),
        ],
    )
    def test_offset(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/addressBlock/offset", test_input)

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].address_blocks) > 0
        assert device.peripherals[0].address_blocks[0].offset == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_size(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/addressBlock/size", test_input)

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].address_blocks) > 0
        assert device.peripherals[0].address_blocks[0].size == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("registers", EnumeratedTokenType.REGISTERS),
            ("buffer", EnumeratedTokenType.BUFFER),
            ("reserved", EnumeratedTokenType.RESERVED),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_usage(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/addressBlock/usage", test_input)

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].address_blocks) > 0
        assert device.peripherals[0].address_blocks[0].usage == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("s", ProtectionStringType.SECURE),
            ("n", ProtectionStringType.NON_SECURE),
            ("p", ProtectionStringType.PRIVILEGED),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/addressBlock/protection", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].address_blocks) > 0
        assert device.peripherals[0].address_blocks[0].protection == expected


class TestInterruptParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("TIM0", "TIM0"),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/interrupt/name", test_input)

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].interrupts) > 0
        assert device.peripherals[0].interrupts[0].name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("TIM0 Interrupt", "TIM0 Interrupt"), pytest.param(None, None)],
    )
    def test_description(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/interrupt/description", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].interrupts) > 0
        assert device.peripherals[0].interrupts[0].description == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            (None, 0),
        ],
    )
    def test_value(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification("/device/peripherals/peripheral/interrupt/value", test_input)

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].interrupts) > 0
        assert device.peripherals[0].interrupts[0].value == expected


class TestClusterParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("teststr", "teststr"),
            pytest.param(None, None),
        ],
    )
    def test_derived_from(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification(
            "/device/peripherals/peripheral/registers/cluster", "derivedFrom", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].derived_from == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_dim(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/dim", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].dim == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_dim_increment(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/dimIncrement", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].dim_increment == expected

    @pytest.mark.parametrize("test_input,expected", [("Test", "Test"), pytest.param(None, None)])
    def test_dim_index(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/dimIndex", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].dim_index == expected

    @pytest.mark.parametrize("test_input,expected", [("Test", "Test"), pytest.param(None, None)])
    def test_dim_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/dimName", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].dim_name == expected

    def test_dim_array_index(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].dim_array_index is not None
        assert (
            device.peripherals[0].registers_clusters[0].dim_array_index.parent
            == device.peripherals[0].registers_clusters[0]
        )

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("Cluster%s", "Cluster%s"),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/name", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("This is a cluster", "This is a cluster"), pytest.param(None, None)],
    )
    def test_description(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/description", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].description == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("ClusterOrig", "ClusterOrig"), pytest.param(None, None)],
    )
    def test_alternate_cluster(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/alternateCluster", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].alternate_cluster == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("HeaderStruct", "HeaderStruct"), pytest.param(None, None)],
    )
    def test_header_struct_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/headerStructName", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].header_struct_name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_address_offset(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/addressOffset", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].address_offset == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_size(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/size", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].size == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("read-only", AccessType.READ_ONLY),
            ("write-only", AccessType.WRITE_ONLY),
            ("read-write", AccessType.READ_WRITE),
            ("writeOnce", AccessType.WRITE_ONCE),
            ("read-writeOnce", AccessType.READ_WRITE_ONCE),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/access", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].access == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("s", ProtectionStringType.SECURE),
            ("n", ProtectionStringType.NON_SECURE),
            ("p", ProtectionStringType.PRIVILEGED),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/protection", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].protection == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_reset_value(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/resetValue", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].reset_value == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_reset_mask(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/cluster/resetMask", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert device.peripherals[0].registers_clusters[0].reset_mask == expected

    def test_registers_clusters(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[0], SVDCluster)
        assert len(device.peripherals[0].registers_clusters[0].registers_clusters) == 3
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[0], SVDRegister)
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[1], SVDCluster)
        assert isinstance(device.peripherals[0].registers_clusters[0].registers_clusters[2], SVDRegister)
        assert (
            device.peripherals[0].registers_clusters[0].registers_clusters[0].parent
            == device.peripherals[0].registers_clusters[0]
        )
        assert (
            device.peripherals[0].registers_clusters[0].registers_clusters[1].parent
            == device.peripherals[0].registers_clusters[0]
        )
        assert (
            device.peripherals[0].registers_clusters[0].registers_clusters[2].parent
            == device.peripherals[0].registers_clusters[0]
        )


class TestRegisterParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("teststr", "teststr"),
            pytest.param(None, None),
        ],
    )
    def test_derived_from(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification(
            "/device/peripherals/peripheral/registers/register", "derivedFrom", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].derived_from == expected

    @pytest.mark.parametrize("test_input,expected", [("4", 4), ("0x4", 4), pytest.param(None, None)])
    def test_dim(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/dim", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].dim == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_dim_increment(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/dimIncrement", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].dim_increment == expected

    @pytest.mark.parametrize("test_input,expected", [("0,1,2,3", "0,1,2,3"), pytest.param(None, None)])
    def test_dim_index(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/dimIndex", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].dim_index == expected

    @pytest.mark.parametrize("test_input,expected", [("Test", "Test"), pytest.param(None, None)])
    def test_dim_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/dimName", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].dim_name == expected

    def test_dim_array_index(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].dim_array_index is not None
        assert (
            device.peripherals[0].registers_clusters[1].dim_array_index.parent
            == device.peripherals[0].registers_clusters[1]
        )

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("Register%s", "Register%s"),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/name", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("Display name", "Display name"), pytest.param(None, None)],
    )
    def test_display_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/displayName", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].display_name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("This is a register", "This is a register"), pytest.param(None, None)],
    )
    def test_description(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/description", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].description == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("AltGroup", "AltGroup"), pytest.param(None, None)],
    )
    def test_alternate_group(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/alternateGroup", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].alternate_group == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("AltRegister", "AltRegister"), pytest.param(None, None)],
    )
    def test_alternate_register(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/alternateRegister", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].alternate_register == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("100", 100),
            ("0x64", 100),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_address_offset(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/addressOffset", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].address_offset == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_size(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/size", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].size == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("read-only", AccessType.READ_ONLY),
            ("write-only", AccessType.WRITE_ONLY),
            ("read-write", AccessType.READ_WRITE),
            ("writeOnce", AccessType.WRITE_ONCE),
            ("read-writeOnce", AccessType.READ_WRITE_ONCE),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/access", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].access == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("s", ProtectionStringType.SECURE),
            ("n", ProtectionStringType.NON_SECURE),
            ("p", ProtectionStringType.PRIVILEGED),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/protection", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].protection == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_reset_value(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/resetValue", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].reset_value == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_reset_mask(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/resetMask", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].reset_mask == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("uint8_t", DataTypeType.UINT8_T),
            ("uint16_t", DataTypeType.UINT16_T),
            ("uint32_t", DataTypeType.UINT32_T),
            ("uint64_t", DataTypeType.UINT64_T),
            ("int8_t", DataTypeType.INT8_T),
            ("int16_t", DataTypeType.INT16_T),
            ("int32_t", DataTypeType.INT32_T),
            ("int64_t", DataTypeType.INT64_T),
            ("uint8_t *", DataTypeType.UINT8_T_PTR),
            ("uint16_t *", DataTypeType.UINT16_T_PTR),
            ("uint32_t *", DataTypeType.UINT32_T_PTR),
            ("uint64_t *", DataTypeType.UINT64_T_PTR),
            ("int8_t *", DataTypeType.INT8_T_PTR),
            ("int16_t *", DataTypeType.INT16_T_PTR),
            ("int32_t *", DataTypeType.INT32_T_PTR),
            ("int64_t *", DataTypeType.INT64_T_PTR),
            pytest.param(None, None),
        ],
    )
    def test_data_type(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/dataType", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].data_type == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("oneToClear", ModifiedWriteValuesType.ONE_TO_CLEAR),
            ("oneToSet", ModifiedWriteValuesType.ONE_TO_SET),
            ("oneToToggle", ModifiedWriteValuesType.ONE_TO_TOGGLE),
            ("zeroToClear", ModifiedWriteValuesType.ZERO_TO_CLEAR),
            ("zeroToSet", ModifiedWriteValuesType.ZERO_TO_SET),
            ("zeroToToggle", ModifiedWriteValuesType.ZERO_TO_TOGGLE),
            ("clear", ModifiedWriteValuesType.CLEAR),
            ("set", ModifiedWriteValuesType.SET),
            ("modify", ModifiedWriteValuesType.MODIFY),
            pytest.param(None, None),
        ],
    )
    def test_modified_write_values(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/modifiedWriteValues", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].modified_write_values == expected

    def test_write_constraint(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert isinstance(device.peripherals[0].registers_clusters[1].write_constraint, SVDWriteConstraint)
        assert (
            device.peripherals[0].registers_clusters[1].write_constraint.parent
            == device.peripherals[0].registers_clusters[1]
        )

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("clear", ReadActionType.CLEAR),
            ("set", ReadActionType.SET),
            ("modify", ReadActionType.MODIFY),
            ("modifyExternal", ReadActionType.MODIFY_EXTERNAL),
            pytest.param(None, None),
        ],
    )
    def test_read_action(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/readAction", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].read_action == expected

    def test_fields(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert isinstance(device.peripherals[0], SVDPeripheral)
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1].fields[0], SVDField)
        assert (
            device.peripherals[0].registers_clusters[1].fields[0].parent == device.peripherals[0].registers_clusters[1]
        )


class TestWriteConstraintParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_write_as_read(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/writeConstraint/writeAsRead", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].write_constraint is not None
        assert device.peripherals[0].registers_clusters[1].write_constraint.write_as_read == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("true", True),
            ("1", True),
            ("false", False),
            ("0", False),
            pytest.param(None, None),
        ],
    )
    def test_use_enumerated_values(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/writeConstraint/useEnumeratedValues", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].write_constraint is not None
        assert device.peripherals[0].registers_clusters[1].write_constraint.use_enumerated_values == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("", (2, 4)),
            pytest.param(None, None),
        ],
    )
    def test_range(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/writeConstraint/range", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert device.peripherals[0].registers_clusters[1].write_constraint is not None
        assert device.peripherals[0].registers_clusters[1].write_constraint.range_ == expected


class TestFieldParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("teststr", "teststr"),
            pytest.param(None, None),
        ],
    )
    def test_derived_from(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification(
            "/device/peripherals/peripheral/registers/register/fields/field", "derivedFrom", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].derived_from == expected

    @pytest.mark.parametrize("test_input,expected", [("4", 4), ("0x4", 4), pytest.param(None, None)])
    def test_dim(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/dim", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].dim == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_dim_increment(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/dimIncrement", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].dim_increment == expected

    @pytest.mark.parametrize("test_input,expected", [("0,1,2,3", "0,1,2,3"), pytest.param(None, None)])
    def test_dim_index(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/dimIndex", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].dim_index == expected

    @pytest.mark.parametrize("test_input,expected", [("Test", "Test"), pytest.param(None, None)])
    def test_dim_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/dimName", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].dim_name == expected

    def test_dim_array_index(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1].fields[0], SVDField)
        assert device.peripherals[0].registers_clusters[1].fields[0].dim_array_index is not None
        assert (
            device.peripherals[0].registers_clusters[1].fields[0].dim_array_index.parent
            == device.peripherals[0].registers_clusters[1].fields[0]
        )

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("Field%s", "Field%s"),
            pytest.param(None, None, marks=pytest.mark.xfail(strict=True, raises=ParserException)),
        ],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/name", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("This is a field", "This is a field"), pytest.param(None, None)],
    )
    def test_description(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/description", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].description == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_bit_offset(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/bitOffset", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].bit_offset == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_bit_width(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/bitWidth", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].bit_width == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_lsb(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/lsb", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].lsb == expected

    @pytest.mark.parametrize("test_input,expected", [("100", 100), ("0x64", 100), pytest.param(None, None)])
    def test_msb(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/msb", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].msb == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("[7:0]", "[7:0]"), pytest.param(None, None)],
    )
    def test_bit_range(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/bitRange", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].bit_range == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("read-only", AccessType.READ_ONLY),
            ("write-only", AccessType.WRITE_ONLY),
            ("read-write", AccessType.READ_WRITE),
            ("writeOnce", AccessType.WRITE_ONCE),
            ("read-writeOnce", AccessType.READ_WRITE_ONCE),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/access", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].access == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("oneToClear", ModifiedWriteValuesType.ONE_TO_CLEAR),
            ("oneToSet", ModifiedWriteValuesType.ONE_TO_SET),
            ("oneToToggle", ModifiedWriteValuesType.ONE_TO_TOGGLE),
            ("zeroToClear", ModifiedWriteValuesType.ZERO_TO_CLEAR),
            ("zeroToSet", ModifiedWriteValuesType.ZERO_TO_SET),
            ("zeroToToggle", ModifiedWriteValuesType.ZERO_TO_TOGGLE),
            ("clear", ModifiedWriteValuesType.CLEAR),
            ("set", ModifiedWriteValuesType.SET),
            ("modify", ModifiedWriteValuesType.MODIFY),
            pytest.param(None, None),
        ],
    )
    def test_modified_write_values(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/modifiedWriteValues", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].modified_write_values == expected

    def test_write_constraint(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1].fields[0].write_constraint, SVDWriteConstraint)
        assert (
            device.peripherals[0].registers_clusters[1].fields[0].write_constraint.parent
            == device.peripherals[0].registers_clusters[1].fields[0]
        )

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("clear", ReadActionType.CLEAR),
            ("set", ReadActionType.SET),
            ("modify", ReadActionType.MODIFY),
            ("modifyExternal", ReadActionType.MODIFY_EXTERNAL),
            pytest.param(None, None),
        ],
    )
    def test_read_action(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/readAction", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].read_action == expected

    def test_enumerated_value_container(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) == 2
        assert isinstance(
            device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0],
            SVDEnumeratedValueContainer,
        )
        assert (
            device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0].parent
            == device.peripherals[0].registers_clusters[1].fields[0]
        )


class TestEnumeratedValueContainerParsing:
    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("teststr", "teststr"),
            pytest.param(None, None),
        ],
    )
    def test_derived_from(
        self,
        get_device_with_attribute_modification: Callable[[str, None | str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_attribute_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/enumeratedValues",
            "derivedFrom",
            test_input,
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) > 0
        assert (
            device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0].derived_from
            == expected
        )

    @pytest.mark.parametrize(
        "test_input,expected",
        [("TimerIntSelect", "TimerIntSelect"), pytest.param(None, None)],
    )
    def test_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/enumeratedValues/name", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0].name == expected

    @pytest.mark.parametrize(
        "test_input,expected",
        [("HeaderName", "HeaderName"), pytest.param(None, None)],
    )
    def test_header_enum_name(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/enumeratedValues/headerEnumName", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) > 0
        assert (
            device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0].header_enum_name
            == expected
        )

    @pytest.mark.parametrize(
        "test_input,expected",
        [
            ("read", EnumUsageType.READ),
            ("write", EnumUsageType.WRITE),
            ("read-write", EnumUsageType.READ_WRITE),
            pytest.param(None, None),
        ],
    )
    def test_usage(
        self,
        get_device_with_element_modification: Callable[[str, None | str], SVDDevice],
        test_input: None | str,
        expected: Any,
    ):
        device = get_device_with_element_modification(
            "/device/peripherals/peripheral/registers/register/fields/field/enumeratedValues/usage", test_input
        )

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) > 0
        assert device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0].usage == expected

    def test_enumerated_values(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) > 0
        assert (
            len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0].enumerated_values)
            == 3
        )
        assert isinstance(
            device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0].enumerated_values[0],
            SVDEnumeratedValue,
        )

    def test_enumerated_values_parent(self, get_device: Callable[[], SVDDevice]):
        device = get_device()

        assert len(device.peripherals) > 0
        assert len(device.peripherals[0].registers_clusters) > 0
        assert isinstance(device.peripherals[0].registers_clusters[1], SVDRegister)
        assert len(device.peripherals[0].registers_clusters[1].fields) > 0
        assert len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers) > 1
        assert (
            len(device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0].enumerated_values)
            == 3
        )

        enumerated_values0 = device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[0]
        enumerated_values1 = device.peripherals[0].registers_clusters[1].fields[0].enumerated_value_containers[1]

        assert enumerated_values0.enumerated_values[0].parent == enumerated_values0
        assert enumerated_values0.enumerated_values[1].parent == enumerated_values0
        assert enumerated_values0.enumerated_values[2].parent == enumerated_values0
        assert enumerated_values1.enumerated_values[0].parent == enumerated_values1
