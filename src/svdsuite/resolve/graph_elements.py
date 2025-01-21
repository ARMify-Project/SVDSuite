from enum import Enum, auto
from abc import ABC

from svdsuite.model.parse import SVDDevice, SVDEnumeratedValueContainer
from svdsuite.model.type_alias import ParsedPeripheralTypes, IntermediatePeripheralTypes
from svdsuite.resolve.exception import ResolveException


class ElementLevel(Enum):
    DEVICE = "Device"
    PERIPHERAL = "Peripheral"
    CLUSTER = "Cluster"
    REGISTER = "Register"
    FIELD = "Field"
    ENUMCONT = "Enum"


class NodeStatus(Enum):
    UNPROCESSED = auto()  # black
    PROCESSED = auto()  # blue


class EdgeType(Enum):
    CHILD_UNRESOLVED = auto()  # black
    CHILD_RESOLVED = auto()  # blue
    PLACEHOLDER = auto()  # red
    DERIVE = auto()  # green


class ResolverNode(ABC):
    pass


class PlaceholderNode(ResolverNode):
    def __init__(self, derive_path: str):
        self._derive_path = derive_path

        super().__init__()

    @property
    def derive_path(self) -> str:
        return self._derive_path


class ElementNode(ResolverNode):
    def __init__(
        self,
        name: None | str,
        level: ElementLevel,
        status: NodeStatus,
        parsed: SVDDevice | ParsedPeripheralTypes,
        processed: None | IntermediatePeripheralTypes = None,
        is_dim_template: bool = False,
    ):
        self._name = name
        self._level = level
        self.status = status
        self._parsed = parsed
        self._is_dim_template = is_dim_template
        self._processed = processed

        super().__init__()

    @property
    def name(self) -> None | str:
        return self._name

    @property
    def level(self) -> ElementLevel:
        return self._level

    @property
    def parsed(self) -> SVDDevice | ParsedPeripheralTypes:
        return self._parsed

    @parsed.setter
    def parsed(self, parsed: SVDEnumeratedValueContainer):
        if not isinstance(parsed, SVDEnumeratedValueContainer):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ResolveException("parsed attribute can only be set to SVDEnumeratedValueContainer")

        self._parsed = parsed

    @property
    def is_dim_template(self) -> bool:
        return self._is_dim_template

    @is_dim_template.setter
    def is_dim_template(self, is_dim_template: bool):
        if self._is_dim_template is True and is_dim_template is False:
            raise ResolveException("is_dim_template attribute is already set to True and can't be set to False")

        self._is_dim_template = is_dim_template

    @property
    def processed(self) -> IntermediatePeripheralTypes:
        if self._processed is None:
            raise ResolveException(f"Processed attribute of node '{self.name}' is None")

        return self._processed

    @property
    def processed_or_none(self) -> None | IntermediatePeripheralTypes:
        return self._processed

    @processed.setter
    def processed(self, processed: IntermediatePeripheralTypes):
        if self._processed is not None:
            raise ResolveException(f"Processed attribute of node '{self.name}' is already set")

        self._processed = processed
