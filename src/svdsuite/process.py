import re
import itertools

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
    Device,
    CPU,
    SauRegionsConfig,
    SauRegion,
    Peripheral,
    Cluster,
    Register,
    Field,
    AddressBlock,
    Interrupt,
    WriteConstraint,
    EnumeratedValueContainer,
    EnumeratedValue,
)
from svdsuite.util.process_parse_model_convert import process_parse_convert_device
from svdsuite.model.types import AccessType, ProtectionStringType, CPUNameType, ModifiedWriteValuesType, EnumUsageType
from svdsuite.resolve.resolver import Resolver
from svdsuite.resolve.exception import EnumeratedValueContainerException
from svdsuite.model.type_alias import ParsedDimablePeripheralTypes, ProcessedDimablePeripheralTypes


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
        resolver_logging_file_path = "/home/fedora/resolver_logging.html"  # TODO remove (debug)
        self._resolver = Resolver(self, resolver_logging_file_path)
        self._processed_device = self._process_device(parsed_device)

    def get_processed_device(self) -> Device:
        return self._processed_device

    def convert_processed_device_to_svd_device(self) -> SVDDevice:
        return process_parse_convert_device(self._processed_device)

    def _process_device(self, parsed_device: SVDDevice) -> Device:
        size = or_if_none(parsed_device.size, 32)
        access = or_if_none(parsed_device.access, AccessType.READ_WRITE)
        protection = or_if_none(parsed_device.protection, ProtectionStringType.ANY)
        reset_value = or_if_none(parsed_device.reset_value, 0)
        reset_mask = or_if_none(parsed_device.reset_mask, 0xFFFFFFFF)

        try:
            peripherals = self._resolver.resolve_peripherals(parsed_device)
        except EnumeratedValueContainerException as e:
            raise ProcessException("Exception within enumerated value container processing") from e

        device = Device(
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

        _InheritProperties().inherit_properties(device)

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

    def _process_peripheral(self, index: int, name: str, parsed: SVDPeripheral, base: None | Peripheral) -> Peripheral:
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
        header_struct_name = or_if_none(parsed.header_struct_name, base.header_struct_name if base else None)
        disable_condition = or_if_none(parsed.disable_condition, base.disable_condition if base else None)
        base_address = parsed.base_address if dim_increment is None else parsed.base_address + dim_increment * index
        address_blocks = self._process_address_blocks(parsed.address_blocks) or (base.address_blocks if base else [])
        interrupts = self._process_interrupts(parsed.interrupts)

        return Peripheral(
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

    def _process_cluster(self, index: int, name: str, parsed: SVDCluster, base: None | Cluster) -> Cluster:
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

        return Cluster(
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

    def _process_register(self, index: int, name: str, parsed: SVDRegister, base: None | Register) -> Register:
        dim = or_if_none(parsed.dim, base.dim if base else None)
        dim_index = or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        size = or_if_none(parsed.size, base.size if base else None)
        access = or_if_none(parsed.access, base.access if base else None)
        protection = or_if_none(parsed.protection, base.protection if base else None)
        reset_value = or_if_none(parsed.reset_value, base.reset_value if base else None)
        reset_mask = or_if_none(parsed.reset_mask, base.reset_mask if base else None)

        display_name = or_if_none(parsed.display_name, base.display_name if base else None)
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

        return Register(
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

    def _process_field(self, index: int, name: str, parsed: SVDField, base: None | Field) -> Field:
        dim = or_if_none(parsed.dim, base.dim if base else None)
        dim_index = or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        access = or_if_none(parsed.access, base.access if base else None)

        description = or_if_none(parsed.description, base.description if base else None)
        lsb, msb = self._process_field_msb_lsb_with_increment(parsed, dim_increment, index)
        modified_write_values = (
            parsed.modified_write_values
            if parsed.modified_write_values is not None
            else (base.modified_write_values if base is not None else ModifiedWriteValuesType.MODIFY)
        )
        write_constraint = or_if_none(
            self._process_write_constraint(parsed.write_constraint), base.write_constraint if base else None
        )
        read_action = or_if_none(parsed.read_action, base.read_action if base else None)

        return Field(
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
                    protection=parsed_address_block.protection,
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
        self, parsed_field: SVDField, dim_increment: None | int, index: int
    ) -> tuple[int, int]:
        field_msb, field_lsb = self._process_field_msb_lsb(parsed_field)
        lsb = field_lsb if dim_increment is None else field_lsb + dim_increment * index
        msb = field_msb if dim_increment is None else field_msb + dim_increment * index
        return lsb, msb

    def _process_field_msb_lsb(self, parsed_field: SVDField) -> tuple[int, int]:
        if parsed_field.bit_offset is not None and parsed_field.bit_width is not None:
            field_lsb = parsed_field.bit_offset
            field_msb = parsed_field.bit_offset + parsed_field.bit_width - 1
        elif parsed_field.lsb is not None and parsed_field.msb is not None:
            field_lsb = parsed_field.lsb
            field_msb = parsed_field.msb
        elif parsed_field.bit_range is not None:
            match = re.match(r"\[(\d+):(\d+)\]", parsed_field.bit_range)
            if match:
                field_msb, field_lsb = map(int, match.groups())
            else:
                raise ValueError(f"Invalid bit range format: {parsed_field.bit_range}")
        else:
            raise ProcessException("Field must have bit_offset and bit_width, lsb and msb, or bit_range")

        return (field_msb, field_lsb)

    def _process_enumerated_value_container(
        self, parsed_enum_container: SVDEnumeratedValueContainer, lsb: int, msb: int
    ) -> EnumeratedValueContainer:
        return _ProcessEnumeratedValueContainer().create_enumerated_value_container(parsed_enum_container, lsb, msb)

    def _extract_and_process_dimension(
        self, parsed_element: ParsedDimablePeripheralTypes, base_element: None | ProcessedDimablePeripheralTypes
    ) -> tuple[bool, list[str]]:
        dim = or_if_none(parsed_element.dim, base_element.dim if base_element else None)
        dim_index = or_if_none(parsed_element.dim_index, base_element.dim_index if base_element else None)

        if dim is None and "%s" in parsed_element.name:
            raise ProcessException("Dim is None, but name contains '%s'")

        if dim is not None and "%s" not in parsed_element.name:
            raise ProcessException("Dim is not None, but name does not contain '%s'")

        return dim is not None, _ProcessDimension().process_dim(
            parsed_element.name, dim, dim_index, type(parsed_element)
        )


class _InheritProperties:
    def inherit_properties(self, device: Device):
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
        registers_clusters: list[Cluster | Register],
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

            if isinstance(register_cluster, Cluster):
                self._inherit_properties_registers_clusters(
                    register_cluster.registers_clusters,
                    register_cluster.size,
                    register_cluster.access,
                    register_cluster.protection,
                    register_cluster.reset_value,
                    register_cluster.reset_mask,
                )
            elif isinstance(register_cluster, Register):  # pyright: ignore[reportUnnecessaryIsInstance]
                self._inherit_properties_fields(
                    register_cluster.fields,
                    register_cluster.access,
                )
            else:
                raise ProcessException("Unknown register cluster type")

    def _inherit_properties_fields(self, fields: list[Field], access: None | AccessType):
        for field in fields:
            field.access = or_if_none(field.access, access)


class _ProcessDimension:
    def process_dim(self, name: str, dim: None | int, dim_index: None | str, element_type: type) -> list[str]:
        if dim is None:
            return [name]
        if dim < 1:
            raise ProcessException("dim value must be greater than 0")

        if "[%s]" in name:
            if element_type is SVDField:
                raise ProcessException("Fields cannot use dim arrays")

            return self._process_dim_array(name, dim)
        elif "%s" in name:
            if element_type is SVDPeripheral:
                raise ProcessException("Peripherals cannot use dim lists")

            return self._process_dim_list(name, dim, dim_index)

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

            if int(start) >= int(end):
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
        else:
            raise ProcessException(f"can't resolve dim index for '{dim_index}'")

        if len(dim_index_list) != dim:
            raise ProcessException(f"dim index '{dim_index}' does not match the dim value '{dim}'")

        return dim_index_list

    def _process_dim_array(self, name: str, dim: int) -> list[str]:
        resolved_names: list[str] = []
        for i in range(dim):
            resolved_names.append(name.replace("[%s]", str(i)))
        return resolved_names

    def _process_dim_list(self, name: str, dim: int, dim_index: None | str) -> list[str]:
        resolved_names: list[str] = []
        for index in self._process_dim_index(dim, dim_index):
            resolved_names.append(name.replace("%s", index))

        return resolved_names


class _ProcessEnumeratedValueContainer:
    def create_enumerated_value_container(
        self, parsed_enum_container: SVDEnumeratedValueContainer, lsb: int, msb: int
    ) -> EnumeratedValueContainer:
        return EnumeratedValueContainer(
            name=parsed_enum_container.name,
            header_enum_name=parsed_enum_container.header_enum_name,
            usage=parsed_enum_container.usage if parsed_enum_container.usage is not None else EnumUsageType.READ_WRITE,
            enumerated_values=self._process_enumerated_values(parsed_enum_container.enumerated_values, lsb, msb),
            parsed=parsed_enum_container,
        )

    def _process_enumerated_values(
        self, parsed_enumerated_values: list[SVDEnumeratedValue], lsb: int, msb: int
    ) -> list[EnumeratedValue]:
        enum_value_validator = _EnumeratedValueValidator()
        enumerated_values: list[EnumeratedValue] = []

        for parsed_enumerated_value in parsed_enumerated_values:
            processed_enumerated_values = self._process_enumerated_value_resolve_wildcard(parsed_enumerated_value)

            for value in processed_enumerated_values:
                enum_value_validator.add_value(value)

            enumerated_values.extend(processed_enumerated_values)

        if default_enumerated_value := enum_value_validator.get_default():
            enumerated_values = self._extend_enumerated_values_with_default(
                enumerated_values, default_enumerated_value, lsb, msb
            )

        return sorted(enumerated_values, key=lambda ev: ev.value if ev.value is not None else 0)

    def _process_enumerated_value_resolve_wildcard(self, parsed_value: SVDEnumeratedValue) -> list[EnumeratedValue]:
        value_list = self._convert_enumerated_value(parsed_value.value) if parsed_value.value else [None]

        enumerated_values: list[EnumeratedValue] = []
        for value in value_list:
            name = parsed_value.name
            if value is not None and parsed_value.value and "x" in parsed_value.value:
                name = f"{name}_{value}"

            enumerated_values.append(
                EnumeratedValue(
                    name=name,
                    description=parsed_value.description,
                    value=value,
                    is_default=parsed_value.is_default or False,
                    parsed=parsed_value,
                )
            )

        return enumerated_values

    def _extend_enumerated_values_with_default(
        self, enumerated_values: list[EnumeratedValue], default: EnumeratedValue, lsb: int, msb: int
    ) -> list[EnumeratedValue]:
        covered_values = {value.value for value in enumerated_values if value.value is not None}
        all_possible_values = set(range(pow(2, msb - lsb + 1)))

        uncovered_values = all_possible_values - covered_values

        for value in uncovered_values:
            enumerated_values.append(
                EnumeratedValue(
                    name=f"{default.name}_{value}",
                    description=default.description,
                    value=value,
                    is_default=False,
                    parsed=default.parsed,
                )
            )

        return [value for value in enumerated_values if not value.is_default]

    def _convert_enumerated_value(self, input_str: str) -> list[int]:
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
        if "x" in binary_str:
            return [int(b, 2) for b in self._replace_x_combinations(binary_str)]
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
        self._seen_values: set[int] = set()
        self._seen_default = None

    def add_value(self, value: EnumeratedValue):
        # Ensure enumerated value names and values are unique
        if value.name in self._seen_names:
            raise ProcessException(f"Duplicate enumerated value name found: {value.name}")
        if value.value in self._seen_values:
            raise ProcessException(f"Duplicate enumerated value value found: {value.value}")
        if value.is_default:
            if value.value is not None:
                raise ProcessException("Default value must not have a value")
            if self._seen_default:
                raise ProcessException("Multiple default values found")
            self._seen_default = value

        # Add to seen names and values
        self._seen_names.add(value.name)
        if value.value is not None:
            self._seen_values.add(value.value)

    def get_default(self) -> None | EnumeratedValue:
        return self._seen_default
