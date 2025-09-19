import logging
from typing import Any, Dict, List, Optional, Union
from mcp import Tool, ServerSession
from mcp.server import Server
from mcp.types import Message, GetToolResult
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class MCPToolResult(BaseModel):
    """Result from MCP tool execution"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None


class MCPIntegration:
    """MCP (Model Context Protocol) integration for FastAPI"""
    
    def __init__(self):
        self.server = Server("curated-agent-mcp")
        self.tools: Dict[str, Tool] = {}
        self._setup_default_tools()
    
    def _setup_default_tools(self):
        """Set up default tools for the MCP server"""
        
        # Document processing tool
        @self.server.tool("process_document")
        async def process_document(path: str, extract_text: bool = True) -> Dict[str, Any]:
            """Process a document and extract information"""
            try:
                # This would integrate with llama-index document processing
                return {
                    "success": True,
                    "path": path,
                    "text_extracted": extract_text,
                    "message": f"Document {path} processed successfully"
                }
            except Exception as e:
                logger.error(f"Error processing document {path}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Data search tool
        @self.server.tool("search_data")
        async def search_data(query: str, limit: int = 10) -> Dict[str, Any]:
            """Search through ingested data"""
            try:
                # This would integrate with llama-index search capabilities
                return {
                    "success": True,
                    "query": query,
                    "results": [],
                    "limit": limit,
                    "message": f"Search completed for: {query}"
                }
            except Exception as e:
                logger.error(f"Error searching data with query {query}: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Creative content tool
        @self.server.tool("generate_content")
        async def generate_content(
            content_type: str,
            prompt: str,
            context: Optional[str] = None
        ) -> Dict[str, Any]:
            """Generate creative content using AI"""
            try:
                return {
                    "success": True,
                    "content_type": content_type,
                    "prompt": prompt,
                    "context": context,
                    "generated_content": f"Generated {content_type} content based on: {prompt}",
                    "message": "Content generated successfully"
                }
            except Exception as e:
                logger.error(f"Error generating content: {e}")
                return {
                    "success": False,
                    "error": str(e)
                }
    
    def register_tool(self, name: str, tool_func: callable) -> None:
        """Register a custom tool with the MCP server"""
        try:
            @self.server.tool(name)
            async def wrapped_tool(**kwargs) -> Dict[str, Any]:
                try:
                    result = await tool_func(**kwargs)
                    return {"success": True, "result": result}
                except Exception as e:
                    return {"success": False, "error": str(e)}
            
            logger.info(f"Registered MCP tool: {name}")
        except Exception as e:
            logger.error(f"Failed to register tool {name}: {e}")
    
    async def execute_tool(self, tool_name: str, **kwargs) -> MCPToolResult:
        """Execute a tool and return the result"""
        try:
            if tool_name not in [tool.name for tool in self.server.tools]:
                return MCPToolResult(
                    success=False,
                    error=f"Tool '{tool_name}' not found"
                )
            
            # Create a session and execute the tool
            session = ServerSession(self.server)
            result = await session.call_tool(tool_name, kwargs)
            
            return MCPToolResult(
                success=True,
                result=result
            )
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return MCPToolResult(
                success=False,
                error=str(e)
            )
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        return [tool.name for tool in self.server.tools]
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        for tool in self.server.tools:
            if tool.name == tool_name:
                return {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema
                }
        return None


# Global MCP integration instance
mcp_integration = MCPIntegration()


def get_mcp_integration() -> MCPIntegration:
    """Get the global MCP integration instance"""
    return mcp_integration