from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated, Dict
import operator
from app.schemas.query_models import EnrichedQuery
import logging

logger = logging.getLogger(__name__)

class FilterState(TypedDict):
    """State passed through filtering pipeline"""
    enriched_query: EnrichedQuery
    candidate_profile: dict
    jobs: Annotated[List, operator.add]
    filtered_jobs: Annotated[List, operator.add]
    filter_stage: str
    rejection_reasons: dict

def filter_role_match(state: FilterState) -> FilterState:
    """Filter 1: Match job title and required skills (40% threshold)"""
    
    query = state["enriched_query"]
    candidate_skills = set(state["candidate_profile"].get("skills", []))
    all_skills = candidate_skills.union(set(query.related_skills))
    
    filtered = []
    for job in state["jobs"]:
        job_skills = set(job.get("skills") or [])
        
        if not job_skills:
            # No skills listed, keep job
            filtered.append(job)
            continue
            
        overlap = len(job_skills.intersection(all_skills))
        overlap_ratio = overlap / len(job_skills) if job_skills else 0
        
        if overlap_ratio >= 0.4:  # 40% skill match threshold
            filtered.append(job)
        else:
            state["rejection_reasons"][job.get("url", "")] = f"Insufficient skill match ({overlap_ratio:.0%})"
    
    state["filtered_jobs"] = filtered
    state["filter_stage"] = "role_match_complete"
    logger.info(f"Filter 1 (Role Match): {len(state['jobs'])} → {len(filtered)} jobs")
    return state

def filter_experience(state: FilterState) -> FilterState:
    """Filter 2: Match years of experience"""
    
    candidate_exp = state["candidate_profile"].get("years_experience", 0)
    
    filtered = []
    for job in state["filtered_jobs"]:
        min_exp = job.get("years_experience_min") or 0
        
        if candidate_exp >= min_exp:
            filtered.append(job)
        else:
            state["rejection_reasons"][job.get("url", "")] = f"Need {min_exp}+ years (have {candidate_exp})"
    
    state["filtered_jobs"] = filtered
    state["filter_stage"] = "experience_complete"
    logger.info(f"Filter 2 (Experience): {len(state['jobs'])} → {len(filtered)} jobs")
    return state

def filter_visa(state: FilterState) -> FilterState:
    """Filter 3: Visa sponsorship requirements"""
    
    visa_status = state["candidate_profile"].get("visa_status", "")
    needs_sponsorship = "sponsorship" in visa_status.lower() or "h1b" in visa_status.lower()
    
    filtered = []
    for job in state["filtered_jobs"]:
        if needs_sponsorship:
            # Candidate needs sponsorship
            if job.get("visa_sponsorship") and not job.get("requires_citizenship"):
                filtered.append(job)
            else:
                state["rejection_reasons"][job.get("url", "")] = "No visa sponsorship or requires citizenship"
        else:
            # Candidate doesn't need sponsorship, keep all jobs
            filtered.append(job)
    
    state["filtered_jobs"] = filtered
    state["filter_stage"] = "visa_complete"
    logger.info(f"Filter 3 (Visa): {len(state['jobs'])} → {len(filtered)} jobs")
    return state

def filter_education(state: FilterState) -> FilterState:
    """Filter 4: Education requirements"""
    
    candidate_edu = state["candidate_profile"].get("education", "")
    edu_levels = {"Bachelor": 1, "Master": 2, "PhD": 3}
    candidate_level = edu_levels.get(candidate_edu, 0)
    
    filtered = []
    for job in state["filtered_jobs"]:
        required_edu = job.get("education_required")
        
        if not required_edu:
            # No education requirement, keep job
            filtered.append(job)
        else:
            required_level = edu_levels.get(required_edu, 0)
            if candidate_level >= required_level:
                filtered.append(job)
            else:
                state["rejection_reasons"][job.get("url", "")] = f"Requires {required_edu} (have {candidate_edu or 'None'})"
    
    state["filtered_jobs"] = filtered
    state["filter_stage"] = "education_complete"
    logger.info(f"Filter 4 (Education): {len(state['jobs'])} → {len(filtered)} jobs")
    return state

def score_skills_alignment(state: FilterState) -> FilterState:
    """Filter 5: Calculate match scores (0-100)"""
    
    candidate_skills = set(state["candidate_profile"].get("skills", []))
    
    scored_jobs = []
    for job in state["filtered_jobs"]:
        job_skills = set(job.get("skills") or [])
        
        if not job_skills:
            score = 50.0  # Default score for jobs without listed skills
        else:
            skill_match = len(job_skills.intersection(candidate_skills)) / len(job_skills)
            score = skill_match * 100
        
        # Add match_score to job dict
        job["match_score"] = round(score, 1)
        scored_jobs.append(job)
    
    # Sort by match score (highest first)
    scored_jobs.sort(key=lambda j: j.get("match_score", 0), reverse=True)
    
    state["filtered_jobs"] = scored_jobs
    state["filter_stage"] = "scoring_complete"
    logger.info(f"Filter 5 (Scoring): Scored {len(scored_jobs)} jobs")
    return state

def build_filtering_graph() -> StateGraph:
    """Build the 5-stage filtering pipeline"""
    
    graph = StateGraph(FilterState)
    
    # Add nodes
    graph.add_node("filter_role", filter_role_match)
    graph.add_node("filter_experience", filter_experience)
    graph.add_node("filter_visa", filter_visa)
    graph.add_node("filter_education", filter_education)
    graph.add_node("score_alignment", score_skills_alignment)
    
    # Define edges (pipeline flow)
    graph.set_entry_point("filter_role")
    graph.add_edge("filter_role", "filter_experience")
    graph.add_edge("filter_experience", "filter_visa")
    graph.add_edge("filter_visa", "filter_education")
    graph.add_edge("filter_education", "score_alignment")
    graph.add_edge("score_alignment", END)
    
    return graph.compile()
