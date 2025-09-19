import logging
import httpx
import asyncio
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime, timezone
from app.core.config import get_settings

# Import HoneyHive service
try:
    from app.services.honeyhive_service import get_honeyhive_service
    HONEYHIVE_AVAILABLE = True
except ImportError:
    HONEYHIVE_AVAILABLE = False

logger = logging.getLogger(__name__)
settings = get_settings()


class ExternalMCPServerResult(BaseModel):
    """Result from external MCP server execution"""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    server_url: Optional[str] = None


class ExternalMCPClient:
    """Client for connecting to external MCP servers"""
    
    def __init__(self):
        self.servers: Dict[str, str] = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        self.honeyhive_service = get_honeyhive_service() if HONEYHIVE_AVAILABLE else None
        self._load_server_config()
    
    def _load_server_config(self):
        """Load external MCP server configuration"""
        # These could be configured via environment variables
        # For now, using placeholder URLs
        self.servers = {
            "media_generation": settings.mcp_media_server_url if hasattr(settings, 'mcp_media_server_url') else None,
            "image_generation": settings.mcp_image_server_url if hasattr(settings, 'mcp_image_server_url') else None,
            "tts_generation": settings.mcp_tts_server_url if hasattr(settings, 'mcp_tts_server_url') else None,
            "video_generation": settings.mcp_video_server_url if hasattr(settings, 'mcp_video_server_url') else None,
        }
        
        # Filter out None values
        self.servers = {k: v for k, v in self.servers.items() if v is not None}
        
        if self.servers:
            logger.info(f"Configured external MCP servers: {list(self.servers.keys())}")
        else:
            logger.info("No external MCP servers configured")
    
    async def call_external_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        parameters: Dict[str, Any]
    ) -> ExternalMCPServerResult:
        """Call a tool on an external MCP server with HoneyHive monitoring"""
        session_id = None
        start_time = datetime.now(timezone.utc)
        
        if self.honeyhive_service:
            session_id = self.honeyhive_service.create_session_id(f"mcp-{server_name}")
        
        if server_name not in self.servers:
            error_msg = f"Server '{server_name}' not configured"
            
            # Log error to HoneyHive
            if self.honeyhive_service and session_id:
                self.honeyhive_service.log_external_mcp_call(
                    session_id=session_id,
                    server_name=server_name,
                    tool_name=tool_name,
                    inputs=parameters,
                    outputs={},
                    success=False,
                    duration_ms=0,
                    error_message=error_msg
                )
            
            return ExternalMCPServerResult(
                success=False,
                error=error_msg
            )
        
        server_url = self.servers[server_name]
        
        try:
            # Construct the API endpoint for tool execution
            endpoint = f"{server_url.rstrip('/')}/tools/execute"
            
            payload = {
                "tool_name": tool_name,
                "parameters": parameters
            }
            
            logger.info(f"Calling external MCP tool: {server_name}/{tool_name}")
            
            response = await self.client.post(
                endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                result_data = response.json()
                
                # Log successful call to HoneyHive
                if self.honeyhive_service and session_id:
                    self.honeyhive_service.log_external_mcp_call(
                        session_id=session_id,
                        server_name=server_name,
                        tool_name=tool_name,
                        inputs=parameters,
                        outputs=result_data,
                        success=True,
                        duration_ms=duration_ms,
                        metadata={
                            "server_url": server_url,
                            "status_code": response.status_code
                        }
                    )
                
                return ExternalMCPServerResult(
                    success=True,
                    result=result_data,
                    server_url=server_url
                )
            else:
                error_msg = f"Server returned {response.status_code}: {response.text}"
                
                # Log error to HoneyHive
                if self.honeyhive_service and session_id:
                    self.honeyhive_service.log_external_mcp_call(
                        session_id=session_id,
                        server_name=server_name,
                        tool_name=tool_name,
                        inputs=parameters,
                        outputs={},
                        success=False,
                        duration_ms=duration_ms,
                        error_message=error_msg,
                        metadata={
                            "server_url": server_url,
                            "status_code": response.status_code
                        }
                    )
                
                return ExternalMCPServerResult(
                    success=False,
                    error=error_msg,
                    server_url=server_url
                )
                
        except Exception as e:
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            error_msg = str(e)
            
            logger.error(f"Error calling external MCP server {server_name}: {e}")
            
            # Log exception to HoneyHive
            if self.honeyhive_service and session_id:
                self.honeyhive_service.log_external_mcp_call(
                    session_id=session_id,
                    server_name=server_name,
                    tool_name=tool_name,
                    inputs=parameters,
                    outputs={},
                    success=False,
                    duration_ms=duration_ms,
                    error_message=error_msg,
                    metadata={
                        "server_url": server_url,
                        "exception_type": type(e).__name__
                    }
                )
            
            return ExternalMCPServerResult(
                success=False,
                error=error_msg,
                server_url=server_url
            )
    
    async def generate_image(
        self, 
        prompt: str, 
        style: Optional[str] = None,
        size: Optional[str] = "1024x1024"
    ) -> ExternalMCPServerResult:
        """Generate an image using external MCP server"""
        parameters = {
            "prompt": prompt,
            "size": size
        }
        if style:
            parameters["style"] = style
            
        # Try media_generation first, then image_generation
        for server in ["media_generation", "image_generation"]:
            if server in self.servers:
                result = await self.call_external_tool(server, "generate_image", parameters)
                if result.success:
                    return result
        
        return ExternalMCPServerResult(
            success=False,
            error="No image generation server available"
        )
    
    async def generate_tts(
        self, 
        text: str, 
        voice: Optional[str] = None,
        format: Optional[str] = "mp3"
    ) -> ExternalMCPServerResult:
        """Generate text-to-speech using external MCP server"""
        parameters = {
            "text": text,
            "format": format
        }
        if voice:
            parameters["voice"] = voice
            
        # Try media_generation first, then tts_generation
        for server in ["media_generation", "tts_generation"]:
            if server in self.servers:
                result = await self.call_external_tool(server, "generate_tts", parameters)
                if result.success:
                    return result
        
        return ExternalMCPServerResult(
            success=False,
            error="No TTS generation server available"
        )
    
    async def generate_video(
        self, 
        prompt: str, 
        duration: Optional[int] = 30,
        style: Optional[str] = None
    ) -> ExternalMCPServerResult:
        """Generate a video using external MCP server"""
        parameters = {
            "prompt": prompt,
            "duration": duration
        }
        if style:
            parameters["style"] = style
            
        # Try media_generation first, then video_generation
        for server in ["media_generation", "video_generation"]:
            if server in self.servers:
                result = await self.call_external_tool(server, "generate_video", parameters)
                if result.success:
                    return result
        
        return ExternalMCPServerResult(
            success=False,
            error="No video generation server available"
        )
    
    async def list_external_tools(self, server_name: Optional[str] = None) -> Dict[str, Any]:
        """List tools available on external MCP servers"""
        if server_name and server_name in self.servers:
            servers_to_check = {server_name: self.servers[server_name]}
        else:
            servers_to_check = self.servers
        
        results = {}
        
        for server, url in servers_to_check.items():
            try:
                endpoint = f"{url.rstrip('/')}/tools"
                response = await self.client.get(endpoint)
                
                if response.status_code == 200:
                    results[server] = {
                        "url": url,
                        "tools": response.json(),
                        "status": "available"
                    }
                else:
                    results[server] = {
                        "url": url,
                        "status": "error",
                        "error": f"HTTP {response.status_code}"
                    }
            except Exception as e:
                results[server] = {
                    "url": url,
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global external MCP client instance
_external_mcp_client = None


async def get_external_mcp_client() -> ExternalMCPClient:
    """Get the global external MCP client instance"""
    global _external_mcp_client
    if _external_mcp_client is None:
        _external_mcp_client = ExternalMCPClient()
    return _external_mcp_client