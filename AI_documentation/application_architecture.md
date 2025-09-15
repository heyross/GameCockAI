# GameCock AI Application Architecture

## Overview
GameCock AI is a comprehensive financial intelligence platform that combines advanced data processing, AI-powered analytics, and vector embeddings to provide deep insights into financial markets. The platform integrates data from multiple authoritative sources including SEC, CFTC, FRED, and DTCC, featuring Raven - an intelligent AI assistant with state-of-the-art RAG capabilities.

## System Architecture

### Core Application Structure
```
GameCockAI/
├── app.py                    # Main application entry point with menu system
├── database.py               # SQLAlchemy database models and operations
├── config.py                 # Application configuration and settings
├── tools.py                  # 28+ analytics tools and function mapping
├── chat_interface.py         # Raven AI chat interface
├── rag.py                    # Basic RAG system with Ollama integration
├── company_manager.py        # Company data management
├── company_data.py           # Target companies storage
├── worker.py                 # Background task processing
├── startup.py                # System initialization and checks
├── ui.py                     # User interface components
└── src/                      # Advanced AI system modules
    ├── rag_unified.py        # Unified RAG system
    ├── rag_enhanced.py       # Enhanced RAG with semantic search
    ├── vector_db.py          # ChromaDB and FAISS vector database
    ├── embedding_service.py  # FinBERT and E5-Large-v2 embeddings
    ├── document_processor.py # Financial document processing
    ├── vector_integration.py # Vector embeddings integration
    ├── tools_vector_enhanced.py # Enhanced analytics with vector understanding
    ├── data_sources/         # Data source integrations
    ├── swap_analysis/        # Swap risk analysis modules
    ├── enhanced_entity_resolver.py # Entity resolution engine
    ├── temporal_analysis_tools.py # Time-series analysis
    └── processor_*.py        # Data processing modules
```

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Central application controller with menu-driven interface
- **Key Features**:
  - 6 main menu options (Target Companies, Entity Search, Download, Process, Query, Database)
  - Comprehensive data download and processing workflows
  - Integration with all system components
  - Error handling and fallback mechanisms

### 2. Database System (`database.py`)
- **Purpose**: SQLAlchemy-based data persistence layer
- **Key Features**:
  - 64+ database tables covering all data types
  - 4.39 million records across multiple regulatory sources
  - Optimized schemas with efficient indexing
  - Support for SEC, CFTC, FRED, DTCC, and Form data

### 3. AI System (`src/rag_*.py`)
- **Purpose**: Advanced AI capabilities with RAG integration
- **Key Features**:
  - Unified RAG system combining all AI functionality
  - Enhanced semantic search with vector embeddings
  - 28 specialized tools for financial analysis
  - Natural language query processing

### 4. Vector Database (`src/vector_db.py`)
- **Purpose**: High-performance semantic search capabilities
- **Key Features**:
  - ChromaDB for document-level semantic search
  - FAISS for numerical vector search
  - 10-50x performance improvements
  - Intelligent caching and optimization

### 5. Data Sources (`src/data_sources/`)
- **Purpose**: Integration with external financial data APIs
- **Key Features**:
  - SEC EDGAR integration
  - CFTC swap data access
  - FRED economic data
  - DTCC derivative data
  - Exchange metrics

### 6. Advanced Analytics (`src/swap_analysis/`, `src/enhanced_entity_resolver.py`)
- **Purpose**: Sophisticated financial analysis capabilities
- **Key Features**:
  - Single party risk analysis
  - Cross-filing correlation engine
  - SEC API-based entity resolution across multiple identifiers
  - Real-time company data integration
  - Temporal analysis and trend detection

## Data Flow Architecture

### 1. Data Ingestion Pipeline
```
External APIs → Data Sources → Downloaders → Processors → Database
     ↓              ↓             ↓            ↓           ↓
  SEC/CFTC/     src/data_    src/processor_  Database   Vector
   FRED/DTCC    sources/     *.py modules    Tables     Store
```

### 2. Query Processing Pipeline
```
User Query → RAG System → Tool Selection → Data Retrieval → AI Analysis → Response
     ↓           ↓            ↓              ↓              ↓           ↓
  Natural    Unified RAG   Function      SEC API/       Vector      Formatted
  Language   System        Mapping       Database/      Search      Output
                                    Vector DB
```

### 3. AI Tool Integration
```
Raven AI → Tool Map → Function Execution → Data Processing → Results → AI Interpretation
    ↓         ↓            ↓                 ↓              ↓           ↓
  Query    TOOL_MAP    Analytics Tools   Database      Structured   Natural
 Analysis  Selection   (28 functions)    Queries       Data         Language
```

## Module Dependencies

### Core Dependencies
- **SQLAlchemy**: Database ORM and management
- **Ollama**: Local LLM integration for Raven AI
- **ChromaDB**: Vector database for semantic search
- **FAISS**: High-performance vector similarity search
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Transformers**: FinBERT and E5-Large-v2 models

### Data Source Dependencies
- **Requests**: HTTP client for API calls
- **BeautifulSoup**: HTML parsing for SEC filings
- **FredAPI**: FRED economic data access
- **Pandas**: Data processing and analysis

### AI/ML Dependencies
- **Sentence-Transformers**: Embedding models
- **ChromaDB**: Vector storage and retrieval
- **FAISS**: Vector similarity search
- **Ollama**: Local LLM inference

## Configuration Management

### Environment Variables
- `FRED_API_KEY`: FRED API access key
- `SEC_USER_AGENT`: SEC EDGAR user agent
- `DATABASE_URI`: Database connection string
- `VECTOR_STORE_PATH`: Vector database storage path

### Configuration Files
- `config.py`: Application settings and directory paths
- `vector_config.json`: Vector database configuration
- `vector_models_info.json`: Model information and settings

## Error Handling and Resilience

### Graceful Degradation
- Fallback mechanisms for missing modules
- Dummy functions for unavailable services
- Error handling decorators for all tools
- Comprehensive logging throughout the system

### Import Resilience
- Multiple import strategies with fallbacks
- Path management for different execution contexts
- Dynamic module loading with error handling
- Service availability flags

## Performance Optimizations

### Vector Database Performance
- 10-50x query speed improvements
- Intelligent caching mechanisms
- Batch processing for large datasets
- Optimized indexing strategies

### Database Performance
- Strategic indexing on frequently queried columns
- Connection pooling and session management
- Query optimization and caching
- Efficient data type usage

### Memory Management
- 80% reduction in working memory usage
- Intelligent cache management
- Lazy loading of large datasets
- Garbage collection optimization

## Security Considerations

### Data Privacy
- Local processing of sensitive financial data
- No external data transmission for analysis
- Secure API key management
- Encrypted storage for sensitive information

### Access Control
- User authentication for API access
- Rate limiting for external API calls
- Input validation and sanitization
- Secure configuration management

## Scalability Architecture

### Horizontal Scaling
- Modular design allows component scaling
- Independent service architecture
- Load balancing capabilities
- Distributed processing support

### Vertical Scaling
- Efficient memory usage patterns
- CPU optimization for vector operations
- GPU acceleration support (CUDA)
- Database query optimization

## Monitoring and Logging

### System Monitoring
- Comprehensive logging throughout all modules
- Performance metrics collection
- Error tracking and reporting
- System health monitoring

### Analytics Monitoring
- Query performance tracking
- Vector search effectiveness
- Tool usage statistics
- User interaction analytics

## Future Architecture Considerations

### Planned Enhancements
- Microservices architecture migration
- Container-based deployment
- Cloud-native scaling
- Advanced ML model integration

### Integration Opportunities
- Real-time data streaming
- Advanced visualization dashboards
- Mobile application support
- API-first architecture

---

*This architecture documentation provides a comprehensive overview of the GameCock AI system structure, components, and design principles. For detailed implementation information, refer to the specific module documentation.*
