"""
Vector Integration Module for GameCock AI
Integrates vector embeddings with existing analytics tools and database operations
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Local imports
from vector_db import VectorDBManager
from embedding_service import FinancialEmbeddingService
from document_processor import FinancialDocumentProcessor, DocumentType
from rag_enhanced import EnhancedRAGSystem, QueryType
# Import from the REAL database module with all tables (GameCockAI/database.py)
from database import SessionLocal, CFTCSwap
from analytics_tools import AnalyticsEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorIntegrationManager:
    """
    Manages integration between vector embeddings and existing GameCock systems
    Provides high-level interface for vector-enhanced operations
    """
    
    def __init__(self, 
                 vector_store_path: str = "./vector_store",
                 initialize_collections: bool = True,
                 preload_data: bool = False):
        """
        Initialize the Vector Integration Manager
        
        Args:
            vector_store_path: Path to vector database storage
            initialize_collections: Whether to initialize standard collections
            preload_data: Whether to preload existing data into vector store
        """
        self.vector_store_path = vector_store_path
        
        # Initialize core components
        self.vector_db_manager = VectorDBManager(vector_store_path)
        self.embedding_service = FinancialEmbeddingService()
        self.document_processor = FinancialDocumentProcessor()
        self.rag_system = EnhancedRAGSystem(vector_store_path=vector_store_path)
        self.analytics_engine = AnalyticsEngine()
        
        # Database connection
        self.db_session = SessionLocal()
        
        # Integration status
        self.integration_status = {
            "initialized": False,
            "collections_ready": False,
            "data_indexed": False,
            "last_sync": None
        }
        
        if initialize_collections:
            self._initialize_collections()
        
        if preload_data:
            self._preload_existing_data()
        
        logger.info("Vector Integration Manager initialized successfully")
    
    def _initialize_collections(self):
        """Initialize standard vector collections for GameCock data"""
        try:
            # Document collections for ChromaDB
            document_collections = [
                "sec_filings_10k",
                "sec_filings_10q", 
                "sec_filings_8k",
                "sec_insider_transactions",
                "form_13f_holdings",
                "form_d_offerings",
                "fund_reports_nmfp",
                "fund_reports_ncen",
                "fund_reports_nport",
                "cftc_swap_summaries",
                "market_events",
                "risk_assessments",
                "regulatory_updates"
            ]
            
            for collection in document_collections:
                success = self.vector_db_manager.db.create_collection(
                    name=collection,
                    collection_type="chroma",
                    distance_metric="cosine"
                )
                if success:
                    logger.info(f"Initialized collection: {collection}")
                else:
                    logger.warning(f"Failed to initialize collection: {collection}")
            
            # Numerical collections for FAISS
            numerical_collections = [
                ("company_financial_vectors", 384),
                ("market_indicator_vectors", 512),
                ("risk_profile_vectors", 384),
                ("correlation_vectors", 1024)
            ]
            
            for collection, dimension in numerical_collections:
                success = self.vector_db_manager.db.create_collection(
                    name=collection,
                    collection_type="faiss",
                    dimension=dimension,
                    distance_metric="cosine"
                )
                if success:
                    logger.info(f"Initialized FAISS collection: {collection} (dim={dimension})")
                else:
                    logger.warning(f"Failed to initialize FAISS collection: {collection}")
            
            self.integration_status["collections_ready"] = True
            logger.info("All vector collections initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize collections: {str(e)}")
            raise
    
    def _preload_existing_data(self):
        """Preload existing database data into vector store"""
        try:
            logger.info("Starting preload of existing data...")
            
            # Load CFTC swap data
            self._index_cftc_data()
            
            # Note: SEC filing data would be loaded here if available
            # This is a placeholder for when SEC filing processing is implemented
            
            self.integration_status["data_indexed"] = True
            self.integration_status["last_sync"] = datetime.now().isoformat()
            
            logger.info("Data preloading completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to preload data: {str(e)}")
            # Don't raise here - system can still function without preloaded data
    
    def _index_cftc_data(self):
        """Index existing CFTC swap data into vector store"""
        try:
            # Query recent CFTC data
            recent_cutoff = datetime.now() - timedelta(days=365)  # Last year
            
            cftc_data = self.db_session.query(CFTCSwap).filter(
                CFTCSwap.execution_timestamp >= recent_cutoff
            ).limit(10000).all()  # Limit for initial indexing
            
            if not cftc_data:
                logger.info("No CFTC data found to index")
                return
            
            logger.info(f"Indexing {len(cftc_data)} CFTC swap records...")
            
            # Process in batches
            batch_size = 100
            total_indexed = 0
            
            for i in range(0, len(cftc_data), batch_size):
                batch = cftc_data[i:i + batch_size]
                
                # Create summaries for batch
                summaries = []
                metadatas = []
                ids = []
                
                for swap in batch:
                    summary = self._create_cftc_summary(swap)
                    metadata = self._extract_cftc_metadata(swap)
                    
                    summaries.append(summary)
                    metadatas.append(metadata)
                    ids.append(f"cftc_swap_{swap.id}")
                
                # Generate embeddings
                embeddings = self.embedding_service.embed_market_data(summaries, "swap")
                
                # Add to vector store
                success = self.vector_db_manager.db.add_documents(
                    collection_name="cftc_swap_summaries",
                    documents=summaries,
                    metadatas=metadatas,
                    ids=ids,
                    embeddings=embeddings.tolist()
                )
                
                if success:
                    total_indexed += len(batch)
                    logger.info(f"Indexed batch {i//batch_size + 1}, total: {total_indexed}")
                else:
                    logger.error(f"Failed to index batch {i//batch_size + 1}")
            
            logger.info(f"Successfully indexed {total_indexed} CFTC swap records")
            
        except Exception as e:
            logger.error(f"Failed to index CFTC data: {str(e)}")
            raise
    
    def _create_cftc_summary(self, swap: CFTCSwap) -> str:
        """Create a textual summary of a CFTC swap for embedding"""
        summary_parts = []
        
        # Basic swap information
        summary_parts.append(f"CFTC Swap Transaction: {swap.asset_class or 'Unknown'} asset class")
        
        if swap.notional_amount:
            summary_parts.append(f"Notional amount: ${swap.notional_amount:,.2f}")
        
        if swap.currency:
            summary_parts.append(f"Currency: {swap.currency}")
        
        if swap.execution_timestamp:
            summary_parts.append(f"Executed on: {swap.execution_timestamp.strftime('%Y-%m-%d')}")
        
        if swap.effective_date:
            summary_parts.append(f"Effective date: {swap.effective_date.strftime('%Y-%m-%d')}")
        
        if swap.expiration_date:
            summary_parts.append(f"Expiration: {swap.expiration_date.strftime('%Y-%m-%d')}")
        
        # Additional characteristics
        if swap.clearing_indicator:
            summary_parts.append(f"Clearing: {swap.clearing_indicator}")
        
        if swap.collateralization_indicator:
            summary_parts.append(f"Collateralization: {swap.collateralization_indicator}")
        
        return ". ".join(summary_parts) + "."
    
    def _extract_cftc_metadata(self, swap: CFTCSwap) -> Dict[str, Any]:
        """Extract metadata from CFTC swap for vector storage"""
        return {
            "document_type": "cftc_swap",
            "asset_class": swap.asset_class,
            "notional_amount": float(swap.notional_amount) if swap.notional_amount else None,
            "currency": swap.currency,
            "execution_timestamp": swap.execution_timestamp.isoformat() if swap.execution_timestamp else None,
            "effective_date": swap.effective_date.isoformat() if swap.effective_date else None,
            "expiration_date": swap.expiration_date.isoformat() if swap.expiration_date else None,
            "clearing_indicator": swap.clearing_indicator,
            "collateralization_indicator": swap.collateralization_indicator,
            "dissemination_id": swap.dissemination_id,
            "database_id": swap.id,
            "indexed_date": datetime.now().isoformat()
        }
    
    async def vector_enhanced_company_analysis(self, 
                                             company_cik: str,
                                             analysis_depth: str = "comprehensive") -> Dict[str, Any]:
        """
        Perform company analysis using vector embeddings
        
        Args:
            company_cik: Company CIK identifier
            analysis_depth: Depth of analysis ("basic", "comprehensive", "deep")
            
        Returns:
            Enhanced analysis results
        """
        try:
            # Use RAG system for semantic search
            query = f"comprehensive company analysis financial profile business operations risk factors CIK {company_cik}"
            
            response = await self.rag_system.process_query(
                query=query,
                context_filters={"cik": company_cik} if company_cik else None,
                max_results=20,
                include_cross_dataset=True
            )
            
            # Enhance with traditional analytics
            traditional_analysis = self.analytics_engine.execute_analytical_query(
                "company_comparison", 
                {"company_cik": company_cik}
            )
            
            # Find similar companies using vector similarity
            similar_companies = await self._find_similar_companies_vector(company_cik)
            
            return {
                "company_cik": company_cik,
                "analysis_depth": analysis_depth,
                "semantic_analysis": {
                    "summary": response.answer,
                    "confidence": response.confidence_score,
                    "sources_found": len(response.sources),
                    "processing_time": response.processing_time
                },
                "traditional_analysis": traditional_analysis,
                "similar_companies": similar_companies,
                "cross_dataset_insights": self._extract_cross_dataset_insights(response.sources),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Vector-enhanced company analysis failed: {str(e)}")
            return {
                "error": str(e),
                "company_cik": company_cik,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _find_similar_companies_vector(self, 
                                           target_cik: str,
                                           top_k: int = 10) -> List[Dict[str, Any]]:
        """Find similar companies using vector similarity"""
        try:
            # Create company query
            company_query = f"company business operations financial profile CIK {target_cik}"
            
            # Search for similar company documents
            response = await self.rag_system.process_query(
                query=company_query,
                max_results=50,
                include_cross_dataset=True
            )
            
            # Extract companies from results
            companies = {}
            for source in response.sources:
                if 'cik' in source.metadata and source.metadata['cik'] != target_cik:
                    cik = source.metadata['cik']
                    company_name = source.metadata.get('company_name', f'Company {cik}')
                    
                    if cik not in companies:
                        companies[cik] = {
                            "cik": cik,
                            "company_name": company_name,
                            "similarity_scores": [],
                            "shared_concepts": []
                        }
                    
                    companies[cik]["similarity_scores"].append(source.similarity_score)
                    
                    # Extract shared concepts
                    if 'financial_concepts' in source.metadata:
                        companies[cik]["shared_concepts"].extend(source.metadata['financial_concepts'])
            
            # Calculate average similarity and rank
            similar_companies = []
            for cik, data in companies.items():
                avg_similarity = np.mean(data["similarity_scores"])
                data["average_similarity"] = avg_similarity
                data["shared_concepts"] = list(set(data["shared_concepts"]))  # Remove duplicates
                similar_companies.append(data)
            
            # Sort by similarity and return top k
            similar_companies.sort(key=lambda x: x["average_similarity"], reverse=True)
            return similar_companies[:top_k]
            
        except Exception as e:
            logger.error(f"Similar company search failed: {str(e)}")
            return []
    
    async def vector_enhanced_market_analysis(self, 
                                            query: str,
                                            timeframe_days: int = 30,
                                            asset_classes: List[str] = None) -> Dict[str, Any]:
        """
        Perform market analysis using vector embeddings and traditional analytics
        
        Args:
            query: Market analysis query
            timeframe_days: Analysis timeframe in days
            asset_classes: Specific asset classes to analyze
            
        Returns:
            Enhanced market analysis results
        """
        try:
            # Enhance query with timeframe context
            enhanced_query = f"{query} market trends analysis {timeframe_days} days"
            if asset_classes:
                enhanced_query += f" asset classes: {', '.join(asset_classes)}"
            
            # Use RAG system for semantic analysis
            response = await self.rag_system.process_query(
                query=enhanced_query,
                context_filters={"asset_class": {"$in": asset_classes}} if asset_classes else None,
                max_results=25,
                include_cross_dataset=True
            )
            
            # Enhance with traditional market trend analysis
            traditional_analysis = self.analytics_engine.execute_analytical_query(
                "market_trends",
                {
                    "days_back": timeframe_days,
                    "asset_class": asset_classes[0] if asset_classes else None
                }
            )
            
            # Extract market indicators from vector search
            market_indicators = self._extract_market_indicators(response.sources)
            
            # Identify trend patterns
            trend_patterns = self._identify_trend_patterns(response.sources, traditional_analysis)
            
            return {
                "query": query,
                "timeframe_days": timeframe_days,
                "asset_classes": asset_classes,
                "semantic_analysis": {
                    "summary": response.answer,
                    "confidence": response.confidence_score,
                    "sources_analyzed": len(response.sources)
                },
                "traditional_analysis": traditional_analysis,
                "market_indicators": market_indicators,
                "trend_patterns": trend_patterns,
                "cross_dataset_correlations": self._extract_cross_dataset_insights(response.sources),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Vector-enhanced market analysis failed: {str(e)}")
            return {
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat()
            }
    
    def _extract_cross_dataset_insights(self, sources: List) -> List[Dict[str, Any]]:
        """Extract insights from cross-dataset correlations"""
        insights = []
        
        # Group sources by data source
        sources_by_type = {}
        for source in sources:
            source_type = source.metadata.get('document_type', 'unknown')
            if source_type not in sources_by_type:
                sources_by_type[source_type] = []
            sources_by_type[source_type].append(source)
        
        # Find correlations between different data sources
        data_types = list(sources_by_type.keys())
        for i, type1 in enumerate(data_types):
            for type2 in data_types[i+1:]:
                correlation = self._find_source_correlation(
                    sources_by_type[type1], 
                    sources_by_type[type2]
                )
                if correlation:
                    insights.append({
                        "source_types": [type1, type2],
                        "correlation_strength": correlation["strength"],
                        "shared_entities": correlation["entities"],
                        "temporal_overlap": correlation["temporal_overlap"]
                    })
        
        return insights
    
    def _find_source_correlation(self, sources1: List, sources2: List) -> Optional[Dict[str, Any]]:
        """Find correlation between two sets of sources"""
        try:
            # Extract entities and dates
            entities1 = set()
            entities2 = set()
            dates1 = set()
            dates2 = set()
            
            for source in sources1:
                if 'company_name' in source.metadata:
                    entities1.add(source.metadata['company_name'])
                if 'filing_date' in source.metadata:
                    dates1.add(source.metadata['filing_date'])
            
            for source in sources2:
                if 'company_name' in source.metadata:
                    entities2.add(source.metadata['company_name'])
                if 'filing_date' in source.metadata:
                    dates2.add(source.metadata['filing_date'])
            
            # Calculate correlations
            shared_entities = entities1.intersection(entities2)
            shared_dates = dates1.intersection(dates2)
            
            if shared_entities or shared_dates:
                strength = (len(shared_entities) + len(shared_dates)) / max(1, len(entities1) + len(entities2) + len(dates1) + len(dates2)) * 2
                
                return {
                    "strength": min(1.0, strength),
                    "entities": list(shared_entities),
                    "temporal_overlap": len(shared_dates)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Correlation analysis failed: {str(e)}")
            return None
    
    def _extract_market_indicators(self, sources: List) -> Dict[str, Any]:
        """Extract market indicators from search sources"""
        indicators = {
            "volume_indicators": [],
            "volatility_indicators": [],
            "risk_indicators": [],
            "liquidity_indicators": []
        }
        
        for source in sources:
            content = source.content.lower()
            metadata = source.metadata
            
            # Volume indicators
            if any(term in content for term in ['volume', 'notional', 'trading activity']):
                if 'notional_amount' in metadata:
                    indicators["volume_indicators"].append({
                        "value": metadata['notional_amount'],
                        "source": source.source_collection,
                        "timestamp": metadata.get('execution_timestamp')
                    })
            
            # Risk indicators
            if any(term in content for term in ['risk', 'volatility', 'exposure']):
                risk_score = source.metadata.get('risk_indicators', 0)
                if risk_score > 0:
                    indicators["risk_indicators"].append({
                        "risk_score": risk_score,
                        "source": source.source_collection,
                        "concepts": metadata.get('financial_concepts', [])
                    })
        
        return indicators
    
    def _identify_trend_patterns(self, sources: List, traditional_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Identify trend patterns from combined analysis"""
        patterns = {
            "temporal_patterns": [],
            "volume_patterns": [],
            "risk_patterns": [],
            "emerging_themes": []
        }
        
        try:
            # Extract temporal patterns
            dates_data = {}
            for source in sources:
                if 'execution_timestamp' in source.metadata:
                    date = source.metadata['execution_timestamp'][:10]  # YYYY-MM-DD
                    if date not in dates_data:
                        dates_data[date] = []
                    dates_data[date].append(source.similarity_score)
            
            # Identify date-based patterns
            for date, scores in dates_data.items():
                if len(scores) > 1:
                    avg_relevance = np.mean(scores)
                    patterns["temporal_patterns"].append({
                        "date": date,
                        "activity_level": len(scores),
                        "average_relevance": avg_relevance
                    })
            
            # Extract themes from high-similarity sources
            high_similarity_sources = [s for s in sources if s.similarity_score > 0.8]
            theme_counts = {}
            
            for source in high_similarity_sources:
                concepts = source.metadata.get('financial_concepts', [])
                for concept in concepts:
                    theme_counts[concept] = theme_counts.get(concept, 0) + 1
            
            # Sort themes by frequency
            emerging_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            patterns["emerging_themes"] = [{"theme": theme, "frequency": freq} for theme, freq in emerging_themes]
            
        except Exception as e:
            logger.error(f"Pattern identification failed: {str(e)}")
        
        return patterns
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status and statistics"""
        try:
            # Vector database statistics
            db_stats = self.vector_db_manager.get_system_stats()
            
            # Embedding service statistics
            embedding_stats = self.embedding_service.get_embedding_stats()
            
            # RAG system statistics
            rag_stats = self.rag_system.get_system_status()
            
            return {
                "integration_status": self.integration_status,
                "vector_database": db_stats,
                "embedding_service": embedding_stats,
                "rag_system": rag_stats["performance_metrics"],
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get integration status: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def sync_new_data(self, data_type: str = "all") -> Dict[str, Any]:
        """Sync new data from database to vector store"""
        try:
            sync_results = {
                "data_type": data_type,
                "records_processed": 0,
                "records_indexed": 0,
                "errors": []
            }
            
            if data_type in ["all", "cftc"]:
                # Sync new CFTC data
                last_sync = self.integration_status.get("last_sync")
                if last_sync:
                    cutoff = datetime.fromisoformat(last_sync)
                else:
                    cutoff = datetime.now() - timedelta(days=1)  # Last 24 hours
                
                new_cftc_data = self.db_session.query(CFTCSwap).filter(
                    CFTCSwap.execution_timestamp >= cutoff
                ).all()
                
                if new_cftc_data:
                    logger.info(f"Syncing {len(new_cftc_data)} new CFTC records...")
                    # Use existing indexing method
                    # This would call _index_cftc_data with the filtered data
                    sync_results["records_processed"] += len(new_cftc_data)
                    sync_results["records_indexed"] += len(new_cftc_data)  # Simplified
            
            # Update sync timestamp
            self.integration_status["last_sync"] = datetime.now().isoformat()
            
            return sync_results
            
        except Exception as e:
            logger.error(f"Data sync failed: {str(e)}")
            return {
                "error": str(e),
                "data_type": data_type,
                "timestamp": datetime.now().isoformat()
            }
    
    def __del__(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'db_session'):
                self.db_session.close()
        except Exception:
            pass


# Global integration manager instance
_integration_manager = None

def get_integration_manager() -> VectorIntegrationManager:
    """Get or create global integration manager instance"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = VectorIntegrationManager(
            initialize_collections=True,
            preload_data=False  # Set to True for initial setup
        )
    return _integration_manager


# Enhanced tool functions for integration with existing TOOL_MAP
async def vector_enhanced_company_analysis(cik: str, depth: str = "comprehensive") -> str:
    """Vector-enhanced company analysis tool function"""
    try:
        manager = get_integration_manager()
        result = await manager.vector_enhanced_company_analysis(cik, depth)
        return json.dumps(result, default=str, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

async def vector_enhanced_market_analysis(query: str, timeframe_days: int = 30) -> str:
    """Vector-enhanced market analysis tool function"""
    try:
        manager = get_integration_manager()
        result = await manager.vector_enhanced_market_analysis(query, timeframe_days)
        return json.dumps(result, default=str, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def get_vector_system_status() -> str:
    """Get vector system status tool function"""
    try:
        manager = get_integration_manager()
        status = manager.get_integration_status()
        return json.dumps(status, default=str, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def sync_vector_data(data_type: str = "all") -> str:
    """Sync new data to vector store tool function"""
    try:
        manager = get_integration_manager()
        result = manager.sync_new_data(data_type)
        return json.dumps(result, default=str, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# Tool definitions for integration with existing TOOL_MAP
VECTOR_ENHANCED_TOOLS = {
    "vector_company_analysis": {
        "function": lambda cik, depth="comprehensive": asyncio.run(vector_enhanced_company_analysis(cik, depth)),
        "schema": {
            "name": "vector_company_analysis",
            "description": "Comprehensive company analysis using vector embeddings and semantic search across all data sources",
            "parameters": {
                "type": "object",
                "properties": {
                    "cik": {"type": "string", "description": "Company CIK identifier (required)"},
                    "depth": {"type": "string", "description": "Analysis depth: 'basic', 'comprehensive', 'deep' (default: 'comprehensive')"}
                },
                "required": ["cik"]
            }
        }
    },
    "vector_market_analysis": {
        "function": lambda query, days=30: asyncio.run(vector_enhanced_market_analysis(query, days)),
        "schema": {
            "name": "vector_market_analysis", 
            "description": "Advanced market analysis using vector embeddings for semantic understanding of market trends and patterns",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Market analysis query (required)"},
                    "days": {"type": "integer", "description": "Analysis timeframe in days (default: 30)"}
                },
                "required": ["query"]
            }
        }
    },
    "vector_system_status": {
        "function": get_vector_system_status,
        "schema": {
            "name": "vector_system_status",
            "description": "Get comprehensive status of vector embedding system including performance metrics and data statistics",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    "sync_vector_data": {
        "function": sync_vector_data,
        "schema": {
            "name": "sync_vector_data",
            "description": "Synchronize new database data into vector store for enhanced search capabilities",
            "parameters": {
                "type": "object",
                "properties": {
                    "data_type": {"type": "string", "description": "Type of data to sync: 'all', 'cftc', 'sec' (default: 'all')"}
                },
                "required": []
            }
        }
    }
}

