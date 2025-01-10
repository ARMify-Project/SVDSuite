from typing import Callable
import pytest

from svdsuite.process import Process
from svdsuite.model.process import Device


@pytest.fixture(name="get_processed_device_from_testfile")
def fixture_get_processed_device_from_testfile(get_test_svd_file_content: Callable[[str], bytes]):
    def _(file_name: str) -> Device:
        file_content = get_test_svd_file_content(file_name)
        return Process.from_xml_content(file_content).get_processed_device()

    return _
