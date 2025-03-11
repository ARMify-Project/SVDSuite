import os
from enum import Enum
from packaging.version import Version
import lxml.etree

from svdsuite.util.xml_parse import safe_parse, safe_fromstring


class SVDSchemaVersion(Enum):
    V1_0 = "1.0"
    V1_1 = "1.1"
    V1_2 = "1.2"
    V1_3_1 = "1.3.1"
    V1_3_2 = "1.3.2"
    V1_3_3 = "1.3.3"
    V1_3_4 = "1.3.4"
    V1_3_5 = "1.3.5"
    V1_3_6 = "1.3.6"
    V1_3_7 = "1.3.7"
    V1_3_8 = "1.3.8"
    V1_3_9 = "1.3.9"
    V1_3_10 = "1.3.10"
    V1_3_11 = "1.3.11"

    @staticmethod
    def get_latest() -> "SVDSchemaVersion":
        versions = [e.value for e in SVDSchemaVersion]
        versions.sort(key=Version)
        return SVDSchemaVersion(versions[-1])


class ValidatorException(Exception):
    pass


class Validator:
    @staticmethod
    def validate_xml_file(
        path: str, get_exception: bool = True, schema_version: SVDSchemaVersion = SVDSchemaVersion.get_latest()
    ) -> bool:
        return Validator._validate(safe_parse(path), get_exception, schema_version)

    @staticmethod
    def validate_xml_content(
        content: bytes, get_exception: bool = True, schema_version: SVDSchemaVersion = SVDSchemaVersion.get_latest()
    ) -> bool:
        return Validator._validate(safe_fromstring(content).getroottree(), get_exception, schema_version)

    @staticmethod
    def validate_xml_str(
        xml_str: str, get_exception: bool = True, schema_version: SVDSchemaVersion = SVDSchemaVersion.get_latest()
    ) -> bool:
        return Validator.validate_xml_content(xml_str.encode(), get_exception, schema_version)

    @staticmethod
    def _validate(
        tree: lxml.etree._ElementTree,  # pyright: ignore[reportPrivateUsage]
        get_exception: bool,
        schema_version: SVDSchemaVersion,
    ) -> bool:
        xsd_path = os.path.join(os.path.dirname(__file__), "schema", f"{schema_version.value}.xsd")
        if not os.path.exists(xsd_path):
            raise ValidatorException(f"Schema file not found: {xsd_path}")

        with open(xsd_path, "rb") as xsd_file:
            schema = lxml.etree.XMLSchema(safe_parse(xsd_file))
            if not schema.validate(tree):
                if get_exception:
                    schema.assertValid(tree)
                return False
        return True
