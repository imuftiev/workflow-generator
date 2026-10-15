from src.pxf.pxf_generator import clear


def test_clear(tmp_path: str):
    directory = tmp_path / "cf"
    directory.mkdir()

    test_file = directory / "old.yaml"
    test_file.write_text("old content")

    clear([str(directory)])

    assert directory.exists()
    assert directory.is_dir()
    assert list(directory.iterdir()) == []