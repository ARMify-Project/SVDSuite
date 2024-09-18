from typing import Callable
import pytest

from svdsuite.process import Process
from svdsuite.model.process import Device, Register
from svdsuite.model.types import EnumeratedTokenType


@pytest.fixture(name="get_processed_device_from_testfile")
def fixture_get_processed_device_from_testfile(get_test_svd_file_content: Callable[[str], bytes]):
    def _(file_name: str) -> Device:
        file_content = get_test_svd_file_content(file_name)
        return Process.from_xml_content(file_content).get_processed_device()

    return _


class TestPeripheralDerivedFrom:
    def test_simple(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_simple.svd")

        assert len(device.peripherals) == 2

        adc2 = device.peripherals[1]
        assert adc2.name == "ADC2"
        assert adc2.version == "1.0"
        assert adc2.description == "Analog-to-Digital Converter"
        assert adc2.alternate_peripheral == "ADCx"
        assert adc2.group_name == "ADC"
        assert adc2.prepend_to_name == "ADC_"
        assert adc2.append_to_name == "_ADC"
        assert adc2.header_struct_name == "adc"
        assert adc2.disable_condition == "!ADC1"
        assert adc2.base_address == 0x40002000
        assert len(adc2.address_blocks) == 1
        assert adc2.address_blocks[0].offset == 0
        assert adc2.address_blocks[0].size == 0x1000
        assert adc2.address_blocks[0].usage == EnumeratedTokenType.REGISTERS
        assert len(adc2.interrupts) == 0
        assert len(adc2.registers_clusters) == 1
        assert isinstance(adc2.registers_clusters[0], Register)
        assert adc2.registers_clusters[0].name == "ADC_ISR"
        assert len(adc2.registers_clusters[0].fields) == 1
        assert adc2.registers_clusters[0].fields[0].name == "ADRDY"

    def test_simple2(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_simple2.svd")

        assert len(device.peripherals) == 2

        adc2 = device.peripherals[1]
        assert adc2.name == "ADC2"
        assert adc2.version == "2.0"
        assert adc2.description == "Analog-to-Digital Converter2"
        assert adc2.alternate_peripheral == "ADCy"
        assert adc2.group_name == "ADCc"
        assert adc2.prepend_to_name == "ADC!"
        assert adc2.append_to_name == "!ADC"
        assert adc2.header_struct_name == "abc"
        assert adc2.disable_condition == "$ADC1"
        assert adc2.base_address == 0x40002000
        assert len(adc2.address_blocks) == 1
        assert adc2.address_blocks[0].offset == 1
        assert adc2.address_blocks[0].size == 0x2000
        assert adc2.address_blocks[0].usage == EnumeratedTokenType.BUFFER
        assert len(adc2.interrupts) == 1
        assert adc2.interrupts[0].name == "ADC2"
        assert adc2.interrupts[0].value == 19
        assert len(adc2.registers_clusters) == 1
        assert isinstance(adc2.registers_clusters[0], Register)
        assert adc2.registers_clusters[0].name == "ADC_ISR"
        assert len(adc2.registers_clusters[0].fields) == 1
        assert adc2.registers_clusters[0].fields[0].name == "ADRDY"

    def test_forward(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_forward.svd")

        assert len(device.peripherals) == 2

        adc2 = device.peripherals[0]
        assert adc2.name == "ADC2"
        assert adc2.version == "1.0"
        assert adc2.description == "Analog-to-Digital Converter"
        assert adc2.alternate_peripheral == "ADCx"
        assert adc2.group_name == "ADC"
        assert adc2.prepend_to_name == "ADC_"
        assert adc2.append_to_name == "_ADC"
        assert adc2.header_struct_name == "adc"
        assert adc2.disable_condition == "!ADC1"
        assert adc2.base_address == 0x40001000
        assert len(adc2.address_blocks) == 1
        assert adc2.address_blocks[0].offset == 0
        assert adc2.address_blocks[0].size == 0x1000
        assert adc2.address_blocks[0].usage == EnumeratedTokenType.REGISTERS
        assert len(adc2.interrupts) == 0
        assert len(adc2.registers_clusters) == 1
        assert isinstance(adc2.registers_clusters[0], Register)
        assert adc2.registers_clusters[0].name == "ADC_ISR"
        assert len(adc2.registers_clusters[0].fields) == 1
        assert adc2.registers_clusters[0].fields[0].name == "ADRDY"

    def test_forward2(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_forward2.svd")

        assert len(device.peripherals) == 2

        adc2 = device.peripherals[0]
        assert adc2.name == "ADC2"
        assert adc2.version == "2.0"
        assert adc2.description == "Analog-to-Digital Converter2"
        assert adc2.alternate_peripheral == "ADCy"
        assert adc2.group_name == "ADCc"
        assert adc2.prepend_to_name == "ADC!"
        assert adc2.append_to_name == "!ADC"
        assert adc2.header_struct_name == "abc"
        assert adc2.disable_condition == "$ADC1"
        assert adc2.base_address == 0x40001000
        assert len(adc2.address_blocks) == 1
        assert adc2.address_blocks[0].offset == 1
        assert adc2.address_blocks[0].size == 0x2000
        assert adc2.address_blocks[0].usage == EnumeratedTokenType.BUFFER
        assert len(adc2.interrupts) == 1
        assert adc2.interrupts[0].name == "ADC2"
        assert adc2.interrupts[0].value == 19
        assert len(adc2.registers_clusters) == 1
        assert isinstance(adc2.registers_clusters[0], Register)
        assert adc2.registers_clusters[0].name == "ADC_ISR"
        assert len(adc2.registers_clusters[0].fields) == 1
        assert adc2.registers_clusters[0].fields[0].name == "ADRDY"

    def test_register_no_overlap(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_register_no_overlap.svd")

        assert len(device.peripherals) == 2

        adc1 = device.peripherals[0]
        adc2 = device.peripherals[1]

        assert len(adc1.registers_clusters) == 1

        assert adc2.name == "ADC2"
        assert adc2.version == "1.0"
        assert adc2.description == "Analog-to-Digital Converter"
        assert adc2.alternate_peripheral == "ADCx"
        assert adc2.group_name == "ADC"
        assert adc2.prepend_to_name == "ADC_"
        assert adc2.append_to_name == "_ADC"
        assert adc2.header_struct_name == "adc"
        assert adc2.disable_condition == "!ADC1"
        assert adc2.base_address == 0x40002000
        assert len(adc2.address_blocks) == 1
        assert adc2.address_blocks[0].offset == 0
        assert adc2.address_blocks[0].size == 0x1000
        assert adc2.address_blocks[0].usage == EnumeratedTokenType.REGISTERS
        assert len(adc2.interrupts) == 0
        assert isinstance(adc2.registers_clusters[0], Register)
        assert adc2.registers_clusters[0].name == "ADC_ISR"
        assert len(adc2.registers_clusters[0].fields) == 1
        assert adc2.registers_clusters[0].fields[0].name == "ADRDY"

        assert len(adc2.registers_clusters) == 2
        assert adc2.registers_clusters[1].name == "ADC_ISR2"

    def test_register_overlap_simple(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_register_overlap_simple.svd")

        assert len(device.peripherals) == 2

        adc1 = device.peripherals[0]
        adc2 = device.peripherals[1]

        assert len(adc1.registers_clusters) == 1
        assert isinstance(adc1.registers_clusters[0], Register)
        assert adc1.registers_clusters[0].name == "ADC_ISR"
        assert len(adc1.registers_clusters[0].fields) == 1
        assert adc1.registers_clusters[0].fields[0].name == "ADRDY"

        assert adc2.name == "ADC2"
        assert adc2.version == "1.0"
        assert adc2.description == "Analog-to-Digital Converter"
        assert adc2.alternate_peripheral == "ADCx"
        assert adc2.group_name == "ADC"
        assert adc2.prepend_to_name == "ADC_"
        assert adc2.append_to_name == "_ADC"
        assert adc2.header_struct_name == "adc"
        assert adc2.disable_condition == "!ADC1"
        assert adc2.base_address == 0x40002000
        assert len(adc2.address_blocks) == 1
        assert adc2.address_blocks[0].offset == 0
        assert adc2.address_blocks[0].size == 0x1000
        assert adc2.address_blocks[0].usage == EnumeratedTokenType.REGISTERS
        assert len(adc2.interrupts) == 0
        assert len(adc2.registers_clusters) == 1
        assert isinstance(adc2.registers_clusters[0], Register)
        assert adc2.registers_clusters[0].name == "ADC_ISR2"
        assert len(adc2.registers_clusters[0].fields) == 0

    def test_register_no_overlap_complex(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_register_no_overlap_complex.svd")

        assert len(device.peripherals) == 2

        adc1 = device.peripherals[0]
        adc2 = device.peripherals[1]

        assert adc1.name == "ADC1"
        assert len(adc1.registers_clusters) == 4
        assert adc1.registers_clusters[0].name == "r1"
        assert adc1.registers_clusters[1].name == "cl1"
        assert adc1.registers_clusters[2].name == "r2"
        assert adc1.registers_clusters[3].name == "cl2"

        assert adc2.name == "ADC2"
        assert len(adc2.registers_clusters) == 5
        assert adc2.registers_clusters[0].name == "r1"
        assert adc2.registers_clusters[1].name == "cl1"
        assert adc2.registers_clusters[2].name == "r2"
        assert adc2.registers_clusters[3].name == "cl2"
        assert adc2.registers_clusters[4].name == "r10"

    def test_register_no_overlap_complex2(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_register_no_overlap_complex2.svd")

        assert len(device.peripherals) == 2

        adc1 = device.peripherals[0]
        adc2 = device.peripherals[1]

        assert adc1.name == "ADC1"
        assert len(adc1.registers_clusters) == 4
        assert adc1.registers_clusters[0].name == "r1"
        assert adc1.registers_clusters[1].name == "cl1"
        assert adc1.registers_clusters[2].name == "r2"
        assert adc1.registers_clusters[3].name == "cl2"

        assert adc2.name == "ADC2"
        assert len(adc2.registers_clusters) == 5
        assert adc2.registers_clusters[0].name == "r1"
        assert adc2.registers_clusters[1].name == "cl1"
        assert adc2.registers_clusters[2].name == "r10"
        assert adc2.registers_clusters[3].name == "r2"
        assert adc2.registers_clusters[4].name == "cl2"

    def test_register_no_overlap_unsorted(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_register_no_overlap_unsorted.svd")

        assert len(device.peripherals) == 2

        adc1 = device.peripherals[0]
        adc2 = device.peripherals[1]

        assert adc1.name == "ADC1"
        assert len(adc1.registers_clusters) == 4
        assert adc1.registers_clusters[0].name == "r1"
        assert adc1.registers_clusters[1].name == "cl1"
        assert adc1.registers_clusters[2].name == "r2"
        assert adc1.registers_clusters[3].name == "cl2"

        assert adc2.name == "ADC2"
        assert len(adc2.registers_clusters) == 5
        assert adc2.registers_clusters[0].name == "r1"
        assert adc2.registers_clusters[1].name == "cl1"
        assert adc2.registers_clusters[2].name == "r2"
        assert adc2.registers_clusters[3].name == "cl2"
        assert adc2.registers_clusters[4].name == "r10"

    def test_register_overlap_complex(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_register_overlap_complex.svd")

        assert len(device.peripherals) == 2

        adc1 = device.peripherals[0]
        adc2 = device.peripherals[1]

        assert adc1.name == "ADC1"
        assert len(adc1.registers_clusters) == 4
        assert adc1.registers_clusters[0].name == "r1"
        assert adc1.registers_clusters[1].name == "cl1"
        assert adc1.registers_clusters[2].name == "r2"
        assert adc1.registers_clusters[3].name == "cl2"

        assert adc2.name == "ADC2"
        assert len(adc2.registers_clusters) == 3
        assert adc2.registers_clusters[0].name == "r1"
        assert adc2.registers_clusters[1].name == "r10"
        assert adc2.registers_clusters[2].name == "cl2"

    def test_register_overlap_complex2(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_register_overlap_complex2.svd")

        assert len(device.peripherals) == 2

        adc1 = device.peripherals[0]
        adc2 = device.peripherals[1]

        assert adc1.name == "ADC1"
        assert len(adc1.registers_clusters) == 4
        assert adc1.registers_clusters[0].name == "r1"
        assert adc1.registers_clusters[1].name == "cl1"
        assert adc1.registers_clusters[2].name == "r2"
        assert adc1.registers_clusters[3].name == "cl2"

        assert adc2.name == "ADC2"
        assert len(adc2.registers_clusters) == 3
        assert adc2.registers_clusters[0].name == "r1"
        assert adc2.registers_clusters[1].name == "r10"
        assert adc2.registers_clusters[2].name == "cl2"

    def test_multiple(self, get_processed_device_from_testfile: Callable[[str], Device]):
        device = get_processed_device_from_testfile("derived_from_multiple.svd")

        assert len(device.peripherals) == 3

        adc1 = device.peripherals[0]
        adc2 = device.peripherals[1]
        adc3 = device.peripherals[2]

        assert adc1.name == "ADC1"
        assert adc1.base_address == 0x40001000
        assert len(adc1.registers_clusters) == 1
        assert adc1.registers_clusters[0].name == "ADC_ISR"
        assert isinstance(adc1.registers_clusters[0], Register)
        assert len(adc1.registers_clusters[0].fields) == 1

        assert adc2.name == "ADC2"
        assert adc2.base_address == 0x40002000
        assert len(adc2.registers_clusters) == 1
        assert adc2.registers_clusters[0].name == "ADC_ISR"
        assert isinstance(adc2.registers_clusters[0], Register)
        assert len(adc2.registers_clusters[0].fields) == 1

        assert adc3.name == "ADC3"
        assert adc3.base_address == 0x40003000
        assert len(adc3.registers_clusters) == 1
        assert adc3.registers_clusters[0].name == "ADC_ISR"
        assert isinstance(adc3.registers_clusters[0], Register)
        assert len(adc3.registers_clusters[0].fields) == 1
