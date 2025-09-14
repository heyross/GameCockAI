"""
Database-First RAG System for GameCock AI
Implements proper database search workflow before falling back to LLM knowledge
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import text, and_, or_
from sqlalchemy.orm import Session
# Import from the REAL database module with all tables (GameCockAI/database.py)
from GameCockAI.database import SessionLocal
import ollama

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseFirstRAG:
    """
    RAG system that searches database first, then generates responses
    Implements proper workflow: Parse Intent → Search DB → Check Company → Offer Downloads
    """
    
    def __init__(self, model_name: str = 'raven-enhanced'):
        self.model_name = model_name
        self.intent_patterns = self._init_intent_patterns()
        self.table_mappings = self._init_table_mappings()
    
    def _init_intent_patterns(self) -> Dict[str, List[str]]:
        """Initialize patterns for intent recognition"""
        return {
            'company_filings': [
                r'(?i)\b(filings?|filed|reports?|sec)\b',
                r'(?i)\b(10-?k|8-?k|quarterly|annual)\b',
                r'(?i)\b(earnings|financial|statements?)\b'
            ],
            'insider_trading': [
                r'(?i)\b(insider|trading|bought|sold|purchase|sale)\b',
                r'(?i)\b(executives?|officers?|directors?)\b',
                r'(?i)\b(form\s*[345])\b'
            ],
            'institutional_holdings': [
                r'(?i)\b(13-?f|holdings?|institutional)\b',
                r'(?i)\b(mutual\s*funds?|hedge\s*funds?)\b',
                r'(?i)\b(portfolio|positions?)\b'
            ],
            'swaps_derivatives': [
                r'(?i)\b(swap|derivative|cftc)\b',
                r'(?i)\b(interest\s*rate|credit|commodity)\b',
                r'(?i)\b(notional|exposure)\b'
            ],
            'market_events': [
                r'(?i)\b(event|news|announcement)\b',
                r'(?i)\b(merger|acquisition|restructur)\b',
                r'(?i)\b(dividend|split|spinoff)\b'
            ]
        }
    
    def _init_table_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Map intents to database tables and search strategies - using actual existing tables"""
        return {
            'company_filings': {
                'primary_tables': ['cftc_swap_data'],  # Only table that exists currently
                'company_fields': [],
                'searchable_fields': ['asset_class', 'action_type', 'product_name'],
                'date_fields': ['event_timestamp'],
                'data_needed': ['SEC 8-K filings', 'SEC 10-K filings', 'SEC submissions'],
                'download_sources': ['SEC EDGAR']
            },
            'insider_trading': {
                'primary_tables': [],  # No tables exist yet
                'company_fields': [],
                'searchable_fields': [],
                'date_fields': [],
                'data_needed': ['SEC insider trading data', 'Form 3/4/5 filings'],
                'download_sources': ['SEC insider transactions data sets']
            },
            'institutional_holdings': {
                'primary_tables': [],  # No tables exist yet
                'company_fields': [],
                'searchable_fields': [],
                'date_fields': [],
                'data_needed': ['Form 13F institutional holdings'],
                'download_sources': ['SEC Form 13F data sets']
            },
            'swaps_derivatives': {
                'primary_tables': ['cftc_swap_data'],
                'company_fields': [],
                'searchable_fields': ['asset_class', 'action_type', 'product_name', 'cleared'],
                'date_fields': ['event_timestamp']
            }
        }
    
    def parse_query_intent(self, query: str) -> Tuple[str, List[str], Optional[str]]:
        """
        Parse user query to extract intent, keywords, and company references
        
        Returns:
            (intent, keywords, company_name)
        """
        # Extract company names (simple pattern - can be enhanced)
        company_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+(?:Inc|Corp|Company|Ltd|LLC))?)\.?\b'
        companies = re.findall(company_pattern, query)
        primary_company = companies[0] if companies else None
        
        # Determine intent
        query_lower = query.lower()
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query))
                score += matches
            intent_scores[intent] = score
        
        # Get primary intent (highest score, default to company_filings)
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])[0] if max(intent_scores.values()) > 0 else 'company_filings'
        
        # Extract keywords (filter out stop words and common terms)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'what', 'when', 'where', 'how', 'why', 'who'}
        keywords = [word for word in re.findall(r'\b\w+\b', query_lower) if word not in stop_words and len(word) > 2]
        
        logger.info(f"Query intent: {primary_intent}, Company: {primary_company}, Keywords: {keywords[:5]}")
        
        return primary_intent, keywords, primary_company
    
    def search_database_for_intent(self, intent: str, keywords: List[str], company_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Search database based on parsed intent
        
        Returns:
            Dictionary with search results and metadata
        """
        if intent not in self.table_mappings:
            return {"error": f"Unknown intent: {intent}"}
        
        mapping = self.table_mappings[intent]
        db = SessionLocal()
        
        try:
            results = {
                'intent': intent,
                'company_searched': company_name,
                'tables_searched': mapping['primary_tables'],
                'data_found': {},
                'company_data_available': False,
                'suggested_actions': []
            }
            
            # Search each table for this intent
            for table_name in mapping['primary_tables']:
                table_results = self._search_table(
                    db, table_name, mapping, keywords, company_name
                )
                if table_results['count'] > 0:
                    results['data_found'][table_name] = table_results
                    if company_name and table_results.get('company_matches', 0) > 0:
                        results['company_data_available'] = True
            
            # Generate suggestions if no company data found
            if company_name and not results['company_data_available']:
                results['suggested_actions'] = [
                    f"Add '{company_name}' to target companies",
                    f"Download {intent.replace('_', ' ')} data for {company_name}",
                    "Search for company CIK and ticker symbol"
                ]
            
            return results
            
        except Exception as e:
            logger.error(f"Database search error: {e}")
            return {"error": f"Database search failed: {str(e)}"}
        finally:
            db.close()
    
    def _search_table(self, db: Session, table_name: str, mapping: Dict, keywords: List[str], company_name: Optional[str]) -> Dict[str, Any]:
        """Search a specific table based on mapping configuration"""
        
        try:
            # Check if table exists first
            inspector = db.get_bind().dialect.get_table_names(db.get_bind())
            if table_name not in inspector:
                return {
                    'table': table_name,
                    'count': 0,
                    'company_matches': 0,
                    'sample_data': [],
                    'search_successful': False,
                    'error': f"Table {table_name} does not exist. Data needs to be loaded.",
                    'data_needed': mapping.get('data_needed', []),
                    'download_sources': mapping.get('download_sources', [])
                }
            
            # Build dynamic search query only if searchable fields exist
            search_conditions = []
            
            if mapping['searchable_fields']:
                keyword_conditions = []
                
                # Add keyword searches across searchable fields (SQLite uses LIKE, not ILIKE)
                for keyword in keywords[:3]:  # Limit to first 3 keywords
                    field_conditions = []
                    for field in mapping['searchable_fields']:
                        field_conditions.append(f"LOWER({field}) LIKE LOWER('%{keyword}%')")
                    if field_conditions:
                        keyword_conditions.append(f"({' OR '.join(field_conditions)})")
                
                if keyword_conditions:
                    search_conditions.append(f"({' AND '.join(keyword_conditions)})")
            
            # Construct final query
            base_query = f"SELECT COUNT(*) as total_count FROM {table_name}"
            if search_conditions:
                where_clause = ' AND '.join(search_conditions)
                count_query = f"{base_query} WHERE {where_clause}"
            else:
                count_query = base_query
            
            # Execute count query
            result = db.execute(text(count_query))
            total_count = result.scalar()
            
            # Get sample data if found
            sample_data = []
            
            if total_count > 0:
                sample_query = count_query.replace("COUNT(*) as total_count", "*") + " LIMIT 3"
                sample_result = db.execute(text(sample_query))
                sample_data = [dict(row) for row in sample_result]
            
            return {
                'table': table_name,
                'count': total_count,
                'company_matches': 0,  # Company matching not implemented for existing tables yet
                'sample_data': sample_data,
                'search_successful': True
            }
            
        except Exception as e:
            logger.warning(f"Search failed for table {table_name}: {e}")
            return {
                'table': table_name,
                'count': 0,
                'company_matches': 0,
                'sample_data': [],
                'search_successful': False,
                'error': str(e)
            }
    
    def generate_database_response(self, query: str, search_results: Dict[str, Any]) -> str:
        """
        Generate response based on database search results
        """
        if 'error' in search_results:
            return f"I encountered an error searching the database: {search_results['error']}"
        
        # Build context from search results
        context_parts = []
        
        context_parts.append(f"Query Intent: {search_results['intent'].replace('_', ' ').title()}")
        context_parts.append(f"Company: {search_results.get('company_searched', 'Not specified')}")
        context_parts.append(f"Tables Searched: {', '.join(search_results['tables_searched'])}")
        
        # Add data found
        if search_results['data_found']:
            context_parts.append("\nData Found:")
            for table, table_results in search_results['data_found'].items():
                context_parts.append(f"- {table}: {table_results['count']} records")
                if search_results['company_searched'] and table_results['company_matches'] > 0:
                    context_parts.append(f"  * {table_results['company_matches']} records for {search_results['company_searched']}")
                
                # Add sample data context
                if table_results['sample_data']:
                    context_parts.append(f"  * Sample data: {str(table_results['sample_data'][:2])}")
        else:
            context_parts.append("\nNo relevant data found in database.")
        
        # Add suggestions
        if search_results['suggested_actions']:
            context_parts.append(f"\nSuggested Actions:")
            for action in search_results['suggested_actions']:
                context_parts.append(f"- {action}")
        
        context = "\n".join(context_parts)
        
        # Generate AI response with database context
        prompt = f"""You are Raven, a financial data assistant. Based on the database search results below, provide a helpful response to the user's query.

Database Search Results:
{context}

User Query: {query}

Instructions:
1. If data was found, summarize what's available and offer to show specific details
2. If company-specific data is missing, explain what data we have and offer to help add the company to targets
3. If no relevant data exists, explain what would need to be downloaded to answer the query
4. Always be specific about what data sources were searched
5. Offer concrete next steps

Response:"""

        try:
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return self._generate_fallback_response(search_results)
    
    def _generate_fallback_response(self, search_results: Dict[str, Any]) -> str:
        """Generate a fallback response when AI is unavailable"""
        
        if not search_results['data_found']:
            if search_results['company_searched']:
                return f"""I searched our database for information about {search_results['company_searched']} but didn't find any relevant data in our {search_results['intent'].replace('_', ' ')} records.

To help answer your query, I can:
1. Add {search_results['company_searched']} to your target companies list
2. Download the relevant data from SEC/CFTC sources
3. Search for the company's CIK identifier

Would you like me to help with any of these steps?"""
            else:
                return f"I searched our {search_results['intent'].replace('_', ' ')} data but didn't find relevant information. Please specify a company name or provide more details about what you're looking for."
        
        # Data was found
        response_parts = [f"I found data in our database related to your {search_results['intent'].replace('_', ' ')} query:"]
        
        for table, results in search_results['data_found'].items():
            response_parts.append(f"• {table}: {results['count']} records")
            if search_results['company_searched'] and results['company_matches'] > 0:
                response_parts.append(f"  Including {results['company_matches']} records for {search_results['company_searched']}")
        
        response_parts.append("\nWould you like me to show you specific details from this data?")
        
        return "\n".join(response_parts)
    
    def query_database_first(self, query: str) -> str:
        """
        Main entry point: Database-first RAG query processing
        
        Workflow:
        1. Parse query intent and extract company/keywords
        2. Search database for relevant information
        3. Generate response based on found data
        4. Offer next steps if data is missing
        """
        try:
            # Step 1: Parse the query
            intent, keywords, company_name = self.parse_query_intent(query)
            
            # Step 2: Search database
            search_results = self.search_database_for_intent(intent, keywords, company_name)
            
            # Step 3: Generate response
            response = self.generate_database_response(query, search_results)
            
            return response
            
        except Exception as e:
            logger.error(f"Database-first RAG failed: {e}")
            return f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question or contact support."


# Global instance
_database_rag_system = None

def get_database_rag_system():
    """Get or create the global database RAG system"""
    global _database_rag_system
    if _database_rag_system is None:
        _database_rag_system = DatabaseFirstRAG()
    return _database_rag_system

def query_raven_database_first(query: str) -> str:
    """
    Database-first query function that replaces the existing RAG
    """
    system = get_database_rag_system()
    return system.query_database_first(query)

if __name__ == "__main__":
    # Test the database-first RAG
    rag = DatabaseFirstRAG()
    
    test_queries = [
        "What data do you have access to?",
        "Show me Apple's 8-K filings",
        "Any insider trading for Microsoft executives?",
        "What institutional holdings data do you have for Tesla?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        response = rag.query_database_first(query)
        print(response)
