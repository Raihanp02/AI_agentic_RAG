from langgraph.prebuilt import InjectedState
from typing import Annotated
from langchain.tools import tool
from langgraph.types import Command

from app.knowledge.service.add_knowledge.pipeline import knowledge_pipeline
from app.llm.service.prompt import ocr_prompt_template

@tool
def extract_document(
    state: Annotated[dict, InjectedState]  # langgraph injects state automatically
) -> str:
    """Extract and read the content of the uploaded document."""
    file_path = state.get("uploaded_file_path")
    if not file_path:
        return "No file uploaded."
    
    parsed = knowledge_pipeline.doc_parser.parse(state["file_bytes"], filename="image.jpg")
    result = ocr_prompt_template.format(document_text=parsed.export_to_markdown())

    return Command(
        update={
            "file_bytes": None,  # clear after use
        },
        resume=result  # this becomes the ToolMessage content
    )