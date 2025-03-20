import warnings
from typing import Literal, Optional, overload

import lxml.etree

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
from svdsuite.util.parser_exception_warning import ParserException, ParserWarning, custom_warning_format
from svdsuite.util.xml_parse import safe_parse, safe_fromstring

warnings.formatwarning = custom_warning_format


@overload
def _to_bool(value: str, default: None = None) -> bool: ...


@overload
def _to_bool(value: None | str, default: bool) -> bool: ...


def _to_bool(value: None | str, default: None | bool = None) -> bool:
    if value is None and default is not None:
        return default

    if value is not None and value.lower() == "true":
        return True

    if value is not None and value.lower() == "false":
        return False

    if value is not None and value == "1":
        return True

    if value is not None and value == "0":
        return False

    raise NotImplementedError(f"can't parse value '{value}' in function _to_bool")


def _to_none_or_bool(value: None | str) -> None | bool:
    if value is None:
        return None

    return _to_bool(value)


@overload
def _to_int(value: str, base: int = 0) -> int: ...


@overload
def _to_int(value: None | str, base: int = 0) -> None | int: ...


def _to_int(value: None | str, base: int = 0) -> None | int:
    if value is None:
        return None

    # transfer binary value to a string int function can handle
    value = value.replace("#", "0b")

    try:
        return int(value, base)
    except ValueError as exc:
        try:
            return int(value)
        except ValueError:
            raise NotImplementedError(f"can't parse value '{value}' in function _to_int") from exc


class Parser:
    @classmethod
    def from_svd_file(cls, path: str):
        return cls(safe_parse(path))

    @staticmethod
    def from_xml_str(xml_str: str):
        return Parser.from_xml_content(xml_str.encode())

    @classmethod
    def from_xml_content(cls, content: bytes):
        return cls(safe_fromstring(content).getroottree())

    def __init__(self, tree: lxml.etree._ElementTree) -> None:  # pyright: ignore[reportPrivateUsage]
        self._parsed_device = self._parse_device(tree.getroot())

    def get_parsed_device(self) -> SVDDevice:
        return self._parsed_device

    @overload
    def _parse_element_text(
        self,
        element_name: str,
        parent: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
        strip: bool = True,
        optional: Literal[False] = False,
    ) -> str: ...

    @overload
    def _parse_element_text(
        self,
        element_name: str,
        parent: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
        strip: bool = True,
        optional: Literal[True] = True,
    ) -> None | str: ...

    def _parse_element_text(
        self,
        element_name: str,
        parent: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
        strip: bool = True,
        optional: bool = False,
    ) -> None | str:
        elements = parent.findall(element_name)

        if len(elements) > 1:
            texts = ", ".join([x.text for x in elements])  # type: ignore[union-attr]
            lines = ", ".join([str(x.sourceline) for x in elements])
            warnings.warn(
                f"Multiple elements '{element_name}' with texts '{texts}' found at svd file source lines '{lines}'. "
                "To be compatible with SVDConv, only the last one will be used",
                ParserWarning,
            )

        if not elements:
            if not optional:
                raise ParserException(f"can't get element '{element_name}'")
            return None

        element = elements[-1]
        if element.text is None:
            if not optional:
                raise ParserException(f"can't get element '{element_name}'")
            return None

        text_before_strip = element.text

        if not strip:
            return text_before_strip

        text_after_strip = text_before_strip.strip()

        if text_before_strip != text_after_strip:
            warnings.warn(
                f"Element '{element_name}' has been stripped from '{text_before_strip}' to '{text_after_strip}'",
                ParserWarning,
            )

        return text_after_strip

    @overload
    def _parse_element_attribute(
        self,
        attribute_name: str,
        element: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
        strip: bool = True,
        optional: Literal[False] = False,
    ) -> str: ...

    @overload
    def _parse_element_attribute(
        self,
        attribute_name: str,
        element: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
        strip: bool = True,
        optional: Literal[True] = True,
    ) -> None | str: ...

    def _parse_element_attribute(
        self,
        attribute_name: str,
        element: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
        strip: bool = True,
        optional: bool = False,
    ) -> None | str:
        attr_before_strip = element.get(attribute_name)

        if attr_before_strip is None:
            if not optional:
                raise ParserException(f"can't get attribute '{attribute_name}' for current element")
            return None

        if not strip:
            return attr_before_strip

        attr_after_strip = attr_before_strip.strip()

        if attr_before_strip != attr_after_strip:
            warnings.warn(
                f"Attribute '{attribute_name}' has been stripped from '{attr_before_strip}' to '{attr_after_strip}'",
                ParserWarning,
            )

        return attr_after_strip

    def _parse_device(self, device_element: lxml.etree._Element) -> SVDDevice:  # pyright: ignore[reportPrivateUsage]
        try:
            ns_key = "xs" if "xs" in device_element.nsmap else "xsi"
            xs_no_namesp = self._parse_element_attribute(
                f"{{{device_element.nsmap[ns_key]}}}noNamespaceSchemaLocation", device_element, optional=False
            )
        except (ParserException, KeyError):
            warnings.warn(
                "Can't find noNamespaceSchemaLocation attribute in the device element. Set to empty string",
                ParserWarning,
            )
            xs_no_namesp = ""

        schema_version = self._parse_element_attribute("schemaVersion", device_element, optional=False)
        vendor = self._parse_element_text("vendor", device_element, optional=True)
        vendor_id = self._parse_element_text("vendorID", device_element, optional=True)
        name = self._parse_element_text("name", device_element, optional=False)
        series = self._parse_element_text("series", device_element, optional=True)
        version = self._parse_element_text("version", device_element, optional=False)

        # dirty hack to handle the case where description is not present although it is required
        # (e.g. DialogSemiconductor.DA1468x_DFP.1.1.3/DA14681.svd)
        description = self._parse_element_text("description", device_element, strip=False, optional=True)
        if description is None:
            warnings.warn("Mandatory description is missing in the device element. Set to empty string", ParserWarning)
            description = ""

        license_text = self._parse_element_text("licenseText", device_element, strip=False, optional=True)
        cpu = self._parse_cpu(device_element)
        header_system_filename = self._parse_element_text("headerSystemFilename", device_element, optional=True)
        header_definitions_prefix = self._parse_element_text("headerDefinitionsPrefix", device_element, optional=True)
        address_unit_bits = _to_int(self._parse_element_text("addressUnitBits", device_element, optional=False))
        width = _to_int(self._parse_element_text("width", device_element, optional=False))
        size, access, protection, reset_value, reset_mask = self._parse_register_properties(device_element)
        peripherals = self._parse_peripherals(device_element)

        device = SVDDevice(
            xs_no_namespace_schema_location=xs_no_namesp,
            schema_version=schema_version,
            vendor=vendor,
            vendor_id=vendor_id,
            name=name,
            series=series,
            version=version,
            description=description,
            license_text=license_text,
            cpu=cpu,
            header_system_filename=header_system_filename,
            header_definitions_prefix=header_definitions_prefix,
            address_unit_bits=address_unit_bits,
            width=width,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            peripherals=peripherals,
        )

        if device.cpu is not None:
            device.cpu.parent = device

        for peripheral in device.peripherals:
            peripheral.parent = device

        return device

    def _parse_register_properties(
        self, element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> tuple[Optional[int], Optional[AccessType], Optional[ProtectionStringType], Optional[int], Optional[int]]:
        size = _to_int(self._parse_element_text("size", element, optional=True))
        access = self._parse_element_text("access", element, optional=True)
        protection = self._parse_element_text("protection", element, optional=True)
        reset_value = _to_int(self._parse_element_text("resetValue", element, optional=True))
        reset_mask = _to_int(self._parse_element_text("resetMask", element, optional=True))

        if access is not None:
            access = AccessType.from_str(access)

        if protection is not None:
            protection = ProtectionStringType.from_str(protection)

        return size, access, protection, reset_value, reset_mask

    def _parse_cpu(self, device_element: lxml.etree._Element) -> None | SVDCPU:  # pyright: ignore[reportPrivateUsage]
        cpu_element = device_element.find("cpu")

        if cpu_element is None:
            return None

        name = CPUNameType.from_str(self._parse_element_text("name", cpu_element, optional=False))
        revision = self._parse_element_text("revision", cpu_element, optional=False)
        endian = EndianType.from_str(self._parse_element_text("endian", cpu_element, optional=False))
        mpu_present = _to_none_or_bool(self._parse_element_text("mpuPresent", cpu_element, optional=True))
        fpu_present = _to_none_or_bool(self._parse_element_text("fpuPresent", cpu_element, optional=True))
        fpu_dp = _to_none_or_bool(self._parse_element_text("fpuDP", cpu_element, optional=True))
        dsp_present = _to_none_or_bool(self._parse_element_text("dspPresent", cpu_element, optional=True))
        icache_present = _to_none_or_bool(self._parse_element_text("icachePresent", cpu_element, optional=True))
        dcache_present = _to_none_or_bool(self._parse_element_text("dcachePresent", cpu_element, optional=True))
        itcm_present = _to_none_or_bool(self._parse_element_text("itcmPresent", cpu_element, optional=True))
        dtcm_present = _to_none_or_bool(self._parse_element_text("dtcmPresent", cpu_element, optional=True))
        vtor_present = _to_none_or_bool(self._parse_element_text("vtorPresent", cpu_element, optional=True))
        nvic_prio_bits = _to_int(self._parse_element_text("nvicPrioBits", cpu_element, optional=False))
        vendor_systick_config = _to_bool(
            self._parse_element_text("vendorSystickConfig", cpu_element, optional=False), default=False
        )
        device_num_interrupts = _to_int(self._parse_element_text("deviceNumInterrupts", cpu_element, optional=True))
        sau_num_regions = _to_int(self._parse_element_text("sauNumRegions", cpu_element, optional=True))
        sau_regions_config = self._parse_sau_regions_config(cpu_element)

        cpu = SVDCPU(
            name=name,
            revision=revision,
            endian=endian,
            mpu_present=mpu_present,
            fpu_present=fpu_present,
            fpu_dp=fpu_dp,
            dsp_present=dsp_present,
            icache_present=icache_present,
            dcache_present=dcache_present,
            itcm_present=itcm_present,
            dtcm_present=dtcm_present,
            vtor_present=vtor_present,
            nvic_prio_bits=nvic_prio_bits,
            vendor_systick_config=vendor_systick_config,
            device_num_interrupts=device_num_interrupts,
            sau_num_regions=sau_num_regions,
            sau_regions_config=sau_regions_config,
        )

        if cpu.sau_regions_config is not None:
            cpu.sau_regions_config.parent = cpu

        return cpu

    def _parse_sau_regions_config(
        self, cpu_element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> None | SVDSauRegionsConfig:
        config_element = cpu_element.find("sauRegionsConfig")

        if config_element is None:
            return None

        enabled = _to_none_or_bool(self._parse_element_attribute("enabled", config_element, optional=True))
        protection_when_disabled = self._parse_element_attribute(
            "protectionWhenDisabled", config_element, optional=True
        )
        regions = self._parse_sau_regions(config_element)

        if protection_when_disabled is not None:
            protection_when_disabled = ProtectionStringType.from_str(protection_when_disabled)

        sau_regions_config = SVDSauRegionsConfig(
            enabled=enabled,
            protection_when_disabled=protection_when_disabled,
            regions=regions,
        )

        for region in sau_regions_config.regions:
            region.parent = sau_regions_config

        return sau_regions_config

    def _parse_sau_regions(
        self, config_element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> list[SVDSauRegion]:
        regions: list[SVDSauRegion] = []
        for region_element in config_element.findall("region"):
            enabled = _to_none_or_bool(self._parse_element_attribute("enabled", region_element, optional=True))
            name = self._parse_element_attribute("name", region_element, optional=True)
            base = _to_int(self._parse_element_text("base", region_element, optional=False))
            limit = _to_int(self._parse_element_text("limit", region_element, optional=False))
            access = SauAccessType.from_str(self._parse_element_text("access", region_element, optional=False))

            regions.append(SVDSauRegion(enabled=enabled, name=name, base=base, limit=limit, access=access))

        return regions

    def _parse_peripherals(
        self, device_element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> list[SVDPeripheral]:
        peripherals_element = device_element.find("peripherals")

        if peripherals_element is None:
            raise ParserException("can't find peripherals element")

        peripherals: list[SVDPeripheral] = []
        for peripheral_element in peripherals_element.findall("peripheral"):
            derived_from = self._parse_element_attribute("derivedFrom", peripheral_element, optional=True)
            name = self._parse_element_text("name", peripheral_element, optional=False)
            version = self._parse_element_text("version", peripheral_element, optional=True)
            description = self._parse_element_text("description", peripheral_element, strip=False, optional=True)
            alternate_peripheral = self._parse_element_text("alternatePeripheral", peripheral_element, optional=True)
            group_name = self._parse_element_text("groupName", peripheral_element, optional=True)
            prepend_to_name = self._parse_element_text("prependToName", peripheral_element, optional=True)
            append_to_name = self._parse_element_text("appendToName", peripheral_element, optional=True)
            header_struct_name = self._parse_element_text("headerStructName", peripheral_element, optional=True)
            disable_condition = self._parse_element_text(
                "disableCondition", peripheral_element, strip=False, optional=True
            )
            base_address = _to_int(self._parse_element_text("baseAddress", peripheral_element, optional=False))
            address_blocks = self._parse_address_blocks(peripheral_element)
            interrupts = self._parse_interrupts(peripheral_element)

            # Some svd files have multiple <registers> elements in a <peripheral> element (not allowed by the schema)
            # To be compatible with SVDConv, all <registers> elements are parsed
            registers_clusters: list[SVDRegister | SVDCluster] = []
            for registers_element in peripheral_element.findall("registers"):
                registers_clusters.extend(self._parse_registers_clusters(registers_element))

            dim, dim_increment, dim_index, dim_name, dim_array_index = self._parse_dim_element_group(peripheral_element)

            size, access, protection, reset_value, reset_mask = self._parse_register_properties(peripheral_element)

            peripheral = SVDPeripheral(
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
                dim=dim,
                dim_increment=dim_increment,
                dim_index=dim_index,
                dim_name=dim_name,
                dim_array_index=dim_array_index,
                size=size,
                access=access,
                protection=protection,
                reset_value=reset_value,
                reset_mask=reset_mask,
                derived_from=derived_from,
            )

            for address_block in peripheral.address_blocks:
                address_block.parent = peripheral

            for interrupt in peripheral.interrupts:
                interrupt.parent = peripheral

            for register_cluster in peripheral.registers_clusters:
                register_cluster.parent = peripheral

            if peripheral.dim_array_index is not None:
                peripheral.dim_array_index.parent = peripheral

            peripherals.append(peripheral)

        return peripherals

    def _parse_register(self, register_element: lxml.etree._Element):  # pyright: ignore[reportPrivateUsage]
        derived_from = self._parse_element_attribute("derivedFrom", register_element, optional=True)
        name = self._parse_element_text("name", register_element, optional=False)
        display_name = self._parse_element_text("displayName", register_element, optional=True)
        description = self._parse_element_text("description", register_element, strip=False, optional=True)
        alternate_group = self._parse_element_text("alternateGroup", register_element, optional=True)
        alternate_register = self._parse_element_text("alternateRegister", register_element, optional=True)
        address_offset = _to_int(self._parse_element_text("addressOffset", register_element, optional=False))
        data_type = self._parse_element_text("dataType", register_element, optional=True)
        modified_write_values = self._parse_element_text("modifiedWriteValues", register_element, optional=True)
        write_constraint = self._parse_write_constraint(register_element)
        read_action = self._parse_element_text("readAction", register_element, optional=True)
        fields = self._parse_fields(register_element)

        dim, dim_increment, dim_index, dim_name, dim_array_index = self._parse_dim_element_group(register_element)

        size, access, protection, reset_value, reset_mask = self._parse_register_properties(register_element)

        if data_type is not None:
            data_type = DataTypeType.from_str(data_type)

        if modified_write_values is not None:
            modified_write_values = ModifiedWriteValuesType.from_str(modified_write_values)

        if read_action is not None:
            read_action = ReadActionType.from_str(read_action)

        register = SVDRegister(
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
            dim=dim,
            dim_increment=dim_increment,
            dim_index=dim_index,
            dim_name=dim_name,
            dim_array_index=dim_array_index,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            derived_from=derived_from,
        )

        if register.write_constraint is not None:
            register.write_constraint.parent = register

        for field in register.fields:
            field.parent = register

        if register.dim_array_index is not None:
            register.dim_array_index.parent = register

        return register

    def _parse_fields(
        self, register_element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> list[SVDField]:
        # Some svd files have multiple <fields> elements in a <register> element (not allowed by the schema)
        # To be compatible with SVDConv, all <fields> elements are parsed
        fields_elements = register_element.findall("fields")
        if not fields_elements:
            return []

        fields: list[SVDField] = []
        for fields_element in fields_elements:
            for field_element in fields_element.findall("field"):
                derived_from = self._parse_element_attribute("derivedFrom", field_element, optional=True)
                name = self._parse_element_text("name", field_element, optional=False)
                description = self._parse_element_text("description", field_element, strip=False, optional=True)
                bit_offset = _to_int(self._parse_element_text("bitOffset", field_element, optional=True))
                bit_width = _to_int(self._parse_element_text("bitWidth", field_element, optional=True))
                lsb = _to_int(self._parse_element_text("lsb", field_element, optional=True))
                msb = _to_int(self._parse_element_text("msb", field_element, optional=True))
                bit_range = self._parse_element_text("bitRange", field_element, optional=True)
                access = self._parse_element_text("access", field_element, optional=True)
                modified_write_values = self._parse_element_text("modifiedWriteValues", field_element, optional=True)
                write_constraint = self._parse_write_constraint(field_element)
                read_action = self._parse_element_text("readAction", field_element, optional=True)
                enumerated_value_containers = self._parse_enumerated_value_containers(field_element)

                dim, dim_increment, dim_index, dim_name, dim_array_index = self._parse_dim_element_group(field_element)

                if access is not None:
                    access = AccessType.from_str(access)

                if modified_write_values is not None:
                    modified_write_values = ModifiedWriteValuesType.from_str(modified_write_values)

                if read_action is not None:
                    read_action = ReadActionType.from_str(read_action)

                field = SVDField(
                    name=name,
                    description=description,
                    bit_offset=bit_offset,
                    bit_width=bit_width,
                    lsb=lsb,
                    msb=msb,
                    bit_range=bit_range,
                    access=access,
                    modified_write_values=modified_write_values,
                    write_constraint=write_constraint,
                    read_action=read_action,
                    enumerated_value_containers=enumerated_value_containers,
                    dim=dim,
                    dim_increment=dim_increment,
                    dim_index=dim_index,
                    dim_name=dim_name,
                    dim_array_index=dim_array_index,
                    derived_from=derived_from,
                )

                if field.write_constraint is not None:
                    field.write_constraint.parent = field

                for enumerated_value_container in field.enumerated_value_containers:
                    enumerated_value_container.parent = field

                if field.dim_array_index is not None:
                    field.dim_array_index.parent = field

                fields.append(field)

        return fields

    def _parse_enumerated_value_containers(
        self, field_element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> list[SVDEnumeratedValueContainer]:
        enumerated_value_containers: list[SVDEnumeratedValueContainer] = []
        for container_element in field_element.findall("enumeratedValues"):
            derived_from = self._parse_element_attribute("derivedFrom", container_element, optional=True)
            name = self._parse_element_text("name", container_element, optional=True)
            header_enum_name = self._parse_element_text("headerEnumName", container_element, optional=True)
            usage = self._parse_element_text("usage", container_element, optional=True)
            enumerated_values = self._parse_enumerated_values(container_element)

            if usage is not None:
                usage = EnumUsageType.from_str(usage)

            enumerated_value_container = SVDEnumeratedValueContainer(
                name=name,
                header_enum_name=header_enum_name,
                usage=usage,
                enumerated_values=enumerated_values,
                derived_from=derived_from,
            )

            for enumerated_value in enumerated_value_container.enumerated_values:
                enumerated_value.parent = enumerated_value_container

            enumerated_value_containers.append(enumerated_value_container)

        return enumerated_value_containers

    def _parse_write_constraint(
        self, parent_element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> None | SVDWriteConstraint:
        write_cronstraint_element = parent_element.find("writeConstraint")

        if write_cronstraint_element is None:
            return None

        write_as_read = _to_none_or_bool(
            self._parse_element_text("writeAsRead", write_cronstraint_element, optional=True)
        )
        use_enumerated_values = _to_none_or_bool(
            self._parse_element_text("useEnumeratedValues", write_cronstraint_element, optional=True)
        )

        if (range_element := write_cronstraint_element.find("range")) is not None:
            minimum = _to_int(self._parse_element_text("minimum", range_element, optional=False))
            maximum = _to_int(self._parse_element_text("maximum", range_element, optional=False))

            range_ = (minimum, maximum)
        else:
            range_ = None

        return SVDWriteConstraint(
            write_as_read=write_as_read,
            use_enumerated_values=use_enumerated_values,
            range_=range_,
        )

    def _parse_cluster(self, cluster_element: lxml.etree._Element):  # pyright: ignore[reportPrivateUsage]
        derived_from = self._parse_element_attribute("derivedFrom", cluster_element, optional=True)
        name = self._parse_element_text("name", cluster_element, optional=False)
        description = self._parse_element_text("description", cluster_element, strip=False, optional=True)
        alternate_cluster = self._parse_element_text("alternateCluster", cluster_element, optional=True)
        header_struct_name = self._parse_element_text("headerStructName", cluster_element, optional=True)
        address_offset = _to_int(self._parse_element_text("addressOffset", cluster_element, optional=False))
        registers_clusters = self._parse_registers_clusters(cluster_element)

        dim, dim_increment, dim_index, dim_name, dim_array_index = self._parse_dim_element_group(cluster_element)

        size, access, protection, reset_value, reset_mask = self._parse_register_properties(cluster_element)

        cluster = SVDCluster(
            name=name,
            description=description,
            alternate_cluster=alternate_cluster,
            header_struct_name=header_struct_name,
            address_offset=address_offset,
            registers_clusters=registers_clusters,
            dim=dim,
            dim_increment=dim_increment,
            dim_index=dim_index,
            dim_name=dim_name,
            dim_array_index=dim_array_index,
            size=size,
            access=access,
            protection=protection,
            reset_value=reset_value,
            reset_mask=reset_mask,
            derived_from=derived_from,
        )

        for register_cluster in cluster.registers_clusters:
            register_cluster.parent = cluster

        if cluster.dim_array_index is not None:
            cluster.dim_array_index.parent = cluster

        return cluster

    def _parse_registers_clusters(
        self, parent_element: None | lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> list[SVDRegister | SVDCluster]:
        if parent_element is None:
            return []

        registers_clusters: list[SVDRegister | SVDCluster] = []
        for element in parent_element:
            if element.tag == "register":
                register = self._parse_register(element)
                registers_clusters.append(register)

            if element.tag == "cluster":
                cluster = self._parse_cluster(element)
                registers_clusters.append(cluster)

        return registers_clusters

    def _parse_interrupts(
        self, peripheral_element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> list[SVDInterrupt]:
        interrupts: list[SVDInterrupt] = []
        for interrupt_element in peripheral_element.findall("interrupt"):
            name = self._parse_element_text("name", interrupt_element, optional=False)
            description = self._parse_element_text("description", interrupt_element, strip=False, optional=True)

            # Necessary for NSING.N32H47x_DFP.1.0.1/N32H474.svd
            try:
                value = _to_int(self._parse_element_text("value", interrupt_element, optional=False))
            except ParserException:
                warnings.warn(
                    f"Can't find mandatory value attribute in the interrupt element with name '{name}'. "
                    "Setting value to 0 to be compatible with SVDConv.",
                    ParserWarning,
                )
                value = 0

            interrupts.append(SVDInterrupt(name=name, description=description, value=value))

        return interrupts

    def _parse_address_blocks(
        self, peripheral_element: lxml.etree._Element  # pyright: ignore[reportPrivateUsage]
    ) -> list[SVDAddressBlock]:
        address_blocks: list[SVDAddressBlock] = []
        for address_block_element in peripheral_element.findall("addressBlock"):
            # dirty hack to handle the case where offset is not present
            # (e.g. Brainchip.AKD1000_DeviceFamilyPack.1.0.2/AKD1000.svd)
            offset = _to_int(self._parse_element_text("offset", address_block_element, optional=True)) or 0
            size = _to_int(self._parse_element_text("size", address_block_element, optional=False))
            usage = EnumeratedTokenType.from_str(
                self._parse_element_text("usage", address_block_element, optional=False)
            )
            protection = self._parse_element_text("protection", address_block_element, optional=True)

            if protection is not None:
                protection = ProtectionStringType.from_str(protection)

            address_blocks.append(SVDAddressBlock(offset=offset, size=size, usage=usage, protection=protection))

        return address_blocks

    def _parse_dim_element_group(
        self,
        element: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
    ) -> tuple[Optional[int], Optional[int], Optional[str], Optional[str], Optional[SVDDimArrayIndex]]:
        dim = _to_int(self._parse_element_text("dim", element, optional=True))
        dim_increment = _to_int(self._parse_element_text("dimIncrement", element, optional=True))
        dim_index = self._parse_element_text("dimIndex", element, optional=True)
        dim_name = self._parse_element_text("dimName", element, optional=True)
        dim_array_index = self.parse_dim_array_index(element)

        return dim, dim_increment, dim_index, dim_name, dim_array_index

    def parse_dim_array_index(
        self,
        element: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
    ) -> None | SVDDimArrayIndex:
        dim_array_index_element = element.find("dimArrayIndex")

        if dim_array_index_element is None:
            return None

        header_enum_name = self._parse_element_text("headerEnumName", dim_array_index_element, optional=True)
        enumerated_values = self._parse_enumerated_values(dim_array_index_element)

        dim_array_index = SVDDimArrayIndex(header_enum_name=header_enum_name, enumerated_values=enumerated_values)

        for enumerated_value in dim_array_index.enumerated_values:
            enumerated_value.parent = dim_array_index

        return dim_array_index

    def _parse_enumerated_values(
        self,
        parent_element: lxml.etree._Element,  # pyright: ignore[reportPrivateUsage]
    ) -> list[SVDEnumeratedValue]:
        enumerated_values: list[SVDEnumeratedValue] = []
        for enumerated_value_element in parent_element.findall("enumeratedValue"):
            name = self._parse_element_text("name", enumerated_value_element, optional=False)
            description = self._parse_element_text("description", enumerated_value_element, strip=False, optional=True)
            value = self._parse_element_text("value", enumerated_value_element, optional=True)
            is_default = _to_none_or_bool(
                self._parse_element_text("isDefault", enumerated_value_element, optional=True)
            )

            enumerated_values.append(
                SVDEnumeratedValue(name=name, description=description, value=value, is_default=is_default)
            )

        return enumerated_values
