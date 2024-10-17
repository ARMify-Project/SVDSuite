import lxml.etree
from svdsuite.model.parse import (
    SVDDevice,
    SVDPeripheral,
    SVDCPU,
    SVDSauRegionsConfig,
    SVDSauRegion,
    SVDAddressBlock,
    SVDInterrupt,
    SVDWriteConstraint,
    SVDEnumeratedValueContainer,
    SVDField,
    SVDRegister,
    SVDCluster,
    SVDEnumeratedValue,
    SVDDimArrayIndex,
)


class Serializer:
    @staticmethod
    def device_to_svd_file(path: str, device: SVDDevice, pretty_print: bool = False, xml_declaration: bool = True):
        with open(path, "wb") as f:
            f.write(
                lxml.etree.tostring(
                    SVDDeviceSerializer(device).to_xml(),
                    pretty_print=pretty_print,
                    xml_declaration=xml_declaration,
                    encoding="utf-8",
                )
            )

    @staticmethod
    def device_to_svd_content(device: SVDDevice, pretty_print: bool = False, xml_declaration: bool = True) -> bytes:
        return lxml.etree.tostring(
            SVDDeviceSerializer(device).to_xml(),
            pretty_print=pretty_print,
            xml_declaration=xml_declaration,
            encoding="utf-8",
        )

    @staticmethod
    def device_to_svd_str(device: SVDDevice, pretty_print: bool = False) -> str:
        return Serializer.device_to_svd_content(device, pretty_print=pretty_print).decode()


class XMLSerializable:
    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        raise NotImplementedError("Subclasses should implement this method")

    def _append_element(self, name: str, text: str) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element(name)
        element.text = text
        return element


class SVDSauRegionSerializer(XMLSerializable):
    def __init__(self, region: SVDSauRegion):
        self.region = region

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("region")

        if self.region.enabled is not None:
            element.attrib["enabled"] = str(self.region.enabled).lower()

        if self.region.name is not None:
            element.attrib["name"] = self.region.name

        element.append(self._append_element("base", text=f"{self.region.base:#x}"))
        element.append(self._append_element("limit", text=f"{self.region.limit:#x}"))
        element.append(self._append_element("access", text=self.region.access.value))

        return element


class SVDSauRegionsConfigSerializer(XMLSerializable):
    def __init__(self, config: SVDSauRegionsConfig):
        self.config = config

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("sauRegionsConfig")

        if self.config.enabled is not None:
            element.attrib["enabled"] = str(self.config.enabled).lower()

        if self.config.protection_when_disabled is not None:
            element.attrib["protectionWhenDisabled"] = self.config.protection_when_disabled.value

        # ensure that we get <sauRegionsConfig ... ></sauRegionsConfig> and not <sauRegionsConfig ... />
        if len(element) == 0 and not self.config.regions:
            element.text = ""

        for region in self.config.regions:
            element.append(SVDSauRegionSerializer(region).to_xml())

        return element


class SVDCPUSerializer(XMLSerializable):
    def __init__(self, cpu: SVDCPU):
        self.cpu = cpu

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("cpu")

        element.append(self._append_element("name", text=self.cpu.name.value))
        element.append(self._append_element("revision", text=self.cpu.revision))
        element.append(self._append_element("endian", text=self.cpu.endian.value))

        if self.cpu.mpu_present is not None:
            element.append(self._append_element("mpuPresent", text=str(self.cpu.mpu_present).lower()))

        if self.cpu.fpu_present is not None:
            element.append(self._append_element("fpuPresent", text=str(self.cpu.fpu_present).lower()))

        if self.cpu.fpu_dp is not None:
            element.append(self._append_element("fpuDP", text=str(self.cpu.fpu_dp).lower()))

        if self.cpu.dsp_present is not None:
            element.append(self._append_element("dspPresent", text=str(self.cpu.dsp_present).lower()))

        if self.cpu.icache_present is not None:
            element.append(self._append_element("icachePresent", text=str(self.cpu.icache_present).lower()))

        if self.cpu.dcache_present is not None:
            element.append(self._append_element("dcachePresent", text=str(self.cpu.dcache_present).lower()))

        if self.cpu.itcm_present is not None:
            element.append(self._append_element("itcmPresent", text=str(self.cpu.itcm_present).lower()))

        if self.cpu.dtcm_present is not None:
            element.append(self._append_element("dtcmPresent", text=str(self.cpu.dtcm_present).lower()))

        if self.cpu.vtor_present is not None:
            element.append(self._append_element("vtorPresent", text=str(self.cpu.vtor_present).lower()))

        element.append(self._append_element("nvicPrioBits", text=str(self.cpu.nvic_prio_bits)))
        element.append(self._append_element("vendorSystickConfig", text=str(self.cpu.vendor_systick_config).lower()))

        if self.cpu.device_num_interrupts is not None:
            element.append(self._append_element("deviceNumInterrupts", text=str(self.cpu.device_num_interrupts)))

        if self.cpu.sau_num_regions is not None:
            element.append(self._append_element("sauNumRegions", text=str(self.cpu.sau_num_regions)))

        if self.cpu.sau_regions_config is not None:
            element.append(SVDSauRegionsConfigSerializer(self.cpu.sau_regions_config).to_xml())

        return element


class SVDEnumeratedValueSerializer(XMLSerializable):
    def __init__(self, enumerated_value: SVDEnumeratedValue):
        self.enumerated_value = enumerated_value

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("enumeratedValue")

        element.append(self._append_element("name", text=self.enumerated_value.name))

        if self.enumerated_value.description is not None:
            element.append(self._append_element("description", text=self.enumerated_value.description))

        if self.enumerated_value.value is not None:
            element.append(self._append_element("value", text=str(self.enumerated_value.value)))

        if self.enumerated_value.is_default is not None:
            element.append(self._append_element("isDefault", text=str(self.enumerated_value.is_default).lower()))

        return element


class SVDDimArrayIndexSerializer(XMLSerializable):
    def __init__(self, dim_array_index: SVDDimArrayIndex):
        self.dim_array_index = dim_array_index

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("dimArrayIndex")

        if self.dim_array_index.header_enum_name is not None:
            element.append(self._append_element("headerEnumName", text=self.dim_array_index.header_enum_name))

        # ensure that we get <dimArrayIndex ... ></dimArrayIndex> and not <dimArrayIndex ... />
        if len(element) == 0 and not self.dim_array_index.enumerated_values:
            element.text = ""

        for enumerated_value in self.dim_array_index.enumerated_values:
            element.append(SVDEnumeratedValueSerializer(enumerated_value).to_xml())

        return element


class SVDAddressBlockSerializer(XMLSerializable):
    def __init__(self, block: SVDAddressBlock):
        self.block = block

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("addressBlock")

        element.append(self._append_element("offset", text=f"{self.block.offset:#x}"))
        element.append(self._append_element("size", text=f"{self.block.size:#x}"))
        element.append(self._append_element("usage", text=self.block.usage.value))

        if self.block.protection is not None:
            element.append(self._append_element("protection", text=self.block.protection.value))

        return element


class SVDInterruptSerializer(XMLSerializable):
    def __init__(self, interrupt: SVDInterrupt):
        self.interrupt = interrupt

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("interrupt")

        element.append(self._append_element("name", text=self.interrupt.name))

        if self.interrupt.description is not None:
            element.append(self._append_element("description", text=self.interrupt.description))

        element.append(self._append_element("value", text=str(self.interrupt.value)))

        return element


class SVDWriteConstraintSerializer(XMLSerializable):
    def __init__(self, constraint: SVDWriteConstraint):
        self.constraint = constraint

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("writeConstraint")

        if self.constraint.write_as_read is not None:
            element.append(self._append_element("writeAsRead", text=str(self.constraint.write_as_read).lower()))

        if self.constraint.use_enumerated_values is not None:
            element.append(
                self._append_element("useEnumeratedValues", text=str(self.constraint.use_enumerated_values).lower())
            )

        if self.constraint.range_ is not None:
            range_element = lxml.etree.Element("range")
            range_element.append(self._append_element("minimum", text=str(self.constraint.range_[0])))
            range_element.append(self._append_element("maximum", text=str(self.constraint.range_[1])))
            element.append(range_element)

        # ensure that we get <writeConstraint ... ></writeConstraint> and not <writeConstraint ... />
        if (
            self.constraint.write_as_read is None
            and self.constraint.use_enumerated_values is None
            and self.constraint.range_ is None
        ):
            element.text = ""

        return element


class SVDEnumeratedValueContainerSerializer(XMLSerializable):
    def __init__(self, value: SVDEnumeratedValueContainer):
        self.value = value

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("enumeratedValues")

        if self.value.derived_from is not None:
            element.attrib["derivedFrom"] = self.value.derived_from

        if self.value.name is not None:
            element.append(self._append_element("name", text=self.value.name))

        if self.value.header_enum_name is not None:
            element.append(self._append_element("headerEnumName", text=self.value.header_enum_name))

        if self.value.usage is not None:
            element.append(self._append_element("usage", text=self.value.usage.value))

        # ensure that we get <enumeratedValues ... ></enumeratedValues> and not <enumeratedValues ... />
        if len(element) == 0 and not self.value.enumerated_values:
            element.text = ""

        for enumerated_value in self.value.enumerated_values:
            element.append(SVDEnumeratedValueSerializer(enumerated_value).to_xml())

        return element


class SVDFieldSerializer(XMLSerializable):
    def __init__(self, field: SVDField):
        self.field = field

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("field")

        if self.field.derived_from is not None:
            element.attrib["derivedFrom"] = self.field.derived_from

        if self.field.dim is not None:
            element.append(self._append_element("dim", text=str(self.field.dim)))

        if self.field.dim_increment is not None:
            element.append(self._append_element("dimIncrement", text=str(self.field.dim_increment)))

        if self.field.dim_index is not None:
            element.append(self._append_element("dimIndex", text=self.field.dim_index))

        if self.field.dim_name is not None:
            element.append(self._append_element("dimName", text=self.field.dim_name))

        if self.field.dim_array_index is not None:
            element.append(SVDDimArrayIndexSerializer(self.field.dim_array_index).to_xml())

        element.append(self._append_element("name", text=self.field.name))

        if self.field.description is not None:
            element.append(self._append_element("description", text=self.field.description))

        if self.field.bit_offset is not None and self.field.bit_width is not None:
            element.append(self._append_element("bitOffset", text=str(self.field.bit_offset)))
            element.append(self._append_element("bitWidth", text=str(self.field.bit_width)))

        if self.field.lsb is not None and self.field.msb is not None:
            element.append(self._append_element("lsb", text=str(self.field.lsb)))
            element.append(self._append_element("msb", text=str(self.field.msb)))

        if self.field.bit_range is not None:
            element.append(self._append_element("bitRange", text=self.field.bit_range))

        if self.field.access is not None:
            element.append(self._append_element("access", text=self.field.access.value))

        if self.field.modified_write_values is not None:
            element.append(self._append_element("modifiedWriteValues", text=self.field.modified_write_values.value))

        if self.field.write_constraint is not None:
            element.append(SVDWriteConstraintSerializer(self.field.write_constraint).to_xml())

        if self.field.read_action is not None:
            element.append(self._append_element("readAction", text=self.field.read_action.value))

        for value in self.field.enumerated_value_containers:
            element.append(SVDEnumeratedValueContainerSerializer(value).to_xml())

        return element


class SVDRegisterSerializer(XMLSerializable):
    def __init__(self, register: SVDRegister):
        self.register = register

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("register")

        if self.register.derived_from is not None:
            element.attrib["derivedFrom"] = self.register.derived_from

        if self.register.dim is not None:
            element.append(self._append_element("dim", text=str(self.register.dim)))

        if self.register.dim_increment is not None:
            element.append(self._append_element("dimIncrement", text=str(self.register.dim_increment)))

        if self.register.dim_index is not None:
            element.append(self._append_element("dimIndex", text=self.register.dim_index))

        if self.register.dim_name is not None:
            element.append(self._append_element("dimName", text=self.register.dim_name))

        if self.register.dim_array_index is not None:
            element.append(SVDDimArrayIndexSerializer(self.register.dim_array_index).to_xml())

        element.append(self._append_element("name", text=self.register.name))

        if self.register.display_name is not None:
            element.append(self._append_element("displayName", text=self.register.display_name))

        if self.register.description is not None:
            element.append(self._append_element("description", text=self.register.description))

        if self.register.alternate_group is not None:
            element.append(self._append_element("alternateGroup", text=self.register.alternate_group))

        if self.register.alternate_register is not None:
            element.append(self._append_element("alternateRegister", text=self.register.alternate_register))

        element.append(self._append_element("addressOffset", text=f"{self.register.address_offset:#x}"))

        if self.register.size is not None:
            element.append(self._append_element("size", text=str(self.register.size)))

        if self.register.access is not None:
            element.append(self._append_element("access", text=self.register.access.value))

        if self.register.protection is not None:
            element.append(self._append_element("protection", text=self.register.protection.value))

        if self.register.reset_value is not None:
            element.append(self._append_element("resetValue", text=f"{self.register.reset_value:#x}"))

        if self.register.reset_mask is not None:
            element.append(self._append_element("resetMask", text=f"{self.register.reset_mask:#x}"))

        if self.register.data_type is not None:
            element.append(self._append_element("dataType", text=self.register.data_type.value))

        if self.register.modified_write_values is not None:
            element.append(self._append_element("modifiedWriteValues", text=self.register.modified_write_values.value))

        if self.register.write_constraint is not None:
            element.append(SVDWriteConstraintSerializer(self.register.write_constraint).to_xml())

        if self.register.read_action is not None:
            element.append(self._append_element("readAction", text=self.register.read_action.value))

        if self.register.fields:
            fields_element = lxml.etree.Element("fields")

            for field in self.register.fields:
                fields_element.append(SVDFieldSerializer(field).to_xml())

            element.append(fields_element)

        return element


class SVDClusterSerializer(XMLSerializable):
    def __init__(self, cluster: SVDCluster):
        self.cluster = cluster

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("cluster")

        if self.cluster.derived_from is not None:
            element.attrib["derivedFrom"] = self.cluster.derived_from

        if self.cluster.dim is not None:
            element.append(self._append_element("dim", text=str(self.cluster.dim)))

        if self.cluster.dim_increment is not None:
            element.append(self._append_element("dimIncrement", text=str(self.cluster.dim_increment)))

        if self.cluster.dim_index is not None:
            element.append(self._append_element("dimIndex", text=self.cluster.dim_index))

        if self.cluster.dim_name is not None:
            element.append(self._append_element("dimName", text=self.cluster.dim_name))

        if self.cluster.dim_array_index is not None:
            element.append(SVDDimArrayIndexSerializer(self.cluster.dim_array_index).to_xml())

        element.append(self._append_element("name", text=self.cluster.name))

        if self.cluster.description is not None:
            element.append(self._append_element("description", text=self.cluster.description))

        if self.cluster.alternate_cluster is not None:
            element.append(self._append_element("alternateCluster", text=self.cluster.alternate_cluster))

        if self.cluster.header_struct_name is not None:
            element.append(self._append_element("headerStructName", text=self.cluster.header_struct_name))

        element.append(self._append_element("addressOffset", text=f"{self.cluster.address_offset:#x}"))

        if self.cluster.size is not None:
            element.append(self._append_element("size", text=str(self.cluster.size)))

        if self.cluster.access is not None:
            element.append(self._append_element("access", text=self.cluster.access.value))

        if self.cluster.protection is not None:
            element.append(self._append_element("protection", text=self.cluster.protection.value))

        if self.cluster.reset_value is not None:
            element.append(self._append_element("resetValue", text=f"{self.cluster.reset_value:#x}"))

        if self.cluster.reset_mask is not None:
            element.append(self._append_element("resetMask", text=f"{self.cluster.reset_mask:#x}"))

        for register_cluster in self.cluster.registers_clusters:
            if isinstance(register_cluster, SVDRegister):
                element.append(SVDRegisterSerializer(register_cluster).to_xml())
            if isinstance(register_cluster, SVDCluster):
                element.append(SVDClusterSerializer(register_cluster).to_xml())

        return element


class SVDPeripheralSerializer(XMLSerializable):
    def __init__(self, peripheral: SVDPeripheral):
        self.peripheral = peripheral

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        element = lxml.etree.Element("peripheral")

        if self.peripheral.derived_from is not None:
            element.attrib["derivedFrom"] = self.peripheral.derived_from

        if self.peripheral.dim is not None:
            element.append(self._append_element("dim", text=str(self.peripheral.dim)))

        if self.peripheral.dim_increment is not None:
            element.append(self._append_element("dimIncrement", text=str(self.peripheral.dim_increment)))

        if self.peripheral.dim_index is not None:
            element.append(self._append_element("dimIndex", text=self.peripheral.dim_index))

        if self.peripheral.dim_name is not None:
            element.append(self._append_element("dimName", text=self.peripheral.dim_name))

        if self.peripheral.dim_array_index is not None:
            element.append(SVDDimArrayIndexSerializer(self.peripheral.dim_array_index).to_xml())

        element.append(self._append_element("name", text=self.peripheral.name))

        if self.peripheral.version is not None:
            element.append(self._append_element("version", text=self.peripheral.version))

        if self.peripheral.description is not None:
            element.append(self._append_element("description", text=self.peripheral.description))

        if self.peripheral.alternate_peripheral is not None:
            element.append(self._append_element("alternatePeripheral", text=self.peripheral.alternate_peripheral))

        if self.peripheral.group_name is not None:
            element.append(self._append_element("groupName", text=self.peripheral.group_name))

        if self.peripheral.prepend_to_name is not None:
            element.append(self._append_element("prependToName", text=self.peripheral.prepend_to_name))

        if self.peripheral.append_to_name is not None:
            element.append(self._append_element("appendToName", text=self.peripheral.append_to_name))

        if self.peripheral.header_struct_name is not None:
            element.append(self._append_element("headerStructName", text=self.peripheral.header_struct_name))

        if self.peripheral.disable_condition is not None:
            element.append(self._append_element("disableCondition", text=self.peripheral.disable_condition))

        element.append(self._append_element("baseAddress", text=f"{self.peripheral.base_address:#x}"))

        if self.peripheral.size is not None:
            element.append(self._append_element("size", text=str(self.peripheral.size)))

        if self.peripheral.access is not None:
            element.append(self._append_element("access", text=self.peripheral.access.value))

        if self.peripheral.protection is not None:
            element.append(self._append_element("protection", text=self.peripheral.protection.value))

        if self.peripheral.reset_value is not None:
            element.append(self._append_element("resetValue", text=f"{self.peripheral.reset_value:#x}"))

        if self.peripheral.reset_mask is not None:
            element.append(self._append_element("resetMask", text=f"{self.peripheral.reset_mask:#x}"))

        for value in self.peripheral.address_blocks:
            element.append(SVDAddressBlockSerializer(value).to_xml())

        for value in self.peripheral.interrupts:
            element.append(SVDInterruptSerializer(value).to_xml())

        if self.peripheral.registers_clusters:
            registers_element = lxml.etree.Element("registers")

            for register_cluster in self.peripheral.registers_clusters:
                if isinstance(register_cluster, SVDRegister):
                    registers_element.append(SVDRegisterSerializer(register_cluster).to_xml())
                if isinstance(register_cluster, SVDCluster):
                    registers_element.append(SVDClusterSerializer(register_cluster).to_xml())

            element.append(registers_element)

        return element


class SVDDeviceSerializer(XMLSerializable):
    def __init__(self, device: SVDDevice):
        self.device = device

    def to_xml(self) -> lxml.etree._Element:  # pyright: ignore[reportPrivateUsage]
        _xs = "http://www.w3.org/2001/XMLSchema-instance"

        element = lxml.etree.Element("device", nsmap={"xs": _xs})

        element.attrib[
            lxml.etree.QName(_xs, "noNamespaceSchemaLocation")  # type: ignore
        ] = self.device.xs_no_namespace_schema_location

        element.attrib["schemaVersion"] = self.device.schema_version

        if self.device.vendor is not None:
            element.append(self._append_element("vendor", text=self.device.vendor))

        if self.device.vendor_id is not None:
            element.append(self._append_element("vendorID", text=self.device.vendor_id))

        element.append(self._append_element("name", text=self.device.name))

        if self.device.series is not None:
            element.append(self._append_element("series", text=self.device.series))

        element.append(self._append_element("version", text=self.device.version))
        element.append(self._append_element("description", text=self.device.description))

        if self.device.license_text is not None:
            element.append(self._append_element("licenseText", text=self.device.license_text))

        if self.device.cpu is not None:
            element.append(SVDCPUSerializer(self.device.cpu).to_xml())

        if self.device.header_system_filename is not None:
            element.append(self._append_element("headerSystemFilename", text=self.device.header_system_filename))

        if self.device.header_definitions_prefix is not None:
            element.append(self._append_element("headerDefinitionsPrefix", text=self.device.header_definitions_prefix))

        element.append(self._append_element("addressUnitBits", text=str(self.device.address_unit_bits)))
        element.append(self._append_element("width", text=str(self.device.width)))

        if self.device.size is not None:
            element.append(self._append_element("size", text=str(self.device.size)))

        if self.device.access is not None:
            element.append(self._append_element("access", text=self.device.access.value))

        if self.device.protection is not None:
            element.append(self._append_element("protection", text=self.device.protection.value))

        if self.device.reset_value is not None:
            element.append(self._append_element("resetValue", text=f"{self.device.reset_value:#x}"))

        if self.device.reset_mask is not None:
            element.append(self._append_element("resetMask", text=f"{self.device.reset_mask:#x}"))

        if self.device.peripherals:
            peripherals_element = lxml.etree.Element("peripherals")

            for peripheral in self.device.peripherals:
                peripherals_element.append(SVDPeripheralSerializer(peripheral).to_xml())

            element.append(peripherals_element)

        return element
