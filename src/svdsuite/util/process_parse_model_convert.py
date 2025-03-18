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
from svdsuite.model.process import (
    CPU,
    AddressBlock,
    Cluster,
    Device,
    DimArrayIndex,
    EnumeratedValueContainer,
    EnumeratedValue,
    Field,
    Interrupt,
    Peripheral,
    Register,
    SauRegion,
    SauRegionsConfig,
    WriteConstraint,
)


def process_parse_convert_sau_region(region: SauRegion) -> SVDSauRegion:
    return SVDSauRegion(
        enabled=region.enabled,
        name=region.name,
        base=region.base,
        limit=region.limit,
        access=region.access,
        parent=None,  # set by parent config
    )


def process_parse_convert_sau_regions_config(config: SauRegionsConfig) -> SVDSauRegionsConfig:
    regions = [process_parse_convert_sau_region(region) for region in config.regions]

    svd_config = SVDSauRegionsConfig(
        enabled=config.enabled,
        protection_when_disabled=config.protection_when_disabled,
        regions=regions,
        parent=None,  # set by parent CPU
    )

    for region in regions:
        region.parent = svd_config

    return svd_config


def process_parse_convert_cpu(cpu: CPU) -> SVDCPU:
    sau_regions_config = (
        process_parse_convert_sau_regions_config(cpu.sau_regions_config) if cpu.sau_regions_config else None
    )

    svd_cpu = SVDCPU(
        name=cpu.name,
        revision=cpu.revision,
        endian=cpu.endian,
        mpu_present=cpu.mpu_present,
        fpu_present=cpu.fpu_present,
        fpu_dp=cpu.fpu_dp,
        dsp_present=cpu.dsp_present,
        icache_present=cpu.icache_present,
        dcache_present=cpu.dcache_present,
        itcm_present=cpu.itcm_present,
        dtcm_present=cpu.dtcm_present,
        vtor_present=cpu.vtor_present,
        nvic_prio_bits=cpu.nvic_prio_bits,
        vendor_systick_config=cpu.vendor_systick_config,
        device_num_interrupts=cpu.device_num_interrupts,
        sau_num_regions=cpu.sau_num_regions,
        sau_regions_config=sau_regions_config,
        parent=None,  # set by parent device
    )

    if sau_regions_config:
        sau_regions_config.parent = svd_cpu

    return svd_cpu


def process_parse_convert_enumerated_value(value: EnumeratedValue) -> SVDEnumeratedValue:
    return SVDEnumeratedValue(
        name=value.name,
        description=value.description,
        value=str(value.value),
        is_default=False,
        parent=None,  # set by parent enumerated value or dim array index
    )


def process_parse_convert_dim_array_index(index: DimArrayIndex) -> SVDDimArrayIndex:
    enumerated_values = [process_parse_convert_enumerated_value(value) for value in index.enumerated_values]

    svd_index = SVDDimArrayIndex(
        header_enum_name=index.header_enum_name,
        enumerated_values=enumerated_values,
        parent=None,  # set by parent field
    )

    for enumerated_value in enumerated_values:
        enumerated_value.parent = svd_index

    return svd_index


def process_parse_convert_address_block(block: AddressBlock) -> SVDAddressBlock:
    return SVDAddressBlock(
        offset=block.offset,
        size=block.size,
        usage=block.usage,
        protection=block.protection,
        parent=None,  # set by parent peripheral
    )


def process_parse_convert_interrupt(interrupt: Interrupt) -> SVDInterrupt:
    return SVDInterrupt(
        name=interrupt.name,
        description=interrupt.description,
        value=interrupt.value,
        parent=None,  # set by parent peripheral
    )


def process_parse_convert_write_constraint(constraint: WriteConstraint) -> SVDWriteConstraint:
    return SVDWriteConstraint(
        write_as_read=constraint.write_as_read,
        use_enumerated_values=constraint.use_enumerated_values,
        range_=constraint.range_,
        parent=None,  # set by parent field or register
    )


def process_parse_convert_enumerated_value_container(value: EnumeratedValueContainer) -> SVDEnumeratedValueContainer:
    enumerated_values = [process_parse_convert_enumerated_value(value) for value in value.enumerated_values]

    svd_value = SVDEnumeratedValueContainer(
        name=value.name,
        header_enum_name=value.header_enum_name,
        usage=value.usage,
        enumerated_values=enumerated_values,
        derived_from=None,
        parent=None,  # set by parent field
    )

    for enumerated_value in enumerated_values:
        enumerated_value.parent = svd_value

    return svd_value


def process_parse_convert_field(field: Field) -> SVDField:
    enumerated_value_containers = [
        process_parse_convert_enumerated_value_container(container) for container in field.enumerated_value_containers
    ]

    svd_field = SVDField(
        name=field.name,
        description=field.description,
        lsb=field.lsb,
        msb=field.msb,
        access=field.access,
        modified_write_values=field.modified_write_values,
        write_constraint=(
            process_parse_convert_write_constraint(field.write_constraint) if field.write_constraint else None
        ),
        read_action=field.read_action,
        enumerated_value_containers=enumerated_value_containers,
        derived_from=None,
        parent=None,  # set by parent register
    )

    for container in enumerated_value_containers:
        container.parent = svd_field

    return svd_field


def process_parse_convert_register(register: Register) -> SVDRegister:
    fields = [process_parse_convert_field(field) for field in register.fields]

    svd_register = SVDRegister(
        name=register.name,
        display_name=register.display_name,
        description=register.description,
        alternate_group=register.alternate_group,
        alternate_register=register.alternate_register,
        address_offset=register.address_offset,
        size=register.size,
        access=register.access,
        protection=register.protection,
        reset_value=register.reset_value,
        reset_mask=register.reset_mask,
        data_type=register.data_type,
        modified_write_values=register.modified_write_values,
        write_constraint=(
            process_parse_convert_write_constraint(register.write_constraint) if register.write_constraint else None
        ),
        read_action=register.read_action,
        fields=fields,
        derived_from=None,
        parent=None,  # set by parent cluster or peripheral
    )

    for field in fields:
        field.parent = svd_register

    return svd_register


def process_parse_convert_cluster(cluster: Cluster) -> SVDCluster:
    registers_clusters: list[SVDCluster | SVDRegister] = []
    for register_cluster in cluster.registers_clusters:
        if isinstance(register_cluster, Register):
            converted = process_parse_convert_register(register_cluster)
        elif isinstance(register_cluster, Cluster):  # pyright: ignore[reportUnnecessaryIsInstance]
            converted = process_parse_convert_cluster(register_cluster)
        else:
            raise ValueError(f"Invalid register type: {type(register_cluster)}")

        registers_clusters.append(converted)

    svd_cluster = SVDCluster(
        name=cluster.name,
        description=cluster.description,
        alternate_cluster=cluster.alternate_cluster,
        header_struct_name=cluster.header_struct_name,
        address_offset=cluster.address_offset,
        size=cluster.size,
        access=cluster.access,
        protection=cluster.protection,
        reset_value=cluster.reset_value,
        reset_mask=cluster.reset_mask,
        registers_clusters=registers_clusters,
        derived_from=None,
        parent=None,  # set by parent cluster or peripheral
    )

    for register_cluster in registers_clusters:
        register_cluster.parent = svd_cluster

    return svd_cluster


def process_parse_convert_peripheral(peripheral: Peripheral) -> SVDPeripheral:
    address_blocks = [process_parse_convert_address_block(block) for block in peripheral.address_blocks]
    interrupts = [process_parse_convert_interrupt(interrupt) for interrupt in peripheral.interrupts]

    registers_clusters: list[SVDCluster | SVDRegister] = []
    for register_cluster in peripheral.registers_clusters:
        if isinstance(register_cluster, Register):
            converted = process_parse_convert_register(register_cluster)
        elif isinstance(register_cluster, Cluster):  # pyright: ignore[reportUnnecessaryIsInstance]
            converted = process_parse_convert_cluster(register_cluster)
        else:
            raise ValueError(f"Invalid register type: {type(register_cluster)}")

        registers_clusters.append(converted)

    svd_peripheral = SVDPeripheral(
        name=peripheral.name,
        version=peripheral.version,
        description=peripheral.description,
        alternate_peripheral=peripheral.alternate_peripheral,
        group_name=peripheral.group_name,
        prepend_to_name=peripheral.prepend_to_name,
        append_to_name=peripheral.append_to_name,
        header_struct_name=peripheral.header_struct_name,
        disable_condition=peripheral.disable_condition,
        base_address=peripheral.base_address,
        size=peripheral.size,
        access=peripheral.access,
        protection=peripheral.protection,
        reset_value=peripheral.reset_value,
        reset_mask=peripheral.reset_mask,
        address_blocks=address_blocks,
        interrupts=interrupts,
        registers_clusters=registers_clusters,
        derived_from=None,
        parent=None,  # set by parent device
    )

    for block in address_blocks:
        block.parent = svd_peripheral

    for interrupt in interrupts:
        interrupt.parent = svd_peripheral

    for register_cluster in registers_clusters:
        register_cluster.parent = svd_peripheral

    return svd_peripheral


def process_parse_convert_device(device: Device) -> SVDDevice:
    peripherals = [process_parse_convert_peripheral(peripheral) for peripheral in device.peripherals]

    svd_device = SVDDevice(
        xs_no_namespace_schema_location="CMSIS-SVD.xsd",
        schema_version="1.3",
        vendor=device.vendor,
        vendor_id=device.vendor_id,
        name=device.name,
        series=device.series,
        version=device.version,
        description=device.description,
        license_text=device.license_text,
        cpu=process_parse_convert_cpu(device.cpu) if device.cpu else None,
        header_system_filename=device.header_system_filename,
        header_definitions_prefix=device.header_definitions_prefix,
        address_unit_bits=device.address_unit_bits,
        width=device.width,
        peripherals=peripherals,
        size=device.size,
        access=device.access,
        protection=device.protection,
        reset_value=device.reset_value,
        reset_mask=device.reset_mask,
    )

    if svd_device.cpu:
        svd_device.cpu.parent = svd_device

    for peripheral in peripherals:
        peripheral.parent = svd_device

    return svd_device
