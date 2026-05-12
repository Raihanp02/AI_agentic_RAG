from docling.document_converter import DocumentConverter
import os 
from fastapi import UploadFile
from pathlib import Path
from fastapi import HTTPException

class DoclingParser:
    def __init__(self):
        self.converter = DocumentConverter()

    def parse(self, source, filename):
        try:
            temp_file_path = Path(f"./temp_{filename}")
            with open(temp_file_path, "wb") as f:
                f.write(source)

            doc = self.converter.convert(str(temp_file_path)).document
            temp_file_path.unlink()

            return doc

        except Exception as e:
            if temp_file_path.exists():
                temp_file_path.unlink()
            raise HTTPException(status_code=500, detail=f"An error occurred during conversion: {str(e)}")
    
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