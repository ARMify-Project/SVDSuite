from typing import List, Union, Tuple
from dataclasses import dataclass, field

from svdsuite.types import (
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

from svdsuite.model.svd import (
    SVDCPU,
    SVDAddressBlock,
    SVDCluster,
    SVDDevice,
    SVDDimArrayIndex,
    SVDEnumeratedValue,
    SVDEnumeratedValueMap,
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
    enabled: bool = True
    name: None | str = None
    base: int
    limit: int
    access: SauAccessType
    parsed: SVDSauRegion


@dataclass(kw_only=True)
class SauRegionsConfig:
    enabled: bool = True
    protection_when_disabled: ProtectionStringType = ProtectionStringType.SECURE
    regions: List[SauRegion] = field(default_factory=list)
    parsed: SVDSauRegionsConfig


@dataclass(kw_only=True)
class CPU:
    name: CPUNameType
    revision: str
    endian: EndianType
    mpu_present: bool = False
    fpu_present: bool = False
    fpu_dp: bool = False
    dsp_present: bool = False
    icache_present: bool = False
    dcache_present: bool = False
    itcm_present: bool = False
    dtcm_present: bool = False
    vtor_present: bool = True
    nvic_prio_bits: int
    vendor_systick_config: bool
    device_num_interrupts: None | int = None
    sau_num_regions: None | int = None
    sau_regions_config: None | SauRegionsConfig = None
    parsed: SVDCPU


@dataclass(kw_only=True)
class EnumeratedValueMap:
    name: str
    description: None | str = None
    value: None | str = None  # int value, but can contain 'do not care' bits represented by >x<
    is_default: None | bool = None
    parsed: SVDEnumeratedValueMap


@dataclass(kw_only=True)
class DimArrayIndex:
    header_enum_name: None | str = None
    enumerated_values_map: List[EnumeratedValueMap]
    parsed: SVDDimArrayIndex


@dataclass(kw_only=True)
class AddressBlock:
    offset: int
    size: int
    usage: EnumeratedTokenType
    protection: None | ProtectionStringType = None
    parsed: SVDAddressBlock


@dataclass(kw_only=True)
class Interrupt:
    name: str
    description: None | str = None
    value: int
    parsed: SVDInterrupt


@dataclass(kw_only=True)
class WriteConstraint:
    write_as_read: None | bool = None
    use_enumerated_values: None | bool = None
    range_: None | Tuple[int, int] = None
    parsed: SVDWriteConstraint


@dataclass(kw_only=True)
class EnumeratedValue:
    name: None | str = None
    header_enum_name: None | str = None
    usage: EnumUsageType = EnumUsageType.READ_WRITE
    enumerated_values_map: List[EnumeratedValueMap]
    derived_from: None | str = None
    parsed: SVDEnumeratedValue


@dataclass(kw_only=True)
class Field:
    name: str
    description: None | str = None
    lsb: int
    msb: int
    access: AccessType
    modified_write_values: ModifiedWriteValuesType = ModifiedWriteValuesType.MODIFY
    write_constraint: None | WriteConstraint = None
    read_action: None | ReadActionType = None
    enumerated_values: List[EnumeratedValue] = field(default_factory=list)
    parsed: SVDField


@dataclass(kw_only=True)
class Register:
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
    name: str
    display_name: None | str = None
    description: None | str = None
    alternate_group: None | str = None
    alternate_register: None | str = None
    address_offset: int
    data_type: None | DataTypeType = None
    modified_write_values: ModifiedWriteValuesType = ModifiedWriteValuesType.MODIFY
    write_constraint: None | WriteConstraint = None
    read_action: None | ReadActionType = None
    fields: List[Field] = field(default_factory=list)
    parsed: SVDRegister


@dataclass(kw_only=True)
class Cluster:
    size: None | int = None
    access: None | AccessType = None
    protection: None | ProtectionStringType = None
    reset_value: None | int = None
    reset_mask: None | int = None
    name: str
    description: None | str = None
    alternate_cluster: None | str = None
    header_struct_name: None | str = None
    address_offset: int
    registers_clusters: List[Union[Register, "Cluster"]] = field(default_factory=list)
    parsed: SVDCluster


@dataclass(kw_only=True)
class Peripheral:
    size: None | int = None
    access: None | AccessType = None
    protection: None | ProtectionStringType = None
    reset_value: None | int = None
    reset_mask: None | int = None
    name: str
    version: None | str = None
    description: None | str = None
    alternate_peripheral: None | str = None
    group_name: None | str = None
    prepend_to_name: None | str = None
    append_to_name: None | str = None
    header_struct_name: None | str = None
    disable_condition: None | str = None
    base_address: int
    address_blocks: List[AddressBlock] = field(default_factory=list)
    interrupts: List[Interrupt] = field(default_factory=list)
    registers_clusters: List[Register | Cluster] = field(default_factory=list)
    parsed: SVDPeripheral


@dataclass(kw_only=True)
class Device:
    size: None | int = None
    access: None | AccessType = None
    protection: None | ProtectionStringType = None
    reset_value: None | int = None
    reset_mask: None | int = None
    vendor: None | str = None
    vendor_id: None | str = None
    name: str
    series: None | str = None
    version: str
    description: str
    license_text: None | str = None
    cpu: None | CPU = None
    header_system_filename: None | str = None
    header_definitions_prefix: None | str = None
    address_unit_bits: int
    width: int
    peripherals: List[Peripheral] = field(default_factory=list)
    parsed: SVDDevice
