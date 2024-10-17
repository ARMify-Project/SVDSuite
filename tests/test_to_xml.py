from typing import Callable, Any
import lxml.etree
import pytest

from svdsuite.model.parse import (
    SVDAddressBlock,
    SVDCluster,
    SVDCPU,
    SVDDevice,
    SVDDimArrayIndex,
    SVDEnumeratedValueContainer,
    SVDEnumeratedValue,
    SVDField,
    SVDInterrupt,
    SVDPeripheral,
    SVDRegister,
    SVDSauRegion,
    SVDSauRegionsConfig,
    SVDWriteConstraint,
)

from svdsuite.model.types import (
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

from svdsuite.serialize import (
    SVDDeviceSerializer,
    SVDPeripheralSerializer,
    SVDCPUSerializer,
    SVDSauRegionsConfigSerializer,
    SVDSauRegionSerializer,
    SVDAddressBlockSerializer,
    SVDInterruptSerializer,
    SVDWriteConstraintSerializer,
    SVDEnumeratedValueContainerSerializer,
    SVDFieldSerializer,
    SVDRegisterSerializer,
    SVDClusterSerializer,
    SVDEnumeratedValueSerializer,
    SVDDimArrayIndexSerializer,
)

SVDObject = (
    SVDSauRegion
    | SVDSauRegionsConfig
    | SVDCPU
    | SVDEnumeratedValue
    | SVDDimArrayIndex
    | SVDAddressBlock
    | SVDInterrupt
    | SVDWriteConstraint
    | SVDEnumeratedValueContainer
    | SVDField
    | SVDRegister
    | SVDCluster
    | SVDPeripheral
    | SVDDevice
)


@pytest.fixture(name="svd_obj_to_xml_str", scope="session")
def fixture_svd_obj_to_xml_str() -> Callable[[SVDObject], str]:
    def _(svd_obj: SVDObject) -> str:
        if isinstance(svd_obj, SVDDevice):
            serializer = SVDDeviceSerializer(svd_obj)
        elif isinstance(svd_obj, SVDPeripheral):
            serializer = SVDPeripheralSerializer(svd_obj)
        elif isinstance(svd_obj, SVDCPU):
            serializer = SVDCPUSerializer(svd_obj)
        elif isinstance(svd_obj, SVDSauRegionsConfig):
            serializer = SVDSauRegionsConfigSerializer(svd_obj)
        elif isinstance(svd_obj, SVDSauRegion):
            serializer = SVDSauRegionSerializer(svd_obj)
        elif isinstance(svd_obj, SVDAddressBlock):
            serializer = SVDAddressBlockSerializer(svd_obj)
        elif isinstance(svd_obj, SVDInterrupt):
            serializer = SVDInterruptSerializer(svd_obj)
        elif isinstance(svd_obj, SVDWriteConstraint):
            serializer = SVDWriteConstraintSerializer(svd_obj)
        elif isinstance(svd_obj, SVDEnumeratedValueContainer):
            serializer = SVDEnumeratedValueContainerSerializer(svd_obj)
        elif isinstance(svd_obj, SVDField):
            serializer = SVDFieldSerializer(svd_obj)
        elif isinstance(svd_obj, SVDRegister):
            serializer = SVDRegisterSerializer(svd_obj)
        elif isinstance(svd_obj, SVDCluster):
            serializer = SVDClusterSerializer(svd_obj)
        elif isinstance(svd_obj, SVDEnumeratedValue):
            serializer = SVDEnumeratedValueSerializer(svd_obj)
        elif isinstance(svd_obj, SVDDimArrayIndex):  # pyright: ignore[reportUnnecessaryIsInstance]
            serializer = SVDDimArrayIndexSerializer(svd_obj)
        else:
            raise TypeError("Unsupported SVDObject type")

        return lxml.etree.tostring(serializer.to_xml(), pretty_print=False).decode()

    return _


@pytest.fixture(name="create_attrib", scope="session")
def fixture_create_attrib() -> Callable[[str, Any], str]:
    def _(key: str, value: Any) -> str:
        if value is None:
            return ""
        return f'{key}="{value}"'

    return _


@pytest.fixture(name="create_element", scope="session")
def fixture_create_element() -> Callable[[str, Any], str]:
    def _(key: str, value: Any) -> str:
        if value is None:
            return ""
        return f"<{key}>{value}</{key}>"

    return _


@pytest.fixture(name="dedent_xml", scope="session")
def fixture_dedent_xml() -> Callable[[str], str]:
    def _(expected_xml: str) -> str:
        return "".join([m.lstrip().replace("  ", " ").replace(" >", ">") for m in expected_xml.split("\n")])

    return _


@pytest.fixture(name="create_sau_region", scope="function")
def fixture_create_sau_region():
    def _(
        enabled: None | bool = True,
        name: None | str = "Region1",
        base: int = 0x1000,
        limit: int = 0x2000,
        access: SauAccessType = SauAccessType.NON_SECURE,
    ) -> SVDSauRegion:
        return SVDSauRegion(
            enabled=enabled,
            name=name,
            base=base,
            limit=limit,
            access=access,
        )

    return _


@pytest.fixture(name="create_sau_regions_config", scope="function")
def fixture_create_sau_regions_config():
    def _(
        enabled: None | bool = True,
        protection_when_disabled: None | ProtectionStringType = ProtectionStringType.SECURE,
        regions: None | list[SVDSauRegion] = None,
    ) -> SVDSauRegionsConfig:
        return SVDSauRegionsConfig(
            enabled=enabled,
            protection_when_disabled=protection_when_disabled,
            regions=[] if regions is None else regions,
        )

    return _


@pytest.fixture(name="create_cpu", scope="function")
def fixture_create_cpu():
    def _(
        name: CPUNameType = CPUNameType.CM0,
        revision: str = "r0p0",
        endian: EndianType = EndianType.LITTLE,
        mpu_present: None | bool = False,
        fpu_present: None | bool = False,
        fpu_dp: None | bool = False,
        dsp_present: None | bool = False,
        icache_present: None | bool = False,
        dcache_present: None | bool = False,
        itcm_present: None | bool = False,
        dtcm_present: None | bool = False,
        vtor_present: None | bool = False,
        nvic_prio_bits: int = 2,
        vendor_systick_config: bool = False,
        device_num_interrupts: None | int = 6,
        sau_num_regions: None | int = 2,
        sau_regions_config: None | SVDSauRegionsConfig = None,
    ) -> SVDCPU:
        return SVDCPU(
            name=name,
            revision=revision,
            endian=endian,
            mpu_present=mpu_present,
            fpu_present=fpu_present,
            fpu_dp=fpu_dp,
            dsp_present=dsp_present,
            icache_present=icache_present,
            dcache_present=dcache_present,
            itcm_present=itcm_present,
            dtcm_present=dtcm_present,
            vtor_present=vtor_present,
            nvic_prio_bits=nvic_prio_bits,
            vendor_systick_config=vendor_systick_config,
            device_num_interrupts=device_num_interrupts,
            sau_num_regions=sau_num_regions,
            sau_regions_config=sau_regions_config,
        )

    return _


@pytest.fixture(name="create_enumerated_value", scope="function")
def fixture_create_enumerated_value():
    def _(
        name: str = "enabled",
        description: None | str = "The clock source clk1 is running.",
        value: None | str = "0b1111",
        is_default: None | bool = None,
    ) -> SVDEnumeratedValue:
        return SVDEnumeratedValue(
            name=name,
            description=description,
            value=value,
            is_default=is_default,
        )

    return _


@pytest.fixture(name="create_dim_array_index", scope="function")
def fixture_create_dim_array_index():
    def _(
        header_enum_name: None | str = "FSMC_EnumArray",
        enumerated_values: None | list[SVDEnumeratedValue] = None,
    ) -> SVDDimArrayIndex:
        return SVDDimArrayIndex(
            header_enum_name=header_enum_name,
            enumerated_values=[] if enumerated_values is None else enumerated_values,
        )

    return _


@pytest.fixture(name="create_address_block", scope="function")
def fixture_create_address_block():
    def _(
        offset: int = 0x4000,
        size: int = 0x1000,
        usage: EnumeratedTokenType = EnumeratedTokenType.REGISTERS,
        protection: None | ProtectionStringType = ProtectionStringType.SECURE,
    ) -> SVDAddressBlock:
        return SVDAddressBlock(
            offset=offset,
            size=size,
            usage=usage,
            protection=protection,
        )

    return _


@pytest.fixture(name="create_interrupt", scope="function")
def fixture_create_interrupt():
    def _(
        name: str = "UART0",
        description: None | str = "UART0 Interrupt",
        value: int = 0,
    ) -> SVDInterrupt:
        return SVDInterrupt(
            name=name,
            description=description,
            value=value,
        )

    return _


@pytest.fixture(name="create_write_constraint", scope="function")
def fixture_create_write_constraint():
    def _(
        write_as_read: None | bool = None,
        use_enumerated_values: None | bool = None,
        range_: None | tuple[int, int] = None,
    ) -> SVDWriteConstraint:
        return SVDWriteConstraint(
            write_as_read=write_as_read,
            use_enumerated_values=use_enumerated_values,
            range_=range_,
        )

    return _


@pytest.fixture(name="create_enumerated_value_container", scope="function")
def fixture_create_enumerated_value_container():
    def _(
        name: None | str = "TimerIntSelect",
        header_enum_name: None | str = "TimerIntSelect_Enum",
        usage: None | EnumUsageType = EnumUsageType.READ,
        enumerated_values: None | list[SVDEnumeratedValue] = None,
        derived_from: None | str = "der.from",
    ) -> SVDEnumeratedValueContainer:
        return SVDEnumeratedValueContainer(
            name=name,
            header_enum_name=header_enum_name,
            usage=usage,
            enumerated_values=[] if enumerated_values is None else enumerated_values,
            derived_from=derived_from,
        )

    return _


@pytest.fixture(name="create_field", scope="function")
def fixture_create_field():
    def _(
        derived_from: None | str = "der.from",
        dim: None | int = None,
        dim_increment: None | int = None,
        dim_index: None | str = None,
        dim_name: None | str = None,
        dim_array_index: None | SVDDimArrayIndex = None,
        name: str = "TimerCtrl0_IntSel",
        description: None | str = "Select interrupt line that is triggered by timer overflow.",
        bit_offset: None | int = 1,
        bit_width: None | int = 3,
        lsb: None | int = None,
        msb: None | int = None,
        bit_range: None | str = None,
        access: None | AccessType = AccessType.READ_WRITE,
        modified_write_values: None | ModifiedWriteValuesType = ModifiedWriteValuesType.ONE_TO_SET,
        write_constraint: None | SVDWriteConstraint = None,
        read_action: None | ReadActionType = ReadActionType.CLEAR,
        enumerated_value_containers: None | list[SVDEnumeratedValueContainer] = None,
    ) -> SVDField:
        return SVDField(
            derived_from=derived_from,
            dim=dim,
            dim_increment=dim_increment,
            dim_index=dim_index,
            dim_name=dim_name,
            dim_array_index=dim_array_index,
            name=name,
            description=description,
            bit_offset=bit_offset,
            bit_width=bit_width,
            lsb=lsb,
            msb=msb,
            bit_range=bit_range,
            access=access,
            modified_write_values=modified_write_values,
            write_constraint=write_constraint,
            read_action=read_action,
            enumerated_value_containers=[] if enumerated_value_containers is None else enumerated_value_containers,
        )

    return _


@pytest.fixture(name="create_register", scope="function")
def fixture_create_register():
    def _(
        derived_from: None | str = "der.from",
        dim: None | int = None,
        dim_increment: None | int = None,
        dim_index: None | str = None,
        dim_name: None | str = None,
        dim_array_index: None | SVDDimArrayIndex = None,
        name: str = "TimerCtrl0",
        display_name: None | str = "Timer Control 0",
        description: None | str = "Timer Control Register 0",
        alternate_group: None | str = "alt_group",
        alternate_register: None | str = "alt_reg",
        address_offset: int = 0x0,
        size: None | int = None,
        access: None | AccessType = None,
        protection: None | ProtectionStringType = None,
        reset_value: None | int = None,
        reset_mask: None | int = None,
        data_type: None | DataTypeType = DataTypeType.UINT8_T,
        modified_write_values: None | ModifiedWriteValuesType = ModifiedWriteValuesType.ONE_TO_SET,
        write_constraint: None | SVDWriteConstraint = None,
        read_action: None | ReadActionType = ReadActionType.CLEAR,
        fields: None | list[SVDField] = None,
    ) -> SVDRegister:
        return SVDRegister(
            derived_from=derived_from,
            dim=dim,
            dim_increment=dim_increment,
            dim_index=dim_index,
            dim_name=dim_name,
            dim_array_index=dim_array_index,
            name=name,
            display_name=display_name,
            description=description,
            alternate_group=alternate_group,
            alternate_register=alternate_register,
            address_offset=address_offset,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            data_type=data_type,
            modified_write_values=modified_write_values,
            write_constraint=write_constraint,
            read_action=read_action,
            fields=[] if fields is None else fields,
        )

    return _


@pytest.fixture(name="create_cluster", scope="function")
def fixture_create_cluster():
    def _(
        derived_from: None | str = "der.from",
        dim: None | int = None,
        dim_increment: None | int = None,
        dim_index: None | str = None,
        dim_name: None | str = None,
        dim_array_index: None | SVDDimArrayIndex = None,
        name: str = "TimerCtrl0",
        description: None | str = "Timer Control Register 0",
        alternate_cluster: None | str = "alt_cluster",
        header_struct_name: None | str = "headername",
        address_offset: int = 0x0,
        size: None | int = None,
        access: None | AccessType = None,
        protection: None | ProtectionStringType = None,
        reset_value: None | int = None,
        reset_mask: None | int = None,
        registers_clusters: None | list[SVDRegister | SVDCluster] = None,
    ) -> SVDCluster:
        return SVDCluster(
            derived_from=derived_from,
            dim=dim,
            dim_increment=dim_increment,
            dim_index=dim_index,
            dim_name=dim_name,
            dim_array_index=dim_array_index,
            name=name,
            description=description,
            alternate_cluster=alternate_cluster,
            header_struct_name=header_struct_name,
            address_offset=address_offset,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            registers_clusters=[] if registers_clusters is None else registers_clusters,
        )

    return _


@pytest.fixture(name="create_peripheral", scope="function")
def fixture_create_peripheral():
    def _(
        derived_from: None | str = "der.from",
        dim: None | int = None,
        dim_increment: None | int = None,
        dim_index: None | str = None,
        dim_name: None | str = None,
        dim_array_index: None | SVDDimArrayIndex = None,
        name: str = "Timer1",
        version: None | str = "1.0",
        description: None | str = "Timer 1 is a standard timer",
        alternate_peripheral: None | str = "Timer1_Alt",
        group_name: None | str = "group_name",
        prepend_to_name: None | str = "prepend",
        append_to_name: None | str = "append",
        header_struct_name: None | str = "headerstruct",
        disable_condition: None | str = "discond",
        base_address: int = 0x40002000,
        size: None | int = None,
        access: None | AccessType = None,
        protection: None | ProtectionStringType = None,
        reset_value: None | int = None,
        reset_mask: None | int = None,
        address_blocks: None | list[SVDAddressBlock] = None,
        interrupts: None | list[SVDInterrupt] = None,
        registers_clusters: None | list[SVDRegister | SVDCluster] = None,
    ):
        return SVDPeripheral(
            derived_from=derived_from,
            dim=dim,
            dim_increment=dim_increment,
            dim_index=dim_index,
            dim_name=dim_name,
            dim_array_index=dim_array_index,
            name=name,
            version=version,
            description=description,
            alternate_peripheral=alternate_peripheral,
            group_name=group_name,
            prepend_to_name=prepend_to_name,
            append_to_name=append_to_name,
            header_struct_name=header_struct_name,
            disable_condition=disable_condition,
            base_address=base_address,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            address_blocks=[] if address_blocks is None else address_blocks,
            interrupts=[] if interrupts is None else interrupts,
            registers_clusters=[] if registers_clusters is None else registers_clusters,
        )

    return _


@pytest.fixture(name="create_device", scope="function")
def fixture_create_device():
    def _(
        xs_no_namespace_schema_location: str = "CMSIS-SVD.xsd",
        schema_version: str = "1.0",
        vendor: None | str = "STMicroelectronics",
        vendor_id: None | str = "ST",
        name: str = "STM32F0",
        series: None | str = "STM32F0",
        version: str = "1.0",
        description: str = "STM32F0 device",
        license_text: None | str = "license",
        cpu: None | SVDCPU = None,
        header_system_filename: None | str = "stm32f0.h",
        header_definitions_prefix: None | str = "TestPrefix",
        address_unit_bits: int = 8,
        width: int = 32,
        size: None | int = None,
        access: None | AccessType = None,
        protection: None | ProtectionStringType = None,
        reset_value: None | int = None,
        reset_mask: None | int = None,
        peripherals: None | list[SVDPeripheral] = None,
    ):
        return SVDDevice(
            xs_no_namespace_schema_location=xs_no_namespace_schema_location,
            schema_version=schema_version,
            vendor=vendor,
            vendor_id=vendor_id,
            name=name,
            series=series,
            version=version,
            description=description,
            license_text=license_text,
            cpu=cpu,
            header_system_filename=header_system_filename,
            header_definitions_prefix=header_definitions_prefix,
            address_unit_bits=address_unit_bits,
            width=width,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            peripherals=[] if peripherals is None else peripherals,
        )

    return _


class TestSVDSauRegion:
    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_enabled(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        test_input: None | bool,
        expected: Any,
    ):
        region = create_sau_region(enabled=test_input)

        expected_xml = f"""\
        <region {create_attrib("enabled", expected)} name="Region1">
            <base>0x1000</base>
            <limit>0x2000</limit>
            <access>n</access>
        </region>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(region)

    @pytest.mark.parametrize("test_input, expected", [("Region1", "Region1"), pytest.param(None, None)])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        test_input: Any,
        expected: Any,
    ):
        region = create_sau_region(name=test_input)

        expected_xml = f"""\
        <region enabled="true" {create_attrib("name", expected)}>
            <base>0x1000</base>
            <limit>0x2000</limit>
            <access>n</access>
        </region>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(region)

    @pytest.mark.parametrize("test_input, expected", [(0x1000, "0x1000")])
    def test_base(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        test_input: Any,
        expected: Any,
    ):
        region = create_sau_region(base=test_input)

        expected_xml = f"""\
        <region enabled="true" name="Region1">
            {create_element("base", expected)}
            <limit>0x2000</limit>
            <access>n</access>
        </region>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(region)

    @pytest.mark.parametrize("test_input, expected", [(0x1000, "0x1000")])
    def test_limit(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        test_input: Any,
        expected: Any,
    ):
        region = create_sau_region(limit=test_input)

        expected_xml = f"""\
        <region enabled="true" name="Region1">
            <base>0x1000</base>
            {create_element("limit", expected)}
            <access>n</access>
        </region>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(region)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (SauAccessType.NON_SECURE_CALLABLE, "c"),
            (SauAccessType.NON_SECURE, "n"),
        ],
    )
    def test_access(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        test_input: Any,
        expected: Any,
    ):
        region = create_sau_region(access=test_input)

        expected_xml = f"""\
        <region enabled="true" name="Region1">
            <base>0x1000</base>
            <limit>0x2000</limit>
            {create_element("access", expected)}
        </region>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(region)


class TestSVDSauRegionsConfig:
    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_enabled(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        test_input: Any,
        expected: Any,
    ):
        config = create_sau_regions_config(enabled=test_input, regions=[create_sau_region()])

        expected_xml = f"""\
        <sauRegionsConfig {create_attrib("enabled", expected)} protectionWhenDisabled="s">
            <region enabled="true" name="Region1">
                <base>0x1000</base>
                <limit>0x2000</limit>
                <access>n</access>
            </region>
        </sauRegionsConfig>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(config)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, "s"),
            (ProtectionStringType.NON_SECURE, "n"),
            (ProtectionStringType.PRIVILEGED, "p"),
            pytest.param(None, None),
        ],
    )
    def test_protection_when_disabled(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        test_input: Any,
        expected: Any,
    ):
        config = create_sau_regions_config(protection_when_disabled=test_input, regions=[create_sau_region()])

        expected_xml = f"""\
        <sauRegionsConfig enabled="true" {create_attrib("protectionWhenDisabled", expected)}>
            <region enabled="true" name="Region1">
                <base>0x1000</base>
                <limit>0x2000</limit>
                <access>n</access>
            </region>
        </sauRegionsConfig>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(config)

    def test_with_empty_region(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
    ):
        config = create_sau_regions_config(regions=None)

        expected_xml = '<sauRegionsConfig enabled="true" protectionWhenDisabled="s"></sauRegionsConfig>'

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(config)

    def test_with_empty_region_and_nothing_else(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
    ):
        config = create_sau_regions_config(enabled=None, protection_when_disabled=None, regions=None)

        expected_xml = "<sauRegionsConfig></sauRegionsConfig>"

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(config)


class TestSVDCPU:
    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (CPUNameType.CM0, "CM0"),
            (CPUNameType.CM0PLUS, "CM0PLUS"),
            (CPUNameType.CM0_PLUS, "CM0+"),
            (CPUNameType.CM1, "CM1"),
            (CPUNameType.CM3, "CM3"),
            (CPUNameType.CM4, "CM4"),
            (CPUNameType.CM7, "CM7"),
            (CPUNameType.CM23, "CM23"),
            (CPUNameType.CM33, "CM33"),
            (CPUNameType.CM35P, "CM35P"),
            (CPUNameType.CM52, "CM52"),
            (CPUNameType.CM55, "CM55"),
            (CPUNameType.CM85, "CM85"),
            (CPUNameType.SC000, "SC000"),
            (CPUNameType.SC300, "SC300"),
            (CPUNameType.ARMV8MML, "ARMV8MML"),
            (CPUNameType.ARMV8MBL, "ARMV8MBL"),
            (CPUNameType.ARMV81MML, "ARMV81MML"),
            (CPUNameType.CA5, "CA5"),
            (CPUNameType.CA7, "CA7"),
            (CPUNameType.CA8, "CA8"),
            (CPUNameType.CA9, "CA9"),
            (CPUNameType.CA15, "CA15"),
            (CPUNameType.CA17, "CA17"),
            (CPUNameType.CA53, "CA53"),
            (CPUNameType.CA57, "CA57"),
            (CPUNameType.CA72, "CA72"),
            (CPUNameType.SMC1, "SMC1"),
            (CPUNameType.OTHER, "other"),
        ],
    )
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(name=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()]))

        expected_xml = f"""\
        <cpu>
            {create_element("name", expected)}
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [("revtest", "revtest")])
    def test_revision(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            revision=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            {create_element("revision", expected)}
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (EndianType.LITTLE, "little"),
            (EndianType.BIG, "big"),
            (EndianType.SELECTABLE, "selectable"),
            (EndianType.OTHER, "other"),
        ],
    )
    def test_endian(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(endian=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()]))

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            {create_element("endian", expected)}
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_mpu_present(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            mpu_present=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            {create_element("mpuPresent", expected)}
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_fpu_present(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            fpu_present=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            {create_element("fpuPresent", expected)}
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_fpu_dp(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(fpu_dp=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()]))

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            {create_element("fpuDP", expected)}
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_dsp_present(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            dsp_present=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            {create_element("dspPresent", expected)}
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_icache_present(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            icache_present=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            {create_element("icachePresent", expected)}
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_dcache_present(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            dcache_present=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            {create_element("dcachePresent", expected)}
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_itcm_present(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            itcm_present=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            {create_element("itcmPresent", expected)}
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_dtcm_present(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            dtcm_present=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            {create_element("dtcmPresent", expected)}
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_vtor_present(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            vtor_present=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            {create_element("vtorPresent", expected)}
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(6, "6")])
    def test_nvic_prio_bits(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            nvic_prio_bits=test_input,
            sau_regions_config=create_sau_regions_config(regions=[create_sau_region()]),
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            {create_element("nvicPrioBits", expected)}
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false")])
    def test_vendor_systick_config(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            vendor_systick_config=test_input,
            sau_regions_config=create_sau_regions_config(regions=[create_sau_region()]),
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            {create_element("vendorSystickConfig", expected)}
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_device_num_interrupts(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            device_num_interrupts=test_input,
            sau_regions_config=create_sau_regions_config(regions=[create_sau_region()]),
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            {create_element("deviceNumInterrupts", expected)}
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_sau_num_regions(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        test_input: Any,
        expected: Any,
    ):
        cpu = create_cpu(
            sau_num_regions=test_input, sau_regions_config=create_sau_regions_config(regions=[create_sau_region()])
        )

        expected_xml = f"""\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            {create_element("sauNumRegions", expected)}
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)

    def test_without_sau_regions_config(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_cpu: Callable[..., SVDCPU],
    ):
        cpu = create_cpu(sau_regions_config=None)

        expected_xml = """\
        <cpu>
            <name>CM0</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
        </cpu>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cpu)


class TestSVDEnumeratedValue:
    @pytest.mark.parametrize("test_input, expected", [("testname", "testname")])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        enumerated_value = create_enumerated_value(name=test_input)

        expected_xml = f"""\
        <enumeratedValue>
            {create_element("name", expected)}
            <description>The clock source clk1 is running.</description>
            <value>0b1111</value>
        </enumeratedValue>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), pytest.param(None, None)])
    def test_description(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        enumerated_value = create_enumerated_value(description=test_input, value=None, is_default=True)

        expected_xml = f"""\
        <enumeratedValue>
            <name>enabled</name>
            {create_element("description", expected)}
            <isDefault>true</isDefault>
        </enumeratedValue>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)

    @pytest.mark.parametrize(
        "test_input, expected", [("1", "1"), ("0b1111", "0b1111"), ("0b111x", "0b111x"), pytest.param(None, None)]
    )
    def test_value(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        enumerated_value = create_enumerated_value(value=test_input)

        expected_xml = f"""\
        <enumeratedValue>
            <name>enabled</name>
            <description>The clock source clk1 is running.</description>
            {create_element("value", expected)}
        </enumeratedValue>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_is_default(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        enumerated_value = create_enumerated_value(is_default=test_input, value=None)

        expected_xml = f"""\
        <enumeratedValue>
            <name>enabled</name>
            <description>The clock source clk1 is running.</description>
            {create_element("isDefault", expected)}
        </enumeratedValue>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)


class TestSVDDimArrayIndex:
    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_header_enum_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        dim_array_index = create_dim_array_index(
            header_enum_name=test_input,
            enumerated_values=[
                create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0"),
                create_enumerated_value(name="TIMER0", description="TIMER0 Peripheral", value="1"),
            ],
        )

        expected_xml = f"""\
        <dimArrayIndex>
            {create_element("headerEnumName", expected)}
            <enumeratedValue>
                <name>UART0</name>
                <description>UART0 Peripheral</description>
                <value>0</value>
            </enumeratedValue>
            <enumeratedValue>
                <name>TIMER0</name>
                <description>TIMER0 Peripheral</description>
                <value>1</value>
            </enumeratedValue>
        </dimArrayIndex>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(dim_array_index)

    def test_with_empty_enumerated_values(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
    ):
        dim_array_index = create_dim_array_index()

        expected_xml = """\
        <dimArrayIndex>
            <headerEnumName>FSMC_EnumArray</headerEnumName>
        </dimArrayIndex>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(dim_array_index)

    def test_with_empty_enumerated_values_and_nothing_else(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
    ):
        dim_array_index = create_dim_array_index(header_enum_name=None)

        expected_xml = "<dimArrayIndex></dimArrayIndex>"

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(dim_array_index)


class TestSVDAddressBlock:
    @pytest.mark.parametrize("test_input, expected", [(0x1000, "0x1000")])
    def test_offset(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_address_block: Callable[..., SVDAddressBlock],
        test_input: Any,
        expected: Any,
    ):
        address_block = create_address_block(offset=test_input)

        expected_xml = f"""\
        <addressBlock>
            {create_element("offset", expected)}
            <size>0x1000</size>
            <usage>registers</usage>
            <protection>s</protection>
        </addressBlock>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(address_block)

    @pytest.mark.parametrize("test_input, expected", [(4096, "0x1000")])
    def test_size(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_address_block: Callable[..., SVDAddressBlock],
        test_input: Any,
        expected: Any,
    ):
        address_block = create_address_block(size=test_input)

        expected_xml = f"""\
        <addressBlock>
            <offset>0x4000</offset>
            {create_element("size", expected)}
            <usage>registers</usage>
            <protection>s</protection>
        </addressBlock>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(address_block)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (EnumeratedTokenType.REGISTERS, "registers"),
            (EnumeratedTokenType.BUFFER, "buffer"),
            (EnumeratedTokenType.RESERVED, "reserved"),
        ],
    )
    def test_usage(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_address_block: Callable[..., SVDAddressBlock],
        test_input: Any,
        expected: Any,
    ):
        address_block = create_address_block(usage=test_input)

        expected_xml = f"""\
        <addressBlock>
            <offset>0x4000</offset>
            <size>0x1000</size>
            {create_element("usage", expected)}
            <protection>s</protection>
        </addressBlock>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(address_block)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, "s"),
            (ProtectionStringType.NON_SECURE, "n"),
            (ProtectionStringType.PRIVILEGED, "p"),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_address_block: Callable[..., SVDAddressBlock],
        test_input: Any,
        expected: Any,
    ):
        address_block = create_address_block(protection=test_input)

        expected_xml = f"""\
        <addressBlock>
            <offset>0x4000</offset>
            <size>0x1000</size>
            <usage>registers</usage>
            {create_element("protection", expected)}
        </addressBlock>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(address_block)


class TestSVDInterrupt:
    @pytest.mark.parametrize("test_input, expected", [("test", "test")])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_interrupt: Callable[..., SVDInterrupt],
        test_input: Any,
        expected: Any,
    ):
        interrupt = create_interrupt(name=test_input)

        expected_xml = f"""\
        <interrupt>
            {create_element("name", expected)}
            <description>UART0 Interrupt</description>
            <value>0</value>
        </interrupt>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(interrupt)

    @pytest.mark.parametrize("test_input, expected", [("testdesc", "testdesc"), pytest.param(None, None)])
    def test_description(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_interrupt: Callable[..., SVDInterrupt],
        test_input: Any,
        expected: Any,
    ):
        interrupt = create_interrupt(description=test_input)

        expected_xml = f"""\
        <interrupt>
            <name>UART0</name>
            {create_element("description", expected)}
            <value>0</value>
        </interrupt>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(interrupt)

    @pytest.mark.parametrize("test_input, expected", [(25, "25")])
    def test_value(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_interrupt: Callable[..., SVDInterrupt],
        test_input: Any,
        expected: Any,
    ):
        interrupt = create_interrupt(value=test_input)

        expected_xml = f"""\
        <interrupt>
            <name>UART0</name>
            <description>UART0 Interrupt</description>
            {create_element("value", expected)}
        </interrupt>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(interrupt)


class TestSVDWriteConstraint:
    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_write_as_read(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        test_input: Any,
        expected: Any,
    ):
        write_constraint = create_write_constraint(write_as_read=test_input)

        expected_xml = f"""\
        <writeConstraint>
            {create_element("writeAsRead", expected)}
        </writeConstraint>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(write_constraint)

    @pytest.mark.parametrize("test_input, expected", [(True, "true"), (False, "false"), pytest.param(None, None)])
    def test_use_enumerated_values(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        test_input: Any,
        expected: Any,
    ):
        write_constraint = create_write_constraint(use_enumerated_values=test_input)

        expected_xml = f"""\
        <writeConstraint>
            {create_element("useEnumeratedValues", expected)}
        </writeConstraint>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(write_constraint)

    @pytest.mark.parametrize("test_input, expected", [((2, 4), ("2", "4"))])
    def test_range_value(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        test_input: Any,
        expected: Any,
    ):
        write_constraint = create_write_constraint(range_=test_input)

        expected_xml = f"""\
        <writeConstraint>
            <range>
                <minimum>{expected[0]}</minimum>
                <maximum>{expected[1]}</maximum>
            </range>
        </writeConstraint>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(write_constraint)

    def test_range_none(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
    ):
        write_constraint = create_write_constraint(range_=None)

        expected_xml = "<writeConstraint></writeConstraint>"

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(write_constraint)


class TestSVDEnumeratedValueContainer:
    @pytest.mark.parametrize("test_input, expected", [("test.name.a", "test.name.a"), pytest.param(None, None)])
    def test_derived_from(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value_container: Callable[..., SVDEnumeratedValueContainer],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        enumerated_value = create_enumerated_value_container(
            derived_from=test_input,
            enumerated_values=[
                create_enumerated_value(name="disabled", description="The clock source is turned off", value="0"),
                create_enumerated_value(name="enabled", description="The clock source is running", value="1"),
            ],
        )

        expected_xml = f"""\
        <enumeratedValues {create_attrib("derivedFrom", expected)}>
            <name>TimerIntSelect</name>
            <headerEnumName>TimerIntSelect_Enum</headerEnumName>
            <usage>read</usage>
            <enumeratedValue>
                <name>disabled</name>
                <description>The clock source is turned off</description>
                <value>0</value>
            </enumeratedValue>
            <enumeratedValue>
                <name>enabled</name>
                <description>The clock source is running</description>
                <value>1</value>
            </enumeratedValue>
        </enumeratedValues>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value_container: Callable[..., SVDEnumeratedValueContainer],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        enumerated_value = create_enumerated_value_container(
            name=test_input,
            enumerated_values=[
                create_enumerated_value(name="disabled", description="The clock source is turned off", value="0"),
                create_enumerated_value(name="enabled", description="The clock source is running", value="1"),
            ],
        )

        expected_xml = f"""\
        <enumeratedValues derivedFrom="der.from">
            {create_element("name", expected)}
            <headerEnumName>TimerIntSelect_Enum</headerEnumName>
            <usage>read</usage>
            <enumeratedValue>
                <name>disabled</name>
                <description>The clock source is turned off</description>
                <value>0</value>
            </enumeratedValue>
            <enumeratedValue>
                <name>enabled</name>
                <description>The clock source is running</description>
                <value>1</value>
            </enumeratedValue>
        </enumeratedValues>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_header_enum_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value_container: Callable[..., SVDEnumeratedValueContainer],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        enumerated_value = create_enumerated_value_container(
            header_enum_name=test_input,
            enumerated_values=[
                create_enumerated_value(name="disabled", description="The clock source is turned off", value="0"),
                create_enumerated_value(name="enabled", description="The clock source is running", value="1"),
            ],
        )

        expected_xml = f"""\
        <enumeratedValues derivedFrom="der.from">
            <name>TimerIntSelect</name>
            {create_element("headerEnumName", expected)}
            <usage>read</usage>
            <enumeratedValue>
                <name>disabled</name>
                <description>The clock source is turned off</description>
                <value>0</value>
            </enumeratedValue>
            <enumeratedValue>
                <name>enabled</name>
                <description>The clock source is running</description>
                <value>1</value>
            </enumeratedValue>
        </enumeratedValues>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)

    @pytest.mark.parametrize(
        "test_input, expected",
        [(EnumUsageType.READ, "read"), (EnumUsageType.WRITE, "write"), (EnumUsageType.READ_WRITE, "read-write")],
    )
    def test_usage(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value_container: Callable[..., SVDEnumeratedValueContainer],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        test_input: Any,
        expected: Any,
    ):
        enumerated_value = create_enumerated_value_container(
            usage=test_input,
            enumerated_values=[
                create_enumerated_value(name="disabled", description="The clock source is turned off", value="0"),
                create_enumerated_value(name="enabled", description="The clock source is running", value="1"),
            ],
        )

        expected_xml = f"""\
        <enumeratedValues derivedFrom="der.from">
            <name>TimerIntSelect</name>
            <headerEnumName>TimerIntSelect_Enum</headerEnumName>
            {create_element("usage", expected)}
            <enumeratedValue>
                <name>disabled</name>
                <description>The clock source is turned off</description>
                <value>0</value>
            </enumeratedValue>
            <enumeratedValue>
                <name>enabled</name>
                <description>The clock source is running</description>
                <value>1</value>
            </enumeratedValue>
        </enumeratedValues>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)

    def test_with_empty_enumerated_values(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value_container: Callable[..., SVDEnumeratedValueContainer],
    ):
        enumerated_value = create_enumerated_value_container(enumerated_values=None)

        expected_xml = """\
        <enumeratedValues derivedFrom="der.from">
            <name>TimerIntSelect</name>
            <headerEnumName>TimerIntSelect_Enum</headerEnumName>
            <usage>read</usage>
        </enumeratedValues>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)

    def test_with_empty_enumerated_values_and_nothing_else(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value_container: Callable[..., SVDEnumeratedValueContainer],
    ):
        enumerated_value = create_enumerated_value_container(
            derived_from=None, name=None, header_enum_name=None, usage=None, enumerated_values=None
        )

        expected_xml = "<enumeratedValues></enumeratedValues>"

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(enumerated_value)


class TestSVDField:
    @pytest.mark.parametrize("test_input, expected", [("test.name.a", "test.name.a"), pytest.param(None, None)])
    def test_derived_from(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(derived_from=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <field {create_attrib("derivedFrom", expected)}>
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_dim(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(
            dim=test_input,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <field derivedFrom="der.from">
            {create_element("dim", expected)}
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_dim_increment(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(
            dim=6,
            dim_increment=test_input,
            dim_index="A,B,C,D,E,Z",
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <dim>6</dim>
            {create_element("dimIncrement", expected)}
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [("teststr", "teststr"), pytest.param(None, None)])
    def test_dim_index(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(
            dim=6,
            dim_increment=4,
            dim_index=test_input,
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            {create_element("dimIndex", expected)}
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_dim_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(
            dim=6,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name=test_input,
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            {create_element("dimName", expected)}
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    def test_dim_without_array_index(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
    ):
        field = create_field(
            dim=6,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name="testname",
            dim_array_index=None,
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = """\
        <field derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>testname</dimName>
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname")])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(name=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <field derivedFrom="der.from">
            {create_element("name", expected)}
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_description(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(description=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            {create_element("description", expected)}
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [((1, 3), ("1", "3")), pytest.param((None, None), (None, None))])
    def test_bit_range_offset_width_style(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(
            bit_offset=test_input[0], bit_width=test_input[1], write_constraint=create_write_constraint(range_=(0, 1))
        )

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            {create_element("bitOffset", expected[0])}
            {create_element("bitWidth", expected[1])}
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [((1, 3), ("1", "3")), pytest.param((None, None), (None, None))])
    def test_bit_range_lsb_msb_style(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(
            lsb=test_input[0],
            msb=test_input[1],
            bit_offset=None,
            bit_width=None,
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            {create_element("lsb", expected[0])}
            {create_element("msb", expected[1])}
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize("test_input, expected", [("[7:0]", "[7:0]"), pytest.param(None, None)])
    def test_bit_range(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(
            bit_range=test_input,
            bit_offset=None,
            bit_width=None,
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            {create_element("bitRange", expected)}
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, "read-only"),
            (AccessType.WRITE_ONLY, "write-only"),
            (AccessType.READ_WRITE, "read-write"),
            (AccessType.WRITE_ONCE, "writeOnce"),
            (AccessType.READ_WRITE_ONCE, "read-writeOnce"),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(access=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            {create_element("access", expected)}
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ModifiedWriteValuesType.ONE_TO_CLEAR, "oneToClear"),
            (ModifiedWriteValuesType.ONE_TO_SET, "oneToSet"),
            (ModifiedWriteValuesType.ONE_TO_TOGGLE, "oneToToggle"),
            (ModifiedWriteValuesType.ZERO_TO_CLEAR, "zeroToClear"),
            (ModifiedWriteValuesType.ZERO_TO_SET, "zeroToSet"),
            (ModifiedWriteValuesType.ZERO_TO_TOGGLE, "zeroToToggle"),
            (ModifiedWriteValuesType.CLEAR, "clear"),
            (ModifiedWriteValuesType.SET, "set"),
            (ModifiedWriteValuesType.MODIFY, "modify"),
            pytest.param(None, None),
        ],
    )
    def test_modified_write_values(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(modified_write_values=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            {create_element("modifiedWriteValues", expected)}
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    def test_without_write_constraint(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_field: Callable[..., SVDField],
    ):
        field = create_field(write_constraint=None)

        expected_xml = """\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ReadActionType.CLEAR, "clear"),
            (ReadActionType.SET, "set"),
            (ReadActionType.MODIFY, "modify"),
            (ReadActionType.MODIFY_EXTERNAL, "modifyExternal"),
            pytest.param(None, None),
        ],
    )
    def test_read_action(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_field: Callable[..., SVDField],
        test_input: Any,
        expected: Any,
    ):
        field = create_field(read_action=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            {create_element("readAction", expected)}
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)

    def test_with_enumerated_value_containers(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_enumerated_value_container: Callable[..., SVDEnumeratedValueContainer],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_field: Callable[..., SVDField],
    ):
        field = create_field(
            write_constraint=None,
            enumerated_value_containers=[
                create_enumerated_value_container(enumerated_values=[create_enumerated_value()]),
                create_enumerated_value_container(enumerated_values=[create_enumerated_value(name="disabled")]),
            ],
        )

        expected_xml = """\
        <field derivedFrom="der.from">
            <name>TimerCtrl0_IntSel</name>
            <description>Select interrupt line that is triggered by timer overflow.</description>
            <bitOffset>1</bitOffset>
            <bitWidth>3</bitWidth>
            <access>read-write</access>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
            <enumeratedValues derivedFrom="der.from">
                <name>TimerIntSelect</name>
                <headerEnumName>TimerIntSelect_Enum</headerEnumName>
                <usage>read</usage>
                <enumeratedValue>
                    <name>enabled</name>
                    <description>The clock source clk1 is running.</description>
                    <value>0b1111</value>
                </enumeratedValue>
            </enumeratedValues>
            <enumeratedValues derivedFrom="der.from">
                <name>TimerIntSelect</name>
                <headerEnumName>TimerIntSelect_Enum</headerEnumName>
                <usage>read</usage>
                <enumeratedValue>
                    <name>disabled</name>
                    <description>The clock source clk1 is running.</description>
                    <value>0b1111</value>
                </enumeratedValue>
            </enumeratedValues>
        </field>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(field)


class TestSVDRegister:
    @pytest.mark.parametrize("test_input, expected", [("test.name.a", "test.name.a"), pytest.param(None, None)])
    def test_derived_from(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(derived_from=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <register {create_attrib("derivedFrom", expected)}>
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_dim(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            dim=test_input,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            {create_element("dim", expected)}
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_dim_increment(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            dim=6,
            dim_increment=test_input,
            dim_index="A,B,C,D,E,Z",
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <dim>6</dim>
            {create_element("dimIncrement", expected)}
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [("A,B,C", "A,B,C"), pytest.param(None, None)])
    def test_dim_index(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            dim=6,
            dim_increment=4,
            dim_index=test_input,
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            {create_element("dimIndex", expected)}
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_dim_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            dim=6,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name=test_input,
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            {create_element("dimName", expected)}
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    def test_dim_without_array_index(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
    ):
        register = create_register(
            dim=6,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name="testname",
            dim_array_index=None,
            write_constraint=create_write_constraint(range_=(0, 1)),
        )

        expected_xml = """\
        <register derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>testname</dimName>
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname")])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(name=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <register derivedFrom="der.from">
            {create_element("name", expected)}
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [("displayname", "displayname"), pytest.param(None, None)])
    def test_display_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(display_name=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            {create_element("displayName", expected)}
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [("testdesc", "testdesc"), pytest.param(None, None)])
    def test_description(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(description=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            {create_element("description", expected)}
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [("alt_gr", "alt_gr"), pytest.param(None, None)])
    def test_alternate_group(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(alternate_group=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            {create_element("alternateGroup", expected)}
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [("alt_reg", "alt_reg"), pytest.param(None, None)])
    def test_alternate_register(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            alternate_register=test_input, write_constraint=create_write_constraint(range_=(0, 1))
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            {create_element("alternateRegister", expected)}
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [(1, "0x1")])
    def test_address_offset(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(address_offset=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            {create_element("addressOffset", expected)}
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [(1, "1"), pytest.param(None, None)])
    def test_size(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            size=test_input,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=0x0,
            write_constraint=None,
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            {create_element("size", expected)}
            <access>read-write</access>
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, "read-only"),
            (AccessType.WRITE_ONLY, "write-only"),
            (AccessType.READ_WRITE, "read-write"),
            (AccessType.WRITE_ONCE, "writeOnce"),
            (AccessType.READ_WRITE_ONCE, "read-writeOnce"),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            size=1,
            access=test_input,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=0x0,
            write_constraint=None,
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <size>1</size>
            {create_element("access", expected)}
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, "s"),
            (ProtectionStringType.NON_SECURE, "n"),
            (ProtectionStringType.PRIVILEGED, "p"),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            size=1,
            access=AccessType.READ_WRITE,
            protection=test_input,
            reset_value=0x0,
            reset_mask=0x0,
            write_constraint=None,
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <size>1</size>
            <access>read-write</access>
            {create_element("protection", expected)}
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [(0x0, "0x0"), pytest.param(None, None)])
    def test_reset_value(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            size=1,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=test_input,
            reset_mask=0x0,
            write_constraint=None,
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <size>1</size>
            <access>read-write</access>
            <protection>s</protection>
            {create_element("resetValue", expected)}
            <resetMask>0x0</resetMask>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize("test_input, expected", [(0xFF, "0xff"), pytest.param(None, None)])
    def test_reset_mask(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            size=1,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=test_input,
            write_constraint=None,
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <size>1</size>
            <access>read-write</access>
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            {create_element("resetMask", expected)}
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (DataTypeType.UINT8_T, "uint8_t"),
            (DataTypeType.UINT16_T, "uint16_t"),
            (DataTypeType.UINT32_T, "uint32_t"),
            (DataTypeType.UINT64_T, "uint64_t"),
            (DataTypeType.INT8_T, "int8_t"),
            (DataTypeType.INT16_T, "int16_t"),
            (DataTypeType.INT32_T, "int32_t"),
            (DataTypeType.INT64_T, "int64_t"),
            (DataTypeType.UINT8_T_PTR, "uint8_t *"),
            (DataTypeType.UINT16_T_PTR, "uint16_t *"),
            (DataTypeType.UINT32_T_PTR, "uint32_t *"),
            (DataTypeType.UINT64_T_PTR, "uint64_t *"),
            (DataTypeType.INT8_T_PTR, "int8_t *"),
            (DataTypeType.INT16_T_PTR, "int16_t *"),
            (DataTypeType.INT32_T_PTR, "int32_t *"),
            (DataTypeType.INT64_T_PTR, "int64_t *"),
            pytest.param(None, None),
        ],
    )
    def test_data_type(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(data_type=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            {create_element("dataType", expected)}
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ModifiedWriteValuesType.ONE_TO_CLEAR, "oneToClear"),
            (ModifiedWriteValuesType.ONE_TO_SET, "oneToSet"),
            (ModifiedWriteValuesType.ONE_TO_TOGGLE, "oneToToggle"),
            (ModifiedWriteValuesType.ZERO_TO_CLEAR, "zeroToClear"),
            (ModifiedWriteValuesType.ZERO_TO_SET, "zeroToSet"),
            (ModifiedWriteValuesType.ZERO_TO_TOGGLE, "zeroToToggle"),
            (ModifiedWriteValuesType.CLEAR, "clear"),
            (ModifiedWriteValuesType.SET, "set"),
            (ModifiedWriteValuesType.MODIFY, "modify"),
            pytest.param(None, None),
        ],
    )
    def test_modified_write_values(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(
            modified_write_values=test_input, write_constraint=create_write_constraint(range_=(0, 1))
        )

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            {create_element("modifiedWriteValues", expected)}
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    def test_without_write_constraint(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_register: Callable[..., SVDRegister],
    ):
        register = create_register(write_constraint=None)

        expected_xml = """\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ReadActionType.CLEAR, "clear"),
            (ReadActionType.SET, "set"),
            (ReadActionType.MODIFY, "modify"),
            (ReadActionType.MODIFY_EXTERNAL, "modifyExternal"),
            pytest.param(None, None),
        ],
    )
    def test_read_action(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        test_input: Any,
        expected: Any,
    ):
        register = create_register(read_action=test_input, write_constraint=create_write_constraint(range_=(0, 1)))

        expected_xml = f"""\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <writeConstraint>
                <range>
                    <minimum>0</minimum>
                    <maximum>1</maximum>
                </range>
            </writeConstraint>
            {create_element("readAction", expected)}
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)

    def test_with_fields(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_field: Callable[..., SVDField],
        create_register: Callable[..., SVDRegister],
    ):
        register = create_register(
            write_constraint=None,
            fields=[create_field(write_constraint=None), create_field(name="TimerCtrl1_IntSel", write_constraint=None)],
        )

        expected_xml = """\
        <register derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <displayName>Timer Control 0</displayName>
            <description>Timer Control Register 0</description>
            <alternateGroup>alt_group</alternateGroup>
            <alternateRegister>alt_reg</alternateRegister>
            <addressOffset>0x0</addressOffset>
            <dataType>uint8_t</dataType>
            <modifiedWriteValues>oneToSet</modifiedWriteValues>
            <readAction>clear</readAction>
            <fields>
                <field derivedFrom="der.from">
                    <name>TimerCtrl0_IntSel</name>
                    <description>Select interrupt line that is triggered by timer overflow.</description>
                    <bitOffset>1</bitOffset>
                    <bitWidth>3</bitWidth>
                    <access>read-write</access>
                    <modifiedWriteValues>oneToSet</modifiedWriteValues>
                    <readAction>clear</readAction>
                </field>
                <field derivedFrom="der.from">
                    <name>TimerCtrl1_IntSel</name>
                    <description>Select interrupt line that is triggered by timer overflow.</description>
                    <bitOffset>1</bitOffset>
                    <bitWidth>3</bitWidth>
                    <access>read-write</access>
                    <modifiedWriteValues>oneToSet</modifiedWriteValues>
                    <readAction>clear</readAction>
                </field>
            </fields>
        </register>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(register)


class TestSVDCluster:
    @pytest.mark.parametrize("test_input, expected", [("test.name.a", "test.name.a"), pytest.param(None, None)])
    def test_derived_from(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(derived_from=test_input)

        expected_xml = f"""\
        <cluster {create_attrib("derivedFrom", expected)}>
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_dim(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            dim=test_input,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            {create_element("dim", expected)}
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_dim_increment(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            dim=6,
            dim_increment=test_input,
            dim_index="A,B,C,D,E,Z",
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <dim>6</dim>
            {create_element("dimIncrement", expected)}
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [("A,B,C", "A,B,C"), pytest.param(None, None)])
    def test_dim_index(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            dim=6,
            dim_increment=4,
            dim_index=test_input,
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            {create_element("dimIndex", expected)}
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_dim_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            dim=6,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name=test_input,
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            {create_element("dimName", expected)}
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    def test_dim_without_array_index(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
    ):
        cluster = create_cluster(
            dim=6,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name="testname",
        )

        expected_xml = """\
        <cluster derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>testname</dimName>
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname")])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(name=test_input)

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            {create_element("name", expected)}
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [("testdesc", "testdesc"), pytest.param(None, None)])
    def test_description(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(description=test_input)

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            {create_element("description", expected)}
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [("altcluster", "altcluster"), pytest.param(None, None)])
    def test_alternate_cluster(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(alternate_cluster=test_input)

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            {create_element("alternateCluster", expected)}
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [("headstructname", "headstructname"), pytest.param(None, None)])
    def test_header_struct_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(header_struct_name=test_input)

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            {create_element("headerStructName", expected)}
            <addressOffset>0x0</addressOffset>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [(1, "0x1")])
    def test_address_offset(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(address_offset=test_input)

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            {create_element("addressOffset", expected)}
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [(1, "1"), pytest.param(None, None)])
    def test_size(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            size=test_input,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
            {create_element("size", expected)}
            <access>read-write</access>
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, "read-only"),
            (AccessType.WRITE_ONLY, "write-only"),
            (AccessType.READ_WRITE, "read-write"),
            (AccessType.WRITE_ONCE, "writeOnce"),
            (AccessType.READ_WRITE_ONCE, "read-writeOnce"),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            size=1,
            access=test_input,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
            <size>1</size>
            {create_element("access", expected)}
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, "s"),
            (ProtectionStringType.NON_SECURE, "n"),
            (ProtectionStringType.PRIVILEGED, "p"),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            size=1,
            access=AccessType.READ_WRITE,
            protection=test_input,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
            <size>1</size>
            <access>read-write</access>
            {create_element("protection", expected)}
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [(0x0, "0x0"), pytest.param(None, None)])
    def test_reset_value(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            size=1,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=test_input,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
            <size>1</size>
            <access>read-write</access>
            <protection>s</protection>
            {create_element("resetValue", expected)}
            <resetMask>0x0</resetMask>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    @pytest.mark.parametrize("test_input, expected", [(0xFF, "0xff"), pytest.param(None, None)])
    def test_reset_mask(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_cluster: Callable[..., SVDCluster],
        test_input: Any,
        expected: Any,
    ):
        cluster = create_cluster(
            size=1,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=test_input,
        )

        expected_xml = f"""\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
            <size>1</size>
            <access>read-write</access>
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            {create_element("resetMask", expected)}
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)

    def test_with_registers_and_cluster(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_write_constraint: Callable[..., SVDWriteConstraint],
        create_register: Callable[..., SVDRegister],
        create_cluster: Callable[..., SVDCluster],
    ):
        cluster = create_cluster(
            registers_clusters=[
                create_register(write_constraint=create_write_constraint(range_=(0, 1))),
                create_cluster(registers_clusters=[create_cluster()]),
                create_register(name="TimerCtrl1"),
            ]
        )

        expected_xml = """\
        <cluster derivedFrom="der.from">
            <name>TimerCtrl0</name>
            <description>Timer Control Register 0</description>
            <alternateCluster>alt_cluster</alternateCluster>
            <headerStructName>headername</headerStructName>
            <addressOffset>0x0</addressOffset>
            <register derivedFrom="der.from">
                <name>TimerCtrl0</name>
                <displayName>Timer Control 0</displayName>
                <description>Timer Control Register 0</description>
                <alternateGroup>alt_group</alternateGroup>
                <alternateRegister>alt_reg</alternateRegister>
                <addressOffset>0x0</addressOffset>
                <dataType>uint8_t</dataType>
                <modifiedWriteValues>oneToSet</modifiedWriteValues>
                <writeConstraint>
                    <range>
                        <minimum>0</minimum>
                        <maximum>1</maximum>
                    </range>
                </writeConstraint>
                <readAction>clear</readAction>
            </register>
            <cluster derivedFrom="der.from">
                <name>TimerCtrl0</name>
                <description>Timer Control Register 0</description>
                <alternateCluster>alt_cluster</alternateCluster>
                <headerStructName>headername</headerStructName>
                <addressOffset>0x0</addressOffset>
                <cluster derivedFrom="der.from">
                    <name>TimerCtrl0</name>
                    <description>Timer Control Register 0</description>
                    <alternateCluster>alt_cluster</alternateCluster>
                    <headerStructName>headername</headerStructName>
                    <addressOffset>0x0</addressOffset>
                </cluster>
            </cluster>
            <register derivedFrom="der.from">
                <name>TimerCtrl1</name>
                <displayName>Timer Control 0</displayName>
                <description>Timer Control Register 0</description>
                <alternateGroup>alt_group</alternateGroup>
                <alternateRegister>alt_reg</alternateRegister>
                <addressOffset>0x0</addressOffset>
                <dataType>uint8_t</dataType>
                <modifiedWriteValues>oneToSet</modifiedWriteValues>
                <readAction>clear</readAction>
            </register>
        </cluster>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(cluster)


class TestSVDPeripheral:
    @pytest.mark.parametrize("test_input, expected", [("test.name.a", "test.name.a"), pytest.param(None, None)])
    def test_derived_from(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_attrib: Callable[[str, None | str], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(derived_from=test_input)

        expected_xml = f"""\
        <peripheral {create_attrib("derivedFrom", expected)}>
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_dim(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            dim=test_input,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            {create_element("dim", expected)}
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [(6, "6"), pytest.param(None, None)])
    def test_dim_increment(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            dim=6,
            dim_increment=test_input,
            dim_index="A,B,C,D,E,Z",
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <dim>6</dim>
            {create_element("dimIncrement", expected)}
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("A,B,C", "A,B,C"), pytest.param(None, None)])
    def test_dim_index(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            dim=6,
            dim_increment=4,
            dim_index=test_input,
            dim_name="dimName",
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            {create_element("dimIndex", expected)}
            <dimName>dimName</dimName>
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_dim_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_dim_array_index: Callable[..., SVDDimArrayIndex],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            dim=6,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name=test_input,
            dim_array_index=create_dim_array_index(
                header_enum_name="FSMC_EnumArray",
                enumerated_values=[create_enumerated_value(name="UART0", description="UART0 Peripheral", value="0")],
            ),
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            {create_element("dimName", expected)}
            <dimArrayIndex>
                <headerEnumName>FSMC_EnumArray</headerEnumName>
                <enumeratedValue>
                    <name>UART0</name>
                    <description>UART0 Peripheral</description>
                    <value>0</value>
              </enumeratedValue>
            </dimArrayIndex>
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    def test_dim_without_array_index(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
    ):
        peripheral = create_peripheral(
            dim=6,
            dim_increment=4,
            dim_index="A,B,C,D,E,Z",
            dim_name="testname",
        )

        expected_xml = """\
        <peripheral derivedFrom="der.from">
            <dim>6</dim>
            <dimIncrement>4</dimIncrement>
            <dimIndex>A,B,C,D,E,Z</dimIndex>
            <dimName>testname</dimName>
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname")])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(name=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            {create_element("name", expected)}
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_version(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(version=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            {create_element("version", expected)}
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_description(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(description=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            {create_element("description", expected)}
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_alternate_peripheral(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(alternate_peripheral=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            {create_element("alternatePeripheral", expected)}
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_group_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(group_name=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            {create_element("groupName", expected)}
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_prepand_to_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(prepend_to_name=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            {create_element("prependToName", expected)}
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_append_to_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(append_to_name=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            {create_element("appendToName", expected)}
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_header_struct_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(header_struct_name=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            {create_element("headerStructName", expected)}
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), pytest.param(None, None)])
    def test_disable_condition(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(disable_condition=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            {create_element("disableCondition", expected)}
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [(0x40002000, "0x40002000")])
    def test_base_address(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(base_address=test_input)

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            {create_element("baseAddress", expected)}
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [(1, "1"), pytest.param(None, None)])
    def test_size(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            size=test_input,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
            {create_element("size", expected)}
            <access>read-write</access>
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, "read-only"),
            (AccessType.WRITE_ONLY, "write-only"),
            (AccessType.READ_WRITE, "read-write"),
            (AccessType.WRITE_ONCE, "writeOnce"),
            (AccessType.READ_WRITE_ONCE, "read-writeOnce"),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            size=1,
            access=test_input,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
            <size>1</size>
            {create_element("access", expected)}
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, "s"),
            (ProtectionStringType.NON_SECURE, "n"),
            (ProtectionStringType.PRIVILEGED, "p"),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            size=1,
            access=AccessType.READ_WRITE,
            protection=test_input,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
            <size>1</size>
            <access>read-write</access>
            {create_element("protection", expected)}
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [(0x0, "0x0"), pytest.param(None, None)])
    def test_reset_value(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            size=1,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=test_input,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
            <size>1</size>
            <access>read-write</access>
            <protection>s</protection>
            {create_element("resetValue", expected)}
            <resetMask>0x0</resetMask>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    @pytest.mark.parametrize("test_input, expected", [(0xFF, "0xff"), pytest.param(None, None)])
    def test_reset_mask(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        test_input: Any,
        expected: Any,
    ):
        peripheral = create_peripheral(
            size=1,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=test_input,
        )

        expected_xml = f"""\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
            <size>1</size>
            <access>read-write</access>
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            {create_element("resetMask", expected)}
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    def test_with_address_blocks(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_address_block: Callable[..., SVDAddressBlock],
        create_peripheral: Callable[..., SVDPeripheral],
    ):
        peripheral = create_peripheral(
            address_blocks=[
                create_address_block(
                    offset=0x0, size=0x400, usage=EnumeratedTokenType.REGISTERS, protection=ProtectionStringType.SECURE
                ),
                create_address_block(
                    offset=0x1, size=0x600, usage=EnumeratedTokenType.REGISTERS, protection=ProtectionStringType.SECURE
                ),
            ]
        )

        expected_xml = """\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
            <addressBlock>
                <offset>0x0</offset>
                <size>0x400</size>
                <usage>registers</usage>
                <protection>s</protection>
            </addressBlock>
            <addressBlock>
                <offset>0x1</offset>
                <size>0x600</size>
                <usage>registers</usage>
                <protection>s</protection>
            </addressBlock>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    def test_with_interrupts(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_interrupt: Callable[..., SVDInterrupt],
        create_peripheral: Callable[..., SVDPeripheral],
    ):
        peripheral = create_peripheral(
            interrupts=[
                create_interrupt(name="TIM1", description="TIM1 Interrupt", value=34),
                create_interrupt(name="TIM2", description="TIM1 Interrupt", value=34),
            ]
        )

        expected_xml = """\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
            <interrupt>
                <name>TIM1</name>
                <description>TIM1 Interrupt</description>
                <value>34</value>
            </interrupt>
            <interrupt>
                <name>TIM2</name>
                <description>TIM1 Interrupt</description>
                <value>34</value>
            </interrupt>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)

    def test_with_registers_clusters(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_register: Callable[..., SVDRegister],
        create_cluster: Callable[..., SVDCluster],
        create_peripheral: Callable[..., SVDPeripheral],
    ):
        peripheral = create_peripheral(
            registers_clusters=[
                create_register(write_constraint=None),
                create_cluster(registers_clusters=[create_cluster()]),
                create_register(name="reg2", write_constraint=None),
            ]
        )

        expected_xml = """\
        <peripheral derivedFrom="der.from">
            <name>Timer1</name>
            <version>1.0</version>
            <description>Timer 1 is a standard timer</description>
            <alternatePeripheral>Timer1_Alt</alternatePeripheral>
            <groupName>group_name</groupName>
            <prependToName>prepend</prependToName>
            <appendToName>append</appendToName>
            <headerStructName>headerstruct</headerStructName>
            <disableCondition>discond</disableCondition>
            <baseAddress>0x40002000</baseAddress>
            <registers>
                <register derivedFrom="der.from">
                    <name>TimerCtrl0</name>
                    <displayName>Timer Control 0</displayName>
                    <description>Timer Control Register 0</description>
                    <alternateGroup>alt_group</alternateGroup>
                    <alternateRegister>alt_reg</alternateRegister>
                    <addressOffset>0x0</addressOffset>
                    <dataType>uint8_t</dataType>
                    <modifiedWriteValues>oneToSet</modifiedWriteValues>
                    <readAction>clear</readAction>
                </register>
                <cluster derivedFrom="der.from">
                    <name>TimerCtrl0</name>
                    <description>Timer Control Register 0</description>
                    <alternateCluster>alt_cluster</alternateCluster>
                    <headerStructName>headername</headerStructName>
                    <addressOffset>0x0</addressOffset>
                    <cluster derivedFrom="der.from">
                        <name>TimerCtrl0</name>
                        <description>Timer Control Register 0</description>
                        <alternateCluster>alt_cluster</alternateCluster>
                        <headerStructName>headername</headerStructName>
                        <addressOffset>0x0</addressOffset>
                    </cluster>
                </cluster>
                <register derivedFrom="der.from">
                    <name>reg2</name>
                    <displayName>Timer Control 0</displayName>
                    <description>Timer Control Register 0</description>
                    <alternateGroup>alt_group</alternateGroup>
                    <alternateRegister>alt_reg</alternateRegister>
                    <addressOffset>0x0</addressOffset>
                    <dataType>uint8_t</dataType>
                    <modifiedWriteValues>oneToSet</modifiedWriteValues>
                    <readAction>clear</readAction>
                </register>
            </registers>
        </peripheral>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(peripheral)


class TestSVDDevice:
    def test_namespace_location_and_schema_version(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
    ):
        device = create_device(xs_no_namespace_schema_location="aa", schema_version="1.3")

        expected_xml = """\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="aa" schemaVersion="1.3">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("testvendor", "testvendor"), pytest.param(None, None)])
    def test_vendor(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(vendor=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            {create_element("vendor", expected)}
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("testid", "testid"), pytest.param(None, None)])
    def test_vendor_id(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(vendor_id=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            {create_element("vendorID", expected)}
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname")])
    def test_name(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(name=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            {create_element("name", expected)}
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("testseries", "testseries"), pytest.param(None, None)])
    def test_series(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(series=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            {create_element("series", expected)}
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("testversion", "testversion")])
    def test_version(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(version=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            {create_element("version", expected)}
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("desc", "desc")])
    def test_description(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(description=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            {create_element("description", expected)}
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("licensetest", "licensetest"), pytest.param(None, None)])
    def test_license_text(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(license_text=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            {create_element("licenseText", expected)}
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    def test_with_cpu(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_sau_region: Callable[..., SVDSauRegion],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
        create_cpu: Callable[..., SVDCPU],
        create_device: Callable[..., SVDDevice],
    ):
        device = create_device(
            cpu=create_cpu(sau_regions_config=create_sau_regions_config(regions=[create_sau_region()]))
        )

        expected_xml = """\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <cpu>
                <name>CM0</name>
                <revision>r0p0</revision>
                <endian>little</endian>
                <mpuPresent>false</mpuPresent>
                <fpuPresent>false</fpuPresent>
                <fpuDP>false</fpuDP>
                <dspPresent>false</dspPresent>
                <icachePresent>false</icachePresent>
                <dcachePresent>false</dcachePresent>
                <itcmPresent>false</itcmPresent>
                <dtcmPresent>false</dtcmPresent>
                <vtorPresent>false</vtorPresent>
                <nvicPrioBits>2</nvicPrioBits>
                <vendorSystickConfig>false</vendorSystickConfig>
                <deviceNumInterrupts>6</deviceNumInterrupts>
                <sauNumRegions>2</sauNumRegions>
                <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                    <region enabled="true" name="Region1">
                        <base>0x1000</base>
                        <limit>0x2000</limit>
                        <access>n</access>
                    </region>
                </sauRegionsConfig>
            </cpu>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("test_h_name", "test_h_name"), pytest.param(None, None)])
    def test_header_system_filename(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(header_system_filename=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            {create_element("headerSystemFilename", expected)}
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [("test_hdp", "test_hdp"), pytest.param(None, None)])
    def test_header_definitions_prefix(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(header_definitions_prefix=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            {create_element("headerDefinitionsPrefix", expected)}
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [(10, "10")])
    def test_address_unit_bits(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(address_unit_bits=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            {create_element("addressUnitBits", expected)}
            <width>32</width>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [(10, "10")])
    def test_width(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(width=test_input)

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            {create_element("width", expected)}
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [(10, "10")])
    def test_size(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(
            size=test_input,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
            {create_element("size", expected)}
            <access>read-write</access>
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, "read-only"),
            (AccessType.WRITE_ONLY, "write-only"),
            (AccessType.READ_WRITE, "read-write"),
            (AccessType.WRITE_ONCE, "writeOnce"),
            (AccessType.READ_WRITE_ONCE, "read-writeOnce"),
            pytest.param(None, None),
        ],
    )
    def test_access(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(
            size=1,
            access=test_input,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
            <size>1</size>
            {create_element("access", expected)}
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, "s"),
            (ProtectionStringType.NON_SECURE, "n"),
            (ProtectionStringType.PRIVILEGED, "p"),
            pytest.param(None, None),
        ],
    )
    def test_protection(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(
            size=1,
            access=AccessType.READ_WRITE,
            protection=test_input,
            reset_value=0x0,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
            <size>1</size>
            <access>read-write</access>
            {create_element("protection", expected)}
            <resetValue>0x0</resetValue>
            <resetMask>0x0</resetMask>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [(0x0, "0x0"), pytest.param(None, None)])
    def test_reset_value(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(
            size=1,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=test_input,
            reset_mask=0x0,
        )

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
            <size>1</size>
            <access>read-write</access>
            <protection>s</protection>
            {create_element("resetValue", expected)}
            <resetMask>0x0</resetMask>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    @pytest.mark.parametrize("test_input, expected", [(0xFF, "0xff"), pytest.param(None, None)])
    def test_reset_mask(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        create_element: Callable[[str, Any], str],
        dedent_xml: Callable[[str], str],
        create_device: Callable[..., SVDDevice],
        test_input: Any,
        expected: Any,
    ):
        device = create_device(
            size=1,
            access=AccessType.READ_WRITE,
            protection=ProtectionStringType.SECURE,
            reset_value=0x0,
            reset_mask=test_input,
        )

        expected_xml = f"""\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
            <size>1</size>
            <access>read-write</access>
            <protection>s</protection>
            <resetValue>0x0</resetValue>
            {create_element("resetMask", expected)}
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)

    def test_with_peripherals(
        self,
        svd_obj_to_xml_str: Callable[[SVDObject], str],
        dedent_xml: Callable[[str], str],
        create_peripheral: Callable[..., SVDPeripheral],
        create_device: Callable[..., SVDDevice],
    ):
        device = create_device(peripherals=[create_peripheral(), create_peripheral(name="Timer2")])

        expected_xml = """\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.0">
            <vendor>STMicroelectronics</vendor>
            <vendorID>ST</vendorID>
            <name>STM32F0</name>
            <series>STM32F0</series>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <licenseText>license</licenseText>
            <headerSystemFilename>stm32f0.h</headerSystemFilename>
            <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
            <peripherals>
                <peripheral derivedFrom="der.from">
                    <name>Timer1</name>
                    <version>1.0</version>
                    <description>Timer 1 is a standard timer</description>
                    <alternatePeripheral>Timer1_Alt</alternatePeripheral>
                    <groupName>group_name</groupName>
                    <prependToName>prepend</prependToName>
                    <appendToName>append</appendToName>
                    <headerStructName>headerstruct</headerStructName>
                    <disableCondition>discond</disableCondition>
                    <baseAddress>0x40002000</baseAddress>
                </peripheral>
                <peripheral derivedFrom="der.from">
                    <name>Timer2</name>
                    <version>1.0</version>
                    <description>Timer 1 is a standard timer</description>
                    <alternatePeripheral>Timer1_Alt</alternatePeripheral>
                    <groupName>group_name</groupName>
                    <prependToName>prepend</prependToName>
                    <appendToName>append</appendToName>
                    <headerStructName>headerstruct</headerStructName>
                    <disableCondition>discond</disableCondition>
                    <baseAddress>0x40002000</baseAddress>
                </peripheral>
            </peripherals>
        </device>
        """

        assert dedent_xml(expected_xml) == svd_obj_to_xml_str(device)
