import ollama
# Import from the REAL database module with all tables (GameCockAI/database.py)
from database import SessionLocal, CFTCSwap

from sqlalchemy import or_

# A simple set of stop words to improve keyword search quality
STOP_WORDS = {
    'a', 'about', 'an', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'how', 'in', 
    'is', 'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'was', 'what', 
    'when', 'where', 'who', 'will', 'with', 'the', 'tell', 'me'
}

def query_raven(query_text):
    """Performs a targeted database query and uses Ollama to answer a question."""
    db = SessionLocal()
    try:
        # Extract keywords and filter out stop words
        keywords = [word for word in query_text.lower().split() if word not in STOP_WORDS]

        # Build a dynamic query to search for keywords in relevant fields
        search_filters = []
        searchable_cols = [CFTCSwap.asset_class, CFTCSwap.action, CFTCSwap.dissemination_id]
        for keyword in keywords:
            for col in searchable_cols:
                search_filters.append(col.ilike(f'%{keyword}%'))

        if not search_filters:
            return "Please provide keywords to search for."

        # Retrieve data using the constructed query
        data = db.query(CFTCSwap).filter(or_(*search_filters)).limit(100).all() # Limit to 100 results

        if not data:
            return "No relevant data found for your query."

        # Format the retrieved data for the LLM context
        context = "\n".join([str(d.__dict__) for d in data])

        prompt = f"""Based on the following data, please answer the question.

Context:
{context}

Question: {query_text}

Answer:"""

        response = ollama.chat(
            model='raven-enhanced',
            messages=[{'role': 'user', 'content': prompt}],
        )
        return response['message']['content']

    finally:
        db.close()
