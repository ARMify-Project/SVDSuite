from dataclasses import dataclass, field

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


@dataclass(kw_only=True)
class SVDSauRegion:
    enabled: None | bool = None
    name: None | str = None
    base: int
    limit: int
    access: SauAccessType
    parent: "None | SVDSauRegionsConfig" = None


@dataclass(kw_only=True)
class SVDSauRegionsConfig:
    enabled: None | bool = None
    protection_when_disabled: None | ProtectionStringType = None
    regions: list[SVDSauRegion] = field(default_factory=list)
    parent: "None | SVDCPU" = None


@dataclass(kw_only=True)
class SVDCPU:
    name: CPUNameType
    revision: str
    endian: EndianType
    mpu_present: None | bool = None
    fpu_present: None | bool = None
    fpu_dp: None | bool = None
    dsp_present: None | bool = None
    icache_present: None | bool = None
    dcache_present: None | bool = None
    itcm_present: None | bool = None
    dtcm_present: None | bool = None
    vtor_present: None | bool = None
    nvic_prio_bits: int
    vendor_systick_config: bool
    device_num_interrupts: None | int = None
    sau_num_regions: None | int = None
    sau_regions_config: None | SVDSauRegionsConfig = None
    parent: "None | SVDDevice" = None


@dataclass(kw_only=True)
class SVDEnumeratedValue:
    name: str
    description: None | str = None
    value: None | str = None  # int value, but can contain 'do not care' bits represented by >x<
    is_default: None | bool = None
    parent: "None | SVDEnumeratedValueContainer | SVDDimArrayIndex" = None


@dataclass(kw_only=True)
class SVDDimArrayIndex:
    header_enum_name: None | str = None
    enumerated_values: list[SVDEnumeratedValue]
    parent: "None | SVDPeripheral | SVDCluster | SVDRegister | SVDField" = None


@dataclass(kw_only=True)
class _SVDDimElementGroup:
    dim: None | int = None
    dim_increment: None | int = None
    dim_index: None | str = None
    dim_name: None | str = None
    dim_array_index: None | SVDDimArrayIndex = None


@dataclass(kw_only=True)
class _SVDRegisterPropertiesGroup:
    size: None | int = None
    access: None | AccessType = None
    protection: None | ProtectionStringType = None
    reset_value: None | int = None
    reset_mask: None | int = None


@dataclass(kw_only=True)
class SVDAddressBlock:
    offset: int
    size: int
    usage: EnumeratedTokenType
    protection: None | ProtectionStringType = None
    parent: "None | SVDPeripheral" = None


@dataclass(kw_only=True)
class SVDInterrupt:
    name: str
    description: None | str = None
    value: int
    parent: "None | SVDPeripheral" = None


@dataclass(kw_only=True)
class SVDWriteConstraint:
    write_as_read: None | bool = None
    use_enumerated_values: None | bool = None
    range_: None | tuple[int, int] = None
    parent: "None | SVDField | SVDRegister" = None


@dataclass(kw_only=True)
class SVDEnumeratedValueContainer:
    name: None | str = None
    header_enum_name: None | str = None
    usage: None | EnumUsageType = None
    enumerated_values: list[SVDEnumeratedValue]
    derived_from: None | str = None
    parent: "None | SVDField" = None


@dataclass(kw_only=True)
class SVDField(_SVDDimElementGroup):
    name: str
    description: None | str = None
    bit_offset: None | int = None
    bit_width: None | int = None
    lsb: None | int = None
    msb: None | int = None
    bit_range: None | str = None
    access: None | AccessType = None
    modified_write_values: None | ModifiedWriteValuesType = None
    write_constraint: None | SVDWriteConstraint = None
    read_action: None | ReadActionType = None
    enumerated_value_containers: list[SVDEnumeratedValueContainer] = field(default_factory=list)
    derived_from: None | str = None
    parent: "None | SVDRegister" = None


@dataclass(kw_only=True)
class SVDRegister(_SVDDimElementGroup, _SVDRegisterPropertiesGroup):
    name: str
    display_name: None | str = None
    description: None | str = None
    alternate_group: None | str = None
    alternate_register: None | str = None
    address_offset: int
    data_type: None | DataTypeType = None
    modified_write_values: None | ModifiedWriteValuesType = None
    write_constraint: None | SVDWriteConstraint = None
    read_action: None | ReadActionType = None
    fields: list[SVDField] = field(default_factory=list)
    derived_from: None | str = None
    parent: "None | SVDCluster  | SVDPeripheral" = None


@dataclass(kw_only=True)
class SVDCluster(_SVDDimElementGroup, _SVDRegisterPropertiesGroup):
    name: str
    description: None | str = None
    alternate_cluster: None | str = None
    header_struct_name: None | str = None
    address_offset: int
    registers_clusters: list["SVDRegister | SVDCluster"] = field(default_factory=list)
    derived_from: None | str = None
    parent: "None | SVDCluster | SVDPeripheral" = None


@dataclass(kw_only=True)
class SVDPeripheral(_SVDDimElementGroup, _SVDRegisterPropertiesGroup):
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
    address_blocks: list[SVDAddressBlock] = field(default_factory=list)
    interrupts: list[SVDInterrupt] = field(default_factory=list)
    registers_clusters: list[SVDRegister | SVDCluster] = field(default_factory=list)
    derived_from: None | str = None
    parent: "None | SVDDevice" = None


@dataclass(kw_only=True)
class SVDDevice(_SVDRegisterPropertiesGroup):
    xs_no_namespace_schema_location: str
    schema_version: str
    vendor: None | str = None
    vendor_id: None | str = None
    name: str
    series: None | str = None
    version: str
    description: str
    license_text: None | str = None
    cpu: None | SVDCPU = None
    header_system_filename: None | str = None
    header_definitions_prefix: None | str = None
    address_unit_bits: int
    width: int
    peripherals: list[SVDPeripheral] = field(default_factory=list)
