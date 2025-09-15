# GameCock AI Module Documentation

## Overview
This document provides detailed documentation for all modules in the GameCock AI system, organized by functionality and purpose. Each module entry includes its purpose, key components, dependencies, and integration points.

## Core Application Modules

### Main Application Module (`app.py`)
**Purpose**: Central application controller with menu-driven interface
**Key Components**:
- Main menu system with 6 primary options
- Data download and processing workflows
- System initialization and startup procedures
- Error handling and user interaction management

**Key Classes/Functions**:
- `main_menu()` - Central menu controller
- `select_target_companies_menu()` - Company management interface
- `download_data_menu()` - Data download coordination
- `process_data_menu()` - Data processing interface
- `query_raven_menu()` - AI query interface
- `database_menu()` - Database management interface

**Dependencies**:
- `database.py` - Database operations
- `tools.py` - Analytics tools
- `chat_interface.py` - AI chat interface
- `worker.py` - Background task processing
- `startup.py` - System initialization

**Integration Points**:
- Connects all system components
- Manages user workflows
- Coordinates data processing pipelines

### Database Module (`database.py`)
**Purpose**: SQLAlchemy-based data persistence layer
**Key Components**:
- 64+ database table models
- Database connection management
- Data validation and constraints
- Performance optimization

**Key Classes**:
- `SecSubmission` - SEC filing metadata
- `CFTCSwap` - CFTC swap transaction data
- `Form13FSubmission` - Form 13F filing data
- `Sec10KSubmission` - 10-K/10-Q filing data
- `Sec8KSubmission` - 8-K filing data
- `NCENSubmission` - N-CEN fund data
- `NPORTSubmission` - N-PORT fund data
- `NMFPSubmission` - N-MFP money market data
- `FormDSubmission` - Form D offering data

**Key Functions**:
- `create_db_and_tables()` - Database initialization
- `get_db_stats()` - Database statistics
- `export_db_to_csv()` - Data export
- `reset_database()` - Database reset

**Dependencies**:
- SQLAlchemy ORM
- SQLite database engine
- Pandas for data export

**Integration Points**:
- Used by all data processing modules
- Accessed by analytics tools
- Integrated with vector database

### Configuration Module (`config.py`)
**Purpose**: Application configuration and settings management
**Key Components**:
- Directory path configuration
- API endpoint definitions
- Environment variable management
- Data source configuration

**Key Variables**:
- `ROOT_DIR` - Application root directory
- `SRC_DIR` - Source code directory
- `DATA_DIR` - Data storage directory
- `DOWNLOADS_DIR` - Download directory
- `SEC_BASE_DIR` - SEC data directory
- `CFTC_BASE_DIR` - CFTC data directory
- `FRED_SOURCE_DIR` - FRED data directory
- `DTCC_SOURCE_DIR` - DTCC data directory

**Dependencies**:
- `os` - Operating system interface
- `dotenv` - Environment variable loading

**Integration Points**:
- Used by all modules for path resolution
- Referenced by data source modules
- Accessed by processing modules

## AI and RAG Modules

### Unified RAG System (`src/rag_unified.py`)
**Purpose**: Unified RAG system combining all AI functionality
**Key Components**:
- Query processing pipeline
- Tool integration system
- Enhanced RAG fallback
- Response generation

**Key Classes**:
- `UnifiedRAGSystem` - Main RAG system controller

**Key Methods**:
- `query_raven()` - Main query processing function
- `_process_tool_query()` - Tool-enabled query processing
- `_process_enhanced_query()` - Enhanced RAG query processing
- `_process_basic_query()` - Basic query processing

**Dependencies**:
- `ollama` - Local LLM integration
- `rag_enhanced.py` - Enhanced RAG system
- `tools.py` - Analytics tools
- `database.py` - Database access

**Integration Points**:
- Integrates with all analytics tools
- Connects to vector database
- Interfaces with chat system

### Enhanced RAG System (`src/rag_enhanced.py`)
**Purpose**: Advanced RAG with vector embeddings and semantic search
**Key Components**:
- Semantic query processing
- Vector similarity search
- Context retrieval and ranking
- AI-powered insights generation

**Key Classes**:
- `EnhancedRAGSystem` - Enhanced RAG controller

**Key Methods**:
- `query()` - Enhanced query processing
- `_semantic_search()` - Vector similarity search
- `_retrieve_context()` - Context retrieval
- `_generate_insights()` - AI insights generation

**Dependencies**:
- `vector_db.py` - Vector database
- `embedding_service.py` - Embedding generation
- `document_processor.py` - Document processing

**Integration Points**:
- Uses vector database for semantic search
- Integrates with document processor
- Connects to embedding service

### Vector Database (`src/vector_db.py`)
**Purpose**: High-performance vector database for semantic search
**Key Components**:
- ChromaDB integration for document search
- FAISS integration for numerical search
- Metadata management system
- Performance optimization

**Key Classes**:
- `GameCockVectorDB` - Vector database controller

**Key Methods**:
- `create_collection()` - Create vector collection
- `add_documents()` - Add documents to collection
- `search()` - Semantic search
- `get_stats()` - Database statistics
- `optimize_index()` - Index optimization

**Dependencies**:
- `chromadb` - Document vector database
- `faiss` - Numerical vector search
- `sqlite3` - Metadata storage

**Integration Points**:
- Used by enhanced RAG system
- Integrated with document processor
- Connected to embedding service

### Embedding Service (`src/embedding_service.py`)
**Purpose**: Financial domain embedding generation
**Key Components**:
- FinBERT model integration
- E5-Large-v2 model support
- Batch processing capabilities
- Caching and optimization

**Key Classes**:
- `FinancialEmbeddingService` - Embedding service controller

**Key Methods**:
- `generate_embeddings()` - Generate document embeddings
- `generate_query_embedding()` - Generate query embeddings
- `batch_process()` - Batch embedding generation
- `clear_cache()` - Cache management

**Dependencies**:
- `sentence_transformers` - Embedding models
- `transformers` - Model loading
- `torch` - Deep learning framework

**Integration Points**:
- Used by vector database
- Integrated with document processor
- Connected to RAG systems

## Analytics and Tools Modules

### Analytics Tools (`tools.py`)
**Purpose**: Comprehensive analytics tools and function mapping
**Key Components**:
- 28+ specialized analytics functions
- Error handling and resilience
- Tool schema definitions
- Function orchestration

**Key Functions**:
- `search_companies()` - Company search
- `add_to_target_list()` - Target management
- `download_data()` - Data download
- `process_data()` - Data processing
- `get_database_statistics()` - Database stats
- `check_task_status()` - Task monitoring

**Key Tool Categories**:
- Company management tools
- Data operation tools
- Analytics and insights tools
- Enhanced entity resolution tools
- Temporal analysis tools

**Dependencies**:
- `database.py` - Database access
- `company_manager.py` - Company data
- `worker.py` - Background tasks
- Various analytics modules

**Integration Points**:
- Used by RAG system for tool execution
- Connects to all data sources
- Integrates with background worker

### Enhanced Entity Resolver (`src/enhanced_entity_resolver.py`)
**Purpose**: Comprehensive entity resolution using SEC API and database sources
**Key Components**:
- Multi-identifier resolution (CIK, CUSIP, ISIN, LEI, Ticker, Name)
- SEC API integration for real-time company data
- Fuzzy matching algorithms
- Relationship discovery
- Confidence scoring

**Key Classes**:
- `EnhancedEntityResolver` - Entity resolution engine
- `EntityProfile` - Entity profile data structure
- `EntityMatch` - Entity match result
- `SecurityInfo` - Security information
- `EntityReference` - Entity relationship

**Key Methods**:
- `resolve_entity()` - Resolve entity using SEC API
- `search_entities()` - Search entities using SEC API
- `get_entity_profile()` - Get comprehensive entity profile
- `find_related_entities()` - Find related entities
- `find_related_securities()` - Find related securities

**Dependencies**:
- `company_manager.py` - SEC API integration
- `database.py` - Database access (fallback)
- `difflib` - String similarity
- `requests` - HTTP client for SEC API

**Integration Points**:
- Uses SEC API for primary entity resolution
- Falls back to database for additional data
- Used by swap analysis modules
- Integrated with analytics tools
- Connected to RAG system

## Data Processing Modules

### Main Processor (`src/processor.py`)
**Purpose**: Central data processing coordination
**Key Components**:
- Data processing pipeline management
- File format handling
- Data validation and cleaning
- Database loading coordination

**Key Functions**:
- `process_zip_files()` - Process ZIP archives
- `process_sec_insider_data()` - Process SEC insider data
- `process_form13f_data()` - Process Form 13F data
- `process_exchange_metrics_data()` - Process exchange data
- `load_data_to_db()` - Load data to database

**Dependencies**:
- `pandas` - Data manipulation
- `database.py` - Database access
- `config.py` - Configuration

**Integration Points**:
- Used by main application
- Connects to all data sources
- Integrates with database system

### SEC Processing Modules
#### 10-K/10-Q Processor (`src/processor_10k.py`)
**Purpose**: Process SEC 10-K and 10-Q filings
**Key Components**:
- Section extraction (Business, Risk Factors, MD&A, Financials)
- Content cleaning and normalization
- Database storage optimization
- Metadata extraction

#### 8-K Processor (`src/processor_8k.py`)
**Purpose**: Process SEC 8-K filings
**Key Components**:
- Item extraction (1.01, 2.02, 5.02, 8.01, etc.)
- Event classification
- Content processing
- Database integration

#### SEC Processor (`src/processor_sec.py`)
**Purpose**: General SEC filing processing
**Key Components**:
- Filing type detection
- Content extraction
- Data validation
- Database loading

### CFTC Processing (`src/processor_cftc_swaps.py`)
**Purpose**: Process CFTC swap data
**Key Components**:
- Swap transaction processing
- Entity resolution
- Risk calculation
- Database integration

### Form Processing Modules
#### Form 13F Processor (`src/processor_form13f.py`)
**Purpose**: Process Form 13F holdings data
**Key Components**:
- Holdings extraction
- Entity matching
- Position calculation
- Database storage

#### Form D Processor (`src/processor_formd.py`)
**Purpose**: Process Form D offering data
**Key Components**:
- Offering details extraction
- Issuer information processing
- Recipient data handling
- Database integration

### N-Series Processing Modules
#### N-CEN Processor (`src/processor_ncen.py`)
**Purpose**: Process N-CEN fund data
**Key Components**:
- Fund information extraction
- Adviser data processing
- Performance metrics calculation
- Database storage

#### N-PORT Processor (`src/processor_nport.py`)
**Purpose**: Process N-PORT portfolio data
**Key Components**:
- Holdings extraction
- Derivative position processing
- Risk metrics calculation
- Database integration

#### N-MFP Processor (`src/processor_nmfp.py`)
**Purpose**: Process N-MFP money market data
**Key Components**:
- Portfolio security processing
- Liquidity analysis
- Yield calculation
- Database storage

## Data Source Modules

### SEC Data Source (`src/data_sources/sec.py`)
**Purpose**: SEC EDGAR API integration
**Key Components**:
- EDGAR filing download
- Insider trading data access
- Form 13F data retrieval
- Exchange metrics download

**Key Functions**:
- `download_edgar_filings()` - Download EDGAR filings
- `download_insider_archives()` - Download insider data
- `download_13F_archives()` - Download 13F data
- `download_exchange_archives()` - Download exchange data

**Dependencies**:
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `config.py` - Configuration

**Integration Points**:
- Used by main application
- Connected to processing modules
- Integrated with database system

### CFTC Data Source (`src/data_sources/cftc.py`)
**Purpose**: CFTC data repository access
**Key Components**:
- Swap data download
- Dealer registration data
- SEF information retrieval
- Historical analytics

**Key Functions**:
- `download_cftc_credit_archives()` - Download credit data
- `download_cftc_rates_archives()` - Download rates data
- `download_cftc_equities_archives()` - Download equity data
- `download_all_swap_data()` - Download all swap data

**Dependencies**:
- `requests` - HTTP client
- `zipfile` - Archive handling
- `config.py` - Configuration

**Integration Points**:
- Used by main application
- Connected to processing modules
- Integrated with database system

### FRED Data Source (`src/data_sources/fred.py`)
**Purpose**: FRED economic data integration
**Key Components**:
- Economic indicator access
- Interest rate data
- Market indicators
- Financial conditions data

**Key Functions**:
- `download_fred_swap_data()` - Download swap rate data
- `download_economic_indicators()` - Download economic data
- `download_interest_rates()` - Download rate data

**Dependencies**:
- `fredapi` - FRED API client
- `pandas` - Data manipulation
- `config.py` - Configuration

**Integration Points**:
- Used by main application
- Connected to processing modules
- Integrated with database system

### DTCC Data Source (`src/data_sources/dtcc.py`)
**Purpose**: DTCC derivative data access
**Key Components**:
- Interest rate swap data
- Credit default swap data
- Equity derivative data
- Options data

**Key Functions**:
- `download_dtcc_swap_data()` - Download swap data
- `download_equity_options()` - Download options data
- `download_credit_swaps()` - Download CDS data

**Dependencies**:
- `requests` - HTTP client
- `pandas` - Data manipulation
- `config.py` - Configuration

**Integration Points**:
- Used by main application
- Connected to processing modules
- Integrated with database system

## Advanced Analytics Modules

### Swap Analysis (`src/swap_analysis/single_party_risk_analyzer.py`)
**Purpose**: Comprehensive swap risk analysis
**Key Components**:
- Single party risk consolidation
- Risk trigger detection
- Obligation tracking
- Cross-filing correlation

**Key Classes**:
- `SinglePartyRiskAnalyzer` - Risk analyzer controller
- `SwapExposure` - Swap exposure data structure
- `RiskTrigger` - Risk trigger event
- `ObligationProfile` - Obligation tracking

**Key Methods**:
- `analyze_single_party_risk()` - Analyze entity risk
- `detect_risk_triggers()` - Detect risk events
- `track_obligations()` - Track obligations
- `aggregate_exposures()` - Aggregate exposures

**Dependencies**:
- `enhanced_entity_resolver.py` - Entity resolution
- `database.py` - Database access
- `pandas` - Data analysis

**Integration Points**:
- Used by analytics tools
- Connected to entity resolver
- Integrated with database system

### Cross-Filing Analysis (`src/cross_filing_analysis/cross_filing_correlation_engine.py`)
**Purpose**: Cross-filing risk correlation analysis
**Key Components**:
- Filing cross-reference analysis
- Entity relationship mapping
- Risk aggregation across entities
- Regulatory compliance monitoring

**Key Classes**:
- `CrossFilingCorrelationEngine` - Correlation engine
- `FilingCorrelation` - Correlation data structure
- `EntityRelationship` - Entity relationship

**Key Methods**:
- `analyze_cross_filing_correlations()` - Analyze correlations
- `map_entity_relationships()` - Map relationships
- `aggregate_risk_across_entities()` - Aggregate risk
- `monitor_compliance()` - Monitor compliance

**Dependencies**:
- `enhanced_entity_resolver.py` - Entity resolution
- `database.py` - Database access
- `pandas` - Data analysis

**Integration Points**:
- Used by swap analysis
- Connected to entity resolver
- Integrated with database system

### Temporal Analysis (`src/temporal_analysis_tools.py`)
**Purpose**: Time-series analysis and trend detection
**Key Components**:
- Risk evolution analysis
- Management view evolution
- Comparative analysis
- Event pattern analysis

**Key Functions**:
- `analyze_risk_evolution()` - Analyze risk changes
- `analyze_management_view_evolution()` - Analyze MD&A changes
- `compare_company_risks()` - Compare company risks
- `analyze_company_events()` - Analyze event patterns

**Dependencies**:
- `database.py` - Database access
- `pandas` - Data analysis
- `numpy` - Numerical computing

**Integration Points**:
- Used by analytics tools
- Connected to database system
- Integrated with RAG system

## Utility and Support Modules

### Worker System (`worker.py`)
**Purpose**: Background task processing
**Key Components**:
- Task queue management
- Worker thread management
- Task monitoring
- Error handling

**Key Classes**:
- `BackgroundWorker` - Worker controller
- `Task` - Task data structure

**Key Methods**:
- `add_task()` - Add task to queue
- `get_task_status()` - Get task status
- `start_worker()` - Start worker threads
- `stop_worker()` - Stop worker threads

**Dependencies**:
- `threading` - Thread management
- `queue` - Task queue
- `json` - Task serialization

**Integration Points**:
- Used by main application
- Connected to analytics tools
- Integrated with data processing

### Company Management (`company_manager.py`)
**Purpose**: Company data management with SEC API integration
**Key Components**:
- SEC API integration for real-time company data
- Company search functionality
- CIK lookup services
- Company data caching
- API integration

**Key Functions**:
- `get_company_map()` - Get company data from SEC API
- `find_company()` - Search companies using SEC data
- `cache_company_data()` - Cache data
- `refresh_company_data()` - Refresh data

**Dependencies**:
- `requests` - HTTP client for SEC API
- `json` - Data serialization
- `pandas` - Data manipulation
- `config.py` - SEC API configuration

**Integration Points**:
- Primary data source for entity resolution
- Used by main application
- Connected to analytics tools
- Integrated with target management
- Used by enhanced entity resolver

### Company Data (`company_data.py`)
**Purpose**: Target company storage and management
**Key Components**:
- Target company list
- Company data persistence
- Data validation
- Storage management

**Key Variables**:
- `TARGET_COMPANIES` - Target company list

**Key Functions**:
- `save_target_companies()` - Save target list
- `load_target_companies()` - Load target list
- `validate_company_data()` - Validate data

**Dependencies**:
- `json` - Data serialization
- `os` - File operations

**Integration Points**:
- Used by main application
- Connected to company manager
- Integrated with analytics tools

### Startup System (`startup.py`)
**Purpose**: System initialization and validation
**Key Components**:
- Dependency checking
- Service validation
- System configuration
- Error handling

**Key Functions**:
- `check_dependencies()` - Check dependencies
- `check_ollama_service()` - Check Ollama
- `check_cuda_support()` - Check CUDA
- `validate_configuration()` - Validate config

**Dependencies**:
- `subprocess` - Process management
- `importlib` - Module loading
- `os` - System interface

**Integration Points**:
- Used by main application
- Connected to all modules
- Integrated with system validation

### UI Components (`ui.py`)
**Purpose**: User interface components
**Key Components**:
- ASCII art displays
- Menu formatting
- Progress indicators
- Error displays

**Key Functions**:
- `gamecock_ascii()` - Display ASCII art
- `gamecat_ascii()` - Display cat ASCII
- `format_menu()` - Format menus
- `display_progress()` - Show progress

**Dependencies**:
- `os` - System interface
- `time` - Timing functions

**Integration Points**:
- Used by main application
- Connected to menu systems
- Integrated with user interface

## Module Dependencies and Integration

### Core Dependencies
- **SQLAlchemy**: Database ORM used by all data modules
- **Pandas**: Data manipulation used by processing modules
- **Requests**: HTTP client used by data source modules
- **Ollama**: LLM integration used by RAG modules

### Module Integration Patterns
1. **Data Flow**: Data Sources → Processors → Database → Analytics
2. **AI Flow**: User Query → RAG System → Tools → Database → Response
3. **Entity Flow**: Entity Query → Resolver → Database → Profile
4. **Risk Flow**: Entity → Risk Analyzer → Database → Risk Profile

### Error Handling Patterns
- Graceful degradation for missing modules
- Fallback mechanisms for service failures
- Comprehensive logging throughout system
- User-friendly error messages

---

*This module documentation provides a comprehensive overview of all modules in the GameCock AI system, their purposes, components, dependencies, and integration points. Each module is designed for modularity, maintainability, and extensibility.*
