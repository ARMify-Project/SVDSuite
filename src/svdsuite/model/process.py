from dataclasses import dataclass, fields as dataclass_fields

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


def reg_prop_validator(
    size: None | int,
    access: None | AccessType,
    protection: None | ProtectionStringType,
    reset_value: None | int,
    reset_mask: None | int,
) -> tuple[int, AccessType, ProtectionStringType, int, int]:
    if size is None or access is None or protection is None or reset_value is None or reset_mask is None:
        raise ValueError("size, access, protection, reset_value, and reset_mask must be specified")

    return size, access, protection, reset_value, reset_mask


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

    @classmethod
    def from_intermediate_field(cls, i_field: IField) -> "Field":
        base_kwargs = {field.name: getattr(i_field, field.name) for field in dataclass_fields(FieldBase)}

        if i_field.access is None:
            raise ValueError("access must be specified")

        return cls(
            **base_kwargs,
            access=i_field.access,
            bit_offset=i_field.lsb,
            bit_width=i_field.msb - i_field.lsb + 1,
            bit_range=(i_field.msb, i_field.lsb),
        )


@dataclass
class RegisterBase:
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
    fields: list[IField]


@dataclass
class Register(RegisterBase):
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
    fields: list[Field]
    base_address: int

    @classmethod
    def from_intermediate_register(
        cls,
        i_register: IRegister,
        fields: list[Field],
        base_address: int,
    ) -> "Register":
        base_kwargs = {field.name: getattr(i_register, field.name) for field in dataclass_fields(RegisterBase)}

        size, access, protection, reset_value, reset_mask = reg_prop_validator(
            i_register.size,
            i_register.access,
            i_register.protection,
            i_register.reset_value,
            i_register.reset_mask,
        )

        return cls(
            **base_kwargs,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            fields=fields,
            base_address=base_address,
        )


@dataclass
class ClusterBase:
    name: str
    description: None | str
    alternate_cluster: None | str
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
    registers_clusters: list["IRegister | ICluster"]


@dataclass
class Cluster(ClusterBase):
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
    registers_clusters: list["Register | Cluster"]
    base_address: int
    end_address: int
    cluster_size: int

    @classmethod
    def from_intermediate_cluster(
        cls,
        i_cluster: ICluster,
        registers_clusters: list["Register | Cluster"],
        base_address: int,
        end_address: int,
        cluster_size: int,
    ) -> "Cluster":
        base_kwargs = {field.name: getattr(i_cluster, field.name) for field in dataclass_fields(ClusterBase)}

        size, access, protection, reset_value, reset_mask = reg_prop_validator(
            i_cluster.size,
            i_cluster.access,
            i_cluster.protection,
            i_cluster.reset_value,
            i_cluster.reset_mask,
        )

        return cls(
            **base_kwargs,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            registers_clusters=registers_clusters,
            base_address=base_address,
            end_address=end_address,
            cluster_size=cluster_size,
        )


@dataclass
class PeripheralBase:
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
    registers_clusters: list[IRegister | ICluster]


@dataclass
class Peripheral(PeripheralBase):
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
    end_address_specified: int  # calculated from address block(s) specification
    end_address_effective: int  # derived by summing the defined registers and clusters
    peripheral_size_specified: int  # calculated from address block(s) specification
    peripheral_size_effective: int  # derived by summing the defined registers and clusters
    registers_clusters: list[Register | Cluster]

    @classmethod
    def from_intermediate_peripheral(
        cls,
        i_peripheral: IPeripheral,
        end_address_specified: int,
        end_address_effective: int,
        peripheral_size_specified: int,
        peripheral_size_effective: int,
        registers_clusters: list[Register | Cluster],
    ) -> "Peripheral":
        base_kwargs = {field.name: getattr(i_peripheral, field.name) for field in dataclass_fields(PeripheralBase)}

        size, access, protection, reset_value, reset_mask = reg_prop_validator(
            i_peripheral.size,
            i_peripheral.access,
            i_peripheral.protection,
            i_peripheral.reset_value,
            i_peripheral.reset_mask,
        )

        return cls(
            **base_kwargs,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            end_address_specified=end_address_specified,
            end_address_effective=end_address_effective,
            peripheral_size_specified=peripheral_size_specified,
            peripheral_size_effective=peripheral_size_effective,
            registers_clusters=registers_clusters,
        )


@dataclass
class DeviceBase:
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
    parsed: SVDDevice


@dataclass
class IDevice(DeviceBase):
    peripherals: list[IPeripheral]


@dataclass
class Device(DeviceBase):
    peripherals: list[Peripheral]

    @classmethod
    def from_intermediate_device(cls, i_device: IDevice, peripherals: list[Peripheral]) -> "Device":
        base_kwargs = {field.name: getattr(i_device, field.name) for field in dataclass_fields(DeviceBase)}

        return cls(**base_kwargs, peripherals=peripherals)
