from typing import TypeAlias, cast
import re
import copy

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
    SVDEnumeratedValueContainer,
    SVDAddressBlock,
    SVDInterrupt,
    SVDWriteConstraint,
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
    EnumeratedValueContainer,
    AddressBlock,
    Interrupt,
    WriteConstraint,
)
from svdsuite.util.process_parse_model_convert import process_parse_convert_device
from svdsuite.model.types import AccessType, ProtectionStringType, CPUNameType, ModifiedWriteValuesType
from svdsuite.util.dim import resolve_dim
from svdsuite.util.resolve import Resolver, _ElementNode


ParsedPeripheralTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField | SVDEnumeratedValueContainer
ParsedDimablePeripheralTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField
ProcessedPeripheralTypes: TypeAlias = Peripheral | Cluster | Register | Field | EnumeratedValueContainer
ProcessedDimablePeripheralTypes: TypeAlias = Peripheral | Cluster | Register | Field


def _or_if_none[T](a: None | T, b: None | T) -> None | T:
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
        # resolver_logging_file_path = "/home/fedora/resolver_logging.html"  # TODO remove (debug)
        self._processed_device = self._process_device(parsed_device, resolver_logging_file_path)

    def get_processed_device(self) -> Device:
        return self._processed_device

    def convert_processed_device_to_svd_device(self) -> SVDDevice:
        return process_parse_convert_device(self._processed_device)

    def _process_device(self, parsed_device: SVDDevice, resolver_logging_file_path: None | str) -> Device:
        size = _or_if_none(parsed_device.size, 32)
        access = _or_if_none(parsed_device.access, AccessType.READ_WRITE)
        protection = _or_if_none(parsed_device.protection, ProtectionStringType.ANY)
        reset_value = _or_if_none(parsed_device.reset_value, 0)
        reset_mask = _or_if_none(parsed_device.reset_mask, 0xFFFFFFFF)

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
            peripherals=[],  # will be added in _ProcessPeripheralElements
            parsed=parsed_device,
        )

        _ProcessPeripheralElements(device, resolver_logging_file_path)

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


class _ProcessPeripheralElements:
    def __init__(self, device: Device, resolver_logging_file_path: None | str):
        self._device = device
        self._resolver = Resolver(resolver_logging_file_path)

        self._resolver.initialization(self._device)

        self._resolver.logger.log_repeating_steps_start()
        previous_nodes: list[_ElementNode] = []
        while not self._resolver.repeating_steps_finished_after_current_round():
            self._resolver.logger.log_round_start()

            self._resolver.resolve_placeholders()
            processable_nodes = self._resolver.get_topological_sorted_processable_nodes()

            if processable_nodes == previous_nodes:
                self._resolver.logger.log_loop_detected()
                raise ProcessException("Stuck in a loop, the same elements are being processed repeatedly")

            previous_nodes = processable_nodes

            for node in processable_nodes:
                self._process_element(node)

            self._resolver.logger.log_round_end()

        self._resolver.logger.log_repeating_steps_finished()
        self._resolver.finalize_processing()

    # TODO split for dimabmle and enum containers
    def _process_element(self, node: _ElementNode):
        parsed_element = node.parsed

        if isinstance(parsed_element, SVDDevice):
            raise ProcessException("Device should not be processed as an element")

        base_node = None
        base_processed_element = None
        if parsed_element.derived_from is not None:
            base_node = self._resolver.get_base_node(node)
            base_processed_element = base_node.processed_or_none

            # Ensure that the base element is processed, except for enum containers
            if base_processed_element is None and not isinstance(parsed_element, SVDEnumeratedValueContainer):
                raise ProcessException(f"Base element not found for node '{parsed_element.name}'")

        # Processing of enum containers is postboned to finalization, since lsb and msb from parent fields are required
        if isinstance(parsed_element, SVDEnumeratedValueContainer):
            self._resolver.update_enumerated_value_container(node, base_node)
            return

        if base_processed_element is not None and not isinstance(
            base_processed_element, ProcessedDimablePeripheralTypes
        ):
            raise ProcessException(f"Base element is not dimable for node '{parsed_element.name}'")

        is_dim, resolved_dim = self._resolve_dim(parsed_element, base_processed_element)
        processed_dimable_elements: list[ProcessedDimablePeripheralTypes] = []
        for index, name in enumerate(resolved_dim):
            processed_dimable_elements.append(
                self._create_dimable_element(index, name, parsed_element, base_processed_element)
            )

        if not processed_dimable_elements:
            raise ProcessException(f"No elements created for {parsed_element}")

        if is_dim:
            processed_dim_element = self._post_process_dim_elements(parsed_element.name, processed_dimable_elements)
            self._resolver.update_dim_element(node, base_node, processed_dimable_elements, processed_dim_element)
        else:
            self._resolver.update_element(node, base_node, processed_dimable_elements[0])

    def _post_process_dim_elements(
        self, dim_name: str, processed_dimable_elements: list[ProcessedDimablePeripheralTypes]
    ) -> ProcessedDimablePeripheralTypes:
        assert len(processed_dimable_elements) >= 1

        processed_dim_template = copy.copy(processed_dimable_elements[0])
        processed_dim_template.name = dim_name

        for processed_dimable_element in processed_dimable_elements:
            processed_dimable_element.dim = None
            processed_dimable_element.dim_increment = None
            processed_dimable_element.dim_index = None

        return processed_dim_template

    def _create_dimable_element(
        self,
        index: int,
        name: str,
        parsed_element: ParsedPeripheralTypes,
        base_element: None | ProcessedPeripheralTypes,
    ) -> ProcessedDimablePeripheralTypes:
        if isinstance(parsed_element, SVDPeripheral):
            return self._create_peripheral(index, name, parsed_element, cast(None | Peripheral, base_element))
        elif isinstance(parsed_element, SVDCluster):
            return self._create_cluster(index, name, parsed_element, cast(None | Cluster, base_element))
        elif isinstance(parsed_element, SVDRegister):
            return self._create_register(index, name, parsed_element, cast(None | Register, base_element))
        elif isinstance(parsed_element, SVDField):
            return self._create_field(index, name, parsed_element, cast(None | Field, base_element))
        else:
            raise ProcessException(f"Unknown type {type(parsed_element)} in _create_dimable_element")

    def _create_peripheral(self, index: int, name: str, parsed: SVDPeripheral, base: None | Peripheral) -> Peripheral:
        dim = _or_if_none(parsed.dim, base.dim if base else None)
        dim_index = _or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = _or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        size = _or_if_none(parsed.size, base.size if base else None)
        access = _or_if_none(parsed.access, base.access if base else None)
        protection = _or_if_none(parsed.protection, base.protection if base else None)
        reset_value = _or_if_none(parsed.reset_value, base.reset_value if base else None)
        reset_mask = _or_if_none(parsed.reset_mask, base.reset_mask if base else None)

        version = _or_if_none(parsed.version, base.version if base else None)
        description = _or_if_none(parsed.description, base.description if base else None)
        alternate_peripheral = _or_if_none(parsed.alternate_peripheral, base.alternate_peripheral if base else None)
        group_name = _or_if_none(parsed.group_name, base.group_name if base else None)
        prepend_to_name = _or_if_none(parsed.prepend_to_name, base.prepend_to_name if base else None)
        append_to_name = _or_if_none(parsed.append_to_name, base.append_to_name if base else None)
        header_struct_name = _or_if_none(parsed.header_struct_name, base.header_struct_name if base else None)
        disable_condition = _or_if_none(parsed.disable_condition, base.disable_condition if base else None)
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

    def _create_cluster(self, index: int, name: str, parsed: SVDCluster, base: None | Cluster) -> Cluster:
        dim = _or_if_none(parsed.dim, base.dim if base else None)
        dim_index = _or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = _or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        size = _or_if_none(parsed.size, base.size if base else None)
        access = _or_if_none(parsed.access, base.access if base else None)
        protection = _or_if_none(parsed.protection, base.protection if base else None)
        reset_value = _or_if_none(parsed.reset_value, base.reset_value if base else None)
        reset_mask = _or_if_none(parsed.reset_mask, base.reset_mask if base else None)

        description = _or_if_none(parsed.description, base.description if base else None)
        alternate_cluster = _or_if_none(parsed.alternate_cluster, base.alternate_cluster if base else None)
        header_struct_name = _or_if_none(parsed.header_struct_name, base.header_struct_name if base else None)
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

    def _create_register(self, index: int, name: str, parsed: SVDRegister, base: None | Register) -> Register:
        dim = _or_if_none(parsed.dim, base.dim if base else None)
        dim_index = _or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = _or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        size = _or_if_none(parsed.size, base.size if base else None)
        access = _or_if_none(parsed.access, base.access if base else None)
        protection = _or_if_none(parsed.protection, base.protection if base else None)
        reset_value = _or_if_none(parsed.reset_value, base.reset_value if base else None)
        reset_mask = _or_if_none(parsed.reset_mask, base.reset_mask if base else None)

        display_name = _or_if_none(parsed.display_name, base.display_name if base else None)
        description = _or_if_none(parsed.description, base.description if base else None)
        alternate_group = _or_if_none(parsed.alternate_group, base.alternate_group if base else None)
        alternate_register = _or_if_none(parsed.alternate_register, base.alternate_register if base else None)
        address_offset = (
            parsed.address_offset if dim_increment is None else parsed.address_offset + dim_increment * index
        )
        data_type = _or_if_none(parsed.data_type, base.data_type if base else None)
        modified_write_values = (
            parsed.modified_write_values
            if parsed.modified_write_values is not None
            else (base.modified_write_values if base is not None else ModifiedWriteValuesType.MODIFY)
        )
        write_constraint = _or_if_none(
            self._process_write_constraint(parsed.write_constraint), base.write_constraint if base else None
        )
        read_action = _or_if_none(parsed.read_action, base.read_action if base else None)

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

    def _create_field(self, index: int, name: str, parsed: SVDField, base: None | Field) -> Field:
        dim = _or_if_none(parsed.dim, base.dim if base else None)
        dim_index = _or_if_none(parsed.dim_index, base.dim_index if base else None)
        dim_increment = _or_if_none(parsed.dim_increment, base.dim_increment if base else None)

        access = _or_if_none(parsed.access, base.access if base else None)

        description = _or_if_none(parsed.description, base.description if base else None)
        lsb, msb = self._process_field_msb_lsb_with_increment(parsed, dim_increment, index)
        modified_write_values = (
            parsed.modified_write_values
            if parsed.modified_write_values is not None
            else (base.modified_write_values if base is not None else ModifiedWriteValuesType.MODIFY)
        )
        write_constraint = _or_if_none(
            self._process_write_constraint(parsed.write_constraint), base.write_constraint if base else None
        )
        read_action = _or_if_none(parsed.read_action, base.read_action if base else None)

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

    def _resolve_dim(
        self, parsed_element: ParsedDimablePeripheralTypes, base_element: None | ProcessedDimablePeripheralTypes
    ) -> tuple[bool, list[str]]:
        dim = _or_if_none(parsed_element.dim, base_element.dim if base_element else None)
        dim_index = _or_if_none(parsed_element.dim_index, base_element.dim_index if base_element else None)

        if dim is None and "%s" in parsed_element.name:
            raise ProcessException("Dim is None, but name contains '%s'")

        if dim is not None and "%s" not in parsed_element.name:
            raise ProcessException("Dim is not None, but name does not contain '%s'")

        return dim is not None, resolve_dim(parsed_element.name, dim, dim_index)

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
