from enum import Enum
import warnings

from svdsuite.util.parser_exception_warning import ParserWarning


class CPUNameType(Enum):
    CM0 = "CM0"
    CM0PLUS = "CM0PLUS"
    CM0_PLUS = "CM0+"
    CM1 = "CM1"
    CM3 = "CM3"
    CM4 = "CM4"
    CM7 = "CM7"
    CM23 = "CM23"
    CM33 = "CM33"
    CM35P = "CM35P"
    CM52 = "CM52"
    CM55 = "CM55"
    CM85 = "CM85"
    SC000 = "SC000"
    SC300 = "SC300"
    ARMV8MML = "ARMV8MML"
    ARMV8MBL = "ARMV8MBL"
    ARMV81MML = "ARMV81MML"
    CA5 = "CA5"
    CA7 = "CA7"
    CA8 = "CA8"
    CA9 = "CA9"
    CA15 = "CA15"
    CA17 = "CA17"
    CA53 = "CA53"
    CA57 = "CA57"
    CA72 = "CA72"
    SMC1 = "SMC1"
    OTHER = "other"

    @classmethod
    def from_str(cls, label: str):
        try:
            return CPUNameType[label.upper()]
        except KeyError:
            pass

        if label == "CM0+":
            return cls.CM0_PLUS

        raise NotImplementedError


class EndianType(Enum):
    LITTLE = "little"
    BIG = "big"
    SELECTABLE = "selectable"
    OTHER = "other"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class ProtectionStringType(Enum):
    SECURE = "s"
    NON_SECURE = "n"
    PRIVILEGED = "p"
    ANY = "any"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class SauAccessType(Enum):
    NON_SECURE_CALLABLE = "c"
    NON_SECURE = "n"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class AccessType(Enum):
    READ_ONLY = "read-only"
    WRITE_ONLY = "write-only"
    READ_WRITE = "read-write"
    WRITE_ONCE = "writeOnce"
    READ_WRITE_ONCE = "read-writeOnce"

    @classmethod
    def from_str(cls, label: str) -> "AccessType | None":
        label_lower = label.lower()

        for item in cls:
            if item.value.lower() == label_lower:
                return item

        # SVDConv accepts write with warning "Deprecated: 'write' Use 'write-only' instead"
        if label_lower == "write":
            return cls.WRITE_ONLY

        # SVDConv accepts read with warning "Deprecated: 'read' Use 'read-only' instead"
        if label_lower == "read":
            return cls.READ_ONLY

        warnings.warn(f"Unknown AccessType '{label}'. Setting access to 'None'.", ParserWarning)

        return None


class EnumeratedTokenType(Enum):
    REGISTERS = "registers"
    BUFFER = "buffer"
    RESERVED = "reserved"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class DataTypeType(Enum):
    UINT8_T = "uint8_t"
    UINT16_T = "uint16_t"
    UINT32_T = "uint32_t"
    UINT64_T = "uint64_t"
    INT8_T = "int8_t"
    INT16_T = "int16_t"
    INT32_T = "int32_t"
    INT64_T = "int64_t"
    UINT8_T_PTR = "uint8_t *"
    UINT16_T_PTR = "uint16_t *"
    UINT32_T_PTR = "uint32_t *"
    UINT64_T_PTR = "uint64_t *"
    INT8_T_PTR = "int8_t *"
    INT16_T_PTR = "int16_t *"
    INT32_T_PTR = "int32_t *"
    INT64_T_PTR = "int64_t *"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class ModifiedWriteValuesType(Enum):
    ONE_TO_CLEAR = "oneToClear"
    ONE_TO_SET = "oneToSet"
    ONE_TO_TOGGLE = "oneToToggle"
    ZERO_TO_CLEAR = "zeroToClear"
    ZERO_TO_SET = "zeroToSet"
    ZERO_TO_TOGGLE = "zeroToToggle"
    CLEAR = "clear"
    SET = "set"
    MODIFY = "modify"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class ReadActionType(Enum):
    CLEAR = "clear"
    SET = "set"
    MODIFY = "modify"
    MODIFY_EXTERNAL = "modifyExternal"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc


class EnumUsageType(Enum):
    READ = "read"
    WRITE = "write"
    READ_WRITE = "read-write"

    @classmethod
    def from_str(cls, label: str):
        try:
            return cls(label)
        except ValueError as exc:
            raise NotImplementedError from exc
