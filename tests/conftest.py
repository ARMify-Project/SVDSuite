import os
from typing import Callable
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
from svdsuite.util.xml_parse import safe_fromstring


@pytest.fixture(name="get_test_svd_file_path", scope="session", autouse=False)
def fixture_get_test_svd_file_path() -> Callable[[str], str]:
    def _(file_name: str):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(test_dir, "svd", file_name)

    return _


@pytest.fixture(name="get_test_svd_file_content", scope="session", autouse=False)
def fixture_get_test_svd_file_content(get_test_svd_file_path: Callable[[str], str]) -> Callable[[str], bytes]:
    def _(file_name: str):
        file_path = get_test_svd_file_path(file_name)

        with open(file_path, "rb") as file:
            return file.read()

    return _


@pytest.fixture(scope="session", autouse=False)
def modify_test_svd_file_and_get_content(
    get_test_svd_file_content: Callable[[str], bytes],
) -> Callable[[str, str, None | str, None | str], bytes]:
    def _(file_name: str, xpath_str: str, attribute: None | str, value: None | str):
        file_content = get_test_svd_file_content(file_name)
        tree = safe_fromstring(file_content)

        element_list = tree.xpath(xpath_str)

        if not isinstance(element_list, list):
            raise ValueError(f"can't find an element for xpath '{xpath_str}'")

        element = element_list[0]

        if not isinstance(element, lxml.etree._Element):  # pyright: ignore[reportPrivateUsage] pylint: disable=W0212
            raise ValueError(f"can't find an element for xpath '{xpath_str}'")

        if attribute is None:
            if value is None:
                parent = element.getparent()

                if parent is None:
                    raise ValueError(f"can't find parent for element with xpath '{xpath_str}'")

                parent.remove(element)
            else:
                element.text = value
        else:
            if value is None:
                del element.attrib[attribute]
            else:
                element.attrib[attribute] = value

        return lxml.etree.tostring(tree, encoding="utf8")

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
