from typing import Callable
import pytest
import lxml.etree

from svdsuite.validate import Validator, SVDSchemaVersion


class TestValidate:
    xml_content = """\
    <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
        <vendor>STMicroelectronics</vendor>
        <vendorID>ST</vendorID>
        <name>STM32F0</name>
        <series>STM32F0</series>
        <version>1.0</version>
        <description>STM32F0 device</description>
        <licenseText>license</licenseText>
        <headerSystemFilename>stm32f0</headerSystemFilename>
        <headerDefinitionsPrefix>TestPrefix</headerDefinitionsPrefix>
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
            <peripheral derivedFrom="test2">
                <name>Timer2</name>
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

    def test_testfile_read(self, get_test_svd_file_path: Callable[[str], str]):
        assert Validator.validate_xml_file(get_test_svd_file_path("parser_testfile.svd"), get_exception=False) is False

    def test_valid_xml_str(self):
        assert Validator.validate_xml_str(self.xml_content) is True

    def test_valid_xml_content(self):
        assert Validator.validate_xml_content(self.xml_content.encode()) is True

    def test_invalid_xml_with_false(self):
        xml_content = """\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
            <name>STM32F0</name>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        assert Validator.validate_xml_str(xml_content, get_exception=False) is False

    @pytest.mark.xfail(strict=True, raises=lxml.etree.DocumentInvalid)
    def test_invalid_xml_with_exception_specified(self):
        xml_content = """\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
            <name>STM32F0</name>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        Validator.validate_xml_str(xml_content, get_exception=True)

    @pytest.mark.xfail(strict=True, raises=lxml.etree.DocumentInvalid)
    def test_invalid_xml_with_exception_not_specified(self):
        xml_content = """\
        <device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
            <name>STM32F0</name>
            <version>1.0</version>
            <description>STM32F0 device</description>
            <addressUnitBits>8</addressUnitBits>
            <width>32</width>
        </device>
        """

        Validator.validate_xml_str(xml_content)

    def test_cpu_which_exist_in_1_3_10_schema(self):
        xml_content = """\
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
        """

        validated = Validator.validate_xml_str(
            xml_content, get_exception=False, schema_version=SVDSchemaVersion.V1_3_10
        )

        assert validated is True

    def test_cpu_which_doesnt_exist_in_1_3_9_schema(self):
        xml_content = """\
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
        """

        validated = Validator.validate_xml_str(xml_content, get_exception=False, schema_version=SVDSchemaVersion.V1_3_9)

        assert validated is False
