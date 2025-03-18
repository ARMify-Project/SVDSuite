from typing import TypeAlias

from svdsuite.model.parse import (
    SVDPeripheral,
    SVDCluster,
    SVDRegister,
    SVDField,
    SVDEnumeratedValueContainer,
)
from svdsuite.model.process import (
    IPeripheral,
    ICluster,
    IRegister,
    IField,
    IEnumeratedValueContainer,
)

ParsedPeripheralTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField | SVDEnumeratedValueContainer
ParsedDimablePeripheralTypes: TypeAlias = SVDPeripheral | SVDCluster | SVDRegister | SVDField
IntermediatePeripheralTypes: TypeAlias = IPeripheral | ICluster | IRegister | IField | IEnumeratedValueContainer
IntermediateDimablePeripheralTypes: TypeAlias = IPeripheral | ICluster | IRegister | IField
