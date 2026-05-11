from app.knowledge.service.add_knowledge.chunk_embedder import HuggingFaceTextEmbedder
from app.knowledge.service.crud_knowledge.retrieve import get_document_from_embedding
from app.knowledge.database.session import get_db

from typing import Optional
from pydantic import BaseModel, Field
from langchain.tools import tool

class RAGTools:
    def __init__(self, text_embedder = HuggingFaceTextEmbedder()):
        self.text_embedder = text_embedder

    async def retrieve(self, session, query: str, category: str = None):
        embedding = self.text_embedder.embed(query)
        retrieved = await get_document_from_embedding(session, embedding, top_k=1, category=category)

        return {
            "message": "Use this retrieved document below as reference, if not relevant dont use it",
            "documents": [
                    {
                        "content": chunk.content,
                        "document_id": chunk.document_id,
                        "chunk_index": chunk.chunk_index,
                    }
                    for chunk in retrieved
                ]
        }

ragtools = RAGTools()

class Schema(BaseModel):
    query: str = Field(..., description="The search query used to find relevant documents in the knowledge base.")
    category: Optional[str] = Field(None, description="Category type for the relevant document, leave blank if not sure.")

@tool(args_schema=Schema)
async def rag_tools(query: str, category: str = None):
    """
    Search and retrieve relevant context from the internal knowledge base.

    Use this tool when:
    - The question requires factual or document-based answers
    - The answer is likely stored in company data, database, or indexed documents
    - The user asks about specific entities, records, or past information
    """
    async with get_db() as db:
        result = await ragtools.retrieve(db, query, category)

    return result