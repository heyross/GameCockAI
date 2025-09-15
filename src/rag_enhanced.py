"""
Enhanced RAG System for GameCock AI with Vector Embeddings
Replaces keyword-based search with semantic vector search for superior performance
"""

import ollama
import numpy as np
import json
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Local imports with error handling
try:
    from .vector_db import GameCockVectorDB, VectorDBManager
except ImportError:
    try:
        from vector_db import GameCockVectorDB, VectorDBManager
    except ImportError:
        GameCockVectorDB = VectorDBManager = None

try:
    from .embedding_service import FinancialEmbeddingService
except ImportError:
    try:
        from embedding_service import FinancialEmbeddingService
    except ImportError:
        FinancialEmbeddingService = None

try:
    from .document_processor import FinancialDocumentProcessor, DocumentType, DocumentChunk
except ImportError:
    try:
        from document_processor import FinancialDocumentProcessor, DocumentType, DocumentChunk
    except ImportError:
        FinancialDocumentProcessor = DocumentType = DocumentChunk = None

# Import from the REAL database module with all tables (GameCockAI/database.py)
from database import SessionLocal, CFTCSwap

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of queries the system can handle"""
    COMPANY_ANALYSIS = "company_analysis"
    MARKET_TRENDS = "market_trends"
    RISK_ASSESSMENT = "risk_assessment"
    REGULATORY_COMPLIANCE = "regulatory_compliance"
    FINANCIAL_METRICS = "financial_metrics"
    CROSS_DATASET = "cross_dataset"
    GENERAL = "general"

@dataclass
class SearchResult:
    """Represents a search result with relevance scoring"""
    chunk_id: str
    content: str
    metadata: Dict[str, Any]
    similarity_score: float
    source_collection: str
    rank: int

@dataclass
class RAGResponse:
    """Complete RAG system response"""
    answer: str
    sources: List[SearchResult]
    query_type: QueryType
    processing_time: float
    confidence_score: float
    metadata: Dict[str, Any]

class EnhancedRAGSystem:
    """
    Enhanced RAG system with vector embeddings and semantic search
    Provides superior performance and understanding compared to keyword-based approach
    """
    
    def __init__(self, 
                 model_name: str = 'raven-enhanced',
                 vector_store_path: str = "./vector_store",
                 cache_size: int = 1000,
                 enable_async: bool = True):
        """
        Initialize the Enhanced RAG System
        
        Args:
            model_name: Name of the Ollama model to use
            vector_store_path: Path to vector database storage
            cache_size: Size of response cache
            enable_async: Whether to enable async processing
        """
        self.model_name = model_name
        self.enable_async = enable_async
        
        # Initialize components
        self.vector_db_manager = VectorDBManager(vector_store_path)
        self.embedding_service = FinancialEmbeddingService()
        self.document_processor = FinancialDocumentProcessor()
        
        # Initialize database connection
        self.db_session = SessionLocal()
        
        # Response cache
        self.response_cache = {}
        self.cache_size = cache_size
        
        # Query classification patterns
        self._init_query_patterns()
        
        # Performance metrics
        self.metrics = {
            "total_queries": 0,
            "cache_hits": 0,
            "avg_response_time": 0.0,
            "successful_queries": 0
        }
        
        logger.info("Enhanced RAG System initialized successfully")
    
    def _init_query_patterns(self):
        """Initialize patterns for query classification"""
        self.query_patterns = {
            QueryType.COMPANY_ANALYSIS: [
                r'company\s+(?:profile|analysis|information)',
                r'(?:analyze|tell me about|describe)\s+(?:company|firm|corporation)',
                r'cik\s+\d+',
                r'(?:business|corporate)\s+(?:model|strategy|operations)'
            ],
            QueryType.MARKET_TRENDS: [
                r'(?:market|trading)\s+(?:trends|patterns|activity)',
                r'(?:price|volume|volatility)\s+(?:trends|movement)',
                r'(?:swap|derivative)\s+(?:market|activity)',
                r'(?:recent|latest)\s+(?:market|trading)\s+(?:data|activity)'
            ],
            QueryType.RISK_ASSESSMENT: [
                r'risk\s+(?:factors|assessment|analysis|profile)',
                r'(?:credit|market|operational|liquidity)\s+risk',
                r'(?:exposure|concentration)\s+(?:risk|analysis)',
                r'risk\s+(?:management|mitigation)'
            ],
            QueryType.REGULATORY_COMPLIANCE: [
                r'(?:regulatory|compliance|filing)\s+(?:requirements|status)',
                r'sec\s+(?:filing|submission|requirement)',
                r'(?:form|filing)\s+(?:10-k|10-q|8-k|13f)',
                r'(?:compliance|regulatory)\s+(?:issues|violations)'
            ],
            QueryType.FINANCIAL_METRICS: [
                r'(?:financial|earnings|revenue|profit)\s+(?:metrics|performance|results)',
                r'(?:balance\s+sheet|income\s+statement|cash\s+flow)',
                r'(?:assets|liabilities|equity|debt)\s+(?:analysis|breakdown)',
                r'(?:financial\s+ratios|performance\s+indicators)'
            ]
        }
    
    async def process_query(self, 
                           query: str,
                           context_filters: Optional[Dict[str, Any]] = None,
                           max_results: int = 10,
                           include_cross_dataset: bool = True) -> RAGResponse:
        """
        Process a query using enhanced semantic search and RAG
        
        Args:
            query: User query string
            context_filters: Optional filters for search context
            max_results: Maximum number of search results to consider
            include_cross_dataset: Whether to search across multiple data sources
            
        Returns:
            RAGResponse with answer and supporting information
        """
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, context_filters)
            if cache_key in self.response_cache:
                logger.info("Cache hit for query")
                self.metrics["cache_hits"] += 1
                cached_response = self.response_cache[cache_key]
                cached_response.metadata["from_cache"] = True
                return cached_response
            
            # Classify query type
            query_type = self._classify_query(query)
            logger.info(f"Classified query as: {query_type.value}")
            
            # Perform semantic search
            search_results = await self._semantic_search(
                query, 
                query_type, 
                context_filters, 
                max_results,
                include_cross_dataset
            )
            
            # Build context from search results
            context = self._build_enhanced_context(search_results, query_type)
            
            # Generate response using LLM
            answer = await self._generate_response(query, context, query_type, search_results)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(search_results, context)
            
            # Create response object
            processing_time = time.time() - start_time
            response = RAGResponse(
                answer=answer,
                sources=search_results,
                query_type=query_type,
                processing_time=processing_time,
                confidence_score=confidence_score,
                metadata={
                    "search_results_count": len(search_results),
                    "context_length": len(context),
                    "timestamp": datetime.now().isoformat(),
                    "from_cache": False
                }
            )
            
            # Cache response
            self._cache_response(cache_key, response)
            
            # Update metrics
            self._update_metrics(processing_time, True)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process query: {str(e)}")
            
            # Create error response
            processing_time = time.time() - start_time
            error_response = RAGResponse(
                answer=f"I encountered an error processing your query: {str(e)}",
                sources=[],
                query_type=QueryType.GENERAL,
                processing_time=processing_time,
                confidence_score=0.0,
                metadata={"error": str(e), "timestamp": datetime.now().isoformat()}
            )
            
            self._update_metrics(processing_time, False)
            return error_response
    
    def _classify_query(self, query: str) -> QueryType:
        """Classify query type using pattern matching"""
        query_lower = query.lower()
        
        # Score each query type
        type_scores = {}
        for query_type, patterns in self.query_patterns.items():
            score = 0
            for pattern in patterns:
                import re
                if re.search(pattern, query_lower):
                    score += 1
            type_scores[query_type] = score
        
        # Return highest scoring type, or GENERAL if no strong match
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            if type_scores[best_type] > 0:
                return best_type
        
        # Additional heuristics for common patterns
        if any(term in query_lower for term in ['company', 'cik', 'firm', 'corporation']):
            return QueryType.COMPANY_ANALYSIS
        elif any(term in query_lower for term in ['market', 'trading', 'swap', 'trend']):
            return QueryType.MARKET_TRENDS
        elif any(term in query_lower for term in ['risk', 'exposure', 'volatility']):
            return QueryType.RISK_ASSESSMENT
        
        return QueryType.GENERAL
    
    async def _semantic_search(self, 
                              query: str,
                              query_type: QueryType,
                              context_filters: Optional[Dict[str, Any]],
                              max_results: int,
                              include_cross_dataset: bool) -> List[SearchResult]:
        """Perform semantic search across relevant collections"""
        
        # Determine target collections based on query type
        target_collections = self._get_target_collections(query_type, include_cross_dataset)
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_financial_documents([query])[0]
        
        # Search across collections
        all_results = []
        
        for collection_name in target_collections:
            try:
                # Perform vector search
                collection_results = self.vector_db_manager.db.query_documents(
                    collection_name=collection_name,
                    query_embeddings=[query_embedding.tolist()],
                    n_results=max_results,
                    where=context_filters,
                    include=["documents", "metadatas", "distances"]
                )
                
                # Convert to SearchResult objects
                if 'documents' in collection_results and collection_results['documents']:
                    for i, doc in enumerate(collection_results['documents'][0]):
                        metadata = collection_results['metadatas'][0][i] if collection_results['metadatas'] else {}
                        distance = collection_results['distances'][0][i] if collection_results['distances'] else 1.0
                        similarity = 1.0 - distance  # Convert distance to similarity
                        
                        search_result = SearchResult(
                            chunk_id=f"{collection_name}_{i}",
                            content=doc,
                            metadata=metadata,
                            similarity_score=similarity,
                            source_collection=collection_name,
                            rank=i
                        )
                        all_results.append(search_result)
                        
            except Exception as e:
                logger.warning(f"Search failed for collection {collection_name}: {str(e)}")
        
        # Sort by similarity score and return top results
        all_results.sort(key=lambda x: x.similarity_score, reverse=True)
        return all_results[:max_results]
    
    def _get_target_collections(self, 
                               query_type: QueryType, 
                               include_cross_dataset: bool) -> List[str]:
        """Determine which collections to search based on query type"""
        
        base_collections = {
            QueryType.COMPANY_ANALYSIS: ["sec_filings", "insider_reports", "form_d_filings"],
            QueryType.MARKET_TRENDS: ["cftc_summaries", "market_events", "sec_filings"],
            QueryType.RISK_ASSESSMENT: ["sec_filings", "risk_assessments", "cftc_summaries"],
            QueryType.REGULATORY_COMPLIANCE: ["sec_filings", "form_d_filings", "fund_reports"],
            QueryType.FINANCIAL_METRICS: ["sec_filings", "fund_reports", "insider_reports"],
            QueryType.GENERAL: ["sec_filings", "cftc_summaries", "market_events"]
        }
        
        collections = base_collections.get(query_type, ["sec_filings"])
        
        if include_cross_dataset:
            # Add additional collections for cross-dataset analysis
            additional_collections = ["market_events", "risk_assessments", "fund_reports"]
            for col in additional_collections:
                if col not in collections:
                    collections.append(col)
        
        # Filter to only existing collections
        existing_collections = self.vector_db_manager.db.list_collections()
        return [col for col in collections if col in existing_collections]
    
    def _build_enhanced_context(self, 
                               search_results: List[SearchResult],
                               query_type: QueryType) -> str:
        """Build intelligent context from search results"""
        
        if not search_results:
            return "No relevant information found."
        
        # Group results by source
        results_by_source = {}
        for result in search_results:
            source = result.source_collection
            if source not in results_by_source:
                results_by_source[source] = []
            results_by_source[source].append(result)
        
        context_parts = []
        
        # Add query-type specific context introduction
        context_parts.append(self._get_context_introduction(query_type))
        
        # Add information from each source
        for source, source_results in results_by_source.items():
            if source_results:
                source_context = self._build_source_context(source, source_results)
                context_parts.append(source_context)
        
        # Add cross-references if multiple sources
        if len(results_by_source) > 1:
            cross_refs = self._identify_cross_references(search_results)
            if cross_refs:
                context_parts.append(f"\nCross-dataset correlations:\n{cross_refs}")
        
        # Add confidence and relevance notes
        high_confidence_results = [r for r in search_results if r.similarity_score > 0.8]
        if high_confidence_results:
            context_parts.append(f"\nNote: {len(high_confidence_results)} highly relevant sources identified.")
        
        return "\n\n".join(context_parts)
    
    def _get_context_introduction(self, query_type: QueryType) -> str:
        """Get appropriate context introduction based on query type"""
        introductions = {
            QueryType.COMPANY_ANALYSIS: "Based on available SEC filings and regulatory data:",
            QueryType.MARKET_TRENDS: "Based on market data and trading information:",
            QueryType.RISK_ASSESSMENT: "Based on risk factors and regulatory filings:",
            QueryType.REGULATORY_COMPLIANCE: "Based on regulatory filings and compliance data:",
            QueryType.FINANCIAL_METRICS: "Based on financial reports and filings:",
            QueryType.GENERAL: "Based on available financial and regulatory data:"
        }
        return introductions.get(query_type, "Based on available data:")
    
    def _build_source_context(self, source: str, results: List[SearchResult]) -> str:
        """Build context section for a specific data source"""
        source_names = {
            "sec_filings": "SEC Filings",
            "cftc_summaries": "CFTC Market Data", 
            "insider_reports": "Insider Trading Data",
            "form_d_filings": "Form D Filings",
            "fund_reports": "Fund Reports",
            "market_events": "Market Events",
            "risk_assessments": "Risk Assessments"
        }
        
        source_name = source_names.get(source, source.replace("_", " ").title())
        context_items = []
        
        for result in results[:3]:  # Limit to top 3 results per source
            # Extract key information
            content_preview = result.content[:300] + "..." if len(result.content) > 300 else result.content
            
            # Add metadata context if available
            metadata_context = ""
            if result.metadata:
                if 'filing_date' in result.metadata:
                    metadata_context += f" (Filed: {result.metadata['filing_date']})"
                if 'company_name' in result.metadata:
                    metadata_context += f" - {result.metadata['company_name']}"
                if 'section' in result.metadata:
                    metadata_context += f" [{result.metadata['section']}]"
            
            context_items.append(f"{content_preview}{metadata_context}")
        
        return f"{source_name}:\n" + "\n\n".join(f"• {item}" for item in context_items)
    
    def _identify_cross_references(self, results: List[SearchResult]) -> str:
        """Identify correlations between different data sources"""
        correlations = []
        
        # Extract entities and dates from results
        entities = {}
        dates = {}
        
        for result in results:
            source = result.source_collection
            
            # Extract companies
            if 'company_name' in result.metadata:
                company = result.metadata['company_name']
                if company not in entities:
                    entities[company] = []
                entities[company].append(source)
            
            # Extract dates
            if 'filing_date' in result.metadata:
                date = result.metadata['filing_date']
                if date not in dates:
                    dates[date] = []
                dates[date].append(source)
        
        # Find overlapping entities
        for entity, sources in entities.items():
            if len(set(sources)) > 1:
                correlations.append(f"• {entity} appears in {', '.join(set(sources))}")
        
        # Find temporal correlations
        for date, sources in dates.items():
            if len(set(sources)) > 1:
                correlations.append(f"• Multiple filings on {date}: {', '.join(set(sources))}")
        
        return "\n".join(correlations[:5])  # Limit to top 5 correlations
    
    async def _generate_response(self, 
                                query: str,
                                context: str,
                                query_type: QueryType,
                                search_results: List[SearchResult]) -> str:
        """Generate response using LLM with enhanced context"""
        
        # Build comprehensive prompt
        prompt = self._build_enhanced_prompt(query, context, query_type, search_results)
        
        try:
            # Use async if enabled
            if self.enable_async:
                response = await self._async_ollama_chat(prompt)
            else:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                response = response['message']['content']
            
            return response
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            return f"I found relevant information but encountered an error generating the response: {str(e)}"
    
    def _build_enhanced_prompt(self, 
                              query: str,
                              context: str,
                              query_type: QueryType,
                              search_results: List[SearchResult]) -> str:
        """Build enhanced prompt with query-specific instructions"""
        
        base_instructions = """
        You are Raven, an expert financial data assistant with access to comprehensive regulatory and market data.
        Your goal is to provide accurate, insightful, and actionable financial analysis.
        
        Guidelines:
        1. Base your response on the provided context data
        2. Cite specific sources when making claims
        3. Highlight important risk factors or regulatory considerations
        4. Provide quantitative data when available
        5. Explain complex financial concepts clearly
        6. Note any limitations in the available data
        """
        
        # Add query-type specific instructions
        type_instructions = {
            QueryType.COMPANY_ANALYSIS: """
            For company analysis:
            - Provide comprehensive business overview
            - Highlight key financial metrics and trends
            - Identify major risk factors
            - Compare to industry context when possible
            """,
            QueryType.MARKET_TRENDS: """
            For market trend analysis:
            - Identify key patterns and movements
            - Provide statistical insights when available
            - Explain potential market drivers
            - Highlight any unusual activity or anomalies
            """,
            QueryType.RISK_ASSESSMENT: """
            For risk assessment:
            - Categorize risks by type (credit, market, operational, etc.)
            - Assess severity and likelihood
            - Provide risk mitigation recommendations
            - Consider regulatory implications
            """
        }
        
        specific_instructions = type_instructions.get(query_type, "")
        
        # Build confidence indicators
        high_confidence_sources = len([r for r in search_results if r.similarity_score > 0.8])
        confidence_note = f"\nNote: Response based on {len(search_results)} sources, {high_confidence_sources} highly relevant."
        
        prompt = f"""
        {base_instructions}
        {specific_instructions}
        
        Context Information:
        {context}
        
        User Query: {query}
        
        Please provide a comprehensive response based on the context information above.
        {confidence_note}
        
        Response:
        """
        
        return prompt
    
    async def _async_ollama_chat(self, prompt: str) -> str:
        """Async wrapper for Ollama chat"""
        loop = asyncio.get_event_loop()
        
        def sync_chat():
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        
        with ThreadPoolExecutor(max_workers=1) as executor:
            response = await loop.run_in_executor(executor, sync_chat)
            return response
    
    def _calculate_confidence_score(self, 
                                   search_results: List[SearchResult],
                                   context: str) -> float:
        """Calculate confidence score for the response"""
        if not search_results:
            return 0.0
        
        # Base score from search result quality
        avg_similarity = np.mean([result.similarity_score for result in search_results])
        high_quality_results = len([r for r in search_results if r.similarity_score > 0.7])
        
        # Context quality score
        context_score = min(1.0, len(context) / 1000)  # Normalize by context length
        
        # Diversity score (multiple sources)
        unique_sources = len(set(result.source_collection for result in search_results))
        diversity_score = min(1.0, unique_sources / 3)  # Normalize by expected source count
        
        # Combine scores
        confidence = (avg_similarity * 0.5 + 
                     (high_quality_results / len(search_results)) * 0.3 +
                     context_score * 0.1 +
                     diversity_score * 0.1)
        
        return min(1.0, confidence)
    
    def _generate_cache_key(self, query: str, context_filters: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for query and filters"""
        combined = f"{query}_{json.dumps(context_filters, sort_keys=True) if context_filters else ''}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _cache_response(self, cache_key: str, response: RAGResponse):
        """Cache response with size limit"""
        if len(self.response_cache) >= self.cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.response_cache))
            del self.response_cache[oldest_key]
        
        self.response_cache[cache_key] = response
    
    def _update_metrics(self, processing_time: float, success: bool):
        """Update performance metrics"""
        self.metrics["total_queries"] += 1
        
        if success:
            self.metrics["successful_queries"] += 1
        
        # Update rolling average
        current_avg = self.metrics["avg_response_time"]
        total_queries = self.metrics["total_queries"]
        self.metrics["avg_response_time"] = ((current_avg * (total_queries - 1)) + processing_time) / total_queries
    
    def add_documents_to_index(self, 
                              documents: List[Tuple[str, DocumentType, Dict[str, Any]]],
                              batch_size: int = 10) -> Dict[str, Any]:
        """
        Add new documents to the vector index
        
        Args:
            documents: List of (content, document_type, metadata) tuples
            batch_size: Batch size for processing
            
        Returns:
            Processing statistics
        """
        try:
            # Process documents in batches
            total_chunks = 0
            processing_errors = []
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                for content, doc_type, metadata in batch:
                    try:
                        # Process document into chunks
                        result = self.document_processor.process_document(content, doc_type, metadata)
                        
                        # Generate embeddings for chunks
                        chunk_texts = [chunk.content for chunk in result.chunks]
                        if chunk_texts:
                            embeddings = self.embedding_service.embed_financial_documents(chunk_texts)
                            
                            # Determine target collection
                            collection_name = self._get_collection_for_document_type(doc_type)
                            
                            # Add to vector database
                            chunk_ids = [chunk.chunk_id for chunk in result.chunks]
                            chunk_metadatas = [chunk.metadata for chunk in result.chunks]
                            
                            success = self.vector_db_manager.db.add_documents(
                                collection_name=collection_name,
                                documents=chunk_texts,
                                metadatas=chunk_metadatas,
                                ids=chunk_ids,
                                embeddings=embeddings.tolist()
                            )
                            
                            if success:
                                total_chunks += len(result.chunks)
                            else:
                                processing_errors.append(f"Failed to add document to {collection_name}")
                        
                    except Exception as e:
                        error_msg = f"Failed to process document: {str(e)}"
                        logger.error(error_msg)
                        processing_errors.append(error_msg)
            
            return {
                "documents_processed": len(documents),
                "total_chunks_added": total_chunks,
                "errors": processing_errors,
                "success": len(processing_errors) == 0
            }
            
        except Exception as e:
            logger.error(f"Batch document processing failed: {str(e)}")
            return {
                "documents_processed": 0,
                "total_chunks_added": 0,
                "errors": [str(e)],
                "success": False
            }
    
    def _get_collection_for_document_type(self, doc_type: DocumentType) -> str:
        """Map document type to vector collection"""
        mapping = {
            DocumentType.SEC_10K: "sec_filings",
            DocumentType.SEC_10Q: "sec_filings", 
            DocumentType.SEC_8K: "sec_filings",
            DocumentType.SEC_INSIDER: "insider_reports",
            DocumentType.FORM_13F: "form_d_filings",
            DocumentType.FORM_D: "form_d_filings",
            DocumentType.N_MFP: "fund_reports",
            DocumentType.N_CEN: "fund_reports",
            DocumentType.N_PORT: "fund_reports",
            DocumentType.CFTC_SWAP: "cftc_summaries",
            DocumentType.EXCHANGE_DATA: "market_events"
        }
        return mapping.get(doc_type, "sec_filings")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Vector database stats
            db_stats = self.vector_db_manager.get_system_stats()
            
            # Embedding service stats
            embedding_stats = self.embedding_service.get_embedding_stats()
            
            # System metrics
            cache_hit_rate = (self.metrics["cache_hits"] / max(1, self.metrics["total_queries"])) * 100
            success_rate = (self.metrics["successful_queries"] / max(1, self.metrics["total_queries"])) * 100
            
            return {
                "status": "operational",
                "vector_database": db_stats,
                "embedding_service": embedding_stats,
                "performance_metrics": {
                    **self.metrics,
                    "cache_hit_rate_percent": cache_hit_rate,
                    "success_rate_percent": success_rate
                },
                "cache_status": {
                    "cached_responses": len(self.response_cache),
                    "cache_size_limit": self.cache_size
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def clear_cache(self):
        """Clear response cache"""
        self.response_cache.clear()
        logger.info("Response cache cleared")
    
    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'db_session'):
                self.db_session.close()
        except Exception:
            pass


# Convenience function for backward compatibility
def query_raven(query_text: str, messages: Optional[List[Dict]] = None) -> str:
    """
    Enhanced query function that maintains compatibility with existing interface
    while providing vector-enhanced capabilities
    """
    try:
        # Initialize enhanced RAG system (cached for efficiency)
        if not hasattr(query_raven, '_rag_system'):
            query_raven._rag_system = EnhancedRAGSystem()
        
        rag_system = query_raven._rag_system
        
        # Process query using enhanced system
        import asyncio
        
        async def process_async():
            return await rag_system.process_query(query_text)
        
        # Run async query
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        response = loop.run_until_complete(process_async())
        
        # Return formatted response
        return f"{response.answer}\n\nSources: {len(response.sources)} relevant documents found.\nConfidence: {response.confidence_score:.1%}\nProcessing time: {response.processing_time:.2f}s"
        
    except Exception as e:
        logger.error(f"Enhanced query processing failed, falling back to simple response: {str(e)}")
        return f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question."


# Initialize global RAG system instance
_global_rag_system = None

def get_rag_system() -> EnhancedRAGSystem:
    """Get or create global RAG system instance"""
    global _global_rag_system
    if _global_rag_system is None:
        _global_rag_system = EnhancedRAGSystem()
    return _global_rag_system

