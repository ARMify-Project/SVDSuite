from dataclasses import dataclass
from typing import Self
import copy

from svdsuite.parse import SVDParser
from svdsuite.svd_model import (
    SVDDevice,
    SVDCPU,
    SVDEnumeratedValue,
    SVDEnumeratedValueMap,
    SVDField,
    SVDPeripheral,
    SVDSauRegion,
    SVDSauRegionsConfig,
    SVDAddressBlock,
    SVDInterrupt,
    SVDRegister,
    SVDCluster,
    SVDWriteConstraint,
)
from svdsuite.process_model import (
    Device,
    CPU,
    EnumeratedValue,
    EnumeratedValueMap,
    Field,
    Peripheral,
    SauRegion,
    SauRegionsConfig,
    AddressBlock,
    Interrupt,
    Register,
    Cluster,
    WriteConstraint,
)
from svdsuite.types import CPUNameType, EnumUsageType, ModifiedWriteValuesType, ProtectionStringType, AccessType


@dataclass
class _RegisterPropertiesInheritance:
    size: None | int = None
    access: None | AccessType = None
    protection: None | ProtectionStringType = None
    reset_value: None | int = None
    reset_mask: None | int = None

    def get_obj(
        self,
        size: None | int,
        access: None | AccessType,
        protection: None | ProtectionStringType,
        reset_value: None | int,
        reset_mask: None | int,
    ) -> Self:
        attributes = {
            "size": size,
            "access": access,
            "protection": protection,
            "reset_value": reset_value,
            "reset_mask": reset_mask,
        }
        new_obj = None
        for attr, new_value in attributes.items():
            if new_value is not None and getattr(self, attr) != new_value:
                if new_obj is None:
                    new_obj = copy.deepcopy(self)
                setattr(new_obj, attr, new_value)
        return new_obj if new_obj is not None else self


class SVDProcessException(Exception):
    pass


class SVDProcess:
    @classmethod
    def for_xml_file(cls, path: str):
        return cls(SVDParser.for_xml_file(path))

    @classmethod
    def for_xml_str(cls, xml_str: str):
        return cls(SVDParser.for_xml_content(xml_str.encode()))

    @classmethod
    def for_xml_content(cls, content: bytes):
        return cls(SVDParser.for_xml_content(content))

    def __init__(self, parser: SVDParser) -> None:
        self._parser = parser

    def get_processed_device(self) -> Device:
        return self._process_device(self._parser.get_parsed_device())

    def _process_device(self, parsed_device: SVDDevice) -> Device:
        register_properties_inheritance = _RegisterPropertiesInheritance(
            size=parsed_device.size,
            access=parsed_device.access,
            protection=parsed_device.protection,
            reset_value=parsed_device.reset_value,
            reset_mask=parsed_device.reset_mask,
        )

        return Device(
            size=register_properties_inheritance.size,
            access=register_properties_inheritance.access,
            protection=register_properties_inheritance.protection,
            reset_value=register_properties_inheritance.reset_value,
            reset_mask=register_properties_inheritance.reset_mask,
            vendor=parsed_device.vendor,
            vendor_id=parsed_device.vendor_id,
            name=parsed_device.name,
            series=parsed_device.series,
            version=parsed_device.version,
            description=parsed_device.description,
            license_text=parsed_device.license_text,
            cpu=self._process_cpu(parsed_device.cpu),
            header_system_filename=parsed_device.header_system_filename,
            header_definitions_prefix=parsed_device.header_definitions_prefix,
            address_unit_bits=parsed_device.address_unit_bits,
            width=parsed_device.width,
            peripherals=self._process_peripherals(parsed_device.peripherals, register_properties_inheritance),
            parsed=parsed_device,
        )

    def _process_cpu(self, parsed_cpu: None | SVDCPU) -> None | CPU:
        if parsed_cpu is None:
            return None

        return CPU(
            name=CPUNameType.CM0PLUS if parsed_cpu.name == CPUNameType.CM0_PLUS else parsed_cpu.name,
            revision=parsed_cpu.revision,
            endian=parsed_cpu.endian,
            mpu_present=False if parsed_cpu.mpu_present is None else parsed_cpu.mpu_present,
            fpu_present=False if parsed_cpu.fpu_present is None else parsed_cpu.fpu_present,
            fpu_dp=False if parsed_cpu.fpu_dp is None else parsed_cpu.fpu_dp,
            dsp_present=False if parsed_cpu.dsp_present is None else parsed_cpu.dsp_present,
            icache_present=False if parsed_cpu.icache_present is None else parsed_cpu.icache_present,
            dcache_present=False if parsed_cpu.dcache_present is None else parsed_cpu.dcache_present,
            itcm_present=False if parsed_cpu.itcm_present is None else parsed_cpu.itcm_present,
            dtcm_present=False if parsed_cpu.dtcm_present is None else parsed_cpu.dtcm_present,
            vtor_present=True if parsed_cpu.vtor_present is None else parsed_cpu.vtor_present,
            nvic_prio_bits=parsed_cpu.nvic_prio_bits,
            vendor_systick_config=parsed_cpu.vendor_systick_config,
            device_num_interrupts=parsed_cpu.device_num_interrupts,
            sau_num_regions=parsed_cpu.sau_num_regions,
            sau_regions_config=self._process_sau_regions_config(parsed_cpu.sau_regions_config),
            parsed=parsed_cpu,
        )

    def _process_sau_regions_config(
        self, parsed_sau_regions_config: None | SVDSauRegionsConfig
    ) -> None | SauRegionsConfig:
        if parsed_sau_regions_config is None:
            return None

        return SauRegionsConfig(
            enabled=True if parsed_sau_regions_config.enabled is None else parsed_sau_regions_config.enabled,
            protection_when_disabled=(
                ProtectionStringType.SECURE
                if parsed_sau_regions_config.protection_when_disabled is None
                else parsed_sau_regions_config.protection_when_disabled
            ),
            regions=self._process_sau_regions(parsed_sau_regions_config.regions),
            parsed=parsed_sau_regions_config,
        )

    def _process_sau_regions(self, parsed_sau_regions: list[SVDSauRegion]) -> list[SauRegion]:
        regions: list[SauRegion] = []
        for parsed_region in parsed_sau_regions:
            regions.append(
                SauRegion(
                    enabled=True if parsed_region.enabled is None else parsed_region.enabled,
                    name=parsed_region.name,
                    base=parsed_region.base,
                    limit=parsed_region.limit,
                    access=parsed_region.access,
                    parsed=parsed_region,
                )
            )

        return regions

    def _process_peripherals(
        self, parsed_peripherals: list[SVDPeripheral], register_properties_inheritance: _RegisterPropertiesInheritance
    ) -> list[Peripheral]:
        peripherals: list[Peripheral] = []
        for parsed_peripheral in parsed_peripherals:
            peripheral = self._process_peripheral(parsed_peripheral, register_properties_inheritance)
            peripherals.append(peripheral)

        return peripherals

    def _process_peripheral(
        self, parsed_peripheral: SVDPeripheral, register_properties_inheritance: _RegisterPropertiesInheritance
    ) -> Peripheral:
        # TODO dim
        # TODO derived_from

        register_properties_inheritance = register_properties_inheritance.get_obj(
            parsed_peripheral.size,
            parsed_peripheral.access,
            parsed_peripheral.protection,
            parsed_peripheral.reset_value,
            parsed_peripheral.reset_mask,
        )

        return Peripheral(
            size=register_properties_inheritance.size,
            access=register_properties_inheritance.access,
            protection=register_properties_inheritance.protection,
            reset_value=register_properties_inheritance.reset_value,
            reset_mask=register_properties_inheritance.reset_mask,
            name=parsed_peripheral.name,
            version=parsed_peripheral.version,
            description=parsed_peripheral.description,
            alternate_peripheral=parsed_peripheral.alternate_peripheral,
            group_name=parsed_peripheral.group_name,
            prepend_to_name=parsed_peripheral.prepend_to_name,
            append_to_name=parsed_peripheral.append_to_name,
            header_struct_name=parsed_peripheral.header_struct_name,
            disable_condition=parsed_peripheral.disable_condition,
            base_address=parsed_peripheral.base_address,
            address_blocks=self._process_address_blocks(
                parsed_peripheral.address_blocks, register_properties_inheritance.protection
            ),
            interrupts=self._process_interrupts(parsed_peripheral.interrupts),
            registers_clusters=self._process_registers_clusters(
                parsed_peripheral.registers_clusters, register_properties_inheritance
            ),
            derived_from=parsed_peripheral.derived_from,
            parsed=parsed_peripheral,
        )

    def _process_address_blocks(
        self, parsed_address_blocks: list[SVDAddressBlock], peripheral_protection: None | ProtectionStringType
    ) -> list[AddressBlock]:
        address_blocks: list[AddressBlock] = []
        for parsed_address_block in parsed_address_blocks:
            address_blocks.append(
                AddressBlock(
                    offset=parsed_address_block.offset,
                    size=parsed_address_block.size,
                    usage=parsed_address_block.usage,
                    protection=(
                        parsed_address_block.protection
                        if parsed_address_block.protection is not None
                        else peripheral_protection
                    ),
                    parsed=parsed_address_block,
                )
            )

        return address_blocks

    def _process_interrupts(self, parsed_interrupts: list[SVDInterrupt]) -> list[Interrupt]:
        interrupts: list[Interrupt] = []
        for parsed_interrupt in parsed_interrupts:
            interrupts.append(
                Interrupt(
                    name=parsed_interrupt.name,
                    description=parsed_interrupt.description,
                    value=parsed_interrupt.value,
                    parsed=parsed_interrupt,
                )
            )

        return interrupts

    def _process_registers_clusters(
        self,
        parsed_registers_clusters: list[SVDRegister | SVDCluster],
        register_properties_inheritance: _RegisterPropertiesInheritance,
    ) -> list[Register | Cluster]:
        registers_clusters: list[Register | Cluster] = []
        for parsed_register_cluster in parsed_registers_clusters:
            if isinstance(parsed_register_cluster, SVDRegister):
                register = self._process_register(parsed_register_cluster, register_properties_inheritance)
                registers_clusters.append(register)

            if isinstance(parsed_register_cluster, SVDCluster):
                cluster = self._process_cluster(parsed_register_cluster, register_properties_inheritance)
                registers_clusters.append(cluster)

        return registers_clusters

    def _process_cluster(
        self, parsed_cluster: SVDCluster, register_properties_inheritance: _RegisterPropertiesInheritance
    ) -> Cluster:
        # TODO dim
        # TODO derived_from

        register_properties_inheritance = register_properties_inheritance.get_obj(
            parsed_cluster.size,
            parsed_cluster.access,
            parsed_cluster.protection,
            parsed_cluster.reset_value,
            parsed_cluster.reset_mask,
        )

        return Cluster(
            size=register_properties_inheritance.size,
            access=register_properties_inheritance.access,
            protection=register_properties_inheritance.protection,
            reset_value=register_properties_inheritance.reset_value,
            reset_mask=register_properties_inheritance.reset_mask,
            name=parsed_cluster.name,
            description=parsed_cluster.description,
            alternate_cluster=parsed_cluster.alternate_cluster,
            header_struct_name=parsed_cluster.header_struct_name,
            address_offset=parsed_cluster.address_offset,
            registers_clusters=self._process_registers_clusters(
                parsed_cluster.registers_clusters, register_properties_inheritance
            ),
            derived_from=parsed_cluster.derived_from,
            parsed=parsed_cluster,
        )

    def _process_register(
        self, parsed_register: SVDRegister, register_properties_inheritance: _RegisterPropertiesInheritance
    ) -> Register:
        # TODO dim
        # TODO derived_from

        register_properties_inheritance = register_properties_inheritance.get_obj(
            parsed_register.size,
            parsed_register.access,
            parsed_register.protection,
            parsed_register.reset_value,
            parsed_register.reset_mask,
        )

        if register_properties_inheritance.size is None:
            raise SVDProcessException("size can't be none at register level")

        if register_properties_inheritance.access is None:
            raise SVDProcessException("access can't be none at register level")

        if register_properties_inheritance.protection is None:
            raise SVDProcessException("protection can't be none at register level")

        if register_properties_inheritance.reset_value is None:
            raise SVDProcessException("reset_value can't be none at register level")

        if register_properties_inheritance.reset_mask is None:
            raise SVDProcessException("reset_mask can't be none at register level")

        return Register(
            size=register_properties_inheritance.size,
            access=register_properties_inheritance.access,
            protection=register_properties_inheritance.protection,
            reset_value=register_properties_inheritance.reset_value,
            reset_mask=register_properties_inheritance.reset_mask,
            name=parsed_register.name,
            display_name=parsed_register.display_name,
            description=parsed_register.description,
            alternate_group=parsed_register.alternate_group,
            alternate_register=parsed_register.alternate_register,
            address_offset=parsed_register.address_offset,
            data_type=parsed_register.data_type,
            modified_write_values=(
                parsed_register.modified_write_values
                if parsed_register.modified_write_values is not None
                else ModifiedWriteValuesType.MODIFY
            ),
            write_constraint=self._process_write_constraint(parsed_register.write_constraint),
            read_action=parsed_register.read_action,
            fields=self._process_fields(parsed_register.fields, register_properties_inheritance.access),
            derived_from=parsed_register.derived_from,
            parsed=parsed_register,
        )

    def _process_write_constraint(self, write_constraint: None | SVDWriteConstraint) -> None | WriteConstraint:
        if write_constraint is None:
            return None

        return WriteConstraint(
            write_as_read=write_constraint.write_as_read,
            use_enumerated_values=write_constraint.use_enumerated_values,
            range_=write_constraint.range_,
            parsed=write_constraint,
        )

    def _process_fields(self, parsed_fields: list[SVDField], register_access: AccessType) -> list[Field]:
        # TODO dim
        # TODO derived_from

        fields: list[Field] = []
        for parsed_field in parsed_fields:
            fields.append(
                Field(
                    name=parsed_field.name,
                    description=parsed_field.description,
                    bit_offset=parsed_field.bit_offset,
                    bit_width=parsed_field.bit_width,
                    lsb=parsed_field.lsb,
                    msb=parsed_field.msb,
                    bit_range=parsed_field.bit_range,
                    access=parsed_field.access if parsed_field.access is not None else register_access,
                    modified_write_values=(
                        parsed_field.modified_write_values
                        if parsed_field.modified_write_values is not None
                        else ModifiedWriteValuesType.MODIFY
                    ),
                    write_constraint=self._process_write_constraint(parsed_field.write_constraint),
                    read_action=parsed_field.read_action,
                    enumerated_values=self._process_enumerated_values(parsed_field.enumerated_values),
                    derived_from=parsed_field.derived_from,
                    parsed=parsed_field,
                )
            )

        return fields

    def _process_enumerated_values(self, parsed_enumerated_values: list[SVDEnumeratedValue]) -> list[EnumeratedValue]:
        # TODO derived_from

        enumerated_values: list[EnumeratedValue] = []
        for parsed_enumerated_value in parsed_enumerated_values:
            enumerated_values.append(
                EnumeratedValue(
                    name=parsed_enumerated_value.name,
                    header_enum_name=parsed_enumerated_value.header_enum_name,
                    usage=(
                        parsed_enumerated_value.usage
                        if parsed_enumerated_value.usage is not None
                        else EnumUsageType.READ_WRITE
                    ),
                    enumerated_values_map=self._process_enumerated_values_map(
                        parsed_enumerated_value.enumerated_values_map
                    ),
                    derived_from=parsed_enumerated_value.derived_from,
                    parsed=parsed_enumerated_value,
                )
            )

        return enumerated_values

    def _process_enumerated_values_map(
        self, parsed_enumerated_values_map: list[SVDEnumeratedValueMap]
    ) -> list[EnumeratedValueMap]:
        enumerated_values_map: list[EnumeratedValueMap] = []
        for parsed_enumerated_value in parsed_enumerated_values_map:
            enumerated_values_map.append(
                EnumeratedValueMap(
                    name=parsed_enumerated_value.name,
                    description=parsed_enumerated_value.description,
                    value=parsed_enumerated_value.value,
                    is_default=parsed_enumerated_value.is_default,
                    parsed=parsed_enumerated_value,
                )
            )

        return enumerated_values_map
