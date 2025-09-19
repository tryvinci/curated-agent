import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timezone
import json
import traceback
from functools import wraps

try:
    from honeyhive import HoneyHive
    from honeyhive.models import Event, EventType, Feedback
    HONEYHIVE_AVAILABLE = True
except ImportError:
    HONEYHIVE_AVAILABLE = False

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class HoneyHiveService:
    """HoneyHive integration for AI observability and monitoring"""
    
    def __init__(self):
        self.enabled = getattr(settings, 'honeyhive_enabled', True) and HONEYHIVE_AVAILABLE
        self.client = None
        
        if self.enabled:
            try:
                api_key = getattr(settings, 'honeyhive_api_key', None)
                if api_key:
                    self.client = HoneyHive(api_key=api_key)
                    logger.info("HoneyHive client initialized successfully")
                else:
                    logger.warning("HoneyHive API key not provided - running without observability")
                    self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize HoneyHive client: {e}")
                self.enabled = False
        else:
            logger.info("HoneyHive not available or disabled")
    
    def log_llm_interaction(
        self,
        session_id: str,
        model: str,
        prompt: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost: Optional[float] = None
    ) -> bool:
        """Log an LLM interaction to HoneyHive"""
        if not self.enabled or not self.client:
            return False
        
        try:
            event = Event(
                session_id=session_id,
                event_type=EventType.MODEL,
                inputs={
                    "prompt": prompt,
                    "model": model
                },
                outputs={
                    "response": response
                },
                metadata={
                    **(metadata or {}),
                    "duration_ms": duration_ms,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cost": cost,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                error=None
            )
            
            self.client.events.create(event)
            return True
            
        except Exception as e:
            logger.error(f"Failed to log LLM interaction to HoneyHive: {e}")
            return False
    
    def log_tool_usage(
        self,
        session_id: str,
        tool_name: str,
        tool_inputs: Dict[str, Any],
        tool_outputs: Dict[str, Any],
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Log tool usage to HoneyHive"""
        if not self.enabled or not self.client:
            return False
        
        try:
            event = Event(
                session_id=session_id,
                event_type=EventType.TOOL,
                inputs={
                    "tool_name": tool_name,
                    **tool_inputs
                },
                outputs=tool_outputs,
                metadata={
                    **(metadata or {}),
                    "success": success,
                    "duration_ms": duration_ms,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                error=error_message
            )
            
            self.client.events.create(event)
            return True
            
        except Exception as e:
            logger.error(f"Failed to log tool usage to HoneyHive: {e}")
            return False
    
    def log_workflow_execution(
        self,
        session_id: str,
        workflow_name: str,
        task_description: str,
        agent_results: List[Dict[str, Any]],
        final_result: str,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Log complete workflow execution to HoneyHive"""
        if not self.enabled or not self.client:
            return False
        
        try:
            event = Event(
                session_id=session_id,
                event_type=EventType.CHAIN,
                inputs={
                    "workflow_name": workflow_name,
                    "task_description": task_description
                },
                outputs={
                    "final_result": final_result,
                    "agent_results": agent_results
                },
                metadata={
                    **(metadata or {}),
                    "success": success,
                    "duration_ms": duration_ms,
                    "agent_count": len(agent_results),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                error=error_message
            )
            
            self.client.events.create(event)
            return True
            
        except Exception as e:
            logger.error(f"Failed to log workflow execution to HoneyHive: {e}")
            return False
    
    def log_document_processing(
        self,
        session_id: str,
        operation: str,
        document_count: int,
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Log document processing operations to HoneyHive"""
        if not self.enabled or not self.client:
            return False
        
        try:
            event = Event(
                session_id=session_id,
                event_type=EventType.TOOL,
                inputs={
                    "operation": operation,
                    "document_count": document_count
                },
                outputs={
                    "success": success,
                    "processed_documents": document_count if success else 0
                },
                metadata={
                    **(metadata or {}),
                    "duration_ms": duration_ms,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                error=error_message
            )
            
            self.client.events.create(event)
            return True
            
        except Exception as e:
            logger.error(f"Failed to log document processing to HoneyHive: {e}")
            return False
    
    def log_external_mcp_call(
        self,
        session_id: str,
        server_name: str,
        tool_name: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        success: bool,
        metadata: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Log external MCP server calls to HoneyHive"""
        if not self.enabled or not self.client:
            return False
        
        try:
            event = Event(
                session_id=session_id,
                event_type=EventType.TOOL,
                inputs={
                    "server_name": server_name,
                    "tool_name": tool_name,
                    **inputs
                },
                outputs=outputs,
                metadata={
                    **(metadata or {}),
                    "success": success,
                    "duration_ms": duration_ms,
                    "external_service": True,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                error=error_message
            )
            
            self.client.events.create(event)
            return True
            
        except Exception as e:
            logger.error(f"Failed to log external MCP call to HoneyHive: {e}")
            return False
    
    def add_feedback(
        self,
        session_id: str,
        rating: int,
        feedback_text: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Add user feedback to HoneyHive"""
        if not self.enabled or not self.client:
            return False
        
        try:
            feedback = Feedback(
                session_id=session_id,
                rating=rating,
                feedback=feedback_text,
                metadata=metadata or {}
            )
            
            self.client.feedback.create(feedback)
            return True
            
        except Exception as e:
            logger.error(f"Failed to add feedback to HoneyHive: {e}")
            return False
    
    def create_session_id(self, prefix: str = "curated-agent") -> str:
        """Create a unique session ID for tracking"""
        import uuid
        return f"{prefix}-{uuid.uuid4().hex[:8]}-{int(datetime.now(timezone.utc).timestamp())}"
    
    def get_session_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific session"""
        if not self.enabled or not self.client:
            return None
        
        try:
            # This would use HoneyHive's analytics API when available
            # For now, return basic info
            return {
                "session_id": session_id,
                "status": "tracked",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get session metrics from HoneyHive: {e}")
            return None


def honeyhive_monitor(session_id_prefix: str = "operation"):
    """Decorator to monitor function execution with HoneyHive"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            honeyhive_service = get_honeyhive_service()
            session_id = honeyhive_service.create_session_id(session_id_prefix)
            start_time = datetime.now(timezone.utc)
            
            try:
                result = await func(*args, session_id=session_id, **kwargs)
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                # Log successful execution
                honeyhive_service.log_tool_usage(
                    session_id=session_id,
                    tool_name=func.__name__,
                    tool_inputs={"args": str(args), "kwargs": str(kwargs)},
                    tool_outputs={"result": str(result)[:1000]},  # Truncate large results
                    success=True,
                    duration_ms=duration_ms
                )
                
                return result
                
            except Exception as e:
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                # Log failed execution
                honeyhive_service.log_tool_usage(
                    session_id=session_id,
                    tool_name=func.__name__,
                    tool_inputs={"args": str(args), "kwargs": str(kwargs)},
                    tool_outputs={},
                    success=False,
                    duration_ms=duration_ms,
                    error_message=str(e)
                )
                
                raise e
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            honeyhive_service = get_honeyhive_service()
            session_id = honeyhive_service.create_session_id(session_id_prefix)
            start_time = datetime.now(timezone.utc)
            
            try:
                result = func(*args, session_id=session_id, **kwargs)
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                # Log successful execution
                honeyhive_service.log_tool_usage(
                    session_id=session_id,
                    tool_name=func.__name__,
                    tool_inputs={"args": str(args), "kwargs": str(kwargs)},
                    tool_outputs={"result": str(result)[:1000]},  # Truncate large results
                    success=True,
                    duration_ms=duration_ms
                )
                
                return result
                
            except Exception as e:
                duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                
                # Log failed execution
                honeyhive_service.log_tool_usage(
                    session_id=session_id,
                    tool_name=func.__name__,
                    tool_inputs={"args": str(args), "kwargs": str(kwargs)},
                    tool_outputs={},
                    success=False,
                    duration_ms=duration_ms,
                    error_message=str(e)
                )
                
                raise e
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Global HoneyHive service instance
_honeyhive_service = None


def get_honeyhive_service() -> HoneyHiveService:
    """Get the global HoneyHive service instance"""
    global _honeyhive_service
    if _honeyhive_service is None:
        _honeyhive_service = HoneyHiveService()
    return _honeyhive_service