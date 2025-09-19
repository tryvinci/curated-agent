from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path

from app.services.mcp_integration import get_mcp_integration, MCPToolResult
from app.services.llama_index_service import get_llama_index_service

router = APIRouter(prefix="/api/v1/mcp", tags=["MCP Tools"])


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution"""
    tool_name: str
    parameters: Dict[str, Any] = {}


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution"""
    success: bool
    tool_name: str
    result: Optional[Any] = None
    error: Optional[str] = None


@router.get("/tools")
async def list_available_tools():
    """List all available MCP tools"""
    try:
        mcp = get_mcp_integration()
        tools = mcp.get_available_tools()
        
        tool_details = []
        for tool_name in tools:
            info = mcp.get_tool_info(tool_name)
            if info:
                tool_details.append(info)
        
        return JSONResponse(content={
            "success": True,
            "tools": tool_details,
            "count": len(tool_details)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@router.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get information about a specific tool"""
    try:
        mcp = get_mcp_integration()
        info = mcp.get_tool_info(tool_name)
        
        if not info:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        return JSONResponse(content={
            "success": True,
            "tool": info
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tool info: {str(e)}")


@router.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(request: ToolExecutionRequest):
    """Execute an MCP tool with given parameters"""
    try:
        mcp = get_mcp_integration()
        result = await mcp.execute_tool(request.tool_name, **request.parameters)
        
        return ToolExecutionResponse(
            success=result.success,
            tool_name=request.tool_name,
            result=result.result,
            error=result.error
        )
        
    except Exception as e:
        return ToolExecutionResponse(
            success=False,
            tool_name=request.tool_name,
            error=str(e)
        )