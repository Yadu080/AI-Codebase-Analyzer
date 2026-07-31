import logging
import os

import numpy as np

logger = logging.getLogger(__name__)

# Skip the optional accelerated download client — it's extra memory/process
# overhead we don't need for a single small model file on a RAM-constrained
# host. Must be set before huggingface_hub is imported.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")

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

    logger.info("Downloading embedding model %s/%s...", _MODEL_REPO, _MODEL_FILE)
    model_path = hf_hub_download(repo_id=_MODEL_REPO, filename=_MODEL_FILE)
    logger.info("Model downloaded to %s", model_path)

    tokenizer_path = hf_hub_download(repo_id=_MODEL_REPO, filename="tokenizer.json")
    logger.info("Tokenizer downloaded to %s", tokenizer_path)

    tokenizer = Tokenizer.from_file(tokenizer_path)
    tokenizer.enable_truncation(max_length=_MAX_SEQ_LENGTH)
    pad_id = tokenizer.token_to_id("[PAD]") or 0
    tokenizer.enable_padding(pad_id=pad_id, pad_token="[PAD]")
    logger.info("Tokenizer ready")

    # Full graph optimization can transiently use significantly more memory
    # during session creation than the model itself needs at rest — basic
    # optimization is enough for a model this small and keeps that spike
    # from happening on a 512MB host. Single-threaded since a free instance
    # typically has one CPU anyway, and each onnxruntime thread reserves its
    # own scratch buffers.
    session_options = ort.SessionOptions()
    session_options.intra_op_num_threads = 1
    session_options.inter_op_num_threads = 1
    session_options.graph_optimization_level = (
        ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
    )

    logger.info("Creating ONNX Runtime session...")
    session = ort.InferenceSession(
        model_path, sess_options=session_options, providers=["CPUExecutionProvider"]
    )
    logger.info("ONNX Runtime session ready")

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
