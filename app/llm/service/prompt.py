
ocr_prompt_template = """The user has uploaded a document. Below is the extracted content (may be partial or imperfectly formatted):

<document>
{document_text}
</document>

Use the document content to answer the user's question if it's relevant to what they asked. 
If the document is empty or unreadable, let the user know the file could not be extracted properly."""