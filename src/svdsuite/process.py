import re
import itertools
import warnings

from svdsuite.parse import Parser
from svdsuite.model.parse import (
    SVDDevice,
    SVDCPU,
    SVDSauRegionsConfig,
    SVDSauRegion,
    SVDPeripheral,
    SVDCluster,
    SVDRegister,
    SVDField,
    SVDAddressBlock,
    SVDInterrupt,
    SVDWriteConstraint,
    SVDEnumeratedValueContainer,
    SVDEnumeratedValue,
)
from svdsuite.model.process import (
    IDevice,
    Device,
    CPU,
    SauRegionsConfig,
    SauRegion,
    IPeripheral,
    Peripheral,
    ICluster,
    Cluster,
    IRegister,
    Register,
    IField,
    Field,
    AddressBlock,
    Interrupt,
    WriteConstraint,
    IEnumeratedValueContainer,
    EnumeratedValueContainer,
    IEnumeratedValue,
    EnumeratedValue,
)
from svdsuite.util.process_parse_model_convert import process_parse_convert_device
from svdsuite.model.types import AccessType, ProtectionStringType, CPUNameType, ModifiedWriteValuesType, EnumUsageType
from svdsuite.resolve.resolver import Resolver
from svdsuite.resolve.exception import (
    EnumeratedValueContainerException,
    LoopException,
    CycleException,
    UnprocessedNodesException,
)
from svdsuite.model.type_alias import ParsedDimablePeripheralTypes, IntermediateDimablePeripheralTypes


def or_if_none[T](a: None | T, b: None | T) -> None | T:
    return a if a is not None else b


class ProcessException(Exception):
    pass


class ProcessWarning(Warning):
    pass


class Process:
    @classmethod
    def from_svd_file(cls, path: str, resolver_logging_file_path: None | str = None):
        return cls(Parser.from_svd_file(path).get_parsed_device(), resolver_logging_file_path)

    @classmethod
    def from_xml_str(cls, xml_str: str, resolver_logging_file_path: None | str = None):
        return cls(Parser.from_xml_content(xml_str.encode()).get_parsed_device(), resolver_logging_file_path)

    @classmethod
    def from_xml_content(cls, content: bytes, resolver_logging_file_path: None | str = None):
        return cls(Parser.from_xml_content(content).get_parsed_device(), resolver_logging_file_path)

    def __init__(self, parsed_device: SVDDevice, resolver_logging_file_path: None | str) -> None:
        self._resolver = Resolver(self, resolver_logging_file_path)
        self._processed_device: Device = self._process_device(parsed_device)

    def get_processed_device(self) -> Device:
        return self._processed_device

    def convert_processed_device_to_svd_device(self) -> SVDDevice:
        return process_parse_convert_device(self._processed_device)

    def _process_device(self, parsed_device: SVDDevice) -> Device:
        size = parsed_device.size if parsed_device.size is not None else 32
        access = parsed_device.access if parsed_device.access is not None else AccessType.READ_WRITE
        protection = parsed_device.protection if parsed_device.protection is not None else ProtectionStringType.ANY
        reset_value = parsed_device.reset_value if parsed_device.reset_value is not None else 0
        reset_mask = parsed_device.reset_mask if parsed_device.reset_mask is not None else 0xFFFFFFFF

        try:
            peripherals = self._resolver.resolve_peripherals(parsed_device)
        except EnumeratedValueContainerException as e:
            raise ProcessException("Exception within enumerated value container processing") from e
        except LoopException as e:
            raise ProcessException("Resolving stucks in a loop") from e
        except CycleException as e:
            raise ProcessException("A circular inheritance was detected during resolving") from e
        except UnprocessedNodesException as e:
            raise ProcessException("Some nodes were not processed during resolving") from e

        intermediate_device = IDevice(
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
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
            peripherals=peripherals,
            parsed=parsed_device,
        )

        _InheritProperties().inherit_properties(intermediate_device)

        device = _ValidateAndFinalize().validate_and_finalize(intermediate_device)

        return device

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

    def _process_peripheral(
        self, index: int, name: str, parsed: SVDPeripheral, base: None | IPeripheral
    ) -> IPeripheral:
        dim = or_if_none(parsed.dim, base.dim if base else None)
        dim_index = or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        size = or_if_none(parsed.size, base.size if base else None)
        access = or_if_none(parsed.access, base.access if base else None)
        protection = or_if_none(parsed.protection, base.protection if base else None)
        reset_value = or_if_none(parsed.reset_value, base.reset_value if base else None)
        reset_mask = or_if_none(parsed.reset_mask, base.reset_mask if base else None)

        version = or_if_none(parsed.version, base.version if base else None)
        description = or_if_none(parsed.description, base.description if base else None)
        alternate_peripheral = or_if_none(parsed.alternate_peripheral, base.alternate_peripheral if base else None)
        group_name = or_if_none(parsed.group_name, base.group_name if base else None)
        prepend_to_name = or_if_none(parsed.prepend_to_name, base.prepend_to_name if base else None)
        append_to_name = or_if_none(parsed.append_to_name, base.append_to_name if base else None)
        header_struct_name = parsed.header_struct_name  # not inherited in svdconv
        disable_condition = or_if_none(parsed.disable_condition, base.disable_condition if base else None)
        base_address = parsed.base_address if dim_increment is None else parsed.base_address + dim_increment * index
        address_blocks = self._process_address_blocks(parsed.address_blocks) or (base.address_blocks if base else [])
        interrupts = self._process_interrupts(parsed.interrupts)

        return IPeripheral(
            dim=dim,
            dim_index=dim_index,
            dim_increment=dim_increment,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
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
            address_blocks=address_blocks,
            interrupts=interrupts,
            registers_clusters=[],
            parsed=parsed,
        )

    def _process_cluster(self, index: int, name: str, parsed: SVDCluster, base: None | ICluster) -> ICluster:
        dim = or_if_none(parsed.dim, base.dim if base else None)
        dim_index = or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        size = or_if_none(parsed.size, base.size if base else None)
        access = or_if_none(parsed.access, base.access if base else None)
        protection = or_if_none(parsed.protection, base.protection if base else None)
        reset_value = or_if_none(parsed.reset_value, base.reset_value if base else None)
        reset_mask = or_if_none(parsed.reset_mask, base.reset_mask if base else None)

        description = or_if_none(parsed.description, base.description if base else None)
        alternate_cluster = or_if_none(parsed.alternate_cluster, base.alternate_cluster if base else None)
        header_struct_name = or_if_none(parsed.header_struct_name, base.header_struct_name if base else None)
        address_offset = (
            parsed.address_offset if dim_increment is None else parsed.address_offset + dim_increment * index
        )

        return ICluster(
            dim=dim,
            dim_index=dim_index,
            dim_increment=dim_increment,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            name=name,
            description=description,
            alternate_cluster=alternate_cluster,
            header_struct_name=header_struct_name,
            address_offset=address_offset,
            registers_clusters=[],
            parsed=parsed,
        )

    def _process_register(
        self, index: int, name: str, display_name: None | str, parsed: SVDRegister, base: None | IRegister
    ) -> IRegister:
        dim = or_if_none(parsed.dim, base.dim if base else None)
        dim_index = or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        size = or_if_none(parsed.size, base.size if base else None)
        access = or_if_none(parsed.access, base.access if base else None)
        protection = or_if_none(parsed.protection, base.protection if base else None)
        reset_value = or_if_none(parsed.reset_value, base.reset_value if base else None)
        reset_mask = or_if_none(parsed.reset_mask, base.reset_mask if base else None)

        description = or_if_none(parsed.description, base.description if base else None)
        alternate_group = or_if_none(parsed.alternate_group, base.alternate_group if base else None)
        alternate_register = or_if_none(parsed.alternate_register, base.alternate_register if base else None)
        address_offset = (
            parsed.address_offset if dim_increment is None else parsed.address_offset + dim_increment * index
        )
        data_type = or_if_none(parsed.data_type, base.data_type if base else None)
        modified_write_values = (
            parsed.modified_write_values
            if parsed.modified_write_values is not None
            else (base.modified_write_values if base is not None else ModifiedWriteValuesType.MODIFY)
        )
        write_constraint = or_if_none(
            self._process_write_constraint(parsed.write_constraint), base.write_constraint if base else None
        )
        read_action = or_if_none(parsed.read_action, base.read_action if base else None)

        if display_name is not None and "[%s]" in display_name:
            display_name = display_name.replace("[%s]", str(index))

        return IRegister(
            dim=dim,
            dim_index=dim_index,
            dim_increment=dim_increment,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            name=name,
            display_name=display_name,
            description=description,
            alternate_group=alternate_group,
            alternate_register=alternate_register,
            address_offset=address_offset,
            data_type=data_type,
            modified_write_values=modified_write_values,
            write_constraint=write_constraint,
            read_action=read_action,
            fields=[],
            parsed=parsed,
        )

    def _process_field(self, index: int, name: str, parsed: SVDField, base: None | IField) -> IField:
        dim = or_if_none(parsed.dim, base.dim if base else None)
        dim_index = or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        access = or_if_none(parsed.access, base.access if base else None)

        description = or_if_none(parsed.description, base.description if base else None)
        lsb, msb = self._process_field_msb_lsb_with_increment(parsed, dim_increment, index, base)
        modified_write_values = (
            parsed.modified_write_values
            if parsed.modified_write_values is not None
            else (base.modified_write_values if base is not None else ModifiedWriteValuesType.MODIFY)
        )
        write_constraint = or_if_none(
            self._process_write_constraint(parsed.write_constraint), base.write_constraint if base else None
        )
        read_action = or_if_none(parsed.read_action, base.read_action if base else None)

        return IField(
            dim=dim,
            dim_index=dim_index,
            dim_increment=dim_increment,
            access=access,
            name=name,
            description=description,
            lsb=lsb,
            msb=msb,
            modified_write_values=modified_write_values,
            write_constraint=write_constraint,
            read_action=read_action,
            enumerated_value_containers=[],
            parsed=parsed,
        )

    def _process_address_blocks(self, parsed_address_blocks: list[SVDAddressBlock]) -> list[AddressBlock]:
        address_blocks: list[AddressBlock] = []
        for parsed_address_block in parsed_address_blocks:
            address_blocks.append(
                AddressBlock(
                    offset=parsed_address_block.offset,
                    size=parsed_address_block.size,
                    usage=parsed_address_block.usage,
                    protection=parsed_address_block.protection or ProtectionStringType.ANY,
                    parsed=parsed_address_block,
                )
            )

        return sorted(address_blocks, key=lambda ab: ab.offset)

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

        return sorted(interrupts, key=lambda i: i.value)

    def _process_write_constraint(self, parsed_write_constraint: None | SVDWriteConstraint) -> None | WriteConstraint:
        if parsed_write_constraint is None:
            return None

        return WriteConstraint(
            write_as_read=parsed_write_constraint.write_as_read,
            use_enumerated_values=parsed_write_constraint.use_enumerated_values,
            range_=parsed_write_constraint.range_,
            parsed=parsed_write_constraint,
        )

    def _process_field_msb_lsb_with_increment(
        self, parsed_field: SVDField, dim_increment: None | int, index: int, base: None | IField
    ) -> tuple[int, int]:
        field_msb, field_lsb = self._process_field_msb_lsb(parsed_field, base)
        lsb = field_lsb if dim_increment is None else field_lsb + dim_increment * index
        msb = field_msb if dim_increment is None else field_msb + dim_increment * index
        return lsb, msb

    def _process_field_msb_lsb(self, parsed_field: SVDField, base: None | IField) -> tuple[int, int]:
        bit_offset = or_if_none(parsed_field.bit_offset, base.lsb if base else None)
        bit_width = or_if_none(parsed_field.bit_width, base.msb - base.lsb + 1 if base else None)
        lsb = or_if_none(parsed_field.lsb, base.lsb if base else None)
        msb = or_if_none(parsed_field.msb, base.msb if base else None)
        bit_range = or_if_none(parsed_field.bit_range, f"{base.msb}:{base.lsb}" if base else None)

        field_lsb = None
        field_msb = None

        if parsed_field.bit_offset is not None or parsed_field.bit_width is not None:
            if bit_offset is not None and bit_width is not None:
                field_lsb = bit_offset
                field_msb = bit_offset + bit_width - 1

        if parsed_field.lsb is not None or parsed_field.msb is not None:
            if lsb is not None and msb is not None:
                field_lsb = lsb
                field_msb = msb

        if parsed_field.bit_range is not None:
            if bit_range is not None:
                match = re.match(r"\[(\d+):(\d+)\]", bit_range)
                if match:
                    field_msb, field_lsb = map(int, match.groups())

                    if field_msb < field_lsb:
                        warnings.warn(
                            f"BitRange '{bit_range}' has a smaller MSB than LSB. "
                            f"Switching bitRange to [{field_lsb}:{field_msb}]",
                            ProcessWarning,
                        )
                        field_msb, field_lsb = field_lsb, field_msb
                else:
                    raise ProcessException(f"Invalid bit range format: {parsed_field.bit_range}")

        if field_lsb is None or field_msb is None:
            raise ProcessException("Field must have bit_offset and bit_width, lsb and msb, or bit_range")

        if field_msb < field_lsb:
            warnings.warn(
                f"Field with name '{parsed_field.name}': MSB '{field_msb}' is smaller than LSB '{field_lsb}'",
                ProcessWarning,
            )

        return (field_msb, field_lsb)

    def _process_enumerated_value_container(
        self, parsed_enum_container: SVDEnumeratedValueContainer, lsb: int, msb: int
    ) -> IEnumeratedValueContainer:
        return _ProcessEnumeratedValueContainer().create_enumerated_value_container(parsed_enum_container, lsb, msb)

    def _extract_and_process_dimension(
        self, parsed_element: ParsedDimablePeripheralTypes, base_element: None | IntermediateDimablePeripheralTypes
    ) -> tuple[bool, list[str], list[None | str]]:
        dim = or_if_none(parsed_element.dim, base_element.dim if base_element else None)
        dim_index = or_if_none(parsed_element.dim_index, base_element.dim_index if base_element else None)

        display_name = None
        if isinstance(parsed_element, SVDRegister):
            if isinstance(base_element, IRegister):
                display_name = or_if_none(
                    parsed_element.display_name, base_element.display_name if base_element else None
                )
            else:
                display_name = parsed_element.display_name
        else:
            display_name = None

        if dim is None and "%s" in parsed_element.name:
            raise ProcessException(f"Dim is None, but name '{parsed_element.name}' contains '%s'")

        if dim is not None and "%s" not in parsed_element.name:
            warnings.warn(
                f"Dim is not None, but name '{parsed_element.name}' does not contain '%s'. Setting dim to None",
                ProcessWarning,
            )
            dim = None

        if display_name is not None and dim is None and "%s" in display_name:
            raise ProcessException(f"Dim is None, but display_name '{display_name}' contains '%s'")

        return dim is not None, *_ProcessDimension().process_dim(
            parsed_element.name, display_name, dim, dim_index, type(parsed_element)
        )


class _InheritProperties:
    def inherit_properties(self, device: IDevice):
        for peripheral in device.peripherals:
            peripheral.size = or_if_none(peripheral.size, device.size)
            peripheral.access = or_if_none(peripheral.access, device.access)
            peripheral.protection = or_if_none(peripheral.protection, device.protection)
            peripheral.reset_value = or_if_none(peripheral.reset_value, device.reset_value)
            peripheral.reset_mask = or_if_none(peripheral.reset_mask, device.reset_mask)

            self._inherit_properties_registers_clusters(
                peripheral.registers_clusters,
                peripheral.size,
                peripheral.access,
                peripheral.protection,
                peripheral.reset_value,
                peripheral.reset_mask,
            )

    def _inherit_properties_registers_clusters(
        self,
        registers_clusters: list[ICluster | IRegister],
        size: None | int,
        access: None | AccessType,
        protection: None | ProtectionStringType,
        reset_value: None | int,
        reset_mask: None | int,
    ):
        for register_cluster in registers_clusters:
            register_cluster.size = or_if_none(register_cluster.size, size)
            register_cluster.access = or_if_none(register_cluster.access, access)
            register_cluster.protection = or_if_none(register_cluster.protection, protection)
            register_cluster.reset_value = or_if_none(register_cluster.reset_value, reset_value)
            register_cluster.reset_mask = or_if_none(register_cluster.reset_mask, reset_mask)

            if isinstance(register_cluster, ICluster):
                self._inherit_properties_registers_clusters(
                    register_cluster.registers_clusters,
                    register_cluster.size,
                    register_cluster.access,
                    register_cluster.protection,
                    register_cluster.reset_value,
                    register_cluster.reset_mask,
                )
            elif isinstance(register_cluster, IRegister):  # pyright: ignore[reportUnnecessaryIsInstance]
                self._inherit_properties_fields(
                    register_cluster.fields,
                    register_cluster.access,
                    register_cluster.write_constraint,
                )
            else:
                raise ProcessException("Unknown register cluster type")

    def _inherit_properties_fields(
        self, fields: list[IField], access: None | AccessType, write_constraint: None | WriteConstraint
    ):
        for field in fields:
            field.access = or_if_none(field.access, access)
            field.write_constraint = or_if_none(field.write_constraint, write_constraint)


def _to_byte(value: int) -> int:
    if value % 8 != 0:
        raise ProcessException("Value must be a multiple of 8")

    return value // 8


def _get_alignment(size_bytes: int) -> int:
    if size_bytes == 1:
        return 1
    elif size_bytes == 2:
        return 2
    elif size_bytes == 4:
        return 4
    elif size_bytes == 8:
        return 4
    elif size_bytes == 16:
        return 4
    else:
        raise ProcessException(f"Unsupported register size: {size_bytes} bytes")


class _ValidateAndFinalize:
    def validate_and_finalize(self, i_device: IDevice) -> Device:
        # Finalize the device by processing its peripherals.
        peripherals = self._validate_and_finalize_peripherals(i_device.peripherals)
        return Device.from_intermediate_device(i_device, peripherals)

    def _validate_and_finalize_peripherals(self, i_peripherals: list[IPeripheral]) -> list[Peripheral]:
        peripheral_lookup: dict[str, Peripheral] = {}
        finalized_peripherals: list[Peripheral] = []
        for i_peripheral in i_peripherals:
            peripheral = self._validate_and_finalize_peripheral(i_peripheral)
            if peripheral:
                if peripheral.name in peripheral_lookup:
                    raise ProcessException(f"Duplicate peripheral name found: {peripheral.name}")
                peripheral_lookup[peripheral.name] = peripheral

                finalized_peripherals.append(peripheral)

        finalized_peripherals.sort(key=lambda p: (p.base_address, p.name))
        self._check_peripheral_address_overlaps(finalized_peripherals, peripheral_lookup)

        return finalized_peripherals

    def _validate_and_finalize_peripheral(self, i_peripheral: IPeripheral) -> None | Peripheral:
        # Finalize registers/clusters.
        registers_clusters = self._validate_and_finalize_registers_clusters(
            i_peripheral.registers_clusters, i_peripheral.base_address
        )
        if not registers_clusters:
            warnings.warn(
                f"Peripheral '{i_peripheral.name}' has no registers or clusters. Peripheral will be ignored!",
                ProcessWarning,
            )
            return None

        # Warn if base address is not 4-byte aligned.
        if i_peripheral.base_address % 4 != 0:
            warnings.warn(
                f"Peripheral '{i_peripheral.name}' base address is not 4 byte aligned",
                ProcessWarning,
            )

        # Check if specified size is a multiple of 8.
        if i_peripheral.size is not None and i_peripheral.size % 8 != 0:
            warnings.warn(
                f"Peripheral '{i_peripheral.name}' size must be a multiple of 8. Peripheral will be ignored!",
                ProcessWarning,
            )
            return None

        # Ensure address blocks are provided.
        if not i_peripheral.address_blocks:
            raise ProcessException(f"Peripheral '{i_peripheral.name}' has no address blocks")

        # Validate that address blocks do not overlap.
        self._validate_address_blocks(i_peripheral)

        # Calculate specified end address and total size from address blocks.
        end_address_specified = max(
            i_peripheral.base_address + ab.offset + ab.size - 1 for ab in i_peripheral.address_blocks
        )
        peripheral_size_specified = sum(ab.size for ab in i_peripheral.address_blocks)

        # Calculate effective end address and total size from registers/clusters.
        end_address_effective = max(
            i_peripheral.base_address
            + r.address_offset
            + ((_to_byte(r.size) if isinstance(r, Register) else r.cluster_size))
            - 1
            for r in registers_clusters
        )
        peripheral_size_effective = end_address_effective - i_peripheral.base_address + 1

        peripheral = Peripheral.from_intermediate_peripheral(
            i_peripheral=i_peripheral,
            registers_clusters=registers_clusters,
            registers=self._extract_registers(registers_clusters),
            end_address_effective=end_address_effective,
            end_address_specified=end_address_specified,
            peripheral_size_effective=peripheral_size_effective,
            peripheral_size_specified=peripheral_size_specified,
        )

        return peripheral

    def _extract_registers(self, registers_clusters: list[Cluster | Register]) -> list[Register]:
        # Recursively extract registers from clusters and registers
        registers: list[Register] = []
        for element in registers_clusters:
            if isinstance(element, Register):
                registers.append(element)
            elif isinstance(element, Cluster):  # pyright: ignore[reportUnnecessaryIsInstance]
                registers.extend(self._extract_registers(element.registers_clusters))

        registers.sort(key=lambda r: (r.base_address, r.name))
        return registers

    def _validate_address_blocks(self, i_peripheral: IPeripheral) -> None:
        for idx in range(1, len(i_peripheral.address_blocks)):
            prev = i_peripheral.address_blocks[idx - 1]
            curr = i_peripheral.address_blocks[idx]
            if curr.offset < prev.offset + prev.size:
                warnings.warn(
                    f"Address block with offset '{curr.offset}' overlaps with address block "
                    f"with offset '{prev.offset}'",
                    ProcessWarning,
                )

    def _check_peripheral_address_overlaps(
        self, finalized_peripherals: list[Peripheral], peripheral_lookup: dict[str, Peripheral]
    ):
        effective_intervals: list[tuple[int, str]] = []
        specified_intervals: list[tuple[int, str]] = []
        for periph in finalized_peripherals:
            allowed_names = self._compute_allowed_alternate_peripheral_names(periph, peripheral_lookup)

            # Check effective address overlaps.
            for end, name in effective_intervals:
                if periph.base_address <= end:
                    if allowed_names:
                        if name not in allowed_names:
                            warnings.warn(
                                f"Effective peripheral address overlap: '{periph.name}' overlaps with '{name}', "
                                f"which is not among the allowed alternate peripherals {allowed_names}",
                                ProcessWarning,
                            )
                    else:
                        existing_peripheral = peripheral_lookup[name]
                        if (
                            not existing_peripheral.alternate_peripheral
                            or existing_peripheral.alternate_peripheral != periph.name
                        ):
                            warnings.warn(
                                f"Effective peripheral address overlap: '{periph.name}' overlaps with '{name}'",
                                ProcessWarning,
                            )

            # Check specified address overlaps.
            for end, name in specified_intervals:
                if periph.base_address <= end:
                    if allowed_names:
                        if name not in allowed_names:
                            warnings.warn(
                                f"Specified peripheral address overlap in address_blocks: '{periph.name}' overlaps "
                                f"with '{name}', which is not among the allowed alternate peripherals {allowed_names}",
                                ProcessWarning,
                            )
                    else:
                        existing_peripheral = peripheral_lookup[name]
                        if (
                            not existing_peripheral.alternate_peripheral
                            or existing_peripheral.alternate_peripheral != periph.name
                        ):
                            warnings.warn(
                                f"Specified peripheral address overlap in address_blocks: '{periph.name}' "
                                f"overlaps with '{name}'",
                                ProcessWarning,
                            )

            effective_intervals.append((periph.end_address_effective, periph.name))
            specified_intervals.append((periph.end_address, periph.name))

    def _compute_allowed_alternate_peripheral_names(
        self, periph: Peripheral, peripheral_lookup: dict[str, Peripheral]
    ) -> set[str]:
        if periph.alternate_peripheral is None:
            return set()

        allowed: set[str] = set()
        stack = [periph.alternate_peripheral]

        while stack:
            current = stack.pop()
            if current in allowed:
                continue

            allowed.add(current)
            # Add peripherals that have 'current' as their alternate.
            stack.extend(name for name, p in peripheral_lookup.items() if p.alternate_peripheral == current)
            # If the current peripheral has an alternate (primary), add it.
            primary = peripheral_lookup[current].alternate_peripheral
            if primary is not None:
                stack.append(primary)

        return allowed

    def _validate_and_finalize_registers_clusters(
        self, i_registers_clusters: list[ICluster | IRegister], parent_base: int
    ) -> list[Cluster | Register]:
        def sort_key(reg_cluster: Cluster | Register) -> tuple[int, tuple[int, str], str]:
            # Get alternate_group if it exists; default to None if not (e.g. for Clusters)
            alt = getattr(reg_cluster, "alternate_group", None)
            # If alt is None, return (0, '') so that None sorts before any string; else (1, alt)
            alt_key = (0, "") if alt is None else (1, alt)
            return (reg_cluster.base_address, alt_key, reg_cluster.name)

        register_lookup: dict[str, Register] = {}
        cluster_lookup: dict[str, Cluster] = {}
        finalized_rc: list[Cluster | Register] = []
        for i_register_cluster in i_registers_clusters:
            register_cluster = self._validate_and_finalize_register_cluster(i_register_cluster, parent_base)
            if register_cluster:
                # If it's a register and has an alternate group, append the alternate group to a temporary name
                if isinstance(register_cluster, Register) and register_cluster.alternate_group:
                    name = f"{register_cluster.name}_{register_cluster.alternate_group}"
                else:
                    name = register_cluster.name

                # Check for duplicate register/cluster names
                if name in register_lookup or name in cluster_lookup:
                    raise ProcessException(f"Duplicate register/cluster name found: {name}")

                # Add the register/cluster to the appropriate lookup
                if isinstance(register_cluster, Register):
                    register_lookup[name] = register_cluster
                elif isinstance(register_cluster, Cluster):  # pyright: ignore[reportUnnecessaryIsInstance]
                    cluster_lookup[name] = register_cluster
                else:
                    raise ProcessException("Unknown register cluster type")

                finalized_rc.append(register_cluster)

        finalized_rc.sort(key=sort_key)
        self._check_registers_clusters_address_overlaps(finalized_rc, register_lookup, cluster_lookup)

        return finalized_rc

    def _validate_and_finalize_register_cluster(
        self, i_reg_cluster: ICluster | IRegister, parent_base: int
    ) -> None | Cluster | Register:
        effective_base = parent_base + i_reg_cluster.address_offset

        # Check if size is not None
        if i_reg_cluster.size is None:
            raise ProcessException(f"Register/Cluster '{i_reg_cluster.name}' size is None")

        # Ensure size is a multiple of 8 if specified.
        if i_reg_cluster.size % 8 != 0:
            warnings.warn(
                f"Register/Cluster '{i_reg_cluster.name}' size must be a multiple of 8. "
                "Register/Cluster will be ignored!",
                ProcessWarning,
            )
            return None

        # Check that the offset is size aligned.
        alignment = _get_alignment(_to_byte(i_reg_cluster.size))
        if i_reg_cluster.address_offset % alignment != 0:
            warnings.warn(
                f"Register/Cluster '{i_reg_cluster.name}' offset ({hex(i_reg_cluster.address_offset)}) "
                f"is not properly aligned to {alignment} bytes.",
                ProcessWarning,
            )

        if isinstance(i_reg_cluster, ICluster):
            children = self._validate_and_finalize_registers_clusters(i_reg_cluster.registers_clusters, effective_base)
            if children:
                cluster_effective_end = max(
                    child.base_address
                    + (_to_byte(child.size) if isinstance(child, Register) else child.cluster_size)
                    - 1
                    for child in children
                )
            else:
                warnings.warn(
                    f"Cluster '{i_reg_cluster.name}' has no registers. Cluster will be ignored!",
                    ProcessWarning,
                )
                return None

            cluster_size = cluster_effective_end - effective_base + 1
            return Cluster.from_intermediate_cluster(
                i_cluster=i_reg_cluster,
                registers_clusters=children,
                base_address=effective_base,
                end_address=cluster_effective_end,
                cluster_size=cluster_size,
            )
        elif isinstance(i_reg_cluster, IRegister):  # pyright: ignore[reportUnnecessaryIsInstance]
            if i_reg_cluster.name.lower() == "reserved":
                warnings.warn(
                    "Register with name 'reserved'. Register will be ignored!",
                    ProcessWarning,
                )
                return None

            if i_reg_cluster.alternate_register is not None and i_reg_cluster.alternate_group is not None:
                raise ProcessException(
                    f"Register '{i_reg_cluster.name}' cannot have both alternate_register and alternate_group"
                )

            return Register.from_intermediate_register(
                i_register=i_reg_cluster,
                fields=self._validate_and_finalize_fields(i_reg_cluster.fields, i_reg_cluster.size),
                base_address=effective_base,
            )

        raise ProcessException("Unknown register cluster type")

    def _check_registers_clusters_address_overlaps(
        self,
        finalized_rc: list[Cluster | Register],
        register_lookup: dict[str, Register],
        cluster_lookup: dict[str, Cluster],
    ):
        intervals: list[tuple[int, str]] = []
        for item in finalized_rc:
            if isinstance(item, Register) and item.alternate_group is not None:
                continue

            # Set type-specific variables.
            if isinstance(item, Register):
                allowed_names = self._compute_allowed_alternate_register_names(item, register_lookup)
                lookup = register_lookup
                alt_attr = "alternate_register"
                type_label = "Register"
                end_addr = item.base_address + _to_byte(item.size) - 1
            else:
                allowed_names = self._compute_allowed_alternate_cluster_names(item, cluster_lookup)
                lookup = cluster_lookup
                alt_attr = "alternate_cluster"
                type_label = "Cluster"
                end_addr = item.end_address

            # Check for overlapping intervals.
            for end, name in intervals:
                if item.base_address <= end:
                    if allowed_names:
                        if name not in allowed_names:
                            warnings.warn(
                                f"{type_label} '{item.name}' overlaps with '{name}', "
                                f"which is not among the allowed alternate {type_label.lower()}s {allowed_names}",
                                ProcessWarning,
                            )
                    else:
                        alt_value = getattr(lookup.get(name, None), alt_attr, None)
                        if alt_value != item.name:
                            warnings.warn(
                                f"{type_label} '{item.name}' overlaps with '{name}'",
                                ProcessWarning,
                            )

            intervals.append((end_addr, item.name))

    def _compute_allowed_alternate_register_names(
        self, register: Register, register_lookup: dict[str, Register]
    ) -> set[str]:
        if register.alternate_register is None:
            return set()

        allowed: set[str] = set()
        stack = [register.alternate_register]

        while stack:
            current = stack.pop()
            if current in allowed:
                continue

            allowed.add(current)
            # Add registers that have 'current' as their alternate.
            stack.extend(name for name, p in register_lookup.items() if p.alternate_register == current)
            # If the current register has an alternate (primary), add it.
            try:
                primary = register_lookup[current].alternate_register
            except KeyError:
                primary = None

            if primary is not None:
                stack.append(primary)

        return allowed

    def _compute_allowed_alternate_cluster_names(
        self, cluster: Cluster, cluster_lookup: dict[str, Cluster]
    ) -> set[str]:
        if cluster.alternate_cluster is None:
            return set()

        allowed: set[str] = set()
        stack = [cluster.alternate_cluster]

        while stack:
            current = stack.pop()
            if current in allowed:
                continue

            allowed.add(current)
            # Add clusters that have 'current' as their alternate.
            stack.extend(name for name, p in cluster_lookup.items() if p.alternate_cluster == current)
            # If the current cluster has an alternate (primary), add it.
            primary = cluster_lookup[current].alternate_cluster
            if primary is not None:
                stack.append(primary)

        return allowed

    def _validate_and_finalize_fields(self, i_fields: list[IField], reg_size: int) -> list[Field]:
        seen_names: set[str] = set()
        fields: list[Field] = []
        for i_field in i_fields:
            if i_field.name.lower() == "reserved":
                warnings.warn(
                    "Field with name 'reserved'. Field will be ignored!",
                    ProcessWarning,
                )
                continue

            if i_field.name in seen_names:
                raise ProcessException(f"Duplicate element name found: {i_field.name}")
            seen_names.add(i_field.name)

            fields.append(
                Field.from_intermediate_field(
                    i_field=i_field,
                    enumerated_value_containers=self._validate_and_finalize_enum_value_containers(
                        i_field.enumerated_value_containers, i_field.lsb, i_field.msb
                    ),
                )
            )

        fields.sort(key=lambda f: f.lsb)

        # Check for overlapping fields but difference between access types (same as in SVDConv SvdRegister::CheckFields)
        read_fields: list[Field] = []
        write_fields: list[Field] = []
        for field in fields:
            # Check if field exceeds register size
            if field.msb >= reg_size:
                warnings.warn(
                    f"Field '{field.name}' msb {field.msb} exceeds register size limit of {reg_size} bits",
                    ProcessWarning,
                )

            # Process based on access type
            if field.access == AccessType.READ_ONLY:
                # Check only the read domain
                for existing in read_fields:
                    if field.lsb <= existing.msb and field.msb >= existing.lsb:
                        raise ProcessException(f"Field '{field.name}' overlaps with '{existing.name}' in read access")
                read_fields.append(field)

            elif field.access == AccessType.WRITE_ONLY:
                # Check only the write domain
                for existing in write_fields:
                    if field.lsb <= existing.msb and field.msb >= existing.lsb:
                        raise ProcessException(f"Field '{field.name}' overlaps with '{existing.name}' in write access")
                write_fields.append(field)

            elif field.access in {AccessType.READ_WRITE, AccessType.WRITE_ONCE, AccessType.READ_WRITE_ONCE}:
                # First, check the read domain.
                for existing in read_fields:
                    if field.lsb <= existing.msb and field.msb >= existing.lsb:
                        raise ProcessException(f"Field '{field.name}' overlaps with '{existing.name}' in read access")
                # If no read conflict, add to read_fields.
                read_fields.append(field)
                # Then, check the write domain.
                for existing in write_fields:
                    if field.lsb <= existing.msb and field.msb >= existing.lsb:
                        raise ProcessException(f"Field '{field.name}' overlaps with '{existing.name}' in write access")
                write_fields.append(field)

        return fields

    def _validate_and_finalize_enum_value_containers(
        self, i_enum_containers: list[IEnumeratedValueContainer], lsb: int, msb: int
    ) -> list[EnumeratedValueContainer]:
        enum_value_containers: list[EnumeratedValueContainer] = []
        for i_enum_container in i_enum_containers:
            enum_value_containers.append(
                EnumeratedValueContainer.from_intermediate_enum_value_container(
                    i_enum_container=i_enum_container,
                    enumerated_values=self._validate_and_finalize_enum_values(
                        i_enum_container.enumerated_values, lsb, msb
                    ),
                )
            )

        return sorted(enum_value_containers, key=lambda evc: (evc.usage.value, len(evc.enumerated_values)))

    def _validate_and_finalize_enum_values(
        self, i_enum_values: list[IEnumeratedValue], lsb: int, msb: int
    ) -> list[EnumeratedValue]:
        enum_values: list[EnumeratedValue] = []
        for i_enum_value in i_enum_values:
            if i_enum_value.value is None:
                raise ProcessException("Enumerated value must have a value")

            if i_enum_value.value < 0 or i_enum_value.value > (2 ** (msb - lsb + 1) - 1):
                warnings.warn(
                    f"Enumerated value '{i_enum_value.name}' with value '{i_enum_value.value}' is outside of the valid "
                    f"range for a field of width {msb - lsb + 1} (0 to {2 ** (msb - lsb + 1) - 1}). "
                    "Enumerated value will be ignored.",
                    ProcessWarning,
                )
                continue

            enum_values.append(
                EnumeratedValue.from_intermediate_enum_value(i_enum_value=i_enum_value, value=i_enum_value.value)
            )

        return enum_values


class _ProcessDimension:
    def process_dim(
        self, name: str, display_name: None | str, dim: None | int, dim_index: None | str, element_type: type
    ) -> tuple[list[str], list[None | str]]:
        if dim is None:
            return ([name], [display_name])
        if dim < 1:
            raise ProcessException("dim value must be greater than 0")

        if "[%s]" in name:
            if element_type is SVDField:
                raise ProcessException("Fields cannot use dim arrays")

            return self._process_dim_array(name, display_name, dim)
        elif "%s" in name:
            if element_type is SVDPeripheral:
                raise ProcessException("Peripherals cannot use dim lists")

            return self._process_dim_list(name, display_name, dim, dim_index)

        raise ProcessException(f"can't resolve dim for '{name}' without a '%s' or '[%s]' in the name")

    def _process_dim_index(self, dim: None | int, dim_index: None | str) -> list[str]:
        if dim is None:
            raise ProcessException("can't resolve dim index without a dim value")
        if dim < 1:
            raise ProcessException("dim value must be greater than 0")

        if dim_index is None:
            dim_index_list = [str(i) for i in range(dim)]
        elif re.match(r"[0-9]+\-[0-9]+", dim_index):
            start, end = dim_index.split("-")

            if int(start) > int(end):
                raise ProcessException(f"dim index '{dim_index}' start value must be less than end value")

            dim_index_list = [str(i) for i in range(int(start), int(end) + 1)]
        elif re.match(r"[A-Z]-[A-Z]", dim_index):
            start, end = dim_index.split("-")

            if ord(start) >= ord(end):
                raise ProcessException(f"dim index '{dim_index}' start value must be less than end value")

            dim_index_list = [chr(i) for i in range(ord(start), ord(end) + 1)]
        elif re.match(r"[_0-9a-zA-Z]+(,\s*[_0-9a-zA-Z]+)+", dim_index):
            dim_index_no_whitespace = re.sub(r"\s+", "", dim_index)
            dim_index_list = dim_index_no_whitespace.split(",")
        # Not supported by the XSD, but required to parse some vendor files
        elif re.match(r"[_0-9a-zA-Z]+", dim_index):
            dim_index_list = [dim_index]
        else:
            raise ProcessException(f"can't resolve dim index for '{dim_index}'")

        if len(dim_index_list) != dim:
            raise ProcessException(f"dim index '{dim_index}' does not match the dim value '{dim}'")

        return dim_index_list

    def _process_dim_array(self, name: str, display_name: None | str, dim: int) -> tuple[list[str], list[None | str]]:
        if display_name is not None and "[%s]" not in display_name and "%s" in display_name:
            raise ProcessException(f"display_name '{display_name}' can't be a list if name is an array")

        resolved_names: list[str] = []
        resolved_display_names: list[None | str] = []
        for i in range(dim):
            resolved_names.append(name.replace("[%s]", str(i)))

            if display_name is not None:
                resolved_display_names.append(display_name.replace("[%s]", str(i)))
            else:
                resolved_display_names.append(None)

        return resolved_names, resolved_display_names

    def _process_dim_list(
        self, name: str, display_name: None | str, dim: int, dim_index: None | str
    ) -> tuple[list[str], list[None | str]]:
        if display_name is not None and "[%s]" in display_name:
            raise ProcessException(f"display_name '{display_name}' can't be an array if name is a list")

        resolved_names: list[str] = []
        resolved_display_names: list[None | str] = []
        for index in self._process_dim_index(dim, dim_index):
            resolved_names.append(name.replace("%s", index))

            if display_name is not None:
                resolved_display_names.append(display_name.replace("%s", index))
            else:
                resolved_display_names.append(None)

        return resolved_names, resolved_display_names


class _ProcessEnumeratedValueContainer:
    def create_enumerated_value_container(
        self, parsed_enum_container: SVDEnumeratedValueContainer, lsb: int, msb: int
    ) -> IEnumeratedValueContainer:
        return IEnumeratedValueContainer(
            name=parsed_enum_container.name,
            header_enum_name=parsed_enum_container.header_enum_name,
            usage=parsed_enum_container.usage if parsed_enum_container.usage is not None else EnumUsageType.READ_WRITE,
            enumerated_values=self._process_enumerated_values(parsed_enum_container.enumerated_values, lsb, msb),
            parsed=parsed_enum_container,
        )

    def _process_enumerated_values(
        self, parsed_enumerated_values: list[SVDEnumeratedValue], lsb: int, msb: int
    ) -> list[IEnumeratedValue]:
        enum_value_validator = _EnumeratedValueValidator()
        enumerated_values: list[IEnumeratedValue] = []

        for parsed_enumerated_value in parsed_enumerated_values:
            processed_enumerated_values = self._process_enumerated_value_resolve_wildcard(parsed_enumerated_value)

            for value in processed_enumerated_values:
                if enum_value_validator.is_value_valid(value):
                    enumerated_values.append(value)

        if default_enumerated_value := enum_value_validator.get_default():
            enumerated_values = self._extend_enumerated_values_with_default(
                enumerated_values, default_enumerated_value, lsb, msb
            )

        return sorted(enumerated_values, key=lambda ev: ev.value if ev.value is not None else 0)

    def _process_enumerated_value_resolve_wildcard(self, parsed_value: SVDEnumeratedValue) -> list[IEnumeratedValue]:
        value_list = self._convert_enumerated_value(parsed_value.value) if parsed_value.value else [None]

        enumerated_values: list[IEnumeratedValue] = []
        for value in value_list:
            name = parsed_value.name

            if name.lower() == "reserved":
                warnings.warn(
                    "Enumerated value with name 'reserved' found. Enumerated values with name 'reserved' are ignored.",
                    ProcessWarning,
                )
                continue

            if value is not None and parsed_value.value:
                substring = (
                    parsed_value.value[2:]
                    if parsed_value.value.lower().startswith("0x")
                    else parsed_value.value.lower()
                )
                if "x" in substring.lower():
                    name = f"{name}_{value}"

            enumerated_values.append(
                IEnumeratedValue(
                    name=name,
                    description=parsed_value.description,
                    value=value,
                    is_default=parsed_value.is_default or False,
                    parsed=parsed_value,
                )
            )

        return enumerated_values

    def _extend_enumerated_values_with_default(
        self, enumerated_values: list[IEnumeratedValue], default: IEnumeratedValue, lsb: int, msb: int
    ) -> list[IEnumeratedValue]:
        covered_values = {value.value for value in enumerated_values if value.value is not None}
        all_possible_values = set(range(pow(2, msb - lsb + 1)))

        uncovered_values = all_possible_values - covered_values

        for value in uncovered_values:
            enumerated_values.append(
                IEnumeratedValue(
                    name=f"{default.name}_{value}",
                    description=default.description,
                    value=value,
                    is_default=False,
                    parsed=default.parsed,
                )
            )

        return [value for value in enumerated_values if not value.is_default]

    def _convert_enumerated_value(self, input_str: str) -> list[int]:
        # transfer binary value to a string int function can handle
        input_str = input_str.lower().replace("#", "0b")

        try:
            if input_str.startswith("0b"):
                return self._process_binary_value_with_wildcard(input_str[2:])
            elif input_str.startswith("0x"):
                return [int(input_str, 16)]
            elif input_str.isdigit():
                return [int(input_str)]
            else:
                raise ProcessException(f"Unrecognized format for input: '{input_str}'")
        except ValueError as exc:
            raise ProcessException(f"Error processing input '{input_str}': {exc}") from exc

    def _process_binary_value_with_wildcard(self, binary_str: str) -> list[int]:
        if "x" in binary_str.lower():
            return [int(b, 2) for b in self._replace_x_combinations(binary_str.lower())]
        return [int(binary_str, 2)]

    def _replace_x_combinations(self, binary_str: str) -> list[str]:
        x_count = binary_str.count("x")
        combinations = itertools.product("01", repeat=x_count)
        return [self._replace_x_with_combination(binary_str, combination) for combination in combinations]

    def _replace_x_with_combination(self, binary_str: str, combination: tuple[str, ...]) -> str:
        temp_str = binary_str
        for bit in combination:
            temp_str = temp_str.replace("x", bit, 1)
        return temp_str


class _EnumeratedValueValidator:
    def __init__(self):
        self._seen_names: set[str] = set()
        self._seen_values: dict[int, str] = {}
        self._seen_default = None

    def is_value_valid(self, value: IEnumeratedValue) -> bool:
        # Ensure enumerated value names and values are unique
        if value.name in self._seen_names:
            warnings.warn(f"Duplicate enumerated value name found: {value.name}. Ignoring value.", ProcessWarning)
            return False
        if value.value in self._seen_values:
            warnings.warn(
                f"Duplicate enumerated value value found for enumerated value with name "
                f"'{value.name}' and value '{value.value}'. "
                f"Enumerated value '{self._seen_values[value.value]}' has the same value."
                f"Ignoring enumerated value with name '{value.name}' and value '{value.value}'.",
                ProcessWarning,
            )
            return False
        if value.is_default:
            if value.value is not None:
                warnings.warn(
                    f"Default value '{value.name}' has a value '{value.value}'. " f"Ignoring value for default value.",
                    ProcessWarning,
                )
                value.value = None
            if self._seen_default:
                raise ProcessException("Multiple default values found")
            self._seen_default = value

        # Add to seen names and values
        self._seen_names.add(value.name)
        if value.value is not None:
            self._seen_values[value.value] = value.name

        return True

    def get_default(self) -> None | IEnumeratedValue:
        return self._seen_default
