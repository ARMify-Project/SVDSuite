from typing import TypeAlias

from svdsuite.model.parse import (
    SVDPeripheral,
    SVDCluster,
    SVDRegister,
    SVDField,
    SVDEnumeratedValueContainer,
)
from svdsuite.model.process import (
    Peripheral,
    Cluster,
    Register,
    Field,
    EnumeratedValueContainer,
)

ParsedPeripheralTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField | SVDEnumeratedValueContainer
ParsedDimablePeripheralTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField
ProcessedPeripheralTypes: TypeAlias = Peripheral | Cluster | Register | Field | EnumeratedValueContainer
ProcessedDimablePeripheralTypes: TypeAlias = Peripheral | Cluster | Register | Field
