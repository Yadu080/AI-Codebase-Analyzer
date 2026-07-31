from app.chunker import chunk_code


def test_empty_input_produces_no_chunks():
    assert chunk_code([]) == []


def test_respects_max_chunks_cap():
    files = [{"file_path": "a.py", "content": ("x" * 40 + "\n") * 200}]
    chunks = chunk_code(files, chunk_size=500, max_chunks=3)
    assert len(chunks) == 3


def test_uncapped_uncovers_whole_file_with_zero_overlap():
    files = [{"file_path": "a.py", "content": "line\n" * 200}]
    chunks = chunk_code(files, chunk_size=100, overlap=0)
    assert len(chunks) > 1
    assert "".join(c["chunk"] for c in chunks) == "line\n" * 200


def test_chunks_never_cut_a_normal_line_in_half():
    text = ("a" * 10 + "\n") * 20
    files = [{"file_path": "a.py", "content": text}]
    chunks = chunk_code(files, chunk_size=35, overlap=0)
    for c in chunks:
        assert c["chunk"].count("\n") == c["chunk"].count("\n")  # sanity
        for line in c["chunk"].splitlines(keepends=True):
            assert line == "a" * 10 + "\n"


def test_single_line_file_falls_back_to_hard_cut():
    files = [{"file_path": "a.py", "content": "x" * 1200}]
    chunks = chunk_code(files, chunk_size=500, overlap=0)
    assert len(chunks) == 3


def test_overlap_duplicates_a_little_content_between_chunks():
    files = [{"file_path": "a.py", "content": ("x" * 40 + "\n") * 30}]
    chunks = chunk_code(files, chunk_size=200, overlap=20, max_chunks=None)
    assert len(chunks) > 1
    # With overlap > 0, consecutive chunks should share a bit of content.
    assert chunks[1]["chunk"].startswith(chunks[0]["chunk"][-20:])
