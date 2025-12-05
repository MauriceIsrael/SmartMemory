"""
Document parsers for different file formats.
"""

import abc
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
import fitz  # PyMuPDF
from smart_memory.logging_config import get_logger

logger = get_logger(__name__)

class DocumentParser(abc.ABC):
    """Abstract base class for document parsers."""
    
    @abc.abstractmethod
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse a document and extract its content and metadata.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Dictionary containing:
            - content: Full text content
            - metadata: Dictionary of metadata (title, page_count, creation_date, etc.)
        """
        pass

    @staticmethod
    def calculate_hash(file_path: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class PDFParser(DocumentParser):
    """Parser for PDF documents using PyMuPDF."""
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        try:
            doc = fitz.open(file_path)
            text_content = []
            
            for page in doc:
                text_content.append(page.get_text())
                
            full_text = "\n\n".join(text_content)
            
            metadata = {
                "format": "pdf",
                "page_count": len(doc),
                "title": doc.metadata.get("title") or file_path.stem,
                "author": doc.metadata.get("author"),
                "creation_date": doc.metadata.get("creationDate"),
            }
            
            doc.close()
            
            return {
                "content": full_text,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise


class TextParser(DocumentParser):
    """Parser for plain text files."""
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            metadata = {
                "format": "text",
                "page_count": 1,
                "title": file_path.stem,
            }
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except UnicodeDecodeError:
            # Fallback for other encodings
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                
                metadata = {
                    "format": "text",
                    "page_count": 1,
                    "title": file_path.stem,
                }
                
                return {
                    "content": content,
                    "metadata": metadata
                }
            except Exception as e:
                logger.error(f"Error parsing text file {file_path}: {e}")
                raise
        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {e}")
            raise


class MarkdownParser(TextParser):
    """Parser for Markdown files."""
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        result = super().parse(file_path)
        result["metadata"]["format"] = "markdown"
        return result
