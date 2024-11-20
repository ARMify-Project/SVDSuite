from dataclasses import dataclass

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

from svdsuite.model.parse import (
    SVDCPU,
    SVDAddressBlock,
    SVDCluster,
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


@dataclass(kw_only=True)
class SauRegion:
    enabled: bool
    name: None | str
    base: int
    limit: int
    access: SauAccessType
    parsed: SVDSauRegion


@dataclass(kw_only=True)
class SauRegionsConfig:
    enabled: bool
    protection_when_disabled: ProtectionStringType
    regions: list[SauRegion]
    parsed: SVDSauRegionsConfig


@dataclass(kw_only=True)
class CPU:
    name: CPUNameType
    revision: str
    endian: EndianType
    mpu_present: bool
    fpu_present: bool
    fpu_dp: bool
    dsp_present: bool
    icache_present: bool
    dcache_present: bool
    itcm_present: bool
    dtcm_present: bool
    vtor_present: bool
    nvic_prio_bits: int
    vendor_systick_config: bool
    device_num_interrupts: None | int
    sau_num_regions: None | int
    sau_regions_config: None | SauRegionsConfig
    parsed: SVDCPU


@dataclass(kw_only=True)
class EnumeratedValue:
    name: str
    description: None | str
    value: None | int
    is_default: bool
    parsed: SVDEnumeratedValue


@dataclass(kw_only=True)
class DimArrayIndex:
    header_enum_name: None | str
    enumerated_values: list[EnumeratedValue]
    parsed: SVDDimArrayIndex


@dataclass(kw_only=True)
class AddressBlock:
    offset: int
    size: int
    usage: EnumeratedTokenType
    protection: None | ProtectionStringType
    parsed: SVDAddressBlock


@dataclass(kw_only=True)
class Interrupt:
    name: str
    description: None | str
    value: int
    parsed: SVDInterrupt


@dataclass(kw_only=True)
class WriteConstraint:
    write_as_read: None | bool
    use_enumerated_values: None | bool
    range_: None | tuple[int, int]
    parsed: SVDWriteConstraint


@dataclass(kw_only=True)
class EnumeratedValueContainer:
    name: None | str
    header_enum_name: None | str
    usage: EnumUsageType
    enumerated_values: list[EnumeratedValue]
    parsed: SVDEnumeratedValueContainer


@dataclass(kw_only=True)
class Field:
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    name: str
    description: None | str
    lsb: int
    msb: int
    access: None | AccessType
    modified_write_values: ModifiedWriteValuesType
    write_constraint: None | WriteConstraint
    read_action: None | ReadActionType
    enumerated_value_containers: list[EnumeratedValueContainer]
    parsed: SVDField


@dataclass(kw_only=True)
class Register:
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    size: None | int
    access: None | AccessType
    protection: None | ProtectionStringType
    reset_value: None | int
    reset_mask: None | int
    name: str
    display_name: None | str
    description: None | str
    alternate_group: None | str
    alternate_register: None | str
    address_offset: int
    data_type: None | DataTypeType
    modified_write_values: ModifiedWriteValuesType
    write_constraint: None | WriteConstraint
    read_action: None | ReadActionType
    fields: list[Field]
    parsed: SVDRegister


@dataclass(kw_only=True)
class Cluster:
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    size: None | int
    access: None | AccessType
    protection: None | ProtectionStringType
    reset_value: None | int
    reset_mask: None | int
    name: str
    description: None | str
    alternate_cluster: None | str
    header_struct_name: None | str
    address_offset: int
    registers_clusters: list["Register | Cluster"]
    parsed: SVDCluster


@dataclass(kw_only=True)
class Peripheral:
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    size: None | int
    access: None | AccessType
    protection: None | ProtectionStringType
    reset_value: None | int
    reset_mask: None | int
    name: str
    version: None | str
    description: None | str
    alternate_peripheral: None | str
    group_name: None | str
    prepend_to_name: None | str
    append_to_name: None | str
    header_struct_name: None | str
    disable_condition: None | str
    base_address: int
    address_blocks: list[AddressBlock]
    interrupts: list[Interrupt]
    registers_clusters: list[Register | Cluster]
    parsed: SVDPeripheral


@dataclass(kw_only=True)
class Device:
    size: None | int
    access: None | AccessType
    protection: None | ProtectionStringType
    reset_value: None | int
    reset_mask: None | int
    vendor: None | str
    vendor_id: None | str
    name: str
    series: None | str
    version: str
    description: str
    license_text: None | str
    cpu: None | CPU
    header_system_filename: None | str
    header_definitions_prefix: None | str
    address_unit_bits: int
    width: int
    peripherals: list[Peripheral]
    parsed: SVDDevice
