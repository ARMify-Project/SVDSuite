import os
from enum import Enum
from packaging.version import Version
import lxml.etree


class SVDSchemaVersion(Enum):
    V1_3_9 = "1.3.9"
    V1_3_10 = "1.3.10"

    @staticmethod
    def get_latest() -> "SVDSchemaVersion":
        versions = [e.value for e in SVDSchemaVersion]
        versions.sort(key=Version)
        return SVDSchemaVersion(versions[-1])


class SVDValidatorException(Exception):
    pass


class SVDValidator:
    @staticmethod
    def validate_xml_file(
        path: str, get_exception: bool = True, schema_version: SVDSchemaVersion = SVDSchemaVersion.get_latest()
    ) -> bool:
        return SVDValidator._validate(lxml.etree.parse(path), get_exception, schema_version)

    @staticmethod
    def validate_xml_content(
        content: bytes, get_exception: bool = True, schema_version: SVDSchemaVersion = SVDSchemaVersion.get_latest()
    ) -> bool:
        return SVDValidator._validate(lxml.etree.fromstring(content).getroottree(), get_exception, schema_version)

    @staticmethod
    def validate_xml_str(
        xml_str: str, get_exception: bool = True, schema_version: SVDSchemaVersion = SVDSchemaVersion.get_latest()
    ) -> bool:
        return SVDValidator.validate_xml_content(xml_str.encode(), get_exception, schema_version)

    @staticmethod
    def _validate(
        tree: lxml.etree._ElementTree,  # pyright: ignore[reportPrivateUsage]
        get_exception: bool,
        schema_version: SVDSchemaVersion,
    ) -> bool:
        xsd_path = os.path.join(os.path.dirname(__file__), "schema", f"{schema_version.value}.xsd")
        if not os.path.exists(xsd_path):
            raise SVDValidatorException(f"Schema file not found: {xsd_path}")

        with open(xsd_path, "rb") as xsd_file:
            schema = lxml.etree.XMLSchema(lxml.etree.parse(xsd_file))
            if not schema.validate(tree):
                if get_exception:
                    schema.assertValid(tree)
                return False
        return True
