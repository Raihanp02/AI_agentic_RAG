from docling.chunking import HybridChunker

class DoclingHybridChunker:
    def __init__(self, max_tokens=512, tokenizer=None, merge_peers=True):
        self.max_tokens = max_tokens
        self.tokenizer = tokenizer
        self.merge_peers = merge_peers

        self.chunker = HybridChunker(max_tokens=max_tokens, tokenizer=tokenizer if tokenizer else None, merge_peers=merge_peers)

    def chunk(self, document):
        chunks = self.chunker.chunk(dl_doc=document)
        chunks = list(chunks)
        chunks = [self.chunker.contextualize(chunk=c) for c in chunks]

        return chunks