from typing import BinaryIO
import warnings
from lxml import etree

from svdsuite.util.parser_exception_warning import ParserWarning, custom_warning_format

warnings.formatwarning = custom_warning_format

# Define the five most common encodings to try.
_COMMON_ENCODINGS = ["utf-8", "windows-1252", "iso-8859-1", "utf-16", "ascii"]


def safe_parse(path_or_file: str | BinaryIO) -> etree._ElementTree:  # pyright: ignore[reportPrivateUsage]
    # First attempt: no encoding, recover=False.
    try:
        parser = etree.XMLParser(recover=False)
        tree = etree.parse(path_or_file, parser=parser)
        return tree
    except etree.XMLSyntaxError as e:
        original_exception = e

    # Second attempt: try common encodings with recover=False.
    for enc in _COMMON_ENCODINGS:
        try:
            parser = etree.XMLParser(encoding=enc, recover=False)
            tree = etree.parse(path_or_file, parser=parser)
            warnings.warn(
                f"XML file parsed using fallback encoding '{enc}' with recover=False.",
                ParserWarning,
            )
            return tree
        except etree.XMLSyntaxError:
            continue

    # Third attempt: try common encodings with recover=True.
    for enc in _COMMON_ENCODINGS:
        try:
            parser = etree.XMLParser(encoding=enc, recover=True)
            tree = etree.parse(path_or_file, parser=parser)
            warnings.warn(
                f"XML file parsed using fallback encoding '{enc}' with recover=True.",
                ParserWarning,
            )
            return tree
        except etree.XMLSyntaxError:
            continue

    # If all attempts fail, re-raise the original exception.
    raise original_exception


def safe_fromstring(content: bytes) -> etree._Element:  # pyright: ignore[reportPrivateUsage]
    # First attempt: no encoding, recover=False.
    try:
        parser = etree.XMLParser(recover=False)
        root = etree.fromstring(content, parser=parser)
        return root
    except etree.XMLSyntaxError as e:
        original_exception = e

    # Second attempt: try common encodings with recover=False.
    for enc in _COMMON_ENCODINGS:
        try:
            parser = etree.XMLParser(encoding=enc, recover=False)
            root = etree.fromstring(content, parser=parser)
            warnings.warn(
                f"XML content parsed using fallback encoding '{enc}' with recover=False.",
                ParserWarning,
            )
            return root
        except etree.XMLSyntaxError:
            continue

    # Third attempt: try common encodings with recover=True.
    for enc in _COMMON_ENCODINGS:
        try:
            parser = etree.XMLParser(encoding=enc, recover=True)
            root = etree.fromstring(content, parser=parser)
            warnings.warn(
                f"XML content parsed using fallback encoding '{enc}' with recover=True.",
                ParserWarning,
            )
            return root
        except etree.XMLSyntaxError:
            continue

    # If all attempts fail, re-raise the original exception.
    raise original_exception
