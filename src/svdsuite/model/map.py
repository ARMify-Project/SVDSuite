from dataclasses import dataclass, field

from svdsuite.model.process import IPeripheral, IRegister, IField
from svdsuite.model.types import AccessType, ProtectionStringType


@dataclass(kw_only=True)
class MapRegister:
    size: int
    access: AccessType
    protection: ProtectionStringType
    reset_value: int
    reset_mask: int
    name: str
    display_name: None | str = None
    description: None | str = None
    address: int
    fields: list[IField] = field(default_factory=list)
    processed: IRegister


@dataclass(kw_only=True)
class MapPeripheral:
    name: str
    description: None | str = None
    address: int
    allocated_range: tuple[int, int]
    registers: list[MapRegister] = field(default_factory=list)
    processed: IPeripheral
