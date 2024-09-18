import tempfile

from svdsuite.serialize import Serializer
from svdsuite.model.parse import SVDDevice


class TestSerialize:
    expected_svd_str = """\
<?xml version='1.0' encoding='utf-8'?>
<device xmlns:xs="http://www.w3.org/2001/XMLSchema-instance" xs:noNamespaceSchemaLocation="CMSIS-SVD.xsd" schemaVersion="1.3">
  <name>STM32F0</name>
  <version>1.0</version>
  <description>STM32F0 device</description>
  <addressUnitBits>8</addressUnitBits>
  <width>32</width>
</device>
"""

    def test_device_to_svd_str(self):
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
            cpu=None,
            header_system_filename=None,
            header_definitions_prefix=None,
            address_unit_bits=8,
            width=32,
            peripherals=[],
        )

        svd_str = Serializer.device_to_svd_str(device, pretty_print=True)

        assert svd_str == self.expected_svd_str

    def test_device_to_svd_content(self):
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
            cpu=None,
            header_system_filename=None,
            header_definitions_prefix=None,
            address_unit_bits=8,
            width=32,
            peripherals=[],
        )

        svd_content = Serializer.device_to_svd_content(device, pretty_print=True)

        assert svd_content == self.expected_svd_str.encode()

    def test_device_to_svd_file(self):
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
            cpu=None,
            header_system_filename=None,
            header_definitions_prefix=None,
            address_unit_bits=8,
            width=32,
            peripherals=[],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            Serializer.device_to_svd_file(temp_dir + "/test.svd", device, pretty_print=True)

            with open(temp_dir + "/test.svd", "r", encoding="utf8") as f:
                svd_str = f.read()

        assert svd_str == self.expected_svd_str
