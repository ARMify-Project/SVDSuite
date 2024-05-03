from typing import List, Tuple, Union
from enum import Enum
from dataclasses import dataclass
import lxml.etree


def _append_element(name: str, text: str) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
    element = lxml.etree.Element(name)
    element.text = text
    return element


class CPUNameType(Enum):
    CM0 = "CM0"
    CM0PLUS = "CM0PLUS"
    CM0_PLUS = "CM0+"
    CM1 = "CM1"
    CM3 = "CM3"
    CM4 = "CM4"
    CM7 = "CM7"
    CM23 = "CM23"
    CM33 = "CM33"
    CM35P = "CM35P"
    CM52 = "CM52"
    CM55 = "CM55"
    CM85 = "CM85"
    SC000 = "SC000"
    SC300 = "SC300"
    ARMV8MML = "ARMV8MML"
    ARMV8MBL = "ARMV8MBL"
    ARMV81MML = "ARMV81MML"
    CA5 = "CA5"
    CA7 = "CA7"
    CA8 = "CA8"
    CA9 = "CA9"
    CA15 = "CA15"
    CA17 = "CA17"
    CA53 = "CA53"
    CA57 = "CA57"
    CA72 = "CA72"
    SMC1 = "SMC1"
    OTHER = "other"

    @classmethod
    def from_str(cls, label: str):
        try:
            return CPUNameType[label.upper()]
        except KeyError:
            pass

        if label == "CM0+":
            return cls.CM0_PLUS

        raise NotImplementedError


class EndianType(Enum):
    LITTLE = "little"
    BIG = "big"
    SELECTABLE = "selectable"
    OTHER = "other"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class ProtectionStringType(Enum):
    SECURE = "s"
    NON_SECURE = "n"
    PRIVILEGED = "p"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class SauAccessType(Enum):
    NON_SECURE_CALLABLE = "c"
    NON_SECURE = "n"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class AccessType(Enum):
    READ_ONLY = "read-only"
    WRITE_ONLY = "write-only"
    READ_WRITE = "read-write"
    WRITE_ONCE = "writeOnce"
    READ_WRITE_ONCE = "read-writeOnce"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class EnumeratedTokenType(Enum):
    REGISTERS = "registers"
    BUFFER = "buffer"
    RESERVED = "reserved"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class DataTypeType(Enum):
    UINT8_T = "uint8_t"
    UINT16_T = "uint16_t"
    UINT32_T = "uint32_t"
    UINT64_T = "uint64_t"
    INT8_T = "int8_t"
    INT16_T = "int16_t"
    INT32_T = "int32_t"
    INT64_T = "int64_t"
    UINT8_T_PTR = "uint8_t *"
    UINT16_T_PTR = "uint16_t *"
    UINT32_T_PTR = "uint32_t *"
    UINT64_T_PTR = "uint64_t *"
    INT8_T_PTR = "int8_t *"
    INT16_T_PTR = "int16_t *"
    INT32_T_PTR = "int32_t *"
    INT64_T_PTR = "int64_t *"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class ModifiedWriteValuesType(Enum):
    ONE_TO_CLEAR = "oneToClear"
    ONE_TO_SET = "oneToSet"
    ONE_TO_TOGGLE = "oneToToggle"
    ZERO_TO_CLEAR = "zeroToClear"
    ZERO_TO_SET = "zeroToSet"
    ZERO_TO_TOGGLE = "zeroToToggle"
    CLEAR = "clear"
    SET = "set"
    MODIFY = "modify"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class ReadActionType(Enum):
    CLEAR = "clear"
    SET = "set"
    MODIFY = "modify"
    MODIFY_EXTERNAL = "modifyExternal"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class EnumUsageType(Enum):
    READ = "read"
    WRITE = "write"
    READ_WRITE = "read-write"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


@dataclass
class SVDSauRegion:
    enabled: None | bool
    name: None | str
    base: int
    limit: int
    access: SauAccessType

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("region")

        if self.enabled is not None:
            element.attrib["enabled"] = str(self.enabled).lower()

        if self.name is not None:
            element.attrib["name"] = self.name

        element.append(_append_element("base", text=f"{self.base:#x}"))
        element.append(_append_element("limit", text=f"{self.limit:#x}"))
        element.append(_append_element("access", text=self.access.value))

        return element


@dataclass
class SVDSauRegionsConfig:
    enabled: None | bool
    protection_when_disabled: None | ProtectionStringType
    regions: List[SVDSauRegion]

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("sauRegionsConfig")

        if self.enabled is not None:
            element.attrib["enabled"] = str(self.enabled).lower()

        if self.protection_when_disabled is not None:
            element.attrib["protectionWhenDisabled"] = self.protection_when_disabled.value

        # ensure that we get <sauRegionsConfig ... ></sauRegionsConfig> and not <sauRegionsConfig ... />
        if len(element) == 0 and not self.regions:
            element.text = ""

        for region in self.regions:
            element.append(region.to_xml())

        return element


@dataclass
class SVDCPU:
    name: CPUNameType
    revision: str
    endian: EndianType
    mpu_present: None | bool
    fpu_present: None | bool
    fpu_dp: None | bool
    dsp_present: None | bool
    icache_present: None | bool
    dcache_present: None | bool
    itcm_present: None | bool
    dtcm_present: None | bool
    vtor_present: None | bool
    nvic_prio_bits: int
    vendor_systick_config: bool
    device_num_interrupts: None | int
    sau_num_regions: None | int
    sau_regions_config: None | SVDSauRegionsConfig

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("cpu")

        element.append(_append_element("name", text=self.name.value))
        element.append(_append_element("revision", text=self.revision))
        element.append(_append_element("endian", text=self.endian.value))

        if self.mpu_present is not None:
            element.append(_append_element("mpuPresent", text=str(self.mpu_present).lower()))

        if self.fpu_present is not None:
            element.append(_append_element("fpuPresent", text=str(self.fpu_present).lower()))

        if self.fpu_dp is not None:
            element.append(_append_element("fpuDP", text=str(self.fpu_dp).lower()))

        if self.dsp_present is not None:
            element.append(_append_element("dspPresent", text=str(self.dsp_present).lower()))

        if self.icache_present is not None:
            element.append(_append_element("icachePresent", text=str(self.icache_present).lower()))

        if self.dcache_present is not None:
            element.append(_append_element("dcachePresent", text=str(self.dcache_present).lower()))

        if self.itcm_present is not None:
            element.append(_append_element("itcmPresent", text=str(self.itcm_present).lower()))

        if self.dtcm_present is not None:
            element.append(_append_element("dtcmPresent", text=str(self.dtcm_present).lower()))

        if self.vtor_present is not None:
            element.append(_append_element("vtorPresent", text=str(self.vtor_present).lower()))

        element.append(_append_element("nvicPrioBits", text=str(self.nvic_prio_bits)))
        element.append(_append_element("vendorSystickConfig", text=str(self.vendor_systick_config).lower()))

        if self.device_num_interrupts is not None:
            element.append(_append_element("deviceNumInterrupts", text=str(self.device_num_interrupts)))

        if self.sau_num_regions is not None:
            element.append(_append_element("sauNumRegions", text=str(self.sau_num_regions)))

        if self.sau_regions_config is not None:
            element.append(self.sau_regions_config.to_xml())

        return element


@dataclass
class SVDEnumeratedValueMap:
    name: str
    description: None | str
    value: None | str  # int value, but can contain 'do not care' bits represented by >x<
    is_default: None | bool

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("enumeratedValue")

        element.append(_append_element("name", text=self.name))

        if self.description is not None:
            element.append(_append_element("description", text=self.description))

        if self.value is not None:
            element.append(_append_element("value", text=self.value))

        if self.is_default is not None:
            element.append(_append_element("isDefault", text=str(self.is_default).lower()))

        return element


@dataclass
class SVDDimArrayIndex:
    header_enum_name: None | str
    enumerated_values_map: List[SVDEnumeratedValueMap]

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("dimArrayIndex")

        if self.header_enum_name is not None:
            element.append(_append_element("headerEnumName", text=self.header_enum_name))

        # ensure that we get <dimArrayIndex ... ></dimArrayIndex> and not <dimArrayIndex ... />
        if len(element) == 0 and not self.enumerated_values_map:
            element.text = ""

        for value in self.enumerated_values_map:
            element.append(value.to_xml())

        return element


@dataclass
class _SVDDimElementGroup:
    dim: None | int
    dim_increment: None | int
    dim_index: None | str
    dim_name: None | str
    dim_array_index: None | SVDDimArrayIndex


@dataclass
class _SVDRegisterPropertiesGroup:
    size: None | int
    access: None | AccessType
    protection: None | ProtectionStringType
    reset_value: None | int
    reset_mask: None | int


@dataclass
class SVDAddressBlock:
    offset: int
    size: int
    usage: EnumeratedTokenType
    protection: None | ProtectionStringType

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("addressBlock")

        element.append(_append_element("offset", text=f"{self.offset:#x}"))
        element.append(_append_element("size", text=f"{self.size:#x}"))
        element.append(_append_element("usage", text=self.usage.value))

        if self.protection is not None:
            element.append(_append_element("protection", text=self.protection.value))

        return element


@dataclass
class SVDInterrupt:
    name: str
    description: None | str
    value: int

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("interrupt")

        element.append(_append_element("name", text=self.name))

        if self.description is not None:
            element.append(_append_element("description", text=self.description))

        element.append(_append_element("value", text=str(self.value)))

        return element


@dataclass
class SVDWriteConstraint:
    write_as_read: None | bool
    use_enumerated_values: None | bool
    range_: None | Tuple[int, int]

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("writeConstraint")

        if self.write_as_read is not None:
            element.append(_append_element("writeAsRead", text=str(self.write_as_read).lower()))

        if self.use_enumerated_values is not None:
            element.append(_append_element("useEnumeratedValues", text=str(self.use_enumerated_values).lower()))

        if self.range_ is not None:
            range_element = lxml.etree.Element("range")
            range_element.append(_append_element("minimum", text=str(self.range_[0])))
            range_element.append(_append_element("maximum", text=str(self.range_[1])))
            element.append(range_element)

        # ensure that we get <writeConstraint ... ></writeConstraint> and not <writeConstraint ... />
        if self.write_as_read is None and self.use_enumerated_values is None and self.range_ is None:
            element.text = ""

        return element


@dataclass
class SVDEnumeratedValue:
    name: None | str
    header_enum_name: None | str
    usage: None | EnumUsageType
    enumerated_values_map: List[SVDEnumeratedValueMap]
    derived_from: None | str

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("enumeratedValues")

        if self.derived_from is not None:
            element.attrib["derivedFrom"] = self.derived_from

        if self.name is not None:
            element.append(_append_element("name", text=self.name))

        if self.header_enum_name is not None:
            element.append(_append_element("headerEnumName", text=self.header_enum_name))

        if self.usage is not None:
            element.append(_append_element("usage", text=self.usage.value))

        # ensure that we get <enumeratedValues ... ></enumeratedValues> and not <enumeratedValues ... />
        if len(element) == 0 and not self.enumerated_values_map:
            element.text = ""

        for value in self.enumerated_values_map:
            element.append(value.to_xml())

        return element


@dataclass
class SVDField(_SVDDimElementGroup):
    name: str
    description: None | str
    bit_offset: None | int
    bit_width: None | int
    lsb: None | int
    msb: None | int
    bit_range: None | str
    access: None | AccessType
    modified_write_values: None | ModifiedWriteValuesType
    write_constraint: None | SVDWriteConstraint
    read_action: None | ReadActionType
    enumerated_values: List[SVDEnumeratedValue]
    derived_from: None | str

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("field")

        if self.derived_from is not None:
            element.attrib["derivedFrom"] = self.derived_from

        if self.dim is not None:
            element.append(_append_element("dim", text=str(self.dim)))

        if self.dim_increment is not None:
            element.append(_append_element("dimIncrement", text=str(self.dim_increment)))

        if self.dim_index is not None:
            element.append(_append_element("dimIndex", text=self.dim_index))

        if self.dim_name is not None:
            element.append(_append_element("dimName", text=self.dim_name))

        if self.dim_array_index is not None:
            element.append(self.dim_array_index.to_xml())

        element.append(_append_element("name", text=self.name))

        if self.description is not None:
            element.append(_append_element("description", text=self.description))

        if self.bit_offset is not None and self.bit_width is not None:
            element.append(_append_element("bitOffset", text=str(self.bit_offset)))
            element.append(_append_element("bitWidth", text=str(self.bit_width)))

        if self.lsb is not None and self.msb is not None:
            element.append(_append_element("lsb", text=str(self.lsb)))
            element.append(_append_element("msb", text=str(self.msb)))

        if self.bit_range is not None:
            element.append(_append_element("bitRange", text=self.bit_range))

        if self.access is not None:
            element.append(_append_element("access", text=self.access.value))

        if self.modified_write_values is not None:
            element.append(_append_element("modifiedWriteValues", text=self.modified_write_values.value))

        if self.write_constraint is not None:
            element.append(self.write_constraint.to_xml())

        if self.read_action is not None:
            element.append(_append_element("readAction", text=self.read_action.value))

        for value in self.enumerated_values:
            element.append(value.to_xml())

        return element


@dataclass
class SVDRegister(_SVDDimElementGroup, _SVDRegisterPropertiesGroup):
    name: str
    display_name: None | str
    description: None | str
    alternate_group: None | str
    alternate_register: None | str
    address_offset: int
    data_type: None | DataTypeType
    modified_write_values: None | ModifiedWriteValuesType
    write_constraint: None | SVDWriteConstraint
    read_action: None | ReadActionType
    fields: List[SVDField]
    derived_from: None | str

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("register")

        if self.derived_from is not None:
            element.attrib["derivedFrom"] = self.derived_from

        if self.dim is not None:
            element.append(_append_element("dim", text=str(self.dim)))

        if self.dim_increment is not None:
            element.append(_append_element("dimIncrement", text=str(self.dim_increment)))

        if self.dim_index is not None:
            element.append(_append_element("dimIndex", text=self.dim_index))

        if self.dim_name is not None:
            element.append(_append_element("dimName", text=self.dim_name))

        if self.dim_array_index is not None:
            element.append(self.dim_array_index.to_xml())

        element.append(_append_element("name", text=self.name))

        if self.display_name is not None:
            element.append(_append_element("displayName", text=self.display_name))

        if self.description is not None:
            element.append(_append_element("description", text=self.description))

        if self.alternate_group is not None:
            element.append(_append_element("alternateGroup", text=self.alternate_group))

        if self.alternate_register is not None:
            element.append(_append_element("alternateRegister", text=self.alternate_register))

        element.append(_append_element("addressOffset", text=f"{self.address_offset:#x}"))

        if self.size is not None:
            element.append(_append_element("size", text=str(self.size)))

        if self.access is not None:
            element.append(_append_element("access", text=self.access.value))

        if self.protection is not None:
            element.append(_append_element("protection", text=self.protection.value))

        if self.reset_value is not None:
            element.append(_append_element("resetValue", text=f"{self.reset_value:#x}"))

        if self.reset_mask is not None:
            element.append(_append_element("resetMask", text=f"{self.reset_mask:#x}"))

        if self.data_type is not None:
            element.append(_append_element("dataType", text=self.data_type.value))

        if self.modified_write_values is not None:
            element.append(_append_element("modifiedWriteValues", text=self.modified_write_values.value))

        if self.write_constraint is not None:
            element.append(self.write_constraint.to_xml())

        if self.read_action is not None:
            element.append(_append_element("readAction", text=self.read_action.value))

        if self.fields:
            fields_element = lxml.etree.Element("fields")

            for field in self.fields:
                fields_element.append(field.to_xml())

            element.append(fields_element)

        return element


@dataclass
class SVDCluster(_SVDDimElementGroup, _SVDRegisterPropertiesGroup):
    name: str
    description: None | str
    alternate_cluster: None | str
    header_struct_name: None | str
    address_offset: int
    registers_clusters: List[Union[SVDRegister, "SVDCluster"]]
    derived_from: None | str

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("cluster")

        if self.derived_from is not None:
            element.attrib["derivedFrom"] = self.derived_from

        if self.dim is not None:
            element.append(_append_element("dim", text=str(self.dim)))

        if self.dim_increment is not None:
            element.append(_append_element("dimIncrement", text=str(self.dim_increment)))

        if self.dim_index is not None:
            element.append(_append_element("dimIndex", text=self.dim_index))

        if self.dim_name is not None:
            element.append(_append_element("dimName", text=self.dim_name))

        if self.dim_array_index is not None:
            element.append(self.dim_array_index.to_xml())

        element.append(_append_element("name", text=self.name))

        if self.description is not None:
            element.append(_append_element("description", text=self.description))

        if self.alternate_cluster is not None:
            element.append(_append_element("alternateCluster", text=self.alternate_cluster))

        if self.header_struct_name is not None:
            element.append(_append_element("headerStructName", text=self.header_struct_name))

        element.append(_append_element("addressOffset", text=f"{self.address_offset:#x}"))

        if self.size is not None:
            element.append(_append_element("size", text=str(self.size)))

        if self.access is not None:
            element.append(_append_element("access", text=self.access.value))

        if self.protection is not None:
            element.append(_append_element("protection", text=self.protection.value))

        if self.reset_value is not None:
            element.append(_append_element("resetValue", text=f"{self.reset_value:#x}"))

        if self.reset_mask is not None:
            element.append(_append_element("resetMask", text=f"{self.reset_mask:#x}"))

        for register_cluster in self.registers_clusters:
            element.append(register_cluster.to_xml())

        return element


@dataclass
class SVDPeripheral(_SVDDimElementGroup, _SVDRegisterPropertiesGroup):
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
    address_blocks: List[SVDAddressBlock]
    interrupts: List[SVDInterrupt]
    registers_clusters: List[SVDRegister | SVDCluster]
    derived_from: None | str

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("peripheral")

        if self.derived_from is not None:
            element.attrib["derivedFrom"] = self.derived_from

        if self.dim is not None:
            element.append(_append_element("dim", text=str(self.dim)))

        if self.dim_increment is not None:
            element.append(_append_element("dimIncrement", text=str(self.dim_increment)))

        if self.dim_index is not None:
            element.append(_append_element("dimIndex", text=self.dim_index))

        if self.dim_name is not None:
            element.append(_append_element("dimName", text=self.dim_name))

        if self.dim_array_index is not None:
            element.append(self.dim_array_index.to_xml())

        element.append(_append_element("name", text=self.name))

        if self.version is not None:
            element.append(_append_element("version", text=self.version))

        if self.description is not None:
            element.append(_append_element("description", text=self.description))

        if self.alternate_peripheral is not None:
            element.append(_append_element("alternatePeripheral", text=self.alternate_peripheral))

        if self.group_name is not None:
            element.append(_append_element("groupName", text=self.group_name))

        if self.prepend_to_name is not None:
            element.append(_append_element("prependToName", text=self.prepend_to_name))

        if self.append_to_name is not None:
            element.append(_append_element("appendToName", text=self.append_to_name))

        if self.header_struct_name is not None:
            element.append(_append_element("headerStructName", text=self.header_struct_name))

        if self.disable_condition is not None:
            element.append(_append_element("disableCondition", text=self.disable_condition))

        element.append(_append_element("baseAddress", text=f"{self.base_address:#x}"))

        if self.size is not None:
            element.append(_append_element("size", text=str(self.size)))

        if self.access is not None:
            element.append(_append_element("access", text=self.access.value))

        if self.protection is not None:
            element.append(_append_element("protection", text=self.protection.value))

        if self.reset_value is not None:
            element.append(_append_element("resetValue", text=f"{self.reset_value:#x}"))

        if self.reset_mask is not None:
            element.append(_append_element("resetMask", text=f"{self.reset_mask:#x}"))

        for value in self.address_blocks:
            element.append(value.to_xml())

        for value in self.interrupts:
            element.append(value.to_xml())

        if self.registers_clusters:
            registers_element = lxml.etree.Element("registers")

            for register_cluster in self.registers_clusters:
                registers_element.append(register_cluster.to_xml())

            element.append(registers_element)

        return element


@dataclass
class SVDDevice(_SVDRegisterPropertiesGroup):
    xs_no_namespace_schema_location: str
    schema_version: str
    vendor: None | str
    vendor_id: None | str
    name: str
    series: None | str
    version: str
    description: str
    license_text: None | str
    cpu: None | SVDCPU
    header_system_filename: None | str
    header_definitions_prefix: None | str
    address_unit_bits: int
    width: int
    peripherals: List[SVDPeripheral]

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        _xs = "http://www.w3.org/2001/XMLSchema-instance"

        element = lxml.etree.Element("device", nsmap={"xs": _xs})

        element.attrib[
            lxml.etree.QName(_xs, "noNamespaceSchemaLocation")  # type: ignore
        ] = self.xs_no_namespace_schema_location

        element.attrib["schemaVersion"] = self.schema_version

        if self.vendor is not None:
            element.append(_append_element("vendor", text=self.vendor))

        if self.vendor_id is not None:
            element.append(_append_element("vendorID", text=self.vendor_id))

        element.append(_append_element("name", text=self.name))

        if self.series is not None:
            element.append(_append_element("series", text=self.series))

        element.append(_append_element("version", text=self.version))
        element.append(_append_element("description", text=self.description))

        if self.license_text is not None:
            element.append(_append_element("licenseText", text=self.license_text))

        if self.cpu is not None:
            element.append(self.cpu.to_xml())

        if self.header_system_filename is not None:
            element.append(_append_element("headerSystemFilename", text=self.header_system_filename))

        if self.header_definitions_prefix is not None:
            element.append(_append_element("headerDefinitionsPrefix", text=self.header_definitions_prefix))

        element.append(_append_element("addressUnitBits", text=str(self.address_unit_bits)))
        element.append(_append_element("width", text=str(self.width)))

        if self.size is not None:
            element.append(_append_element("size", text=str(self.size)))

        if self.access is not None:
            element.append(_append_element("access", text=self.access.value))

        if self.protection is not None:
            element.append(_append_element("protection", text=self.protection.value))

        if self.reset_value is not None:
            element.append(_append_element("resetValue", text=f"{self.reset_value:#x}"))

        if self.reset_mask is not None:
            element.append(_append_element("resetMask", text=f"{self.reset_mask:#x}"))

        if self.peripherals:
            peripherals_element = lxml.etree.Element("peripherals")

            for peripheral in self.peripherals:
                peripherals_element.append(peripheral.to_xml())

            element.append(peripherals_element)

        return element
