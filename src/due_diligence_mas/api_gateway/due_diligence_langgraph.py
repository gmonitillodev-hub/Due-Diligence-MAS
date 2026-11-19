from due_diligence_mas.mas_definition.classes.company import CompanyInfo
from due_diligence_mas.mas_definition.langgraph.graph.due_diligence import DueDiligence_Graph
from due_diligence_mas.mas_definition.utils.execution_db import ExecutionStatus, get_execution, update_execution
from due_diligence_mas.utils.session_manager import create_session_id
from fastapi.responses import PlainTextResponse
from fastapi import BackgroundTasks, FastAPI, HTTPException, Response, Cookie
import os
import uvicorn
from enum import Enum

from pydantic import BaseModel
from due_diligence_mas.utils.logger import setup_logger

logger = setup_logger("lg_api_gateway")

class InferenceRequest(BaseModel):
    company_info: CompanyInfo

class Decision(Enum):
    PROCEED = "proceed"
    END = "end"
class ResumeRequest(BaseModel):
    decision: Decision

graph_gateway = FastAPI()

due_diligence_graph = DueDiligence_Graph()

@graph_gateway.get("/health")
async def health():
    return {"status": "available"}

@graph_gateway.get('/system_info')
async def system_info():
    return {
        "version": "1.0.0",
        "author": "Giuseppe Monitillo",
        "description": "LLM Mock provider - This provider will return always 200 and proper responses",
        "status": "PartiallyAvailable"
    }
    
def _run_in_background(company_info: CompanyInfo, session_id: str):
    try:
        due_diligence_graph.run(company_info, session_id)
    except Exception as e:
        # The execution row is already marked as failed by the graph
        logger.error(f"Background run failed (sessionId: {session_id}): {e}")

def _resume_in_background(decision: str, session_id: str):
    try:
        due_diligence_graph.resume(decision, session_id)
    except Exception as e:
        logger.error(f"Background resume failed (sessionId: {session_id}): {e}")

@graph_gateway.post('/inference')
async def run_graph(
    payload: InferenceRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    sessionId = Cookie(None)
):
    """ 
        Always create a new session
    """
    try:
        sessionId = create_session_id()
            
        # The graph runs after the response is sent; follow it with GET /execution
        background_tasks.add_task(_run_in_background, payload.company_info, sessionId)
  
        """ 
            Set sessionId cookie that will be used in next iterations 
        """  
        response.set_cookie(key="sessionId", value=sessionId)

        return {"status": "initialized"}
    
    except Exception as e:
                
        error_message = getattr(e, "message", None) or str(e)
        status_code = getattr(e, "status_code", 500)
        logger.error(f"Inference failed (sessionId: {sessionId}, status: {status_code}): {error_message}")
        raise HTTPException(status_code=status_code, detail=f"Sorry, something went wrong. - Details: {error_message}")
   
@graph_gateway.post('/resume')
async def resume_after_interrupt(
    payload: ResumeRequest,
    response: Response,
    background_tasks: BackgroundTasks,
    sessionId = Cookie(None)
):
    
    try:
    
        if (sessionId is None):
            raise ValueError("SessionId not provided")

        execution = get_execution(sessionId)
        if execution is None or execution["status"] != ExecutionStatus.AWAITING_REVIEW.value:
            raise HTTPException(status_code=409, detail="No execution awaiting review to resume for this session")

        # The graph resumes after the response is sent; follow it with GET /execution
        background_tasks.add_task(_resume_in_background, payload.decision.value, sessionId)
        # Status is set now so a second /resume cannot be accepted while the first is running
        update_execution(sessionId, status=ExecutionStatus.RUNNING, pending_review=None)

        return {"sessionId": sessionId, "status": "resumed"}
    
    except HTTPException:
        raise
    except Exception as e:
                
        error_message = getattr(e, "message", None) or str(e)
        status_code = getattr(e, "status_code", 500)
        logger.error(f"Resume failed (sessionId: {sessionId}, status: {status_code}): {error_message}")
        raise HTTPException(status_code=status_code, detail=f"Sorry, something went wrong. - Details: {error_message}")     
    
@graph_gateway.get('/execution')
async def get_execution_status(sessionId = Cookie(None)):
    if sessionId is None:
        raise HTTPException(status_code=400, detail="SessionId not provided")
    execution = get_execution(sessionId)
    if execution is None:
        raise HTTPException(status_code=404, detail=f"Execution {sessionId} not found")
    return execution

@graph_gateway.get('/memo', response_class=PlainTextResponse)
async def get_memo(sessionId = Cookie(None)):
    if sessionId is None:
        raise HTTPException(status_code=400, detail="SessionId not provided")
    execution = get_execution(sessionId)
    if execution is None:
        raise HTTPException(status_code=404, detail=f"Execution {sessionId} not found")
    if not execution["memo_markdown"]:
        raise HTTPException(status_code=409, detail=f"Memo not available yet (status: {execution['status']})")
    return PlainTextResponse(execution["memo_markdown"], media_type="text/markdown; charset=utf-8")

""" @graph_gateway.get('/session/{session_id}/data')
def get_session_data(session_id: str):
    
    try:
        return cc_agent.export_session_data(sessionId=session_id)
    
    except Exception as e:
        logger.error(f"Failed to export session data (session_id: {session_id}): {e}")
        return e


     """
     
     
def init_gateway():    
    
    host = os.getenv("AGENT_GATEWAY_HOST", "127.0.0.1")
    port = int(os.getenv("AGENT_GATEWAY_PORT", "8100"))

    try:
        
        uvicorn.run(
            "due_diligence_mas.api_gateway.due_diligence_langgraph:graph_gateway",
            host=host,
            port=port,
            reload=True,
        )
        
    except Exception as e:
        logger.error(f"Error initializing Agent gateway: {e}")
        print(f"    Error initialing Agent gateway - Details: {e}")