"""
Service for managing documents in the dashboard backend.
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from fastapi import UploadFile, HTTPException

from smart_memory.document.document_loader import DocumentLoader
from smart_memory.document.vocabulary import DOC
from smart_memory.logging_config import get_logger
from services.memory_service import get_memory_service

logger = get_logger(__name__)

class DocumentService:
    def __init__(self):
        self.memory = get_memory_service()
        self.loader = DocumentLoader(self.memory.p_graph)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all loaded documents."""
        # Query graph for documents
        query = """
        PREFIX doc: <http://semanticmemory.org/document#>
        SELECT ?doc ?title ?format ?date ?pageCount
        WHERE {
            ?doc doc:title ?title .
            OPTIONAL { ?doc doc:fileFormat ?format }
            OPTIONAL { ?doc doc:uploadDate ?date }
            OPTIONAL { ?doc doc:pageCount ?pageCount }
        }
        ORDER BY DESC(?date)
        """
        results = list(self.memory.p_graph.query(query))
        documents = []
        for row in results:
            documents.append({
                "id": str(row["doc"]).split("#")[-1],
                "uri": str(row["doc"]),
                "title": str(row["title"]),
                "format": str(row["format"]) if row["format"] else None,
                "upload_date": str(row["date"]) if row["date"] else None,
                "page_count": int(row["pageCount"]) if row.get("pageCount") else None,
            })
        return documents

    async def upload_document(self, file: UploadFile) -> Dict[str, Any]:
        """Upload and process a document file."""
        # Save temp file
        import tempfile
        import shutil
        
        temp_dir = Path("cache/uploads")
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / file.filename
        
        try:
            with temp_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            # Load into graph
            doc_uri = self.loader.load_file(temp_path, store_content=False)
            
            # Extract rules (trigger logic) via RuleExtractor
            from smart_memory.document.rule_extractor import RuleExtractor
            from smart_memory.tools.pending_rules import add_pending_rule
            import uuid
            
            # Re-read content for extraction (since store_content=False)
            parser = self.loader.parsers.get(temp_path.suffix.lower())
            if parser:
                res = parser.parse(temp_path)
                content = res["content"]
                
                extractor = RuleExtractor()
                rules = await extractor.extract_rules(content, file.filename)
                
                # Save rules
                for rule in rules:
                    rule_id = rule.get('rule_id', f"rule_{uuid.uuid4().hex[:8]}")
                    rule['source_doc_uri'] = str(doc_uri)
                    add_pending_rule(rule_id, rule)
            
            # Save graph
            self.memory.p_graph.graph.serialize(destination=str(self.memory.graph_file), format="turtle")
            
            return {
                "status": "success",
                "message": f"Document {file.filename} uploaded and processed",
                "rules_extracted": len(rules) if 'rules' in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"Error uploading document: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            # Cleanup temp file if needed? Or keep for cache?
            # For now keep it
            pass

_document_service: Optional[DocumentService] = None

def get_document_service() -> DocumentService:
    global _document_service
    if _document_service is None:
        _document_service = DocumentService()
    return _document_service
