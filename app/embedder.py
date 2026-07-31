import os

import numpy as np

# Pre-converted ONNX build of sentence-transformers/all-MiniLM-L6-v2 — same
# model weights, same embeddings, just packaged for onnxruntime instead of
# PyTorch. Override via env var if a specific file path 404s on the model
# repo (e.g. fall back to "onnx/model.onnx" for the unquantized fp32 build).
_MODEL_REPO = os.getenv("EMBEDDING_MODEL_REPO", "Xenova/all-MiniLM-L6-v2")
_MODEL_FILE = os.getenv("EMBEDDING_MODEL_FILE", "onnx/model_quantized.onnx")
_MAX_SEQ_LENGTH = 256

_session = None
_tokenizer = None
_input_names = None


def _load():
    # Downloaded and initialized lazily so the API process stays light until
    # the first /analyze or /ask call actually needs to embed something.
    global _session, _tokenizer, _input_names
    if _session is not None:
        return _session, _tokenizer, _input_names

    from huggingface_hub import hf_hub_download
    from tokenizers import Tokenizer
    import onnxruntime as ort

    model_path = hf_hub_download(repo_id=_MODEL_REPO, filename=_MODEL_FILE)
    tokenizer_path = hf_hub_download(repo_id=_MODEL_REPO, filename="tokenizer.json")

    tokenizer = Tokenizer.from_file(tokenizer_path)
    tokenizer.enable_truncation(max_length=_MAX_SEQ_LENGTH)
    pad_id = tokenizer.token_to_id("[PAD]") or 0
    tokenizer.enable_padding(pad_id=pad_id, pad_token="[PAD]")

    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    input_names = {i.name for i in session.get_inputs()}

    _session, _tokenizer, _input_names = session, tokenizer, input_names
    return _session, _tokenizer, _input_names


def _mean_pool(last_hidden_state, attention_mask):
    # Same mean-pooling-over-tokens that sentence-transformers uses for this
    # model, done by hand in numpy since we're not going through torch.
    mask = attention_mask[..., None].astype(np.float32)
    summed = (last_hidden_state * mask).sum(axis=1)
    counts = np.clip(mask.sum(axis=1), a_min=1e-9, a_max=None)
    return summed / counts


def _encode(texts, batch_size=32):
    session, tokenizer, input_names = _load()

    all_embeddings = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        encoded = tokenizer.encode_batch(batch)

        available = {
            "input_ids": np.array([e.ids for e in encoded], dtype=np.int64),
            "attention_mask": np.array(
                [e.attention_mask for e in encoded], dtype=np.int64
            ),
            "token_type_ids": np.array(
                [e.type_ids for e in encoded], dtype=np.int64
            ),
        }
        # Only feed inputs this particular ONNX export actually declares.
        feed = {name: available[name] for name in input_names if name in available}

        outputs = session.run(None, feed)
        pooled = _mean_pool(outputs[0], available["attention_mask"])
        all_embeddings.append(pooled)

    return np.concatenate(all_embeddings, axis=0)


def embed_chunks(chunks):
    texts = [c["chunk"] for c in chunks]
    return _encode(texts)


def embed_query(query):
    return _encode([query])
