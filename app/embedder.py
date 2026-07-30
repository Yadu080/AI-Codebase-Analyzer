_model = None


def _get_model():
    # Imported and loaded lazily so the API process stays light until the
    # first /analyze or /ask call actually needs the model (keeps /health
    # fast and avoids paying the RAM cost on processes that never embed).
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    return _model


def embed_chunks(chunks):

    texts = [c["chunk"] for c in chunks]

    embeddings = _get_model().encode(texts, batch_size=32, show_progress_bar=False)

    return embeddings


def embed_query(query):

    return _get_model().encode([query], show_progress_bar=False)