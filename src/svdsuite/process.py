import itertools
from dataclasses import dataclass
from typing import TypeAlias, TypeVar, Self, Optional
import copy
import re
import bisect

from svdsuite.parse import Parser
from svdsuite.model.parse import (
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
from svdsuite.model.process import (
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
from svdsuite.model.types import CPUNameType, EnumUsageType, ModifiedWriteValuesType, ProtectionStringType, AccessType
from svdsuite.util.dim import resolve_dim
from svdsuite.util.process_parse_model_convert import process_parse_convert_device

SVDElementTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField

T = TypeVar("T")


def _or_if_none(a: Optional[T], b: Optional[T]) -> Optional[T]:
    return a if a is not None else b


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
        attributes: dict[str, None | int | AccessType | ProtectionStringType] = {
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


class _RegisterClusterMap:
    def __init__(self):
        # list of tuples (start, end, reference)
        self.regions: list[tuple[int, int, Cluster | Register]] = []

    def add_region(self, start: int, end: int, reference: Cluster | Register) -> None:
        def region_key(region: tuple[int, int, Cluster | Register]) -> tuple[int, int, str]:
            return (region[0], region[1], region[2].name)

        bisect.insort(self.regions, (start, end, reference), key=region_key)

    def get_highest_region(self) -> tuple[int, int, Cluster | Register]:
        return self.regions[-1]

    def merge_and_overwrite_with(self, other: "_RegisterClusterMap") -> None:
        """
        Merges the current _RegisterClusterMap with another _RegisterClusterMap.
        Overlapping regions from the current map are overwritten by the regions from 'other'.
        """

        def region_overlaps(
            region1: tuple[int, int, Cluster | Register], region2: tuple[int, int, Cluster | Register]
        ) -> bool:
            start1, end1, _ = region1
            start2, end2, _ = region2
            return start1 <= end2 and end1 >= start2

        for other_region in other.regions:
            overlapping_regions = [region for region in self.regions if region_overlaps(region, other_region)]
            for region in overlapping_regions:
                self.regions.remove(region)

            self.add_region(*other_region)

    @staticmethod
    def build_map_from_registers_clusters(
        registers_clusters: list[Register | Cluster],
    ) -> "_RegisterClusterMap":
        memory_map = _RegisterClusterMap()
        for register_cluster in registers_clusters:
            if isinstance(register_cluster, Cluster):
                cluster_map = _RegisterClusterMap.build_map_from_registers_clusters(register_cluster.registers_clusters)
                memory_map.add_region(
                    register_cluster.address_offset,
                    register_cluster.address_offset + cluster_map.get_highest_region()[1],
                    register_cluster,
                )

            if isinstance(register_cluster, Register):
                register_size_bit = register_cluster.size

                if register_size_bit % 8 != 0:
                    raise ValueError(f"register size of {register_cluster.name} is not a multiple of 8")

                register_size_byte = register_size_bit // 8

                memory_map.add_region(
                    register_cluster.address_offset,
                    register_cluster.address_offset + register_size_byte - 1,
                    register_cluster,
                )

        return memory_map


class _Node:
    def __init__(
        self,
        name: str,
        element: SVDElementTypes,
        alternative_names: set[str],
        dim_values: list[str],
        register_properties: _RegisterPropertiesInheritance,
    ) -> None:
        self.name: str = name
        self.element = element
        self.alternative_names: set[str] = alternative_names
        self.dim_values: list[str] = dim_values
        self.register_properties = register_properties
        self._hash = hash(self.name)

    def __repr__(self) -> str:
        return f"Node({self.name}, {self.element})"

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _Node):
            return NotImplemented
        return self.name == other.name


class _DirectedGraphException(Exception):
    pass


class _DirectedGraph:
    def __init__(self) -> None:
        self.graph: dict[_Node, list[_Node]] = {}
        self.node_types: dict[type[SVDElementTypes], list[_Node]] = {
            SVDField: [],
            SVDRegister: [],
            SVDCluster: [],
            SVDPeripheral: [],
        }
        self.completed_nodes: set[_Node] = set()
        self.node_lookup: dict[str, _Node] = {}
        self.alternative_name_lookup: dict[str, _Node] = {}
        self.reverse_graph: dict[_Node, set[_Node]] = {}

    def add_node(
        self,
        full_name: str,
        element: SVDElementTypes,
        register_properties: _RegisterPropertiesInheritance,
        parent_node: None | _Node = None,
    ) -> _Node:
        print(f"Adding node {full_name} of type {type(element)}")  # TODO DEBUG

        if self._find_node_by_name(full_name):
            raise ValueError(f"Node with name {full_name} already exists in the graph")

        dim_values = self._resolve_dim_values(element)
        alternative_names = self._generate_alternative_names(element, parent_node, dim_values)
        print(f"Alternative names for node {full_name}: {alternative_names}")  # TODO DEBUG

        node = _Node(full_name, element, set(alternative_names), dim_values, register_properties)

        self.graph[node] = []
        self.node_types[type(element)].append(node)
        self.node_lookup[full_name] = node
        for alt_name in alternative_names:
            self.alternative_name_lookup[alt_name] = node

        return node

    def add_edge(self, from_name: str, to_name: str) -> None:
        from_node = self._find_node_by_name(from_name)
        to_node = self._find_node_by_name(to_name)

        if from_node is not None and to_node is not None:
            print(f"Adding edge from {from_node.name} to {to_node.name}")  #  TODO DEBUG
            self.graph[from_node].append(to_node)
            if to_node not in self.reverse_graph:
                self.reverse_graph[to_node] = set()
            self.reverse_graph[to_node].add(from_node)
        else:
            raise ValueError("Both nodes must exist in the graph")

    def get_next_node_without_outgoing_edges(self) -> None | _Node:
        type_priority: list[type[SVDElementTypes]] = [SVDField, SVDRegister, SVDCluster, SVDPeripheral]

        for node_type in type_priority:
            for node in self.node_types[node_type]:
                if node not in self.completed_nodes and not self.graph[node]:
                    return node
        return None

    def mark_node_as_completed(self, name: str) -> None:
        node = self._find_node_by_name(name)
        if node:
            self.completed_nodes.add(node)
            if node in self.reverse_graph:
                for predecessor in self.reverse_graph[node]:
                    self.graph[predecessor].remove(node)
                del self.reverse_graph[node]

    def _generate_alternative_names(
        self, element: SVDElementTypes, parent_node: None | _Node, dim_values: list[str]
    ) -> set[str]:
        alternative_names: set[str] = set()

        if isinstance(element, SVDPeripheral):
            alternative_names = set(dim_values)
        else:
            if parent_node is None:
                raise ValueError("Parent node must be provided for cluster, register, field")

            alternative_names.update(self._combine_names(parent_node.alternative_names, set([element.name])))
            alternative_names.update(self._combine_names(set([parent_node.name]), set(dim_values)))
            alternative_names.update(self._combine_names(parent_node.alternative_names, set(dim_values)))

        return alternative_names

    def _resolve_dim_values(self, element: SVDElementTypes) -> list[str]:
        if element.dim is not None:
            return resolve_dim(element.name, element.dim, element.dim_index)
        return []

    def _combine_names(self, names1: set[str], names2: set[str]) -> set[str]:
        return {f"{item1}.{item2}" for item1, item2 in itertools.product(names1, names2)}

    def detect_cycle(self) -> bool:
        visited: set[_Node] = set()
        rec_stack: set[_Node] = set()

        def dfs(node: _Node) -> bool:
            if node in rec_stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            rec_stack.add(node)

            for neighbor in self.graph[node]:
                if dfs(neighbor):
                    return True

            rec_stack.remove(node)
            return False

        for node in self.graph:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def _find_node_by_name(self, name: str) -> None | _Node:
        if name in self.node_lookup:
            return self.node_lookup[name]
        if name in self.alternative_name_lookup:
            return self.alternative_name_lookup[name]

        return None


class _Resolver:
    def __init__(self, parsed_device: SVDDevice) -> None:
        self._parsed_device = parsed_device
        self._graph = _DirectedGraph()
        self._derived_mapping: list[tuple[str, str]] = []
        self._resolve_next_code_called = False

        self._build_resolve_graph()

    def resolve_next_node(self) -> None | _Node:
        if not self._resolve_next_code_called:
            self._resolve_next_code_called = True
            if self._graph.detect_cycle():
                raise _DirectedGraphException("Detected cycle in graph")

        node = self._graph.get_next_node_without_outgoing_edges()

        if node is not None:
            self._graph.mark_node_as_completed(node.name)

        return node

    def find_derived_nodes(self, node: _Node) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        for derived_node_name, base_node_name in self._derived_mapping:
            if base_node_name == node.name or base_node_name in node.alternative_names:
                if "." in base_node_name:
                    element_derived_rel_name = base_node_name.split(".")[-1]
                else:
                    element_derived_rel_name = base_node_name

                if "%s" in element_derived_rel_name:
                    element_derived_rel_name = node.dim_values[0]

                result.append((derived_node_name, element_derived_rel_name))

        return result

    def _build_resolve_graph(self) -> None:
        register_properties_device = _RegisterPropertiesInheritance(
            size=self._parsed_device.size,
            access=self._parsed_device.access,
            protection=self._parsed_device.protection,
            reset_value=self._parsed_device.reset_value,
            reset_mask=self._parsed_device.reset_mask,
        )

        # iterate over peripherals, clusters, registers, fields to build graph and the mapping of derived_from
        for parsed_peripheral in self._parsed_device.peripherals:
            register_properties_peripheral = register_properties_device.get_obj(
                parsed_peripheral.size,
                parsed_peripheral.access,
                parsed_peripheral.protection,
                parsed_peripheral.reset_value,
                parsed_peripheral.reset_mask,
            )

            peripheral_node = self._graph.add_node(
                parsed_peripheral.name, parsed_peripheral, register_properties_peripheral
            )

            if parsed_peripheral.derived_from is not None:
                self._derived_mapping.append((parsed_peripheral.name, parsed_peripheral.derived_from))

            stack = [
                (item, parsed_peripheral.name, peripheral_node, register_properties_peripheral)
                for item in parsed_peripheral.registers_clusters
            ]
            while stack:
                register_cluster, current_path, peripheral_node_, register_properties_parent = stack.pop(0)
                if isinstance(register_cluster, SVDCluster):
                    self._handle_cluster(
                        register_cluster, current_path, peripheral_node_, register_properties_parent, stack
                    )
                if isinstance(register_cluster, SVDRegister):
                    self._handle_register(register_cluster, current_path, peripheral_node_, register_properties_parent)

        # add edges for derived_from
        for element_name, derived_from_name in self._derived_mapping:
            self._graph.add_edge(element_name, derived_from_name)

    def _handle_cluster(
        self,
        cluster: SVDCluster,
        current_path: str,
        parent_node: _Node,
        register_properties_parent: _RegisterPropertiesInheritance,
        stack: list[tuple[SVDRegister | SVDCluster, str, _Node, _RegisterPropertiesInheritance]],
    ) -> None:
        register_properties_cluster = register_properties_parent.get_obj(
            cluster.size,
            cluster.access,
            cluster.protection,
            cluster.reset_value,
            cluster.reset_mask,
        )

        cluster_name = f"{current_path}.{cluster.name}"
        cluster_node = self._graph.add_node(cluster_name, cluster, register_properties_cluster, parent_node)
        self._graph.add_edge(current_path, cluster_name)
        self._handle_derived_from(cluster_name, cluster.derived_from, current_path)

        stack.extend(
            (nested_item, cluster_name, cluster_node, register_properties_cluster)
            for nested_item in cluster.registers_clusters
        )

    def _handle_register(
        self,
        register: SVDRegister,
        current_path: str,
        parent_node: _Node,
        register_properties_parent: _RegisterPropertiesInheritance,
    ) -> None:
        register_properties_register = register_properties_parent.get_obj(
            register.size,
            register.access,
            register.protection,
            register.reset_value,
            register.reset_mask,
        )

        register_name = f"{current_path}.{register.name}"
        register_node = self._graph.add_node(register_name, register, register_properties_register, parent_node)
        self._graph.add_edge(current_path, register_name)
        self._handle_derived_from(register_name, register.derived_from, current_path)

        for field in register.fields:
            self._handle_field(field, register_name, register_node, register_properties_register.access)

    def _handle_field(
        self, field: SVDField, register_name: str, parent_node: _Node, register_access: None | AccessType
    ) -> None:
        register_properties_field = _RegisterPropertiesInheritance(
            size=None,
            access=field.access if field.access is not None else register_access,
            protection=None,
            reset_value=None,
            reset_mask=None,
        )

        field_name = f"{register_name}.{field.name}"
        self._graph.add_node(field_name, field, register_properties_field, parent_node)
        self._graph.add_edge(register_name, field_name)
        self._handle_derived_from(field_name, field.derived_from, register_name)

    def _handle_derived_from(self, derived_node_name: str, element_name: None | str, path: str) -> None:
        if element_name is not None:
            if "." not in element_name:
                self._derived_mapping.append((derived_node_name, f"{path}.{element_name}"))
            else:
                self._derived_mapping.append((derived_node_name, element_name))


class ProcessException(Exception):
    pass


class Process:
    @classmethod
    def from_svd_file(cls, path: str):
        return cls(Parser.from_svd_file(path).get_parsed_device())

    @classmethod
    def from_xml_str(cls, xml_str: str):
        return cls(Parser.from_xml_content(xml_str.encode()).get_parsed_device())

    @classmethod
    def from_xml_content(cls, content: bytes):
        return cls(Parser.from_xml_content(content).get_parsed_device())

    def __init__(self, parsed_device: SVDDevice) -> None:
        self._processed_device = self._process_device(parsed_device)

    def get_processed_device(self) -> Device:
        return self._processed_device

    def convert_processed_device_to_svd_device(self) -> SVDDevice:
        return process_parse_convert_device(self._processed_device)

    def _process_device(self, parsed_device: SVDDevice) -> Device:
        return Device(
            size=parsed_device.size,
            access=parsed_device.access,
            protection=parsed_device.protection,
            reset_value=parsed_device.reset_value,
            reset_mask=parsed_device.reset_mask,
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
            peripherals=_ProcessPeripheralElements(parsed_device).process_peripherals(),
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


def _process_write_constraint(write_constraint: None | SVDWriteConstraint) -> None | WriteConstraint:
    if write_constraint is None:
        return None

    return WriteConstraint(
        write_as_read=write_constraint.write_as_read,
        use_enumerated_values=write_constraint.use_enumerated_values,
        range_=write_constraint.range_,
        parsed=write_constraint,
    )


class _ProcessField:
    def __init__(self, resolver: _Resolver) -> None:
        self._resolver = resolver
        self._processed_fields: dict[str, list[Field]] = {}
        self._derived_base_node_lookup: dict[str, Field] = {}

    def process_field(self, node: _Node) -> None:
        parsed_field = self._validate_svdfield(node.element)
        derived_nodes = self._resolver.find_derived_nodes(node)

        for index in range(parsed_field.dim or 1):
            field = self._create_field(node, parsed_field, index)
            self._insert_field(node, field)
            self._process_derived_nodes(derived_nodes, field)

    def get_processed_field(self, name: str) -> list[Field]:
        try:
            return self._processed_fields[name]
        except KeyError:
            return []

    def _validate_svdfield(self, element: SVDElementTypes) -> SVDField:
        if not isinstance(element, SVDField):
            raise ProcessException(f"Expected SVDField, got {type(element)}")
        return element

    def _validate_access(self, access: None | AccessType) -> AccessType:
        if access is None:
            raise ProcessException("Access can't be None for field")
        return access

    def _create_field(self, node: _Node, parsed_field: SVDField, index: int) -> Field:
        name = parsed_field.name if not node.dim_values else node.dim_values[index]

        if node.name in self._derived_base_node_lookup:
            return self._handle_derived_field(node, parsed_field, index, name)
        else:
            return self._handle_non_derived_field(node, parsed_field, index, name)

    def _handle_derived_field(self, node: _Node, parsed_field: SVDField, index: int, name: str) -> Field:
        base_element = self._derived_base_node_lookup[node.name]
        description = _or_if_none(parsed_field.description, base_element.description)

        try:
            lsb, msb = self._process_field_msb_lsb_with_increment(parsed_field, node, index)
        except ProcessException:
            lsb = base_element.lsb
            msb = base_element.msb

        access = self._validate_access(_or_if_none(parsed_field.access, base_element.access))
        modified_write_values = parsed_field.modified_write_values or base_element.modified_write_values
        write_constraint = _or_if_none(
            _process_write_constraint(parsed_field.write_constraint), base_element.write_constraint
        )
        read_action = _or_if_none(parsed_field.read_action, base_element.read_action)
        enumerated_values = (
            self._process_enumerated_values(parsed_field.enumerated_values) or base_element.enumerated_values
        )

        return Field(
            name=name,
            description=description,
            lsb=lsb,
            msb=msb,
            access=access,
            modified_write_values=modified_write_values,
            write_constraint=write_constraint,
            read_action=read_action,
            enumerated_values=enumerated_values,
            parsed=parsed_field,
        )

    def _handle_non_derived_field(self, node: _Node, parsed_field: SVDField, index: int, name: str) -> Field:
        description = parsed_field.description
        lsb, msb = self._process_field_msb_lsb_with_increment(parsed_field, node, index)
        access = self._validate_access(node.register_properties.access)
        modified_write_values = parsed_field.modified_write_values or ModifiedWriteValuesType.MODIFY
        write_constraint = _process_write_constraint(parsed_field.write_constraint)
        read_action = parsed_field.read_action
        enumerated_values = self._process_enumerated_values(parsed_field.enumerated_values)

        return Field(
            name=name,
            description=description,
            lsb=lsb,
            msb=msb,
            access=access,
            modified_write_values=modified_write_values,
            write_constraint=write_constraint,
            read_action=read_action,
            enumerated_values=enumerated_values,
            parsed=parsed_field,
        )

    def _process_field_msb_lsb_with_increment(self, parsed_field: SVDField, node: _Node, index: int) -> tuple[int, int]:
        field_msb, field_lsb = self._process_field_msb_lsb(parsed_field)
        lsb = field_lsb if node.element.dim_increment is None else field_lsb + node.element.dim_increment * index
        msb = field_msb if node.element.dim_increment is None else field_msb + node.element.dim_increment * index
        return lsb, msb

    def _insert_field(self, node: _Node, field: Field) -> None:
        parent_name = ".".join(node.name.split(".")[:-1])
        if parent_name not in self._processed_fields:
            self._processed_fields[parent_name] = []
        bisect.insort(self._processed_fields[parent_name], field, key=lambda x: x.lsb)

    def _process_derived_nodes(self, derived_nodes: list[tuple[str, str]], field: Field) -> None:
        for derived_node_name, base_node_rel_name in derived_nodes:
            if field.name == base_node_rel_name:
                self._derived_base_node_lookup[derived_node_name] = field

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

    def _process_enumerated_values(self, parsed_enumerated_values: list[SVDEnumeratedValue]) -> list[EnumeratedValue]:
        enumerated_values: list[EnumeratedValue] = []
        for parsed_enumerated_value in parsed_enumerated_values:
            if parsed_enumerated_value.derived_from is not None:
                raise NotImplementedError("Derived from is not supported for enumerated values")

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


class _ProccessedRegistersClusters:
    def __init__(self) -> None:
        self._processed_registers_clusters: dict[str, list[Cluster | Register]] = {}

    def get_processed_register_cluster(self, name: str) -> list[Cluster | Register]:
        try:
            return self._processed_registers_clusters[name]
        except KeyError:
            return []

    def insert_element(self, name: str, register_cluster: Cluster | Register) -> None:
        if name not in self._processed_registers_clusters:
            self._processed_registers_clusters[name] = []

        bisect.insort(self._processed_registers_clusters[name], register_cluster, key=lambda x: x.address_offset)


class _ProcessRegister:
    def __init__(
        self,
        resolver: _Resolver,
        process_field: _ProcessField,
        processed_registers_clusters: _ProccessedRegistersClusters,
    ) -> None:
        self._resolver = resolver
        self._process_field = process_field
        self._processed_register_cluster = processed_registers_clusters
        self._derived_base_node_lookup: dict[str, Register] = {}

    def process_register(self, node: _Node) -> None:
        parsed_register = self._validate_svdregister(node.element)
        derived_nodes = self._resolver.find_derived_nodes(node)

        for index in range(parsed_register.dim or 1):
            register = self._create_register(node, parsed_register, index)
            self._insert_register(node, register)
            self._process_derived_nodes(derived_nodes, register)

    def _validate_svdregister(self, element: SVDElementTypes) -> SVDRegister:
        if not isinstance(element, SVDRegister):
            raise ProcessException(f"Expected SVDRegister, got {type(element)}")
        return element

    def _create_register(self, node: _Node, parsed_register: SVDRegister, index: int) -> Register:
        name = parsed_register.name if not node.dim_values else node.dim_values[index]

        if node.name in self._derived_base_node_lookup:
            return self._handle_derived_register(node, parsed_register, index, name)
        else:
            return self._handle_non_derived_register(node, parsed_register, index, name)

    def _validate_register_properties(
        self,
        size: None | int,
        access: None | AccessType,
        protection: None | ProtectionStringType,
        reset_value: None | int,
        reset_mask: None | int,
    ) -> tuple[int, AccessType, ProtectionStringType, int, int]:
        if size is None:
            raise ProcessException("Size can't be None for register")
        if access is None:
            raise ProcessException("Access can't be None for register")
        if protection is None:
            protection = ProtectionStringType.ANY
        if reset_value is None:
            raise ProcessException("Reset value can't be None for register")
        if reset_mask is None:
            raise ProcessException("Reset mask can't be None for register")

        return (size, access, protection, reset_value, reset_mask)

    def _handle_derived_register(self, node: _Node, parsed_register: SVDRegister, index: int, name: str) -> Register:
        base_element = self._derived_base_node_lookup[node.name]

        size, access, protection, reset_value, reset_mask = self._validate_register_properties(
            _or_if_none(node.register_properties.size, base_element.size),
            _or_if_none(node.register_properties.access, base_element.access),
            _or_if_none(node.register_properties.protection, base_element.protection),
            _or_if_none(node.register_properties.reset_value, base_element.reset_value),
            _or_if_none(node.register_properties.reset_mask, base_element.reset_mask),
        )

        display_name = _or_if_none(parsed_register.display_name, base_element.display_name)
        description = _or_if_none(parsed_register.description, base_element.description)
        alternate_group = _or_if_none(parsed_register.alternate_group, base_element.alternate_group)
        alternate_register = _or_if_none(parsed_register.alternate_register, base_element.alternate_register)
        address_offset = (
            parsed_register.address_offset
            if parsed_register.dim_increment is None
            else parsed_register.address_offset + parsed_register.dim_increment * index
        )
        data_type = _or_if_none(parsed_register.data_type, base_element.data_type)
        modified_write_values = parsed_register.modified_write_values or base_element.modified_write_values
        write_constraint = _or_if_none(
            _process_write_constraint(parsed_register.write_constraint), base_element.write_constraint
        )
        read_action = _or_if_none(parsed_register.read_action, base_element.read_action)
        fields = self._derive_fields(node.name, base_element)

        return Register(
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
            fields=fields,
            parsed=parsed_register,
        )

    def _derive_fields(self, name: str, base_element: Register) -> list[Field]:
        def overlap(field1: Field, field2: Field) -> bool:
            return not (field1.msb < field2.lsb or field2.msb < field1.lsb)

        merged = base_element.fields[:]
        for parsed_field in self._process_field.get_processed_field(name):
            merged = [base_field for base_field in merged if not overlap(base_field, parsed_field)]
            merged.append(parsed_field)

        merged.sort(key=lambda field: field.lsb)
        return merged

    def _handle_non_derived_register(
        self, node: _Node, parsed_register: SVDRegister, index: int, name: str
    ) -> Register:
        size, access, protection, reset_value, reset_mask = self._validate_register_properties(
            node.register_properties.size,
            node.register_properties.access,
            node.register_properties.protection,
            node.register_properties.reset_value,
            node.register_properties.reset_mask,
        )

        display_name = parsed_register.display_name
        description = parsed_register.description
        alternate_group = parsed_register.alternate_group
        alternate_register = parsed_register.alternate_register
        address_offset = (
            parsed_register.address_offset
            if parsed_register.dim_increment is None
            else parsed_register.address_offset + parsed_register.dim_increment * index
        )
        data_type = parsed_register.data_type
        modified_write_values = parsed_register.modified_write_values or ModifiedWriteValuesType.MODIFY
        write_constraint = _process_write_constraint(parsed_register.write_constraint)
        read_action = parsed_register.read_action
        fields = self._process_field.get_processed_field(node.name)

        return Register(
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
            fields=fields,
            parsed=parsed_register,
        )

    def _insert_register(self, node: _Node, register: Register) -> None:
        parent_name = ".".join(node.name.split(".")[:-1])
        self._processed_register_cluster.insert_element(parent_name, register)

    def _process_derived_nodes(self, derived_nodes: list[tuple[str, str]], register: Register) -> None:
        for derived_node_name, base_node_rel_name in derived_nodes:
            if register.name == base_node_rel_name:
                self._derived_base_node_lookup[derived_node_name] = register


class _ProcessCluster:
    def __init__(
        self,
        resolver: _Resolver,
        process_register: _ProcessRegister,
        processed_register_cluster: _ProccessedRegistersClusters,
    ) -> None:
        self._resolver = resolver
        self._process_register = process_register
        self._processed_registers_clusters = processed_register_cluster
        self._derived_base_node_lookup: dict[str, Cluster] = {}

    def process_cluster(self, node: _Node) -> None:
        parsed_cluster = self._validate_svdcluster(node.element)
        derived_nodes = self._resolver.find_derived_nodes(node)

        for index in range(parsed_cluster.dim or 1):
            cluster = self._create_cluster(node, parsed_cluster, index)
            self._insert_cluster(node, cluster)
            self._process_derived_nodes(derived_nodes, cluster)

    def _validate_svdcluster(self, element: SVDElementTypes) -> SVDCluster:
        if not isinstance(element, SVDCluster):
            raise ProcessException(f"Expected SVDCluster, got {type(element)}")
        return element

    def _create_cluster(self, node: _Node, parsed_cluster: SVDCluster, index: int) -> Cluster:
        name = parsed_cluster.name if not node.dim_values else node.dim_values[index]

        if node.name in self._derived_base_node_lookup:
            return self._handle_derived_cluster(node, parsed_cluster, index, name)
        else:
            return self._handle_non_derived_cluster(node, parsed_cluster, index, name)

    def _handle_derived_cluster(self, node: _Node, parsed_cluster: SVDCluster, index: int, name: str) -> Cluster:
        base_element = self._derived_base_node_lookup[node.name]

        size = _or_if_none(node.register_properties.size, base_element.size)
        access = _or_if_none(node.register_properties.access, base_element.access)
        protection = _or_if_none(node.register_properties.protection, base_element.protection)
        reset_value = _or_if_none(node.register_properties.reset_value, base_element.reset_value)
        reset_mask = _or_if_none(node.register_properties.reset_mask, base_element.reset_mask)
        description = _or_if_none(parsed_cluster.description, base_element.description)
        alternate_cluster = _or_if_none(parsed_cluster.alternate_cluster, base_element.alternate_cluster)
        header_struct_name = _or_if_none(parsed_cluster.header_struct_name, base_element.header_struct_name)
        address_offset = (
            parsed_cluster.address_offset
            if parsed_cluster.dim_increment is None
            else parsed_cluster.address_offset + parsed_cluster.dim_increment * index
        )
        registers_clusters = self._derive_registers_clusters(node, base_element)

        return Cluster(
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
            registers_clusters=registers_clusters,
            parsed=parsed_cluster,
        )

    def _derive_registers_clusters(self, node: _Node, base_element: Cluster) -> list[Cluster | Register]:
        parsed_registers_clusters = self._processed_registers_clusters.get_processed_register_cluster(node.name)
        base_memory_map = _RegisterClusterMap.build_map_from_registers_clusters(base_element.registers_clusters)
        parsed_memory_map = _RegisterClusterMap.build_map_from_registers_clusters(parsed_registers_clusters)

        base_memory_map.merge_and_overwrite_with(parsed_memory_map)
        return [region[2] for region in base_memory_map.regions]

    def _handle_non_derived_cluster(self, node: _Node, parsed_cluster: SVDCluster, index: int, name: str) -> Cluster:
        size = node.register_properties.size
        access = node.register_properties.access
        protection = node.register_properties.protection
        reset_value = node.register_properties.reset_value
        reset_mask = node.register_properties.reset_mask
        description = parsed_cluster.description
        alternate_cluster = parsed_cluster.alternate_cluster
        header_struct_name = parsed_cluster.header_struct_name
        address_offset = (
            parsed_cluster.address_offset
            if parsed_cluster.dim_increment is None
            else parsed_cluster.address_offset + parsed_cluster.dim_increment * index
        )
        registers_clusters = self._processed_registers_clusters.get_processed_register_cluster(node.name)

        return Cluster(
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
            registers_clusters=registers_clusters,
            parsed=parsed_cluster,
        )

    def _insert_cluster(self, node: _Node, cluster: Cluster) -> None:
        parent_name = ".".join(node.name.split(".")[:-1])
        self._processed_registers_clusters.insert_element(parent_name, cluster)

    def _process_derived_nodes(self, derived_nodes: list[tuple[str, str]], cluster: Cluster) -> None:
        for derived_node_name, base_node_rel_name in derived_nodes:
            if cluster.name == base_node_rel_name:
                self._derived_base_node_lookup[derived_node_name] = cluster


class _ProcessPeripheral:
    def __init__(self, resolver: _Resolver, processed_register_cluster: _ProccessedRegistersClusters) -> None:
        self._resolver = resolver
        self._processed_peripherals: list[Peripheral] = []
        self._processed_registers_clusters = processed_register_cluster
        self._derived_base_node_lookup: dict[str, Peripheral] = {}

    def process_peripheral(self, node: _Node) -> None:
        parsed_peripheral = self._validate_svdperipheral(node.element)
        derived_nodes = self._resolver.find_derived_nodes(node)

        for index in range(parsed_peripheral.dim or 1):
            peripheral = self._create_peripheral(node, parsed_peripheral, index)
            self._insert_peripheral(peripheral)
            self._process_derived_nodes(derived_nodes, peripheral)

    def get_processed_peripherals(self) -> list[Peripheral]:
        return self._processed_peripherals

    def _validate_svdperipheral(self, element: SVDElementTypes) -> SVDPeripheral:
        if not isinstance(element, SVDPeripheral):
            raise ProcessException(f"Expected SVDPeripheral, got {type(element)}")
        return element

    def _create_peripheral(self, node: _Node, parsed_peripheral: SVDPeripheral, index: int) -> Peripheral:
        name = parsed_peripheral.name if not node.dim_values else node.dim_values[index]

        if node.name in self._derived_base_node_lookup:
            return self._handle_derived_peripheral(node, parsed_peripheral, index, name)
        else:
            return self._handle_non_derived_peripheral(node, parsed_peripheral, index, name)

    def _handle_derived_peripheral(
        self, node: _Node, parsed_peripheral: SVDPeripheral, index: int, name: str
    ) -> Peripheral:
        base_element = self._derived_base_node_lookup[node.name]

        size = _or_if_none(node.register_properties.size, base_element.size)
        access = _or_if_none(node.register_properties.access, base_element.access)
        protection = _or_if_none(node.register_properties.protection, base_element.protection)
        reset_value = _or_if_none(node.register_properties.reset_value, base_element.reset_value)
        reset_mask = _or_if_none(node.register_properties.reset_mask, base_element.reset_mask)
        version = _or_if_none(parsed_peripheral.version, base_element.version)
        description = _or_if_none(parsed_peripheral.description, base_element.description)
        alternate_peripheral = _or_if_none(parsed_peripheral.alternate_peripheral, base_element.alternate_peripheral)
        group_name = _or_if_none(parsed_peripheral.group_name, base_element.group_name)
        prepend_to_name = _or_if_none(parsed_peripheral.prepend_to_name, base_element.prepend_to_name)
        append_to_name = _or_if_none(parsed_peripheral.append_to_name, base_element.append_to_name)
        header_struct_name = _or_if_none(parsed_peripheral.header_struct_name, base_element.header_struct_name)
        disable_condition = _or_if_none(parsed_peripheral.disable_condition, base_element.disable_condition)
        base_address = (
            parsed_peripheral.base_address
            if parsed_peripheral.dim_increment is None
            else parsed_peripheral.base_address + parsed_peripheral.dim_increment * index
        )
        address_blocks = self._process_address_blocks(parsed_peripheral.address_blocks, protection)
        if not address_blocks:
            address_blocks = base_element.address_blocks
        interrupts = self._process_interrupts(parsed_peripheral.interrupts)
        registers_clusters = self._derive_registers_clusters(node, base_element)

        return Peripheral(
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
            registers_clusters=registers_clusters,
            parsed=parsed_peripheral,
        )

    def _derive_registers_clusters(self, node: _Node, base_element: Peripheral) -> list[Cluster | Register]:
        parsed_registers_clusters = self._processed_registers_clusters.get_processed_register_cluster(node.name)
        base_memory_map = _RegisterClusterMap.build_map_from_registers_clusters(base_element.registers_clusters)
        parsed_memory_map = _RegisterClusterMap.build_map_from_registers_clusters(parsed_registers_clusters)

        base_memory_map.merge_and_overwrite_with(parsed_memory_map)
        return [region[2] for region in base_memory_map.regions]

    def _handle_non_derived_peripheral(
        self, node: _Node, parsed_peripheral: SVDPeripheral, index: int, name: str
    ) -> Peripheral:
        size = node.register_properties.size
        access = node.register_properties.access
        protection = node.register_properties.protection
        reset_value = node.register_properties.reset_value
        reset_mask = node.register_properties.reset_mask
        version = parsed_peripheral.version
        description = parsed_peripheral.description
        alternate_peripheral = parsed_peripheral.alternate_peripheral
        group_name = parsed_peripheral.group_name
        prepend_to_name = parsed_peripheral.prepend_to_name
        append_to_name = parsed_peripheral.append_to_name
        header_struct_name = parsed_peripheral.header_struct_name
        disable_condition = parsed_peripheral.disable_condition
        base_address = (
            parsed_peripheral.base_address
            if parsed_peripheral.dim_increment is None
            else parsed_peripheral.base_address + parsed_peripheral.dim_increment * index
        )
        address_blocks = self._process_address_blocks(parsed_peripheral.address_blocks, protection)
        interrupts = self._process_interrupts(parsed_peripheral.interrupts)
        registers_clusters = self._processed_registers_clusters.get_processed_register_cluster(node.name)

        return Peripheral(
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
            registers_clusters=registers_clusters,
            parsed=parsed_peripheral,
        )

    def _insert_peripheral(self, peripheral: Peripheral) -> None:
        bisect.insort(self._processed_peripherals, peripheral, key=lambda x: x.base_address)

    def _process_derived_nodes(self, derived_nodes: list[tuple[str, str]], peripheral: Peripheral) -> None:
        for derived_node_name, base_node_rel_name in derived_nodes:
            if peripheral.name == base_node_rel_name:
                self._derived_base_node_lookup[derived_node_name] = peripheral

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


class _ProcessPeripheralElements:
    def __init__(self, parsed_device: SVDDevice) -> None:
        self._resolver = _Resolver(parsed_device)
        self._process_field = _ProcessField(self._resolver)
        self._processed_registers_clusters = _ProccessedRegistersClusters()
        self._process_register = _ProcessRegister(
            self._resolver, self._process_field, self._processed_registers_clusters
        )
        self._process_cluster = _ProcessCluster(
            self._resolver, self._process_register, self._processed_registers_clusters
        )
        self._process_peripheral = _ProcessPeripheral(self._resolver, self._processed_registers_clusters)

    def process_peripherals(self) -> list[Peripheral]:
        while node := self._resolver.resolve_next_node():
            print(f"Resolved node: {node.name}")  # TODO DEBUG

            if isinstance(node.element, SVDPeripheral):
                self._process_peripheral.process_peripheral(node)
            if isinstance(node.element, SVDCluster):
                self._process_cluster.process_cluster(node)
            if isinstance(node.element, SVDRegister):
                self._process_register.process_register(node)
            if isinstance(node.element, SVDField):
                self._process_field.process_field(node)

        return self._process_peripheral.get_processed_peripherals()
