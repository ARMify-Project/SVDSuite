# SVDSuite

**SVDSuite** is a Python package to parse, process, manipulate, validate, and generate [CMSIS SVD](https://open-cmsis-pack.github.io/svd-spec/main/index.html) files. Currently, the suite supports CMSIS-SVD standard 1.3.10-dev11, whereas the validation supports additionally standard 1.3.9.

> The CMSIS System View Description format(CMSIS-SVD) formalizes the description of the system contained in Arm Cortex-M processor-based microcontrollers, in particular, the memory mapped registers of peripherals. The detail contained in system view descriptions is comparable to the data in device reference manuals. The information ranges from high level functional descriptions of a peripheral all the way down to the definition and purpose of an individual bit field in a memory mapped register.
>
>CMSIS-SVD files are developed and maintained by silicon vendors. Silicon vendors distribute their descriptions as part of CMSIS Device Family Packs. Tool vendors use CMSIS-SVD files for providing device-specific debug views of peripherals in their debugger. Last but not least, CMSIS-compliant device header files are generated from CMSIS-SVD files. [^1]

[^1]: https://open-cmsis-pack.github.io/svd-spec/main/index.html

> [!CAUTION]
> This Python package is in early development. Code-breaking changes are to be expected!

## Installation

Install **SVDSuite** with `pip`:

```bash
  pip install svdsuite
```
    
## Usage/Examples

### Parse

To parse a CMSIS-SVD file you can utilize the `SVDParser` class.

```python
import pprint
from svdsuite import SVDParser

svd_str = """\
    <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
        xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
        <name>STM32F0</name>
        <version>1.0</version>
        <description>STM32F0 device</description>
        <cpu>
            <name>CM52</name>
            <revision>r0p0</revision>
            <endian>little</endian>
            <mpuPresent>false</mpuPresent>
            <fpuPresent>false</fpuPresent>
            <fpuDP>false</fpuDP>
            <dspPresent>false</dspPresent>
            <icachePresent>false</icachePresent>
            <dcachePresent>false</dcachePresent>
            <itcmPresent>false</itcmPresent>
            <dtcmPresent>false</dtcmPresent>
            <vtorPresent>false</vtorPresent>
            <nvicPrioBits>2</nvicPrioBits>
            <vendorSystickConfig>false</vendorSystickConfig>
            <deviceNumInterrupts>6</deviceNumInterrupts>
            <sauNumRegions>2</sauNumRegions>
            <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
                <region enabled="true" name="Region1">
                    <base>0x1000</base>
                    <limit>0x2000</limit>
                    <access>n</access>
                </region>
            </sauRegionsConfig>
        </cpu>
        <addressUnitBits>8</addressUnitBits>
        <width>32</width>
        <peripherals>
            <peripheral derivedFrom="test">
                <name>Timer1</name>
                <version>1.0</version>
                <description>Timer 1 is a standard timer</description>
                <alternatePeripheral>Timer1_Alt</alternatePeripheral>
                <groupName>group_name</groupName>
                <prependToName>prepend</prependToName>
                <appendToName>append</appendToName>
                <headerStructName>headerstruct</headerStructName>
                <disableCondition>discond</disableCondition>
                <baseAddress>0x40002000</baseAddress>
            </peripheral>
        </peripherals>
    </device>
    """

# Parse the SVD string. Alternatively, you can use the `for_xml_file` method to parse a SVD file
# or the `for_xml_content` method to parse svd byte content.
parser = SVDParser.for_xml_str(svd_str)
# parser = SVDParser.for_xml_file("path/to/svd_file.svd")
# parser = SVDParser.for_xml_content(svd_str.encode())

# Get the SVDDevice object
device = parser.get_device()

# Print the device object
pprint.pprint(device)
```

Output:
```python
SVDDevice(
  size=None,
  access=None,
  protection=None,
  reset_value=None,
  reset_mask=None,
  xs_no_namespace_schema_location='CMSIS-SVD.xsd',
  schema_version='1.3',
  vendor=None,
  vendor_id=None,
  name='STM32F0',
  series=None,
  version='1.0',
  description='STM32F0 device',
  license_text=None,
  cpu=SVDCPU(
    name=<CPUNameType.CM52: 'CM52'>,
    revision='r0p0',
    endian=<EndianType.LITTLE: 'little'>,
    mpu_present=False,
    fpu_present=False,
    fpu_dp=False,
    dsp_present=False,
    icache_present=False,
    dcache_present=False,
    itcm_present=False,
    dtcm_present=False,
    vtor_present=False,
    nvic_prio_bits=2,
    vendor_systick_config=False,
    device_num_interrupts=6,
    sau_num_regions=2,
    sau_regions_config=SVDSauRegionsConfig(
      enabled=True,
      protection_when_disabled=<ProtectionStringType.SECURE: 's'>,
      regions=[
        SVDSauRegion(
          enabled=True,
          name='Region1',
          base=4096,
          limit=8192,
          access=<SauAccessType.NON_SECURE: 'n'>
        )
      ]
    )
  ),
  header_system_filename=None,
  header_definitions_prefix=None,
  address_unit_bits=8,
  width=32,
  peripherals=[
    SVDPeripheral(
      size=None,
      access=None,
      protection=None,
      reset_value=None,
      reset_mask=None,
      dim=None,
      dim_increment=None,
      dim_index=None,
      dim_name=None,
      dim_array_index=None,
      name='Timer1',
      version='1.0',
      description='Timer 1 is a standard timer',
      alternate_peripheral='Timer1_Alt',
      group_name='group_name',
      prepend_to_name='prepend',
      append_to_name='append',
      header_struct_name='headerstruct',
      disable_condition='discond',
      base_address=1073750016,
      address_blocks=[],
      interrupts=[],
      registers_clusters=[],
      derived_from='test'
    )
  ]
)
```

Have a look into `svdsuite/svd_model.py` for all the models (dataclasses).

### Process

Not implemented yet!

### Create/Manipulate

To create or manipulate a CMSIS-SVD file you can utilize the `SVDSerializer` class.

```python
from svdsuite import (
    SVDDevice,
    SVDCPU,
    CPUNameType,
    EndianType,
    SVDSauRegionsConfig,
    ProtectionStringType,
    SVDSauRegion,
    SauAccessType,
    SVDPeripheral,
    SVDSerializer,
)

# Create an example device. Alternatevily, you can parse a CMSIS-SVD file and manipulate it.
device = SVDDevice(
    size=None,
    access=None,
    protection=None,
    reset_value=None,
    reset_mask=None,
    xs_no_namespace_schema_location="CMSIS-SVD.xsd",
    schema_version="1.3",
    vendor=None,
    vendor_id=None,
    name="STM32F0",
    series=None,
    version="1.0",
    description="STM32F0 device",
    license_text=None,
    cpu=SVDCPU(
        name=CPUNameType.CM52,
        revision="r0p0",
        endian=EndianType.LITTLE,
        mpu_present=False,
        fpu_present=False,
        fpu_dp=False,
        dsp_present=False,
        icache_present=False,
        dcache_present=False,
        itcm_present=False,
        dtcm_present=False,
        vtor_present=False,
        nvic_prio_bits=2,
        vendor_systick_config=False,
        device_num_interrupts=6,
        sau_num_regions=2,
        sau_regions_config=SVDSauRegionsConfig(
            enabled=True,
            protection_when_disabled=ProtectionStringType.SECURE,
            regions=[
                SVDSauRegion(
                    enabled=True,
                    name="Region1",
                    base=4096,
                    limit=8192,
                    access=SauAccessType.NON_SECURE,
                )
            ],
        ),
    ),
    header_system_filename=None,
    header_definitions_prefix=None,
    address_unit_bits=8,
    width=32,
    peripherals=[
        SVDPeripheral(
            size=None,
            access=None,
            protection=None,
            reset_value=None,
            reset_mask=None,
            dim=None,
            dim_increment=None,
            dim_index=None,
            dim_name=None,
            dim_array_index=None,
            name="Timer1",
            version="1.0",
            description="Timer 1 is a standard timer",
            alternate_peripheral="Timer1_Alt",
            group_name="group_name",
            prepend_to_name="prepend",
            append_to_name="append",
            header_struct_name="headerstruct",
            disable_condition="discond",
            base_address=1073750016,
            address_blocks=[],
            interrupts=[],
            registers_clusters=[],
            derived_from="test",
        )
    ],
)

# Serialize the device object. Alternatively, you can use the `device_to_svd_file` method to serialize the device
# object to an SVD file, or the `device_to_svd_content` method to serialize the device object to bytes string.
svd_str = SVDSerializer.device_to_svd_str(device, pretty_print=True)
# SVDSerializer.device_to_svd_file("path/to/svd_file.svd", device)
# svd_str = SVDSerializer.device_to_svd_content(device, pretty_print=True).decode()

# Print the serialized device object
print(svd_str)
```

Output:
```xml
<device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
  <name>STM32F0</name>
  <version>1.0</version>
  <description>STM32F0 device</description>
  <cpu>
    <name>CM52</name>
    <revision>r0p0</revision>
    <endian>little</endian>
    <mpuPresent>false</mpuPresent>
    <fpuPresent>false</fpuPresent>
    <fpuDP>false</fpuDP>
    <dspPresent>false</dspPresent>
    <icachePresent>false</icachePresent>
    <dcachePresent>false</dcachePresent>
    <itcmPresent>false</itcmPresent>
    <dtcmPresent>false</dtcmPresent>
    <vtorPresent>false</vtorPresent>
    <nvicPrioBits>2</nvicPrioBits>
    <vendorSystickConfig>false</vendorSystickConfig>
    <deviceNumInterrupts>6</deviceNumInterrupts>
    <sauNumRegions>2</sauNumRegions>
    <sauRegionsConfig enabled="true" protectionWhenDisabled="s">
      <region enabled="true" name="Region1">
        <base>0x1000</base>
        <limit>0x2000</limit>
        <access>n</access>
      </region>
    </sauRegionsConfig>
  </cpu>
  <addressUnitBits>8</addressUnitBits>
  <width>32</width>
  <peripherals>
    <peripheral derivedFrom="test">
      <name>Timer1</name>
      <version>1.0</version>
      <description>Timer 1 is a standard timer</description>
      <alternatePeripheral>Timer1_Alt</alternatePeripheral>
      <groupName>group_name</groupName>
      <prependToName>prepend</prependToName>
      <appendToName>append</appendToName>
      <headerStructName>headerstruct</headerStructName>
      <disableCondition>discond</disableCondition>
      <baseAddress>0x40002000</baseAddress>
    </peripheral>
  </peripherals>
</device>
```

### Validate

To validate a CMSIS-SVD file you can utilize the `SVDValidator` class.

```python
from svdsuite import SVDValidator

xml_str = """\
<device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
    xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
    <name>STM32F0</name>
    <version>1.0</version>
    <description>STM32F0 device</description>
    <addressUnitBits>8</addressUnitBits>
    <width>32</width>
    <peripherals>
        <peripheral derivedFrom="test">
            <name>Timer1</name>
            <baseAddress>0x40002000</baseAddress>
        </peripheral>
    </peripherals>
</device>
"""

# Validate the XML string. If the XML is invalid, an exception is raised, since get_exception=True.
# If get_exception=False, the function returns False on invalid XML without an exception.
# Alternatively, you can use the `validate_xml_file` method to validate an SVD file.
if SVDValidator.validate_xml_str(xml_str, get_exception=True):
    print("SVD is valid")
```

Output:
```
SVD is valid
```


## Roadmap

- [x] Parse svd files from XML to Python dataclasses ✅
- [x] Serialize the Python SVD dataclasses to XML svd files ✅
- [x] Validate svd files against the xsd schema files ✅
- [ ] Process parsed svd files (derivedFrom, nested clusters, ...)


## Running Tests

To run tests, run the following command:

```
  git clone https://github.com/ARMify-Project/SVDSuite.git svdsuite
  cd svdsuite/
  pytest tests/
```


## Acknowledgement

This project was made possible with funding from [NGI Zero Entrust Fund](https://nlnet.nl/thema/NGI0Entrust.html). NGI Zero Entrust Fund is part of the European Commission's [Next Generation Internet](https://www.ngi.eu/) initiative.

Project webpage: https://nlnet.nl/project/ARMify/

## References