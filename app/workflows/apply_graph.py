"""
LangGraph workflow for candidate application processing
"""
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, END
from app.services.llm_service import ResumeMatchingService
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.application import Application
from app.core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class ApplyState(TypedDict):
    """State passed through the workflow"""
    candidate_id: int
    job_id: int
    resume: str
    status: str
    score: Optional[int]
    message: str
    metadata: Dict[str, Any]
    application_id: Optional[int]

def validate_input(state: ApplyState) -> dict:
    """Validate that candidate and job exist"""
    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter(Candidate.id == state["candidate_id"]).first()
        job = db.query(Job).filter(Job.id == state["job_id"]).first()
        
        if not candidate:
            return {**state, "status": "error", "message": "Candidate not found"}
        
        if not job:
            return {**state, "status": "error", "message": "Job not found"}
        
        if not state.get("resume") or len(state["resume"].strip()) < 10:
            return {**state, "status": "error", "message": "Resume text is empty or too short"}
        
        logger.info(f"Validation passed for candidate {state['candidate_id']} applying to job {state['job_id']}")
        return {**state, "status": "validated", "message": "Input validation passed"}
    
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return {**state, "status": "error", "message": f"Validation error: {str(e)}"}
    finally:
        db.close()

def score_match(state: ApplyState) -> dict:
    """Use AI to score resume against job"""
    if state.get("status") == "error":
        return state
    
    db = SessionLocal()
    try:
        # Get candidate and job from database
        candidate = db.query(Candidate).filter(Candidate.id == state["candidate_id"]).first()
        job = db.query(Job).filter(Job.id == state["job_id"]).first()
        
        if not candidate or not job:
            return {**state, "status": "error", "message": "Database record not found during scoring"}
        
        # Run AI scoring
        service = ResumeMatchingService()
        result = service.score_candidate(
            resume_text=state["resume"],
            job_description=job.description,
            requirements=job.requirements
        )
        
        logger.info(f"AI Score: {result.match_score} for candidate {state['candidate_id']} on job {state['job_id']}")
        
        # Return updated state
        return {
            **state,
            "score": result.match_score,
            "status": result.recommendation,
            "message": result.reasoning,
            "metadata": {
                "strengths": result.strengths,
                "gaps": result.gaps
            }
        }
    
    except Exception as e:
        logger.error(f"Scoring error: {str(e)}")
        return {**state, "status": "error", "message": f"Scoring error: {str(e)}"}
    finally:
        db.close()

def save_application(state: ApplyState) -> dict:
    """Save application result to database"""
    db = SessionLocal()
    try:
        # Create application record
        application = Application(
            candidate_id=state["candidate_id"],
            job_id=state["job_id"],
            status=state.get("status", "pending"),
            match_score=state.get("score"),
            strengths=state.get("metadata", {}).get("strengths", []),
            gaps=state.get("metadata", {}).get("gaps", []),
            ai_reasoning=state.get("message", "")
        )
        
        db.add(application)
        db.commit()
        db.refresh(application)
        
        logger.info(f"Application saved with ID: {application.id}")
        
        return {
            **state,
            "application_id": application.id,
            "message": f"Application saved with ID {application.id}: {state.get('message', '')}"
        }
    
    except Exception as e:
        logger.error(f"Save error: {str(e)}")
        db.rollback()
        return {**state, "status": "error", "message": f"Save error: {str(e)}"}
    finally:
        db.close()

def build_apply_graph():
    """Build the LangGraph workflow"""
    graph = StateGraph(ApplyState)
    
    # Add nodes
    graph.add_node("validate_input", validate_input)
    graph.add_node("score_match", score_match)
    graph.add_node("save_application", save_application)
    
    # Set entry point and edges
    graph.set_entry_point("validate_input")
    graph.add_edge("validate_input", "score_match")
    graph.add_edge("score_match", "save_application")
    graph.add_edge("save_application", END)
    
    return graph.compile()
