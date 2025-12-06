"""
Document management endpoints.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException

from services.document_service import get_document_service

router = APIRouter()

@router.get("/documents", response_model=List[Dict[str, Any]])
async def list_documents():
    """List all documents."""
    service = get_document_service()
    return service.list_documents()

@router.post("/documents/upload", response_model=Dict[str, Any])
async def upload_document(file: UploadFile = File(...)):
    """Upload a document."""
    service = get_document_service()
    return await service.upload_document(file)

@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document."""
    service = get_document_service()
    success = service.delete_document(doc_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found or failed to delete")
    
    return {"status": "success", "id": doc_id}
