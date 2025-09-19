from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
from pydantic import BaseModel

try:
    from app.services.honeyhive_service import get_honeyhive_service
    HONEYHIVE_AVAILABLE = True
except ImportError:
    HONEYHIVE_AVAILABLE = False

router = APIRouter(prefix="/api/v1/observability", tags=["Observability"])


class FeedbackRequest(BaseModel):
    """Request model for user feedback"""
    session_id: str
    rating: int  # 1-5 rating
    feedback_text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionMetricsRequest(BaseModel):
    """Request model for session metrics"""
    session_id: str


@router.get("/health")
async def observability_health():
    """Check the health of observability services"""
    try:
        if not HONEYHIVE_AVAILABLE:
            return JSONResponse(content={
                "success": False,
                "service": "HoneyHive",
                "status": "not_available",
                "message": "HoneyHive package not installed"
            })
        
        honeyhive_service = get_honeyhive_service()
        
        return JSONResponse(content={
            "success": True,
            "service": "HoneyHive", 
            "status": "available" if honeyhive_service.enabled else "disabled",
            "enabled": honeyhive_service.enabled,
            "client_initialized": honeyhive_service.client is not None
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check observability health: {str(e)}")


@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for a session"""
    if not HONEYHIVE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HoneyHive observability not available"
        )
    
    try:
        honeyhive_service = get_honeyhive_service()
        
        if not honeyhive_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="HoneyHive service not enabled"
            )
        
        # Validate rating
        if request.rating < 1 or request.rating > 5:
            raise HTTPException(
                status_code=400,
                detail="Rating must be between 1 and 5"
            )
        
        success = honeyhive_service.add_feedback(
            session_id=request.session_id,
            rating=request.rating,
            feedback_text=request.feedback_text,
            metadata=request.metadata
        )
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "Feedback submitted successfully",
                "session_id": request.session_id
            })
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to submit feedback to HoneyHive"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit feedback: {str(e)}")


@router.get("/sessions/{session_id}/metrics")
async def get_session_metrics(session_id: str):
    """Get metrics for a specific session"""
    if not HONEYHIVE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HoneyHive observability not available"
        )
    
    try:
        honeyhive_service = get_honeyhive_service()
        
        if not honeyhive_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="HoneyHive service not enabled"
            )
        
        metrics = honeyhive_service.get_session_metrics(session_id)
        
        if metrics:
            return JSONResponse(content={
                "success": True,
                "session_id": session_id,
                "metrics": metrics
            })
        else:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for session {session_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session metrics: {str(e)}")


@router.get("/status")
async def get_observability_status():
    """Get detailed observability status"""
    try:
        status = {
            "honeyhive_available": HONEYHIVE_AVAILABLE,
            "services": {}
        }
        
        if HONEYHIVE_AVAILABLE:
            honeyhive_service = get_honeyhive_service()
            status["services"]["honeyhive"] = {
                "enabled": honeyhive_service.enabled,
                "client_initialized": honeyhive_service.client is not None,
                "api_key_configured": hasattr(honeyhive_service, 'client') and honeyhive_service.client is not None
            }
        
        return JSONResponse(content={
            "success": True,
            "status": status
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get observability status: {str(e)}")


@router.post("/sessions/{session_id}/events/llm")
async def log_llm_event(session_id: str, event_data: Dict[str, Any]):
    """Log an LLM interaction event"""
    if not HONEYHIVE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HoneyHive observability not available"
        )
    
    try:
        honeyhive_service = get_honeyhive_service()
        
        if not honeyhive_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="HoneyHive service not enabled"
            )
        
        success = honeyhive_service.log_llm_interaction(
            session_id=session_id,
            model=event_data.get("model", "unknown"),
            prompt=event_data.get("prompt", ""),
            response=event_data.get("response", ""),
            metadata=event_data.get("metadata"),
            duration_ms=event_data.get("duration_ms"),
            input_tokens=event_data.get("input_tokens"),
            output_tokens=event_data.get("output_tokens"),
            cost=event_data.get("cost")
        )
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "LLM event logged successfully",
                "session_id": session_id
            })
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to log LLM event to HoneyHive"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log LLM event: {str(e)}")


@router.post("/sessions/{session_id}/events/tool")
async def log_tool_event(session_id: str, event_data: Dict[str, Any]):
    """Log a tool usage event"""
    if not HONEYHIVE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HoneyHive observability not available"
        )
    
    try:
        honeyhive_service = get_honeyhive_service()
        
        if not honeyhive_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="HoneyHive service not enabled"
            )
        
        success = honeyhive_service.log_tool_usage(
            session_id=session_id,
            tool_name=event_data.get("tool_name", "unknown"),
            tool_inputs=event_data.get("inputs", {}),
            tool_outputs=event_data.get("outputs", {}),
            success=event_data.get("success", False),
            metadata=event_data.get("metadata"),
            duration_ms=event_data.get("duration_ms"),
            error_message=event_data.get("error_message")
        )
        
        if success:
            return JSONResponse(content={
                "success": True,
                "message": "Tool event logged successfully",
                "session_id": session_id
            })
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to log tool event to HoneyHive"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log tool event: {str(e)}")


@router.post("/test-logging")
async def test_observability_logging():
    """Test observability logging functionality"""
    if not HONEYHIVE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="HoneyHive observability not available"
        )
    
    try:
        honeyhive_service = get_honeyhive_service()
        
        if not honeyhive_service.enabled:
            raise HTTPException(
                status_code=503,
                detail="HoneyHive service not enabled"
            )
        
        # Create test session
        test_session_id = honeyhive_service.create_session_id("test")
        
        # Log test LLM interaction
        llm_success = honeyhive_service.log_llm_interaction(
            session_id=test_session_id,
            model="test-model",
            prompt="This is a test prompt",
            response="This is a test response",
            metadata={"test": True},
            duration_ms=100,
            input_tokens=10,
            output_tokens=15,
            cost=0.01
        )
        
        # Log test tool usage
        tool_success = honeyhive_service.log_tool_usage(
            session_id=test_session_id,
            tool_name="test_tool",
            tool_inputs={"input": "test"},
            tool_outputs={"output": "test result"},
            success=True,
            duration_ms=50
        )
        
        return JSONResponse(content={
            "success": True,
            "test_session_id": test_session_id,
            "results": {
                "llm_logging": llm_success,
                "tool_logging": tool_success
            },
            "message": "Test logging completed"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to test observability logging: {str(e)}")