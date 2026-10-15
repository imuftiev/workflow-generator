import pytest
from src.pxf.pxf_generator import parse_excel


def test_parse_excel_file_not_found(tmp_path):
    filepath = tmp_path / "missing.xlsx"

    with pytest.raises(FileNotFoundError):
        parse_excel(str(filepath))