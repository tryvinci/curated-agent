from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path

from app.services.llama_index_service import get_llama_index_service

router = APIRouter(prefix="/api/v1/documents", tags=["Document Processing"])


class TextIngestionRequest(BaseModel):
    """Request model for text document ingestion"""
    texts: List[str]
    metadata: Optional[List[Dict[str, Any]]] = None


class DocumentSearchRequest(BaseModel):
    """Request model for document search"""
    query: str
    top_k: int = 5


class DocumentSearchResponse(BaseModel):
    """Response model for document search"""
    success: bool
    query: str
    results: List[Dict[str, Any]] = []
    error: Optional[str] = None


@router.post("/ingest/files")
async def ingest_files(files: List[UploadFile] = File(...)):
    """Ingest documents from uploaded files"""
    try:
        service = get_llama_index_service()
        temp_files = []
        
        # Save uploaded files to temporary location
        for file in files:
            suffix = Path(file.filename).suffix if file.filename else '.txt'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_files.append(tmp_file.name)
        
        # Ingest the documents
        result = service.ingest_documents(temp_files)
        
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except Exception as e:
                print(f"Warning: Could not delete temp file {temp_file}: {e}")
        
        return JSONResponse(content={
            "success": result.success,
            "message": result.message,
            "document_count": result.document_count,
            "error": result.error
        })
        
    except Exception as e:
        # Clean up any remaining temp files
        for temp_file in temp_files if 'temp_files' in locals() else []:
            try:
                os.unlink(temp_file)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Failed to ingest files: {str(e)}")


@router.post("/ingest/text")
async def ingest_text_documents(request: TextIngestionRequest):
    """Ingest text documents directly"""
    try:
        service = get_llama_index_service()
        result = service.ingest_text_documents(request.texts, request.metadata)
        
        return JSONResponse(content={
            "success": result.success,
            "message": result.message,
            "document_count": result.document_count,
            "error": result.error
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest text: {str(e)}")


@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(request: DocumentSearchRequest):
    """Search through ingested documents"""
    try:
        service = get_llama_index_service()
        result = service.search_documents(request.query, request.top_k)
        
        return DocumentSearchResponse(
            success=result.success,
            query=result.query,
            results=result.results,
            error=result.error
        )
        
    except Exception as e:
        return DocumentSearchResponse(
            success=False,
            query=request.query,
            error=str(e)
        )


@router.get("/stats")
async def get_index_stats():
    """Get statistics about the document index"""
    try:
        service = get_llama_index_service()
        stats = service.get_index_stats()
        
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@router.delete("/clear")
async def clear_index():
    """Clear all documents from the index"""
    try:
        service = get_llama_index_service()
        success = service.clear_index()
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "Index cleared successfully"
            })
        else:
            raise HTTPException(status_code=500, detail="Failed to clear index")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear index: {str(e)}")


@router.get("/health")
async def document_health_check():
    """Check the health of the document processing service"""
    try:
        service = get_llama_index_service()
        stats = service.get_index_stats()
        
        return JSONResponse(content={
            "success": True,
            "service_available": stats.get("available", False),
            "document_count": stats.get("document_count", 0),
            "message": "Document service is operational"
        })
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "service_available": False,
            "error": str(e)
        })