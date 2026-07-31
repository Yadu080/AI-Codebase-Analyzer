import numpy as np

from app.retriever import retrieve


class FakeIndex:
    """Stands in for a FAISS index so these tests don't need faiss installed."""

    def __init__(self, result_indices):
        self._result_indices = result_indices

    def search(self, query_embedding, k):
        idx = np.array([self._result_indices[:k]])
        dist = np.zeros_like(idx, dtype="float32")
        return dist, idx


def test_retrieve_returns_requested_chunks_in_order():
    chunks = [{"chunk": f"c{i}"} for i in range(5)]
    index = FakeIndex([0, 1, 2, 3, 4])
    results = retrieve(index, np.zeros((1, 3)), chunks, top_k=3)
    assert [r["chunk"] for r in results] == ["c0", "c1", "c2"]


def test_retrieve_ignores_faiss_missing_result_sentinel():
    # FAISS pads with -1 when the index holds fewer vectors than top_k.
    chunks = [{"chunk": "only"}]
    index = FakeIndex([0, -1, -1])
    results = retrieve(index, np.zeros((1, 3)), chunks, top_k=3)
    assert [r["chunk"] for r in results] == ["only"]


def test_retrieve_handles_empty_chunk_list():
    results = retrieve(FakeIndex([]), np.zeros((1, 3)), [], top_k=5)
    assert results == []
