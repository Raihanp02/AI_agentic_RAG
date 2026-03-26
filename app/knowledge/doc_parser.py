from docling.document_converter import DocumentConverter
import os 
from fastapi import UploadFile

class DoclingParser:
    def __init__(self):
        self.converter = DocumentConverter()

    def parse(self, source):
        if isinstance(source, UploadFile):
            source = source.file
        source = str(source)

        doc = self.converter.convert(source).document
        return doc
    
    def extract_title(self, content, filename):
        """Extract title from document content or filename."""
        # Try to find markdown title
        if not isinstance(content, str):
            content = content.export_to_markdown()
            
        lines = content.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
        
        # Fallback to filename
        return filename
    
    def extract_markdown(self, content):
        """Convert document content to markdown format."""
        if not isinstance(content, str):
            return content.export_to_markdown()
        return content