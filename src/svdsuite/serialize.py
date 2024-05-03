import lxml.etree
from svdsuite.svd_model import SVDDevice


class SVDSerializer:
    @staticmethod
    def device_to_svd_file(path: str, device: SVDDevice, pretty_print: bool = False):
        with open(path, "wb") as f:
            f.write(lxml.etree.tostring(device.to_xml(), pretty_print=pretty_print))

    @staticmethod
    def device_to_svd_content(device: SVDDevice, pretty_print: bool = False) -> bytes:
        return lxml.etree.tostring(device.to_xml(), pretty_print=pretty_print)

    @staticmethod
    def device_to_svd_str(device: SVDDevice, pretty_print: bool = False) -> str:
        return SVDSerializer.device_to_svd_content(device, pretty_print=pretty_print).decode()
