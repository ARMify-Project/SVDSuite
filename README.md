# SVDSuite

> [!NOTE]  
> The long-term goal is to merge **SVDSuite** into the [cmsis-svd](https://github.com/cmsis-svd/cmsis-svd) repository and release it as version 1.0. The author of SVDSuite is also an active maintainer of the [CMSIS-SVD](https://github.com/cmsis-svd) project.

**SVDSuite** is a Python package to parse, process, manipulate, validate, and generate [CMSIS SVD](https://open-cmsis-pack.github.io/svd-spec/main/index.html) files. Currently, the suite supports CMSIS-SVD standard 1.3.10-dev16, whereas the validation additionally supports all previously released standards.

> The CMSIS System View Description format (CMSIS-SVD) formalizes the description of the system contained in Arm Cortex-M processor-based microcontrollers, in particular, the memory-mapped registers of peripherals. The detail contained in system view descriptions is comparable to the data in device reference manuals. The information ranges from high-level functional descriptions of a peripheral all the way down to the definition and purpose of an individual bit field in a memory-mapped register.
>
> CMSIS-SVD files are developed and maintained by silicon vendors. Silicon vendors distribute their descriptions as part of CMSIS Device Family Packs. Tool vendors use CMSIS-SVD files for providing device-specific debug views of peripherals in their debugger. Last but not least, CMSIS-compliant device header files are generated from CMSIS-SVD files. [^1]

### Compatibility with SVDConv

SVDSuite was designed with a strong focus on compatibility with *SVDConv*, the official CMSIS tool for validating and processing SVD files. To ensure full compatibility, all available SVD files were tested against SVDConv ([checkout the comparison repository](https://github.com/ARMify-Project/svdsuite-svdconv-compare)).

### Extended Functionality

In addition to faithfully supporting the CMSIS-SVD specification, SVDSuite offers several enhancements beyond the standard:

- **Forward references**: SVDSuite allows references to elements that are defined later in the same file, providing more flexibility in SVD authoring and structuring.
- **Full resolution of `enumeratedValues`**: Wildcards, default values, and all inheritance scenarios within `enumeratedValues` are fully resolved, enabling consistent and complete interpretation of value definitions.

[^1]: https://open-cmsis-pack.github.io/svd-spec/main/index.html

### SVD Test Files and Test Cases

During the development of **SVDSuite**, it became evident that the CMSIS-SVD standard is sometimes insufficiently documented and leaves room for interpretation. Moreover, *SVDConv*, the official tool provided by Arm for validating and processing SVD files, supports a variety of undocumented features that are not part of the written specification.

These undocumented behaviors include (but are not limited to):

- **Setting and resolving default values** (e.g., for access types, sizes, reset values).
- **Propagation and adjustment of `size` attributes** across the hierarchy.
- **Interpretation of “don’t care” bits** in `enumeratedValues` (e.g., `0b1xxxxxxx`).

To ensure compatibility with these behaviors and to avoid ambiguous interpretations, over **170 comprehensive test cases** were created and are documented [here](https://armify-project.github.io/resolver-tests-documentation/index.html). Each test is based on a fully defined CMSIS-SVD file, enabling systematic validation of how *SVDConv* interprets specific constructs and edge cases. These test files may also be useful for other developers working on SVD parsers.

In addition, **SVDConv** was extended with the options `--debug-output-text` and `--debug-output-json`, allowing developers to inspect how *SVDConv* internally resolves, normalizes, and transforms SVD files. These extensions greatly improve transparency and helped align **SVDSuite**'s behavior with that of *SVDConv*, even in the presence of undocumented logic. The modified version is hosted [here](https://github.com/ARMify-Project/devtools).


## Installation

Install **SVDSuite** with `pip`:

```bash
  pip install svdsuite
```
    
## Usage/Examples

### Process

To process a CMSIS-SVD file, which includes parsing, you can utilize the `Process` class.

```python
from svdsuite import Process
from svdsuite.model import Cluster, Register

svd_str = """\
<?xml version='1.0' encoding='utf-8'?>
<device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
  <name>STM32F0</name>
  <version>1.0</version>
  <description>Test_Example device</description>
  <cpu>
  <name>CM0</name>
  <revision>r0p0</revision>
  <endian>little</endian>
  <mpuPresent>false</mpuPresent>
  <fpuPresent>false</fpuPresent>
  <nvicPrioBits>4</nvicPrioBits>
  <vendorSystickConfig>false</vendorSystickConfig>
  </cpu>
  <addressUnitBits>8</addressUnitBits>
  <width>32</width>
  <peripherals>
    <peripheral>
      <name>TimerExt</name>
      <baseAddress>0x40000000</baseAddress>
      <addressBlock>
        <offset>0x0</offset>
        <size>0x1000</size>
        <usage>registers</usage>
      </addressBlock>
      <registers>
        <register derivedFrom="Timer0.CR1">
          <name>CR1</name>
          <addressOffset>0x00</addressOffset>
        </register>
      </registers>
    </peripheral>
    <peripheral>
      <dim>2</dim>
      <dimIncrement>0x1000</dimIncrement>
      <name>Timer[%s]</name>
      <baseAddress>0x40001000</baseAddress>
      <addressBlock>
        <offset>0x0</offset>
        <size>0x1000</size>
        <usage>registers</usage>
      </addressBlock>
      <registers>
        <cluster>
          <dim>4</dim>
          <dimIncrement>0x20</dimIncrement>
          <name>CC[%s]</name>
          <description>Capture/Compare Channel</description>
          <addressOffset>0x0</addressOffset>
          <register>
            <name>CCR</name>
            <description>Capture/Compare Register</description>
            <addressOffset>0x00</addressOffset>
          </register>
          <register>
            <name>CCMR</name>
            <description>Capture/Compare Mode Register</description>
            <addressOffset>0x04</addressOffset>
          </register>
          <register>
            <name>CCER</name>
            <description>Capture/Compare Enable Register</description>
            <addressOffset>0x08</addressOffset>
          </register>
        </cluster>
        <register>
          <name>CR1</name>
          <description>Control Register 1</description>
          <addressOffset>0x80</addressOffset>
          <size>32</size>
          <access>read-write</access>
          <fields>
            <field>
              <name>CEN</name>
              <description>Counter Enable</description>
              <bitOffset>0</bitOffset>
              <bitWidth>1</bitWidth>
              <enumeratedValues>
                <name>CEN_Values</name>
                <enumeratedValue>
                  <name>Disabled</name>
                  <description>Counter disabled</description>
                  <value>0</value>
                </enumeratedValue>
                <enumeratedValue>
                  <name>Enabled</name>
                  <description>Counter enabled</description>
                  <value>1</value>
                </enumeratedValue>
              </enumeratedValues>
            </field>
            <field>
              <name>CMS</name>
              <description>Center-aligned Mode Selection</description>
              <bitOffset>5</bitOffset>
              <bitWidth>2</bitWidth>
              <enumeratedValues>
                <name>CMS_Values</name>
                <enumeratedValue>
                  <name>EdgeAligned</name>
                  <description>Edge-aligned mode</description>
                  <value>0b00</value>
                </enumeratedValue>
                <enumeratedValue>
                  <name>CenterAligned1</name>
                  <description>Center-aligned mode 1</description>
                  <value>0b01</value>
                </enumeratedValue>
                <enumeratedValue>
                  <name>CenterAligned2</name>
                  <description>Center-aligned mode 2</description>
                  <value>0b10</value>
                </enumeratedValue>
                <enumeratedValue>
                  <name>CenterAligned3</name>
                  <description>Center-aligned mode 3</description>
                  <value>0b11</value>
                </enumeratedValue>
              </enumeratedValues>
            </field>
            <field>
              <name>Status</name>
              <description>Status Field with Don't Care Bits</description>
              <bitOffset>8</bitOffset>
              <bitWidth>8</bitWidth>
              <access>read-only</access>
              <enumeratedValues>
                <name>Status_Values</name>
                <enumeratedValue>
                  <name>OK</name>
                  <description>No error</description>
                  <value>0b0xxxxxxx</value>
                </enumeratedValue>
                <enumeratedValue>
                  <name>Error</name>
                  <description>Error condition</description>
                  <value>0b1xxxxxxx</value>
                </enumeratedValue>
              </enumeratedValues>
            </field>
          </fields>
        </register>
      </registers>
    </peripheral>
  </peripherals>
</device>
    """

# Process the SVD string. Alternatively, you can use the `from_svd_file` method to parse a SVD file
# or the `from_xml_content` method to parse svd byte content.
# Additionally, you can specify a resolver_logging_file_path to debug the resolver step by step.
process = Process.from_xml_str(svd_str)
# parser = Parser.from_svd_file("path/to/svd_file.svd")
# parser = Parser.from_xml_content(svd_str.encode())

# Get the SVDDevice object
device = process.get_processed_device()

print("Print the peripheral names and the register count for each peripheral:")
for peripheral in device.peripherals:
    print(f"Peripheral: {peripheral.name}, Register Count: {len(peripheral.registers)}")

print("\n\nPrint the register names and their base address for each peripheral:")
for peripheral in device.peripherals:
    print(f"Peripheral: {peripheral.name}")
    for register in peripheral.registers:
        print(f"  Register: {register.name}, Base Address: 0x{register.base_address:X}")

print("\n\nPrint the field names and their bit offsets for each register:")
for peripheral in device.peripherals:
    print(f"Peripheral: {peripheral.name}")
    for register in peripheral.registers:
        print(f"  Register: {register.name}")
        for field in register.fields:
            print(f"    Field: {field.name}, Bit Offset: {field.bit_offset}")

print("\n\nPrint the enumerated values for each field:")
for peripheral in device.peripherals:
    print(f"Peripheral: {peripheral.name}")
    for register in peripheral.registers:
        print(f"  Register: {register.name}")
        for field in register.fields:
            print(f"    Field: {field.name}")
            for enum_value_cont in field.enumerated_value_containers:
                for enum_value in enum_value_cont.enumerated_values:
                    print(f"      Enumerated Value: {enum_value.name}, Value: {enum_value.value}")

print("\n\nPrint peripherals with registers but include clusters:")
for peripheral in device.peripherals:
    print(f"Peripheral: {peripheral.name}")
    # We ignore that clusters could be nested here for simplicity
    # In a real-world scenario, you would need to handle nested clusters appropriately
    for reg_cluster in peripheral.registers_clusters:
        if isinstance(reg_cluster, Cluster):
            print(f"  Cluster: {reg_cluster.name}")
            for register in reg_cluster.registers_clusters:
                print(f"    Register: {register.name}, Base Address: 0x{register.base_address:X}")
        elif isinstance(reg_cluster, Register):
            print(f"  Register: {reg_cluster.name}, Base Address: 0x{reg_cluster.base_address:X}")
```

Have a look into `svdsuite/model/process.py` for all the models (dataclasses).

### Parse

To parse a CMSIS-SVD file you can utilize the `Parser` class.

```python
import pprint
from svdsuite import Parser

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

# Parse the SVD string. Alternatively, you can use the `from_svd_file` method to parse a SVD file
# or the `from_xml_content` method to parse svd byte content.
parser = Parser.from_xml_str(svd_str)
# parser = Parser.from_svd_file("path/to/svd_file.svd")
# parser = Parser.from_xml_content(svd_str.encode())

# Get the SVDDevice object
device = parser.get_parsed_device()

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

Have a look into `svdsuite/model/parse.py` for all the models (dataclasses).

### Create/Manipulate

To create or manipulate a CMSIS-SVD file you can utilize the `Serializer` class.

```python
from svdsuite import Serializer
from svdsuite.model import (
    SVDDevice,
    SVDCPU,
    CPUNameType,
    EndianType,
    SVDSauRegionsConfig,
    ProtectionStringType,
    SVDSauRegion,
    SauAccessType,
    SVDPeripheral,
)

# Create an example device. Alternatevily, you can parse a CMSIS-SVD file and manipulate it.
device = SVDDevice(
    xs_no_namespace_schema_location="CMSIS-SVD.xsd",
    schema_version="1.3",
    name="STM32F0",
    version="1.0",
    description="STM32F0 device",
    cpu=SVDCPU(
        name=CPUNameType.CM52,
        revision="r0p0",
        endian=EndianType.LITTLE,
        nvic_prio_bits=2,
        vendor_systick_config=False,
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
    address_unit_bits=8,
    width=32,
    peripherals=[
        SVDPeripheral(
            name="Timer1",
            description="Timer 1 is a standard timer",
            base_address=1073750016,
        )
    ],
)

# Serialize the device object. Alternatively, you can use the `device_to_svd_file` method to serialize the device
# object to an SVD file, or the `device_to_svd_content` method to serialize the device object to bytes string.
svd_str = Serializer.device_to_svd_str(device, pretty_print=True)
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
    <nvicPrioBits>2</nvicPrioBits>
    <vendorSystickConfig>false</vendorSystickConfig>
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
    <peripheral>
      <name>Timer1</name>
      <description>Timer 1 is a standard timer</description>
      <baseAddress>0x40002000</baseAddress>
    </peripheral>
  </peripherals>
</device>
```

### Validate

To validate a CMSIS-SVD file you can utilize the `Validator` class.

```python
from svdsuite import Validator

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
# Alternatively, you can use the `validate_xml_file` or `validate_xml_content` methods.
if Validator.validate_xml_str(xml_str, get_exception=True):
    print("SVD is valid")
```

Output:
```
SVD is valid
```


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