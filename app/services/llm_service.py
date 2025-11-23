"""
LLM Service for AI-powered resume matching
"""
import os
import json
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

class MatchResult(BaseModel):
    """Structured output from LLM matching"""
    match_score: int = Field(description="Match score from 0-100")
    recommendation: str = Field(description="accept, review, or reject")
    strengths: List[str] = Field(description="Key strengths from resume")
    gaps: List[str] = Field(description="Skill gaps vs job requirements")
    reasoning: str = Field(description="Brief explanation of score")

class ResumeMatchingService:
    """Service for AI-powered resume to job matching"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=api_key)
        self.parser = JsonOutputParser(pydantic_object=MatchResult)
        
    def score_candidate(self, resume_text: str, job_description: str, requirements: str) -> MatchResult:
        """
        Score a candidate's resume against a job posting
        
        Args:
            resume_text: The candidate's resume
            job_description: The job description
            requirements: Required skills/qualifications
            
        Returns:
            MatchResult with score, recommendation, and analysis
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical recruiter analyzing candidate resumes.
            
            Analyze the resume against the job requirements and provide a detailed assessment.
            Score from 0-100:
            - 80-100: Excellent match, hire immediately
            - 60-79: Good match, worth reviewing
            - 40-59: Partial match, might be trainable
            - 20-39: Weak match, significant gaps
            - 0-19: Poor match, not suitable
            
            {format_instructions}"""),
            ("user", """
CANDIDATE RESUME:
{resume}

JOB DESCRIPTION:
{job_description}

REQUIRED QUALIFICATIONS:
{requirements}

Provide your assessment in JSON format.""")
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "job_description": job_description,
                "requirements": requirements,
                "resume": resume_text
            })
            return result
        except Exception as e:
            # Fallback if parsing fails
            return MatchResult(
                match_score=0,
                recommendation="error",
                strengths=[],
                gaps=["Unable to parse response"],
                reasoning=f"Error during evaluation: {str(e)}"
            )

    def extract_skills(self, resume_text: str) -> List[str]:
        """Extract technical skills from resume"""
        prompt = ChatPromptTemplate.from_template("""
Extract all technical skills, programming languages, tools, and frameworks 
from this resume. Return as a JSON array of strings.

Resume:
{resume}

Return format: {{"skills": ["skill1", "skill2", ...]}}
""")
        
        chain = prompt | self.llm
        response = chain.invoke({"resume": resume_text})
        
        try:
            data = json.loads(response.content)
            return data.get("skills", [])
        except:
            return []
