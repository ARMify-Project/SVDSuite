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


@dataclass
class SauRegion:
    enabled: bool
    name: None | str
    base: int
    limit: int
    access: SauAccessType
    parsed: SVDSauRegion


@dataclass
class SauRegionsConfig:
    enabled: bool
    protection_when_disabled: ProtectionStringType
    regions: list[SauRegion]
    parsed: SVDSauRegionsConfig


@dataclass
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


@dataclass
class EnumeratedValue:
    name: str
    description: None | str
    value: None | int
    is_default: bool
    parsed: SVDEnumeratedValue


@dataclass
class DimArrayIndex:
    header_enum_name: None | str
    enumerated_values: list[EnumeratedValue]
    parsed: SVDDimArrayIndex


@dataclass
class AddressBlock:
    offset: int
    size: int
    usage: EnumeratedTokenType
    protection: None | ProtectionStringType
    parsed: SVDAddressBlock


@dataclass
class Interrupt:
    name: str
    description: None | str
    value: int
    parsed: SVDInterrupt


@dataclass
class WriteConstraint:
    write_as_read: None | bool
    use_enumerated_values: None | bool
    range_: None | tuple[int, int]
    parsed: SVDWriteConstraint


@dataclass
class EnumeratedValueContainer:
    name: None | str
    header_enum_name: None | str
    usage: EnumUsageType
    enumerated_values: list[EnumeratedValue]
    parsed: SVDEnumeratedValueContainer


@dataclass
class FieldBase:
    name: str
    description: None | str
    lsb: int
    msb: int
    modified_write_values: ModifiedWriteValuesType
    write_constraint: None | WriteConstraint
    read_action: None | ReadActionType
    enumerated_value_containers: list[EnumeratedValueContainer]
    parsed: SVDField


@dataclass
class IField(FieldBase):
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    access: None | AccessType


@dataclass
class Field(FieldBase):
    access: AccessType
    bit_offset: int
    bit_width: int
    bit_range: tuple[int, int]


@dataclass
class RegisterBase:
    name: str
    display_name: None | str
    description: None | str
    alternate_group: None | str
    address_offset: int
    data_type: None | DataTypeType
    modified_write_values: ModifiedWriteValuesType
    write_constraint: None | WriteConstraint
    read_action: None | ReadActionType
    fields: list[IField]
    parsed: SVDRegister


@dataclass
class IRegister(RegisterBase):
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    size: None | int
    access: None | AccessType
    protection: None | ProtectionStringType
    reset_value: None | int
    reset_mask: None | int
    alternate_register: None | str


@dataclass
class Register(RegisterBase):
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
    alternate_register: "None | Register"
    base_address: int


@dataclass
class ClusterBase:
    name: str
    description: None | str
    header_struct_name: None | str
    address_offset: int
    parsed: SVDCluster


@dataclass
class ICluster(ClusterBase):
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    size: None | int
    access: None | AccessType
    protection: None | ProtectionStringType
    reset_value: None | int
    reset_mask: None | int
    alternate_cluster: None | str
    registers_clusters: list["IRegister | ICluster"]


@dataclass
class Cluster(ClusterBase):
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
    alternate_cluster: "None | Cluster"
    registers_clusters: list["Register | Cluster"]
    base_address: int
    end_address: int
    cluster_size: int


@dataclass
class PeripheralBase:
    name: str
    version: None | str
    description: None | str
    group_name: None | str
    prepend_to_name: None | str
    append_to_name: None | str
    header_struct_name: None | str
    disable_condition: None | str
    base_address: int
    address_blocks: list[AddressBlock]
    interrupts: list[Interrupt]
    parsed: SVDPeripheral


@dataclass
class IPeripheral(PeripheralBase):
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    size: None | int
    access: None | AccessType
    protection: None | ProtectionStringType
    reset_value: None | int
    reset_mask: None | int
    alternate_peripheral: None | str
    registers_clusters: list[IRegister | ICluster]


@dataclass
class Peripheral(PeripheralBase):
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
    alternate_peripheral: "None | Peripheral"
    end_address_specified: int  # calculated from address block(s) specification
    end_address_effective: int  # derived by summing the defined registers and clusters
    peripheral_size_specified: int  # calculated from address block(s) specification
    peripheral_size_effective: int  # derived by summing the defined registers and clusters
    registers_clusters: list[Register | Cluster]


@dataclass
class Device:
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
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
    peripherals: list[IPeripheral]
    parsed: SVDDevice
