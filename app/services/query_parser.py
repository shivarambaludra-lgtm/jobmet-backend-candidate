from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from app.schemas.query_models import ParsedQuery
from app.prompts.query_parsing import QUERY_PARSING_PROMPT
import json
import logging

logger = logging.getLogger(__name__)

class QueryParserService:
    """Service for parsing natural language job search queries using LangChain and GPT-4"""
    
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0,
            api_key=openai_api_key
        )
        self.parser = PydanticOutputParser(pydantic_object=ParsedQuery)
        self.prompt = ChatPromptTemplate.from_template(QUERY_PARSING_PROMPT)

    async def parse_query(self, query: str, candidate_profile=None) -> ParsedQuery:
        """
        Parse a natural language query into structured format
        
        Args:
            query: Natural language job search query
            candidate_profile: Optional candidate profile for context
            
        Returns:
            ParsedQuery object with structured data
        """
        # Build context from candidate profile
        context = {
            "candidate_skills": ", ".join(candidate_profile.get("skills", [])) if candidate_profile else "Not specified",
            "years_experience": candidate_profile.get("years_experience", "Not specified") if candidate_profile else "Not specified",
            "location": candidate_profile.get("location", "Not specified") if candidate_profile else "Not specified",
            "visa_status": candidate_profile.get("visa_status", "Not specified") if candidate_profile else "Not specified",
            "education": candidate_profile.get("education", "Not specified") if candidate_profile else "Not specified",
        }
        
        # Format prompt with query and context
        formatted_prompt = self.prompt.format(query=query, **context)
        
        try:
            # Call LLM
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Parse JSON response
            parsed_data = json.loads(response.content)
            return ParsedQuery(**parsed_data)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback: return basic query with just the job title
            return ParsedQuery(
                job_title=query,
                skills_required=[],
                remote=False
            )
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return ParsedQuery(
                job_title=query,
                skills_required=[],
                remote=False
            )
