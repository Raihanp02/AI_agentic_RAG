from functools import lru_cache
from typing import Protocol

from core.config import settings
import threading
import torch
from sentence_transformers import SentenceTransformer

class TextEmbedder(Protocol):
    dimensions: int

    def embed(self, text: str) -> list[float]: ...
    def embed_many(self, texts: list[str]) -> list[list[float]]: ...


class HuggingFaceTextEmbedder:
    def __init__(
        self,
        model_name: str = "BAAI/bge-m3",
        device: str | None = None,
        max_seq_length: int = 512,
        batch_size: int = 32,
        fp16: bool = True,
    ):
        use_fp16 = fp16 and (device or ("cuda" if torch.cuda.is_available() else "cpu")).startswith("cuda")
        self.model = SentenceTransformer(
            model_name,
            device=device,
            model_kwargs={"torch_dtype": torch.float16} if use_fp16 else {},
        )
        self.model.max_seq_length = max_seq_length
        self.batch_size = batch_size
        self.dimensions = self.model.get_sentence_embedding_dimension()
        self._lock = threading.Lock()  # one encode at a time on the device

    def embed(self, text: str) -> list[float]:
        return self.embed_many([text])[0]

    def embed_many(self, texts: list[str], batch_size: int | None = None) -> list[list[float]]:
        if not texts:
            return []
        bs = batch_size or self.batch_size
        with self._lock:
            while True:
                try:
                    vecs = self.model.encode(
                        texts,
                        batch_size=bs,
                        normalize_embeddings=True,
                        show_progress_bar=False,
                    )
                    return vecs.tolist()
                except torch.cuda.OutOfMemoryError:
                    torch.cuda.empty_cache()
                    if bs == 1:
                        raise
                    bs = max(1, bs // 2)  # retry with a smaller batch


@lru_cache(maxsize=1)
def get_embedder() -> TextEmbedder:
    provider = settings.EMBEDDING_PROVIDER
    if provider == "huggingface":
        return HuggingFaceTextEmbedder()
    raise ValueError(f"Unknown embedding provider: {provider}")