from app.repo_summary import generate_repo_summary


def test_summary_counts_only_the_repos_own_files(tmp_path):
    (tmp_path / "main.py").write_text("print(1)")
    (tmp_path / "ui.ts").write_text("export const x = 1")

    vendored = tmp_path / "node_modules" / "pkg"
    vendored.mkdir(parents=True)
    for i in range(50):
        (vendored / f"dep{i}.js").write_text("module.exports = 1")

    summary = generate_repo_summary(str(tmp_path), chunks=[{"chunk": "x"}])

    assert summary["total_files"] == 2
    assert summary["languages"] == ["Python", "TypeScript"]
    assert summary["total_chunks"] == 1


def test_detects_languages_by_extension(tmp_path):
    for name in ("a.py", "b.js", "c.ts", "d.java", "e.cpp", "f.c"):
        (tmp_path / name).write_text("x")

    summary = generate_repo_summary(str(tmp_path), chunks=[])

    assert summary["languages"] == [
        "C",
        "C++",
        "Java",
        "JavaScript",
        "Python",
        "TypeScript",
    ]
