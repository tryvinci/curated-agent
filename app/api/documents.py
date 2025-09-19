from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path

from app.services.llama_index_service import get_llama_index_service

# Import external MCP client
try:
    from app.services.external_mcp_client import get_external_mcp_client
    EXTERNAL_MCP_AVAILABLE = True
except ImportError:
    EXTERNAL_MCP_AVAILABLE = False

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


class AgentQueryRequest(BaseModel):
    """Request model for agent-based queries with tools"""
    query: str
    system_message: Optional[str] = None


class AgentQueryResponse(BaseModel):
    """Response model for agent queries"""
    success: bool
    query: str
    response: Optional[str] = None
    tools_used: List[Dict[str, Any]] = []
    error: Optional[str] = None


class MediaGenerationRequest(BaseModel):
    """Request model for media generation via external MCP"""
    prompt: str
    media_type: str  # "image", "tts", "video"
    style: Optional[str] = None
    size: Optional[str] = None  # for images
    voice: Optional[str] = None  # for TTS
    format: Optional[str] = None  # for TTS
    duration: Optional[int] = None  # for videos


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


@router.post("/query-with-tools", response_model=AgentQueryResponse)
async def query_with_tools(request: AgentQueryRequest):
    """Query documents using LlamaIndex agent with MCP tools"""
    try:
        service = get_llama_index_service()
        result = await service.query_with_tools(request.query, request.system_message)
        
        return AgentQueryResponse(
            success=result.get("success", False),
            query=result.get("query", request.query),
            response=result.get("response"),
            tools_used=result.get("tools_used", []),
            error=result.get("error")
        )
        
    except Exception as e:
        return AgentQueryResponse(
            success=False,
            query=request.query,
            error=str(e)
        )


@router.post("/generate-media")
async def generate_media(request: MediaGenerationRequest):
    """Generate media (image, TTS, video) using external MCP servers"""
    if not EXTERNAL_MCP_AVAILABLE:
        raise HTTPException(
            status_code=503, 
            detail="External MCP client not available"
        )
    
    try:
        client = await get_external_mcp_client()
        
        if request.media_type == "image":
            result = await client.generate_image(
                prompt=request.prompt,
                style=request.style,
                size=request.size or "1024x1024"
            )
        elif request.media_type == "tts":
            result = await client.generate_tts(
                text=request.prompt,
                voice=request.voice,
                format=request.format or "mp3"
            )
        elif request.media_type == "video":
            result = await client.generate_video(
                prompt=request.prompt,
                duration=request.duration or 30,
                style=request.style
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported media type: {request.media_type}"
            )
        
        return JSONResponse(content={
            "success": result.success,
            "media_type": request.media_type,
            "prompt": request.prompt,
            "result": result.result,
            "error": result.error,
            "server_url": result.server_url
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate media: {str(e)}")


@router.get("/external-servers")
async def list_external_servers():
    """List available external MCP servers and their tools"""
    if not EXTERNAL_MCP_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="External MCP client not available"
        )
    
    try:
        client = await get_external_mcp_client()
        servers = await client.list_external_tools()
        
        return JSONResponse(content={
            "success": True,
            "servers": servers
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list servers: {str(e)}")


@router.get("/mcp-tools")
async def list_mcp_tools():
    """List MCP tools available in LlamaIndex integration"""
    try:
        service = get_llama_index_service()
        tools = service.get_mcp_tools()
        
        tool_info = []
        for tool in tools:
            tool_info.append({
                "name": tool.metadata.name if hasattr(tool, 'metadata') else str(tool),
                "description": tool.metadata.description if hasattr(tool, 'metadata') else "No description available"
            })
        
        return JSONResponse(content={
            "success": True,
            "tools": tool_info,
            "count": len(tool_info)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list MCP tools: {str(e)}")