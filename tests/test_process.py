from typing import Callable, Any
import pytest

from svdsuite.process import SVDProcess, _RegisterPropertiesInheritance  # type: ignore
from svdsuite.process_model import (
    AddressBlock,
    Cluster,
    CPU,
    EnumeratedValue,
    EnumeratedValueMap,
    Field,
    Interrupt,
    Peripheral,
    Register,
    SauRegion,
    SauRegionsConfig,
    WriteConstraint,
)
from svdsuite.svd_model import (
    SVDAddressBlock,
    SVDCluster,
    SVDCPU,
    SVDDevice,
    SVDEnumeratedValue,
    SVDEnumeratedValueMap,
    SVDField,
    SVDInterrupt,
    SVDPeripheral,
    SVDRegister,
    SVDSauRegion,
    SVDSauRegionsConfig,
    SVDWriteConstraint,
)
from svdsuite.types import (
    AccessType,
    CPUNameType,
    DataTypeType,
    EndianType,
    EnumeratedTokenType,
    EnumUsageType,
    ModifiedWriteValuesType,
    ProtectionStringType,
    ReadActionType,
    SauAccessType,
)


@pytest.fixture(name="create_register_properties_inheritance")
def fixture_create_register_properties_inheritance() -> Callable[..., _RegisterPropertiesInheritance]:
    def _(
        size: None | int = 0x1000,
        access: None | AccessType = AccessType.READ_ONLY,
        protection: None | ProtectionStringType = ProtectionStringType.SECURE,
        reset_value: None | int = 0x0,
        reset_mask: None | int = 0xFFFFFFFF,
    ) -> _RegisterPropertiesInheritance:
        return _RegisterPropertiesInheritance(
            size=size, access=access, protection=protection, reset_value=reset_value, reset_mask=reset_mask
        )

    return _


class TestProcessInstantiation:
    def test_cls_for_xml_file(self, get_test_svd_file_path: Callable[[str], str]):
        file_path = get_test_svd_file_path("parser_testfile.svd")
        process = SVDProcess.for_xml_file(file_path)

        assert isinstance(process, SVDProcess)

    def test_for_xml_str(self, get_test_svd_file_content: Callable[[str], bytes]):
        file_content = get_test_svd_file_content("parser_testfile.svd")
        file_str = file_content.decode()
        process = SVDProcess.for_xml_str(file_str)

        assert isinstance(process, SVDProcess)

    def test_cls_for_xml_content(self, get_test_svd_file_content: Callable[[str], bytes]):
        file_content = get_test_svd_file_content("parser_testfile.svd")
        process = SVDProcess.for_xml_content(file_content)

        assert isinstance(process, SVDProcess)


class TestEnumeratedValueMapProcess:
    @pytest.fixture
    def helper(
        self,
        create_enumerated_value_map: Callable[..., SVDEnumeratedValueMap],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_enumerated_value_map = create_enumerated_value_map(**kwargs)
            result = SVDProcess(None)._process_enumerated_values_map(  # type: ignore pylint: disable=protected-access
                [svd_enumerated_value_map]
            )
            return getattr(result[0], parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [("UART0", "UART0")])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_description(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("description", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("0x500", "0x500"), (None, None)])
    def test_value(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("value", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, None)])
    def test_is_default(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("is_default", test_input) == expected


# TODO add
# class TestDimArrayIndexProcess:
#     @pytest.fixture
#     def helper(
#         self,
#         create_dim_array_index: Callable[..., SVDDimArrayIndex],
#     ) -> Callable[[str, Any], Any]:
#         def _(parameter: str, test_input: Any) -> Any:
#             kwargs = {parameter: test_input}
#             svd_dim_array_index = create_dim_array_index(**kwargs)
#             result = SVDProcess(None)._process_dim_array_indexs(  # type: ignore pylint: disable=protected-access
#                 [svd_dim_array_index]
#             )
#             return getattr(result[0], parameter)

#         return _


class TestEnumeratedValueProcess:
    @pytest.fixture
    def helper(
        self,
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_enumerated_value = create_enumerated_value(**kwargs)
            result = SVDProcess(None)._process_enumerated_values(  # type: ignore pylint: disable=protected-access
                [svd_enumerated_value]
            )
            return getattr(result[0], parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [("UART0", "UART0"), (None, None)])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("testname", "testname"), (None, None)])
    def test_header_enum_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("header_enum_name", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (EnumUsageType.READ, EnumUsageType.READ),
            (EnumUsageType.WRITE, EnumUsageType.WRITE),
            (EnumUsageType.READ_WRITE, EnumUsageType.READ_WRITE),
            pytest.param(None, EnumUsageType.READ_WRITE),
        ],
    )
    def test_usage(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("usage", test_input) == expected

    def test_enumerated_values_map(
        self,
        helper: Callable[[str, Any], Any],
        create_enumerated_value_map: Callable[..., SVDEnumeratedValueMap],
    ):
        enumerated_values_map = create_enumerated_value_map()
        assert isinstance(helper("enumerated_values_map", [enumerated_values_map])[0], EnumeratedValueMap)

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_derived_from(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("derived_from", test_input) == expected


class TestWriteConstraintProcess:
    @pytest.fixture
    def helper(
        self,
        create_write_constraint: Callable[..., SVDWriteConstraint],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_write_constraint = create_write_constraint(**kwargs)
            result = SVDProcess(None)._process_write_constraint(  # type: ignore pylint: disable=protected-access
                svd_write_constraint
            )
            return getattr(result, parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, None)])
    def test_write_as_read(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("write_as_read", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, None)])
    def test_use_enumerated_values(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("use_enumerated_values", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [((5, 100), (5, 100)), (None, None)])
    def test_range_(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("range_", test_input) == expected


class TestFieldProcess:
    @pytest.fixture
    def helper(
        self,
        create_field: Callable[..., SVDField],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_field = create_field(**kwargs)
            result = SVDProcess(None)._process_fields(  # type: ignore pylint: disable=protected-access
                [svd_field], AccessType.READ_WRITE
            )
            return getattr(result[0], parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [("UART0", "UART0")])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_description(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("description", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(5, 5), (None, None)])
    def test_bit_offset(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("bit_offset", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(5, 5), (None, None)])
    def test_bit_width(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("bit_width", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(5, 5), (None, None)])
    def test_lsb(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("lsb", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(5, 5), (None, None)])
    def test_msb(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("msb", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("5-10", "5-10"), (None, None)])
    def test_bit_range(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("bit_range", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, AccessType.READ_ONLY),
            (AccessType.WRITE_ONLY, AccessType.WRITE_ONLY),
            (AccessType.READ_WRITE, AccessType.READ_WRITE),
            (AccessType.WRITE_ONCE, AccessType.WRITE_ONCE),
            (AccessType.READ_WRITE_ONCE, AccessType.READ_WRITE_ONCE),
            # if None, AccessType is taken from parent register, which is READ_WRITE in this case
            (None, AccessType.READ_WRITE),
        ],
    )
    def test_access(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("access", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ModifiedWriteValuesType.ONE_TO_CLEAR, ModifiedWriteValuesType.ONE_TO_CLEAR),
            (ModifiedWriteValuesType.ONE_TO_SET, ModifiedWriteValuesType.ONE_TO_SET),
            (ModifiedWriteValuesType.ONE_TO_TOGGLE, ModifiedWriteValuesType.ONE_TO_TOGGLE),
            (ModifiedWriteValuesType.ZERO_TO_CLEAR, ModifiedWriteValuesType.ZERO_TO_CLEAR),
            (ModifiedWriteValuesType.ZERO_TO_SET, ModifiedWriteValuesType.ZERO_TO_SET),
            (ModifiedWriteValuesType.ZERO_TO_TOGGLE, ModifiedWriteValuesType.ZERO_TO_TOGGLE),
            (ModifiedWriteValuesType.CLEAR, ModifiedWriteValuesType.CLEAR),
            (ModifiedWriteValuesType.SET, ModifiedWriteValuesType.SET),
            (ModifiedWriteValuesType.MODIFY, ModifiedWriteValuesType.MODIFY),
            (None, ModifiedWriteValuesType.MODIFY),
        ],
    )
    def test_modified_write_values(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("modified_write_values", test_input) == expected

    def test_write_constraint(
        self,
        helper: Callable[[str, Any], Any],
        create_write_constraint: Callable[..., SVDWriteConstraint],
    ):
        write_constraint = create_write_constraint()
        assert isinstance(helper("write_constraint", write_constraint), WriteConstraint)
        assert helper("write_constraint", None) is None

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ReadActionType.CLEAR, ReadActionType.CLEAR),
            (ReadActionType.SET, ReadActionType.SET),
            (ReadActionType.MODIFY, ReadActionType.MODIFY),
            (ReadActionType.MODIFY_EXTERNAL, ReadActionType.MODIFY_EXTERNAL),
            (None, None),
        ],
    )
    def test_read_action(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("read_action", test_input) == expected

    def test_enumerated_values(
        self,
        helper: Callable[[str, Any], Any],
        create_enumerated_value: Callable[..., SVDEnumeratedValue],
    ):
        enumerated_value = create_enumerated_value()
        assert isinstance(helper("enumerated_values", [enumerated_value])[0], EnumeratedValue)

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_derived_from(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("derived_from", test_input) == expected


class TestAddressBlockProcess:
    @pytest.fixture
    def helper(
        self,
        create_address_block: Callable[..., SVDAddressBlock],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_address_block = create_address_block(**kwargs)
            result = SVDProcess(None)._process_address_blocks(  # type: ignore pylint: disable=protected-access
                [svd_address_block], None
            )
            return getattr(result[0], parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [(0x500, 0x500)])
    def test_offset(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("offset", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(0x1000, 0x1000)])
    def test_size(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("size", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (EnumeratedTokenType.REGISTERS, EnumeratedTokenType.REGISTERS),
            (EnumeratedTokenType.BUFFER, EnumeratedTokenType.BUFFER),
            (EnumeratedTokenType.RESERVED, EnumeratedTokenType.RESERVED),
        ],
    )
    def test_usage(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("usage", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, ProtectionStringType.SECURE),
            (ProtectionStringType.NON_SECURE, ProtectionStringType.NON_SECURE),
            (ProtectionStringType.PRIVILEGED, ProtectionStringType.PRIVILEGED),
            (None, None),
        ],
    )
    def test_protection(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("protection", test_input) == expected


class TestInterruptProcess:
    @pytest.fixture
    def helper(
        self,
        create_interrupt: Callable[..., SVDInterrupt],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_interrupt = create_interrupt(**kwargs)
            result = SVDProcess(None)._process_interrupts(  # type: ignore pylint: disable=protected-access
                [svd_interrupt]
            )
            return getattr(result[0], parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [("UART0", "UART0")])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_description(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("description", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(0x500, 0x500)])
    def test_value(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("value", test_input) == expected


class TestRegisterProcess:
    @pytest.fixture
    def helper(
        self,
        create_register: Callable[..., SVDRegister],
        create_register_properties_inheritance: Callable[..., _RegisterPropertiesInheritance],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_register = create_register(**kwargs)
            result = SVDProcess(None)._process_register(  # type: ignore pylint: disable=protected-access
                svd_register, create_register_properties_inheritance()
            )
            return getattr(result, parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_size(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("size", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, AccessType.READ_ONLY),
            (AccessType.WRITE_ONLY, AccessType.WRITE_ONLY),
            (AccessType.READ_WRITE, AccessType.READ_WRITE),
            (AccessType.WRITE_ONCE, AccessType.WRITE_ONCE),
            (AccessType.READ_WRITE_ONCE, AccessType.READ_WRITE_ONCE),
        ],
    )
    def test_access(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("access", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, ProtectionStringType.SECURE),
            (ProtectionStringType.NON_SECURE, ProtectionStringType.NON_SECURE),
            (ProtectionStringType.PRIVILEGED, ProtectionStringType.PRIVILEGED),
        ],
    )
    def test_protection(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("protection", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_reset_value(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("reset_value", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_reset_mask(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("reset_mask", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0", "UART0")])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_display_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("display_name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_description(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("description", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_alternate_group(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("alternate_group", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_alternate_register(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("alternate_register", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_address_offset(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("address_offset", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (DataTypeType.UINT8_T, DataTypeType.UINT8_T),
            (DataTypeType.UINT16_T, DataTypeType.UINT16_T),
            (DataTypeType.UINT32_T, DataTypeType.UINT32_T),
            (DataTypeType.UINT64_T, DataTypeType.UINT64_T),
            (DataTypeType.INT8_T, DataTypeType.INT8_T),
            (DataTypeType.INT16_T, DataTypeType.INT16_T),
            (DataTypeType.INT32_T, DataTypeType.INT32_T),
            (DataTypeType.INT64_T, DataTypeType.INT64_T),
            (DataTypeType.UINT8_T_PTR, DataTypeType.UINT8_T_PTR),
            (DataTypeType.UINT16_T_PTR, DataTypeType.UINT16_T_PTR),
            (DataTypeType.UINT32_T_PTR, DataTypeType.UINT32_T_PTR),
            (DataTypeType.UINT64_T_PTR, DataTypeType.UINT64_T_PTR),
            (DataTypeType.INT8_T_PTR, DataTypeType.INT8_T_PTR),
            (DataTypeType.INT16_T_PTR, DataTypeType.INT16_T_PTR),
            (DataTypeType.INT32_T_PTR, DataTypeType.INT32_T_PTR),
            (DataTypeType.INT64_T_PTR, DataTypeType.INT64_T_PTR),
            (None, None),
        ],
    )
    def test_data_type(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("data_type", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ModifiedWriteValuesType.ONE_TO_CLEAR, ModifiedWriteValuesType.ONE_TO_CLEAR),
            (ModifiedWriteValuesType.ONE_TO_SET, ModifiedWriteValuesType.ONE_TO_SET),
            (ModifiedWriteValuesType.ONE_TO_TOGGLE, ModifiedWriteValuesType.ONE_TO_TOGGLE),
            (ModifiedWriteValuesType.ZERO_TO_CLEAR, ModifiedWriteValuesType.ZERO_TO_CLEAR),
            (ModifiedWriteValuesType.ZERO_TO_SET, ModifiedWriteValuesType.ZERO_TO_SET),
            (ModifiedWriteValuesType.ZERO_TO_TOGGLE, ModifiedWriteValuesType.ZERO_TO_TOGGLE),
            (ModifiedWriteValuesType.CLEAR, ModifiedWriteValuesType.CLEAR),
            (ModifiedWriteValuesType.SET, ModifiedWriteValuesType.SET),
            (ModifiedWriteValuesType.MODIFY, ModifiedWriteValuesType.MODIFY),
            (None, ModifiedWriteValuesType.MODIFY),
        ],
    )
    def test_modified_write_values(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("modified_write_values", test_input) == expected

    def test_write_constraint(
        self,
        helper: Callable[[str, Any], Any],
        create_write_constraint: Callable[..., SVDWriteConstraint],
    ):
        write_constraint = create_write_constraint()
        assert isinstance(helper("write_constraint", write_constraint), WriteConstraint)
        assert helper("write_constraint", None) is None

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ReadActionType.CLEAR, ReadActionType.CLEAR),
            (ReadActionType.SET, ReadActionType.SET),
            (ReadActionType.MODIFY, ReadActionType.MODIFY),
            (ReadActionType.MODIFY_EXTERNAL, ReadActionType.MODIFY_EXTERNAL),
            (None, None),
        ],
    )
    def test_read_action(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("read_action", test_input) == expected

    def test_fields(
        self,
        helper: Callable[[str, Any], Any],
        create_field: Callable[..., SVDField],
    ):
        field = create_field()
        assert isinstance(helper("fields", [field])[0], Field)

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_derived_from(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("derived_from", test_input) == expected


class TestClusterProcess:
    @pytest.fixture
    def helper(
        self,
        create_cluster: Callable[..., SVDCluster],
        create_register_properties_inheritance: Callable[..., _RegisterPropertiesInheritance],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_cluster = create_cluster(**kwargs)
            result = SVDProcess(None)._process_cluster(  # type: ignore pylint: disable=protected-access
                svd_cluster, create_register_properties_inheritance()
            )
            return getattr(result, parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_size(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("size", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, AccessType.READ_ONLY),
            (AccessType.WRITE_ONLY, AccessType.WRITE_ONLY),
            (AccessType.READ_WRITE, AccessType.READ_WRITE),
            (AccessType.WRITE_ONCE, AccessType.WRITE_ONCE),
            (AccessType.READ_WRITE_ONCE, AccessType.READ_WRITE_ONCE),
        ],
    )
    def test_access(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("access", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, ProtectionStringType.SECURE),
            (ProtectionStringType.NON_SECURE, ProtectionStringType.NON_SECURE),
            (ProtectionStringType.PRIVILEGED, ProtectionStringType.PRIVILEGED),
        ],
    )
    def test_protection(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("protection", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_reset_value(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("reset_value", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_reset_mask(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("reset_mask", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0", "UART0")])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_description(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("description", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_alternate_cluster(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("alternate_cluster", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_header_struct_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("header_struct_name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_address_offset(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("address_offset", test_input) == expected

    def test_registers_clusters(
        self,
        helper: Callable[[str, Any], Any],
        create_register: Callable[..., SVDRegister],
        create_cluster: Callable[..., SVDCluster],
    ):
        register = create_register()
        cluster = create_cluster()
        ret1, ret2 = helper("registers_clusters", [register, cluster])
        assert isinstance(ret1, Register)
        assert isinstance(ret2, Cluster)

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_derived_from(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("derived_from", test_input) == expected


class TestPeripheralProcess:
    @pytest.fixture
    def helper(
        self,
        create_peripheral: Callable[..., SVDPeripheral],
        create_register_properties_inheritance: Callable[..., _RegisterPropertiesInheritance],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_peripheral = create_peripheral(**kwargs)
            result = SVDProcess(None)._process_peripheral(  # type: ignore pylint: disable=protected-access
                svd_peripheral, create_register_properties_inheritance()
            )
            return getattr(result, parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_size(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("size", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, AccessType.READ_ONLY),
            (AccessType.WRITE_ONLY, AccessType.WRITE_ONLY),
            (AccessType.READ_WRITE, AccessType.READ_WRITE),
            (AccessType.WRITE_ONCE, AccessType.WRITE_ONCE),
            (AccessType.READ_WRITE_ONCE, AccessType.READ_WRITE_ONCE),
        ],
    )
    def test_access(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("access", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, ProtectionStringType.SECURE),
            (ProtectionStringType.NON_SECURE, ProtectionStringType.NON_SECURE),
            (ProtectionStringType.PRIVILEGED, ProtectionStringType.PRIVILEGED),
        ],
    )
    def test_protection(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("protection", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_reset_value(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("reset_value", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_reset_mask(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("reset_mask", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0", "UART0")])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_version(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("version", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_description(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("description", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_alternate_peripheral(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("alternate_peripheral", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_group_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("group_name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_prepend_to_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("prepend_to_name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_append_to_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("append_to_name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_header_struct_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("header_struct_name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("UART0 Peripheral", "UART0 Peripheral"), (None, None)])
    def test_disable_condition(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("disable_condition", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(0x40000000, 0x40000000)])
    def test_base_address(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("base_address", test_input) == expected

    def test_address_blocks(
        self,
        helper: Callable[[str, Any], Any],
        create_address_block: Callable[..., SVDAddressBlock],
    ):
        address_block = create_address_block()
        assert isinstance(helper("address_blocks", [address_block])[0], AddressBlock)

    def test_interrupts(
        self,
        helper: Callable[[str, Any], Any],
        create_interrupt: Callable[..., SVDInterrupt],
    ):
        interrupt = create_interrupt()
        assert isinstance(helper("interrupts", [interrupt])[0], Interrupt)

    def test_registers_clusters(
        self,
        helper: Callable[[str, Any], Any],
        create_register: Callable[..., SVDRegister],
        create_cluster: Callable[..., SVDCluster],
    ):
        register = create_register()
        cluster = create_cluster()
        ret1, ret2 = helper("registers_clusters", [register, cluster])
        assert isinstance(ret1, Register)
        assert isinstance(ret2, Cluster)

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_derived_from(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("derived_from", test_input) == expected


class TestSauRegionProcess:
    @pytest.fixture
    def helper(
        self,
        create_sau_region: Callable[..., SVDSauRegion],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_sau_region = create_sau_region(**kwargs)
            result = SVDProcess(None)._process_sau_regions(  # type: ignore pylint: disable=protected-access
                [svd_sau_region]
            )
            return getattr(result[0], parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, True)])
    def test_enabled(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("enabled", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(400, 400)])
    def test_base(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("base", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(400, 400)])
    def test_limit(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("limit", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (SauAccessType.NON_SECURE_CALLABLE, SauAccessType.NON_SECURE_CALLABLE),
            (SauAccessType.NON_SECURE, SauAccessType.NON_SECURE),
        ],
    )
    def test_access(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("access", test_input) == expected


class TestSauRegionsConfigProcess:
    @pytest.fixture
    def helper(
        self,
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_sau_regions_config = create_sau_regions_config(**kwargs)
            result = SVDProcess(None)._process_sau_regions_config(  # type: ignore pylint: disable=protected-access
                svd_sau_regions_config
            )
            return getattr(result, parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, True)])
    def test_enabled(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("enabled", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, ProtectionStringType.SECURE),
            (ProtectionStringType.NON_SECURE, ProtectionStringType.NON_SECURE),
            (ProtectionStringType.PRIVILEGED, ProtectionStringType.PRIVILEGED),
            (None, ProtectionStringType.SECURE),
        ],
    )
    def test_protection_when_disabled(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("protection_when_disabled", test_input) == expected

    def test_regions(
        self,
        helper: Callable[[str, Any], Any],
        create_sau_region: Callable[..., SVDSauRegion],
    ):
        sau_region = create_sau_region()
        assert isinstance(helper("regions", [sau_region])[0], SauRegion)


class TestCPUProcess:
    @pytest.fixture
    def helper(
        self,
        create_cpu: Callable[..., SVDCPU],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_cpu = create_cpu(**kwargs)
            result = SVDProcess(None)._process_cpu(svd_cpu)  # type: ignore pylint: disable=protected-access
            return getattr(result, parameter)

        return _

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (CPUNameType.CM0, CPUNameType.CM0),
            (CPUNameType.CM0PLUS, CPUNameType.CM0PLUS),
            (CPUNameType.CM0_PLUS, CPUNameType.CM0PLUS),
            (CPUNameType.CM1, CPUNameType.CM1),
            (CPUNameType.CM3, CPUNameType.CM3),
            (CPUNameType.CM4, CPUNameType.CM4),
            (CPUNameType.CM7, CPUNameType.CM7),
            (CPUNameType.CM23, CPUNameType.CM23),
            (CPUNameType.CM33, CPUNameType.CM33),
            (CPUNameType.CM35P, CPUNameType.CM35P),
            (CPUNameType.CM52, CPUNameType.CM52),
            (CPUNameType.CM55, CPUNameType.CM55),
            (CPUNameType.CM85, CPUNameType.CM85),
            (CPUNameType.SC000, CPUNameType.SC000),
            (CPUNameType.SC300, CPUNameType.SC300),
            (CPUNameType.ARMV8MML, CPUNameType.ARMV8MML),
            (CPUNameType.ARMV8MBL, CPUNameType.ARMV8MBL),
            (CPUNameType.ARMV81MML, CPUNameType.ARMV81MML),
            (CPUNameType.CA5, CPUNameType.CA5),
            (CPUNameType.CA7, CPUNameType.CA7),
            (CPUNameType.CA8, CPUNameType.CA8),
            (CPUNameType.CA9, CPUNameType.CA9),
            (CPUNameType.CA15, CPUNameType.CA15),
            (CPUNameType.CA17, CPUNameType.CA17),
            (CPUNameType.CA53, CPUNameType.CA53),
            (CPUNameType.CA57, CPUNameType.CA57),
            (CPUNameType.CA72, CPUNameType.CA72),
            (CPUNameType.SMC1, CPUNameType.SMC1),
            (CPUNameType.OTHER, CPUNameType.OTHER),
        ],
    )
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test")])
    def test_revision(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("revision", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (EndianType.LITTLE, EndianType.LITTLE),
            (EndianType.BIG, EndianType.BIG),
            (EndianType.SELECTABLE, EndianType.SELECTABLE),
            (EndianType.OTHER, EndianType.OTHER),
        ],
    )
    def test_endian(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("endian", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, False)])
    def test_mpu_present(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("mpu_present", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, False)])
    def test_fpu_present(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("fpu_present", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, False)])
    def test_fpu_dp(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("fpu_dp", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, False)])
    def test_dsp_present(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("dsp_present", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, False)])
    def test_icache_present(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("icache_present", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, False)])
    def test_dcache_present(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("dcache_present", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, False)])
    def test_itcm_present(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("itcm_present", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, False)])
    def test_dtcm_present(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("dtcm_present", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False), (None, True)])
    def test_vtor_present(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("vtor_present", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(32, 32)])
    def test_nvic_prio_bits(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("nvic_prio_bits", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(True, True), (False, False)])
    def test_vendor_systick_config(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("vendor_systick_config", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(24, 24), (None, None)])
    def test_device_num_interrupts(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("device_num_interrupts", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(24, 24), (None, None)])
    def test_sau_num_regions(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("sau_num_regions", test_input) == expected

    def test_sau_regions_config(
        self,
        helper: Callable[[str, Any], Any],
        create_sau_regions_config: Callable[..., SVDSauRegionsConfig],
    ):
        sau_regions_config = create_sau_regions_config()
        assert isinstance(helper("sau_regions_config", sau_regions_config), SauRegionsConfig)
        assert helper("sau_regions_config", None) is None


class TestDeviceProcess:
    @pytest.fixture
    def helper(
        self,
        create_device: Callable[..., SVDDevice],
    ) -> Callable[[str, Any], Any]:
        def _(parameter: str, test_input: Any) -> Any:
            kwargs = {parameter: test_input}
            svd_device = create_device(**kwargs)
            result = SVDProcess(None)._process_device(svd_device)  # type: ignore pylint: disable=protected-access
            return getattr(result, parameter)

        return _

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_size(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("size", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (AccessType.READ_ONLY, AccessType.READ_ONLY),
            (AccessType.WRITE_ONLY, AccessType.WRITE_ONLY),
            (AccessType.READ_WRITE, AccessType.READ_WRITE),
            (AccessType.WRITE_ONCE, AccessType.WRITE_ONCE),
            (AccessType.READ_WRITE_ONCE, AccessType.READ_WRITE_ONCE),
        ],
    )
    def test_access(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("access", test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            (ProtectionStringType.SECURE, ProtectionStringType.SECURE),
            (ProtectionStringType.NON_SECURE, ProtectionStringType.NON_SECURE),
            (ProtectionStringType.PRIVILEGED, ProtectionStringType.PRIVILEGED),
        ],
    )
    def test_protection(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("protection", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_reset_value(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("reset_value", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(500, 500)])
    def test_reset_mask(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("reset_mask", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_vendor(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("vendor", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_vendor_id(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("vendor_id", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test")])
    def test_name(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("name", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_series(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("series", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test")])
    def test_version(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("version", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test")])
    def test_description(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("description", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_license_text(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("license_text", test_input) == expected

    def test_cpu(
        self,
        helper: Callable[[str, Any], Any],
        create_cpu: Callable[..., SVDCPU],
    ):
        cpu = create_cpu()
        assert isinstance(helper("cpu", cpu), CPU)
        assert helper("cpu", None) is None

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_header_system_filename(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("header_system_filename", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [("test", "test"), (None, None)])
    def test_header_definitions_prefix(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("header_definitions_prefix", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(32, 32)])
    def test_address_unit_bits(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("address_unit_bits", test_input) == expected

    @pytest.mark.parametrize("test_input, expected", [(32, 32)])
    def test_width(
        self,
        helper: Callable[[str, Any], Any],
        test_input: Any,
        expected: Any,
    ):
        assert helper("width", test_input) == expected

    def test_peripherals(
        self,
        helper: Callable[[str, Any], Any],
        create_peripheral: Callable[..., SVDPeripheral],
    ):
        peripheral = create_peripheral()
        assert isinstance(helper("peripherals", [peripheral])[0], Peripheral)
