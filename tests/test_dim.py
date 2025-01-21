import pytest

from svdsuite.process import _ProcessDimension, ProcessException  # pyright: ignore[reportPrivateUsage]
from svdsuite.model.parse import SVDCluster


class TestDimUtils:
    @pytest.mark.parametrize(
        "dim,dim_index,expected",
        [
            pytest.param(None, None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
            pytest.param(0, None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
            (1, None, ["0"]),
            (4, None, ["0", "1", "2", "3"]),
            (2, "0-1", ["0", "1"]),
            (4, "3-6", ["3", "4", "5", "6"]),
            (2, "01-02", ["1", "2"]),
            pytest.param(2, "1-1", None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
            pytest.param(2, "1-0", None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
            (2, "A-B", ["A", "B"]),
            (4, "C-F", ["C", "D", "E", "F"]),
            pytest.param(2, "A-A", None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
            pytest.param(2, "B-A", None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
            ###
            (2, "_0aY, _1bZ", ["_0aY", "_1bZ"]),
            pytest.param(3, "_0aY, _1bZ", None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
        ],
    )
    def test_resolve_dim_index(
        self,
        dim: None | int,
        dim_index: None | str,
        expected: None | list[str],
    ):
        result = _ProcessDimension()._process_dim_index(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
            dim, dim_index
        )

        assert result == expected

    @pytest.mark.parametrize(
        "name,dim,dim_index,expected",
        [
            ("GPIO_%s_CTRL", 2, "A, B", (["GPIO_A_CTRL", "GPIO_B_CTRL"], [None, None])),
            ("IRQ%s", 4, "3-6", (["IRQ3", "IRQ4", "IRQ5", "IRQ6"], [None, None, None, None])),
            ("MyArray[%s]", 3, None, (["MyArray0", "MyArray1", "MyArray2"], [None, None, None])),
            pytest.param("MyArray[%s]", 0, None, None, marks=pytest.mark.xfail(strict=True, raises=ProcessException)),
        ],
    )
    def test_resolve_dim(
        self,
        name: str,
        dim: None | int,
        dim_index: None | str,
        expected: None | tuple[list[str], list[None | str]],
    ):
        result = _ProcessDimension().process_dim(  # pylint: disable=W0212 #pyright: ignore[reportPrivateUsage]
            name, None, dim, dim_index, type(SVDCluster)
        )

        assert result == expected
