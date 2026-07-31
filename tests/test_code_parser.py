from app.code_parser import load_code_files


def test_loads_only_supported_extensions(tmp_path):
    (tmp_path / "a.py").write_text("print(1)")
    (tmp_path / "b.txt").write_text("ignored")
    (tmp_path / "c.js").write_text("console.log(1)")

    files = load_code_files(str(tmp_path))
    names = sorted(f["file_path"].split("/")[-1] for f in files)
    assert names == ["a.py", "c.js"]


def test_skips_dependency_and_build_directories(tmp_path):
    (tmp_path / "app.py").write_text("print(1)")

    for skipped in ("node_modules", "venv", "__pycache__", ".git"):
        d = tmp_path / skipped
        d.mkdir()
        (d / "junk.py").write_text("should not be indexed")

    files = load_code_files(str(tmp_path))
    names = sorted(f["file_path"].split("/")[-1] for f in files)
    assert names == ["app.py"]


def test_nested_dependency_directories_are_skipped(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "main.py").write_text("print(1)")

    nested = src / "node_modules" / "pkg"
    nested.mkdir(parents=True)
    (nested / "index.js").write_text("module.exports = 1")

    files = load_code_files(str(tmp_path))
    names = sorted(f["file_path"].split("/")[-1] for f in files)
    assert names == ["main.py"]


def test_no_limit_by_default(tmp_path):
    for i in range(20):
        (tmp_path / f"f{i}.py").write_text("x" * 1000)

    files = load_code_files(str(tmp_path))
    assert len(files) == 20


def test_stops_once_char_budget_is_reached(tmp_path):
    for i in range(20):
        (tmp_path / f"f{i}.py").write_text("x" * 1000)

    files = load_code_files(str(tmp_path), max_total_chars=2500)
    assert len(files) < 20
