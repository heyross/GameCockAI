"""
Unified RAG System for GameCock AI
Combines all RAG functionality into a single, consistent interface
"""

import ollama
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
# Import from the REAL database module with all tables (GameCockAI/database.py)
try:
    from ..database import SessionLocal, CFTCSwap
except ImportError:
    # Fallback for when imported from different context
    import sys
    import os
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from database import SessionLocal, CFTCSwap
from sqlalchemy import or_

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import tools if available
try:
    import sys
    import os
    
    # Add GameCockAI directory to path if needed
    gamecock_path = os.path.join(os.path.dirname(__file__), 'GameCockAI')
    if os.path.exists(gamecock_path) and gamecock_path not in sys.path:
        sys.path.append(gamecock_path)
    
    try:
        from ..tools import TOOL_MAP
    except ImportError:
        # Fallback for when imported from different context
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        from tools import TOOL_MAP
    TOOLS_AVAILABLE = True
    logger.info(f"✅ Tools loaded: {len(TOOL_MAP)} available")
except ImportError as e:
    logger.warning(f"⚠️ Tools not available: {e}")
    TOOL_MAP = {}
    TOOLS_AVAILABLE = False

# Import enhanced RAG if available
try:
    from rag_enhanced import EnhancedRAGSystem
    ENHANCED_RAG_AVAILABLE = True
    logger.info("✅ Enhanced RAG system available")
except ImportError as e:
    logger.warning(f"⚠️ Enhanced RAG not available: {e}")
    ENHANCED_RAG_AVAILABLE = False

# Simple stop words for basic keyword search
STOP_WORDS = {
    'a', 'about', 'an', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'how', 'in', 
    'is', 'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'was', 'what', 
    'when', 'where', 'who', 'will', 'with', 'the', 'tell', 'me'
}


class UnifiedRAGSystem:
    """
    Unified RAG system that handles all query types with fallback capabilities
    """
    
    def __init__(self, model_name: str = 'raven-enhanced'):
        self.model_name = model_name
        self.enhanced_rag = None
        
        # Initialize enhanced RAG if available
        if ENHANCED_RAG_AVAILABLE:
            try:
                self.enhanced_rag = EnhancedRAGSystem()
                logger.info("✅ Enhanced RAG initialized")
            except Exception as e:
                logger.warning(f"⚠️ Enhanced RAG initialization failed: {e}")
                self.enhanced_rag = None
    
    def query_raven(self, 
                   user_query: str, 
                   messages: Optional[List[Dict]] = None,
                   use_tools: bool = True,
                   use_enhanced_rag: bool = True) -> str:
        """
        Unified query function that handles all query types
        
        Args:
            user_query: The user's query string
            messages: Optional conversation history (for tool-enabled queries)
            use_tools: Whether to use available tools
            use_enhanced_rag: Whether to use enhanced RAG system
            
        Returns:
            Response string
        """
        try:
            # Strategy 1: Enhanced RAG with tools (if available and requested)
            if use_enhanced_rag and self.enhanced_rag and use_tools and TOOLS_AVAILABLE and messages is not None:
                return self._query_with_enhanced_rag_and_tools(user_query, messages)
            
            # Strategy 2: Tools only (if available and messages provided)
            elif use_tools and TOOLS_AVAILABLE and messages is not None:
                return self._query_with_tools_only(user_query, messages)
            
            # Strategy 3: Enhanced RAG only (if available)
            elif use_enhanced_rag and self.enhanced_rag:
                return self._query_with_enhanced_rag_only(user_query)
            
            # Strategy 4: Basic RAG fallback
            else:
                return self._query_with_basic_rag(user_query)
                
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question."
    
    def _query_with_enhanced_rag_and_tools(self, user_query: str, messages: List[Dict]) -> str:
        """Query using enhanced RAG system with tool support"""
        try:
            # Add user message to conversation
            messages.append({'role': 'user', 'content': user_query})
            
            # First, get enhanced RAG context
            import asyncio
            
            async def get_context():
                response = await self.enhanced_rag.process_query(user_query)
                return response
            
            # Run async query
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            rag_response = loop.run_until_complete(get_context())
            
            # Add RAG context to conversation
            context_message = {
                'role': 'system',
                'content': f"Relevant context from database: {rag_response.answer}"
            }
            messages.append(context_message)
            
            # Now use tools if needed
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                tools=[tool['schema'] for tool in TOOL_MAP.values()],
                tool_choice='auto'
            )
            messages.append(response['message'])
            
            # Handle tool calls if any
            if response['message'].get('tool_calls'):
                return self._execute_tools(response['message']['tool_calls'], messages)
            
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Enhanced RAG + tools error: {e}")
            raise
    
    def _query_with_tools_only(self, user_query: str, messages: List[Dict]) -> str:
        """Query using tools only (GameCockAI/rag.py logic)"""
        try:
            messages.append({'role': 'user', 'content': user_query})
            
            # First call to model to decide on tool use
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                tools=[tool['schema'] for tool in TOOL_MAP.values()],
                tool_choice='auto'
            )
            messages.append(response['message'])
            
            # Check if model decided to use tools
            if not response['message'].get('tool_calls'):
                return response['message']['content']
            
            # Execute tools
            return self._execute_tools(response['message']['tool_calls'], messages)
            
        except Exception as e:
            logger.error(f"Tools-only query error: {e}")
            raise
    
    def _query_with_enhanced_rag_only(self, user_query: str) -> str:
        """Query using enhanced RAG system only"""
        try:
            import asyncio
            
            async def process_async():
                return await self.enhanced_rag.process_query(user_query)
            
            # Run async query
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            response = loop.run_until_complete(process_async())
            
            return f"{response.answer}\n\nSources: {len(response.sources)} relevant documents found.\nConfidence: {response.confidence_score:.1%}\nProcessing time: {response.processing_time:.2f}s"
            
        except Exception as e:
            logger.error(f"Enhanced RAG error: {e}")
            raise
    
    def _query_with_basic_rag(self, user_query: str) -> str:
        """Basic RAG fallback (original rag.py logic)"""
        try:
            db = SessionLocal()
            
            # Extract keywords and filter stop words
            keywords = [word for word in user_query.lower().split() if word not in STOP_WORDS]
            
            # Build dynamic query
            search_filters = []
            searchable_cols = [CFTCSwap.asset_class, CFTCSwap.action, CFTCSwap.dissemination_id]
            for keyword in keywords:
                for col in searchable_cols:
                    search_filters.append(col.ilike(f'%{keyword}%'))
            
            if not search_filters:
                return "Please provide keywords to search for."
            
            # Retrieve data
            data = db.query(CFTCSwap).filter(or_(*search_filters)).limit(100).all()
            
            if not data:
                return "No relevant data found for your query."
            
            # Format data for LLM
            context = "\n".join([str(d.__dict__) for d in data])
            
            prompt = f"""Based on the following data, please answer the question.

Context:
{context}

Question: {user_query}

Answer:"""
            
            response = ollama.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
            )
            return response['message']['content']
            
        except Exception as e:
            logger.error(f"Basic RAG error: {e}")
            raise
        finally:
            try:
                db.close()
            except:
                pass
    
    def _execute_tools(self, tool_calls: List[Dict], messages: List[Dict]) -> str:
        """Execute tool calls and return final response"""
        try:
            for tool_call in tool_calls:
                tool_name = tool_call['function']['name']
                tool_args = tool_call['function']['arguments']
                
                if tool_name in TOOL_MAP:
                    tool_function = TOOL_MAP[tool_name]['function']
                    
                    try:
                        tool_result = tool_function(**tool_args)
                        messages.append({
                            'role': 'tool',
                            'content': str(tool_result),
                        })
                    except Exception as e:
                        logger.error(f"Tool execution error for {tool_name}: {e}")
                        messages.append({
                            'role': 'tool',
                            'content': f'Error: Could not execute tool {tool_name}. Reason: {e}',
                        })
            
            # Get final response with tool results
            final_response = ollama.chat(
                model=self.model_name,
                messages=messages
            )
            messages.append(final_response['message'])
            return final_response['message']['content']
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Error executing tools: {e}"


# Global unified system instance
_unified_rag_system = None

def get_unified_rag_system():
    """Get or create the global unified RAG system"""
    global _unified_rag_system
    if _unified_rag_system is None:
        _unified_rag_system = UnifiedRAGSystem()
    return _unified_rag_system


# Backward compatibility functions
def query_raven(user_query: str, messages: Optional[List[Dict]] = None) -> str:
    """
    Unified query_raven function with backward compatibility
    
    This function now prioritizes the tool orchestrator that uses existing application functionality:
    - query_raven(query) -> Tool orchestrator for intelligent workflow
    - query_raven(query, messages) -> Tool orchestrator with conversation context
    """
    try:
        # NEW: Use tool orchestrator as primary method - this uses existing app functionality!
        try:
            from rag_tool_orchestrator import query_raven_with_tools
            logger.info("Using tool orchestrator (recommended approach)")
            return query_raven_with_tools(user_query, messages)
        except ImportError:
            logger.warning("Tool orchestrator not available, falling back to legacy methods")
        
        # FALLBACK 1: Handle common "what data" queries with dedicated response
        if any(phrase in user_query.lower() for phrase in ['what data', 'data access', 'data available', 'data sources']):
            try:
                from tools_interface import get_data_access_summary
                return get_data_access_summary()
            except ImportError:
                logger.warning("Tools interface not available for data summary")
        
        # FALLBACK 2: Use database-first RAG for better query handling
        try:
            from rag_database_first import query_raven_database_first
            
            # If no messages provided, use database-first approach
            if messages is None:
                return query_raven_database_first(user_query)
            
            # If messages provided, check if we should use tools
            if TOOLS_AVAILABLE:
                system = get_unified_rag_system()
                return system.query_raven(
                    user_query=user_query,
                    messages=messages,
                    use_tools=True,
                    use_enhanced_rag=True
                )
            else:
                # Fallback to database-first even with messages
                return query_raven_database_first(user_query)
                
        except ImportError:
            logger.warning("Database-first RAG not available, using final fallback")
            system = get_unified_rag_system()
            
            # Determine which approach to use based on parameters
            use_tools = messages is not None and TOOLS_AVAILABLE
            use_enhanced_rag = system.enhanced_rag is not None
            
            return system.query_raven(
                user_query=user_query,
                messages=messages,
                use_tools=use_tools,
                use_enhanced_rag=use_enhanced_rag
            )
        
    except Exception as e:
        logger.error(f"Unified query_raven error: {e}")
        return f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question."


# Convenience function for tool-enabled queries
def query_raven_with_tools(user_query: str, messages: List[Dict]) -> str:
    """Query with tools explicitly enabled - now uses tool orchestrator"""
    try:
        # NEW: Use tool orchestrator for all tool-enabled queries
        from rag_tool_orchestrator import query_raven_with_tools as orchestrator_query
        return orchestrator_query(user_query, messages)
    except ImportError:
        logger.warning("Tool orchestrator not available, using legacy tool system")
        try:
            system = get_unified_rag_system()
            return system.query_raven(
                user_query=user_query,
                messages=messages,
                use_tools=True,
                use_enhanced_rag=True
            )
        except Exception as e:
            logger.error(f"Tool-enabled query error: {e}")
            return f"I encountered an error processing your query with tools: {str(e)}. Please try again."
    except Exception as e:
        logger.error(f"Tool orchestrator error: {e}")
        return f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question."


# Convenience function for basic queries
def query_raven_basic(user_query: str) -> str:
    """Basic query without tools"""
    try:
        system = get_unified_rag_system()
        return system.query_raven(
            user_query=user_query,
            messages=None,
            use_tools=False,
            use_enhanced_rag=True
        )
    except Exception as e:
        logger.error(f"Basic query error: {e}")
        return f"I encountered an error processing your query: {str(e)}. Please try rephrasing your question."


if __name__ == "__main__":
    # Test the unified system
    print("Testing Unified RAG System...")
    
    # Test basic query
    response1 = query_raven("What data do you have access to?")
    print(f"Basic query response: {response1[:200]}...")
    
    # Test with messages (tool-enabled)
    messages = [{'role': 'system', 'content': 'You are a helpful financial assistant.'}]
    response2 = query_raven("What data do you have access to?", messages)
    print(f"Tool-enabled query response: {response2[:200]}...")
