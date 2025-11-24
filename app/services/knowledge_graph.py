from neo4j import GraphDatabase
from app.schemas.query_models import ParsedQuery, EnrichedQuery
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class KnowledgeGraphService:
    """Service for enriching queries using Neo4j knowledge graph"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """Close the Neo4j driver connection"""
        self.driver.close()

    def enrich_query(self, parsed_query: ParsedQuery) -> EnrichedQuery:
        """
        Enrich a parsed query with knowledge graph data
        
        Args:
            parsed_query: Structured query from parser
            
        Returns:
            EnrichedQuery with additional context from knowledge graph
        """
        with self.driver.session() as session:
            # Get related skills
            related_skills = self._get_related_skills(session, parsed_query.skills_required)
            
            # Get job title synonyms and variations
            expanded_titles = self._get_job_title_synonyms(session, parsed_query.job_title)
            
            # Get companies offering visa sponsorship
            sponsor_companies = []
            if parsed_query.visa_requirements:
                sponsor_companies = self._get_sponsor_companies(session, parsed_query.visa_requirements)
            
            # Get education alternatives
            education_alts = []
            if parsed_query.education_level:
                education_alts = self._get_education_alternatives(session, parsed_query.education_level)

            return EnrichedQuery(
                original_query=parsed_query,
                expanded_job_titles=expanded_titles,
                related_skills=related_skills,
                sponsor_companies=sponsor_companies,
                education_alternatives=education_alts
            )

    def _get_related_skills(self, session, skills: List[str]) -> List[str]:
        """Find related skills through graph traversal"""
        if not skills:
            return []
        
        query = """
        UNWIND $skills AS skill
        MATCH (s:Skill {name: skill})-[:RELATED_TO*1..2]-(rs:Skill)
        WHERE rs.name <> skill
        RETURN DISTINCT rs.name AS skill, rs.popularity AS popularity
        ORDER BY popularity DESC
        LIMIT 10
        """
        
        try:
            result = session.run(query, skills=skills)
            return [record["skill"] for record in result]
        except Exception as e:
            logger.error(f"Error getting related skills: {e}")
            return []

    def _get_job_title_synonyms(self, session, job_title: str) -> List[str]:
        """Find job title synonyms and variations"""
        query = """
        MATCH (jt:JobTitle)
        WHERE toLower(jt.name) CONTAINS toLower($title)
        OPTIONAL MATCH (jt)-[:SYNONYM_OF]-(alt:JobTitle)
        RETURN DISTINCT COALESCE(alt.name, jt.name) AS title
        LIMIT 5
        """
        
        try:
            result = session.run(query, title=job_title)
            return [record["title"] for record in result]
        except Exception as e:
            logger.error(f"Error getting job title synonyms: {e}")
            return [job_title]

    def _get_sponsor_companies(self, session, visa_type: str) -> List[Dict[str, str]]:
        """Find companies that sponsor specific visa types"""
        # Extract visa type (e.g., "H1B" from "H1B Sponsorship")
        visa_short = visa_type.split()[0] if visa_type else ""
        
        query = """
        MATCH (c:Company)-[:SPONSORS_VISA]->(v:VisaType)
        WHERE v.type = $visa_type
        RETURN c.name AS name, c.id AS id, c.size AS size, c.industry AS industry
        LIMIT 50
        """
        
        try:
            result = session.run(query, visa_type=visa_short)
            return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Error getting sponsor companies: {e}")
            return []

    def _get_education_alternatives(self, session, education: str) -> List[str]:
        """Find alternative education levels"""
        query = """
        MATCH (e:EducationLevel {level: $education})
        RETURN e.level AS level
        """
        
        try:
            result = session.run(query, education=education)
            return [record["level"] for record in result]
        except Exception as e:
            logger.error(f"Error getting education alternatives: {e}")
            return []
