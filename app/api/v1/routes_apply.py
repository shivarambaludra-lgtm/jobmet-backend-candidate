from fastapi import APIRouter
from pydantic import BaseModel
from app.workflows.apply_graph import build_apply_graph

router = APIRouter()

class ApplyRequest(BaseModel):
    candidate_id: str
    job_id: str
    resume_text: str

class ApplyResponse(BaseModel):
    application_id: str
    status: str
    message: str

@router.post("/apply", response_model=ApplyResponse)
async def apply_to_job(payload: ApplyRequest):
    graph = build_apply_graph()
    result = graph.invoke({
        "candidate_id": payload.candidate_id,
        "job_id": payload.job_id,
        "resume_text": payload.resume_text,
        "status": "received",
        "message": "",
    })
    return ApplyResponse(
        application_id="temp-123",
        status=result["status"],
        message=result["message"],
    )
