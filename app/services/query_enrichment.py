from app.services.query_parser import QueryParserService
from app.services.knowledge_graph import KnowledgeGraphService
from app.schemas.query_models import EnrichedQuery
import redis
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

class QueryEnrichmentService:
    """Orchestrator service that combines query parsing and knowledge graph enrichment with caching"""
    
    def __init__(
        self,
        query_parser: QueryParserService,
        knowledge_graph: KnowledgeGraphService,
        redis_client: redis.Redis
    ):
        self.parser = query_parser
        self.kg = knowledge_graph
        self.cache = redis_client

    async def process_query(self, query: str, candidate_profile=None) -> EnrichedQuery:
        """
        Process a query through the full pipeline: parse -> enrich -> cache
        
        Args:
            query: Natural language search query
            candidate_profile: Optional candidate profile for personalization
            
        Returns:
            EnrichedQuery with parsed and enriched data
        """
        # Check cache first
        cache_key = self._generate_cache_key(query, candidate_profile)
        
        try:
            cached = self.cache.get(cache_key)
            if cached:
                logger.info(f"Cache hit for query: {query[:50]}...")
                return EnrichedQuery(**json.loads(cached))
        except Exception as e:
            logger.warning(f"Cache read error: {e}")

        # Parse query with LLM
        parsed_query = await self.parser.parse_query(query, candidate_profile)
        
        # Enrich with knowledge graph
        enriched_query = self.kg.enrich_query(parsed_query)
        
        # Cache the result (24 hour TTL)
        try:
            self.cache.setex(
                cache_key,
                86400,  # 24 hours
                enriched_query.model_dump_json()
            )
            logger.info(f"Cached enriched query for: {query[:50]}...")
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
        
        return enriched_query

    def _generate_cache_key(self, query: str, profile) -> str:
        """Generate a unique cache key based on query and profile"""
        profile_hash = ""
        if profile:
            # Hash the profile to create a stable key
            profile_str = json.dumps(profile, sort_keys=True)
            profile_hash = hashlib.md5(profile_str.encode()).hexdigest()[:8]
        
        query_hash = hashlib.md5(query.encode()).hexdigest()[:12]
        return f"query:{query_hash}:{profile_hash}"
