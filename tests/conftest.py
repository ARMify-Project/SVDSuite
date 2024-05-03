import os
from typing import Callable
import lxml.etree
import pytest


@pytest.fixture(name="get_test_svd_file_path", scope="session", autouse=False)
def fixture_get_test_svd_file_path() -> Callable[[str], str]:
    def _(file_name: str):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(test_dir, "svd", file_name)

    return _


@pytest.fixture(name="get_test_svd_file_content", scope="session", autouse=False)
def fixture_get_test_svd_file_content(get_test_svd_file_path: Callable[[str], str]) -> Callable[[str], bytes]:
    def _(file_name: str):
        file_path = get_test_svd_file_path(file_name)

        with open(file_path, "rb") as file:
            return file.read()

    return _


@pytest.fixture(scope="session", autouse=False)
def modify_test_svd_file_and_get_content(
    get_test_svd_file_content: Callable[[str], bytes]
) -> Callable[[str, str, None | str, None | str], bytes]:
    def _(file_name: str, xpath_str: str, attribute: None | str, value: None | str):
        file_content = get_test_svd_file_content(file_name)
        tree = lxml.etree.fromstring(file_content)

        element_list = tree.xpath(xpath_str)

        if not isinstance(element_list, list):
            raise ValueError(f"can't find an element for xpath '{xpath_str}'")

        element = element_list[0]

        if not isinstance(element, lxml.etree._Element):  # pyright: ignore[reportPrivateUsage] pylint: disable=W0212
            raise ValueError(f"can't find an element for xpath '{xpath_str}'")

        if attribute is None:
            if value is None:
                parent = element.getparent()

                if parent is None:
                    raise ValueError(f"can't find parent for element with xpath '{xpath_str}'")

                parent.remove(element)
            else:
                element.text = value
        else:
            if value is None:
                del element.attrib[attribute]
            else:
                element.attrib[attribute] = value

        return lxml.etree.tostring(tree, encoding="utf8")

    return _
