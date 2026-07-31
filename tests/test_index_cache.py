import numpy as np
import pytest

from app import index_cache

faiss = pytest.importorskip("faiss")


@pytest.fixture(autouse=True)
def isolated_cache_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(index_cache, "CACHE_DIR", str(tmp_path / "cache"))


def _build_index(vectors):
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)
    return index


def test_missing_entry_returns_none():
    assert index_cache.load("does-not-exist") is None


def test_round_trips_index_chunks_and_summary():
    vectors = np.random.rand(5, 8).astype("float32")
    chunks = [{"file_path": "a.py", "chunk": f"c{i}"} for i in range(5)]
    summary = {"total_files": 1, "total_chunks": 5}

    index_cache.save("k1", _build_index(vectors), chunks, summary)
    loaded = index_cache.load("k1")

    assert loaded is not None
    index, loaded_chunks, loaded_summary = loaded
    assert loaded_chunks == chunks
    assert loaded_summary == summary
    assert index.ntotal == 5

    # The restored index must return the same neighbours as the original.
    _, indices = index.search(vectors[:1], 1)
    assert indices[0][0] == 0


def test_key_changes_with_commit_and_settings():
    base = index_cache.cache_key("data/owner__repo", "sha1", "model|None|None")

    assert base == index_cache.cache_key("data/owner__repo", "sha1", "model|None|None")
    # A new commit must not reuse the old embeddings.
    assert base != index_cache.cache_key("data/owner__repo", "sha2", "model|None|None")
    # Neither may a different model or chunk limit.
    assert base != index_cache.cache_key("data/owner__repo", "sha1", "other|None|None")
    assert base != index_cache.cache_key("data/owner__repo", "sha1", "model|500|None")
    # Different repository, same commit string.
    assert base != index_cache.cache_key("data/other__repo", "sha1", "model|None|None")


def test_corrupt_entry_is_ignored_rather_than_raising(tmp_path):
    import os

    os.makedirs(index_cache.CACHE_DIR, exist_ok=True)
    faiss_path, meta_path = index_cache._paths("bad")
    with open(faiss_path, "w") as f:
        f.write("not a faiss index")
    with open(meta_path, "w") as f:
        f.write("{}")

    assert index_cache.load("bad") is None
