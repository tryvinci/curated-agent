from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path

from app.services.mcp_integration import get_mcp_integration, MCPToolResult
from app.services.llama_index_service import get_llama_index_service

router = APIRouter(prefix="/agent/mcp", tags=["Agent MCP Tools"])


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
    """List all available MCP tools for agent use"""
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
            "count": len(tool_details),
            "endpoint": "/agent/mcp",
            "description": "MCP tools available for agent use"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@router.get("/tools/{tool_name}")
async def get_tool_info(tool_name: str):
    """Get detailed information about a specific MCP tool"""
    try:
        mcp = get_mcp_integration()
        tool_info = mcp.get_tool_info(tool_name)
        
        if tool_info:
            return JSONResponse(content={
                "success": True,
                "tool": tool_info
            })
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tool info: {str(e)}")


@router.post("/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    """Execute an MCP tool with given parameters"""
    try:
        mcp = get_mcp_integration()
        
        # Execute the tool
        result = mcp.execute_tool(request.tool_name, request.parameters)
        
        if result.success:
            return JSONResponse(content={
                "success": True,
                "tool_name": request.tool_name,
                "result": result.result,
                "error": None
            })
        else:
            return JSONResponse(content={
                "success": False,
                "tool_name": request.tool_name,
                "result": None,
                "error": result.error
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute tool: {str(e)}")


@router.get("/")
async def agent_mcp_info():
    """Get information about the agent MCP endpoint"""
    return JSONResponse(content={
        "success": True,
        "endpoint": "/agent/mcp",
        "description": "Agent MCP tools interface",
        "available_endpoints": [
            "GET /agent/mcp/tools - List all available MCP tools",
            "GET /agent/mcp/tools/{tool_name} - Get tool information", 
            "POST /agent/mcp/tools/execute - Execute a tool",
            "GET /agent/mcp/ - This information endpoint"
        ],
        "note": "This endpoint provides the same MCP functionality as /api/v1/mcp but at the agent-specific path"
    })


@router.get("/health")
async def agent_mcp_health():
    """Check health of MCP integration for agent use"""
    try:
        mcp = get_mcp_integration()
        tools = mcp.get_available_tools()
        
        return JSONResponse(content={
            "success": True,
            "status": "healthy",
            "available_tools": len(tools),
            "mcp_integration": "active",
            "endpoint": "/agent/mcp"
        })
        
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "status": "unhealthy", 
            "error": str(e),
            "endpoint": "/agent/mcp"
        }, status_code=503)


# Additional agent-specific endpoints for enhanced functionality

@router.get("/capabilities")
async def get_agent_capabilities():
    """Get capabilities available through agent MCP interface"""
    try:
        mcp = get_mcp_integration()
        llama_service = get_llama_index_service()
        
        tools = mcp.get_available_tools()
        tool_categories = {}
        
        # Categorize tools
        for tool_name in tools:
            info = mcp.get_tool_info(tool_name)
            if info:
                category = "general"
                if "document" in tool_name.lower():
                    category = "document_processing"
                elif any(x in tool_name.lower() for x in ["search", "query"]):
                    category = "search_retrieval"
                elif any(x in tool_name.lower() for x in ["generate", "create"]):
                    category = "generation"
                
                if category not in tool_categories:
                    tool_categories[category] = []
                tool_categories[category].append(tool_name)
        
        return JSONResponse(content={
            "success": True,
            "capabilities": {
                "mcp_tools": {
                    "available": True,
                    "count": len(tools),
                    "categories": tool_categories
                },
                "document_processing": {
                    "available": llama_service is not None,
                    "features": ["semantic_search", "document_ingestion", "knowledge_retrieval"] if llama_service else []
                },
                "agent_integration": {
                    "available": True,
                    "features": ["tool_execution", "workflow_integration", "session_tracking"]
                }
            },
            "endpoint": "/agent/mcp"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent capabilities: {str(e)}")


@router.post("/execute-workflow")
async def execute_agent_workflow(workflow_data: Dict[str, Any]):
    """Execute a workflow using agent MCP tools"""
    try:
        mcp = get_mcp_integration()
        
        # Extract workflow parameters
        tools_to_execute = workflow_data.get("tools", [])
        workflow_context = workflow_data.get("context", {})
        
        if not tools_to_execute:
            raise HTTPException(status_code=400, detail="No tools specified for workflow execution")
        
        results = []
        for tool_config in tools_to_execute:
            tool_name = tool_config.get("name")
            tool_params = tool_config.get("parameters", {})
            
            if not tool_name:
                continue
                
            # Execute the tool
            result = mcp.execute_tool(tool_name, tool_params)
            results.append({
                "tool_name": tool_name,
                "success": result.success,
                "result": result.result,
                "error": result.error
            })
        
        # Calculate overall success
        successful_tools = sum(1 for r in results if r["success"])
        overall_success = successful_tools > 0
        
        return JSONResponse(content={
            "success": overall_success,
            "workflow_results": results,
            "summary": {
                "total_tools": len(results),
                "successful_tools": successful_tools,
                "failed_tools": len(results) - successful_tools
            },
            "context": workflow_context
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute agent workflow: {str(e)}")