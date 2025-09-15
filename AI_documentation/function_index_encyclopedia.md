# GameCock AI Function Index Encyclopedia

## Overview
This encyclopedia provides a comprehensive index of all functions, classes, and modules in the GameCock AI system, organized by category and functionality. Each entry includes the file location, purpose, and key parameters.

## Core Application Functions

### Main Application (`app.py`)

#### Menu Functions
- **`main_menu()`** - Main application menu controller
  - **File**: `app.py:77`
  - **Purpose**: Central menu system with 6 main options
  - **Returns**: None (interactive menu)

- **`select_target_companies_menu()`** - Target company selection interface
  - **File**: `app.py:113`
  - **Purpose**: Company search, addition, and management
  - **Returns**: None (interactive menu)

- **`download_data_menu()`** - Data download interface
  - **File**: `app.py:179`
  - **Purpose**: Multi-source data download coordination
  - **Returns**: None (interactive menu)

- **`process_data_menu()`** - Data processing interface
  - **File**: `app.py:546`
  - **Purpose**: Data processing and database loading
  - **Returns**: None (interactive menu)

- **`query_raven_menu()`** - AI query interface
  - **File**: `app.py:914`
  - **Purpose**: Launch Raven AI chat interface
  - **Returns**: None (launches chat)

- **`database_menu()`** - Database management interface
  - **File**: `app.py:919`
  - **Purpose**: Database statistics, export, and management
  - **Returns**: None (interactive menu)

#### Data Download Functions
- **`fred_download_menu()`** - FRED data download
  - **File**: `app.py:204`
  - **Purpose**: Download FRED swap rate data
  - **Returns**: None (downloads data)

- **`edgar_download_menu()`** - EDGAR filings download
  - **File**: `app.py:241`
  - **Purpose**: Download SEC EDGAR filings
  - **Returns**: None (downloads filings)

- **`download_all_edgar_filings()`** - Comprehensive EDGAR download
  - **File**: `app.py:362`
  - **Purpose**: Download all EDGAR filings for target companies
  - **Returns**: None (downloads all filings)

- **`cftc_download_submenu()`** - CFTC data download
  - **File**: `app.py:398`
  - **Purpose**: CFTC data download coordination
  - **Returns**: None (interactive menu)

- **`sec_download_submenu()`** - SEC data download
  - **File**: `app.py:455`
  - **Purpose**: SEC data download coordination
  - **Returns**: None (interactive menu)

#### Data Processing Functions
- **`process_cftc_submenu()`** - CFTC data processing
  - **File**: `app.py:571`
  - **Purpose**: Process CFTC data files
  - **Returns**: None (processes data)

- **`process_sec_submenu()`** - SEC data processing
  - **File**: `app.py:610`
  - **Purpose**: Process SEC data files
  - **Returns**: None (processes data)

- **`process_all_downloaded_data()`** - Comprehensive data processing
  - **File**: `app.py:779`
  - **Purpose**: Process all downloaded data
  - **Returns**: None (processes all data)

- **`process_edgar_filings(filing_type)`** - EDGAR filing processing
  - **File**: `app.py:679`
  - **Purpose**: Process specific EDGAR filing types
  - **Parameters**: `filing_type` (str) - Type of filing to process
  - **Returns**: None (processes filings)

- **`process_all_edgar_filings()`** - All EDGAR filings processing
  - **File**: `app.py:718`
  - **Purpose**: Process all EDGAR filing types
  - **Returns**: None (processes all filings)

- **`process_all_sec_data()`** - All SEC data processing
  - **File**: `app.py:750`
  - **Purpose**: Process all SEC data types
  - **Returns**: None (processes all SEC data)

#### System Functions
- **`run_startup_checks()`** - System initialization
  - **File**: `app.py:949`
  - **Purpose**: Perform all startup checks
  - **Returns**: None (initializes system)

- **`initialize_database()`** - Database initialization
  - **File**: `app.py:967`
  - **Purpose**: Initialize database tables
  - **Returns**: None (initializes database)

## Database Functions (`database.py`)

### Database Management
- **`create_db_and_tables()`** - Create database tables
  - **File**: `database.py:1413`
  - **Purpose**: Create all database tables if they don't exist
  - **Returns**: bool - Success status

- **`get_db_stats(db_session=None)`** - Get database statistics
  - **File**: `database.py:1422`
  - **Purpose**: Returns table names and row counts
  - **Parameters**: `db_session` (Session, optional) - Database session
  - **Returns**: dict - Table statistics

- **`export_db_to_csv(output_path)`** - Export database to CSV
  - **File**: `database.py:1443`
  - **Purpose**: Export CFTC swap data to CSV
  - **Parameters**: `output_path` (str) - Output file path
  - **Returns**: None (exports data)

- **`reset_database()`** - Reset database
  - **File**: `database.py:1454`
  - **Purpose**: Drop and recreate all tables
  - **Returns**: None (resets database)

### Database Models
- **`SecSubmission`** - SEC submission model
  - **File**: `database.py:16`
  - **Purpose**: SEC filing submission metadata
  - **Key Fields**: accession_number, filing_date, document_type

- **`CFTCSwap`** - CFTC swap data model
  - **File**: `database.py:1162`
  - **Purpose**: Comprehensive swap transaction data
  - **Key Fields**: dissemination_id, asset_class, notional_amount

- **`Form13FSubmission`** - Form 13F submission model
  - **File**: `database.py:184`
  - **Purpose**: Form 13F filing metadata
  - **Key Fields**: accession_number, cik, period_of_report

## AI and RAG Functions

### Unified RAG System (`src/rag_unified.py`)

#### Core RAG Functions
- **`query_raven(user_query, messages=None, use_tools=True, use_enhanced_rag=True)`** - Main RAG query function
  - **File**: `src/rag_unified.py:88`
  - **Purpose**: Unified query processing with tool integration
  - **Parameters**: 
    - `user_query` (str) - User's query
    - `messages` (List[Dict], optional) - Conversation history
    - `use_tools` (bool) - Enable tool usage
    - `use_enhanced_rag` (bool) - Use enhanced RAG system
  - **Returns**: str - AI response

- **`UnifiedRAGSystem`** - Unified RAG system class
  - **File**: `src/rag_unified.py:70`
  - **Purpose**: Main RAG system controller
  - **Key Methods**: query_raven, _process_tool_query, _process_enhanced_query

### Enhanced RAG System (`src/rag_enhanced.py`)
- **`EnhancedRAGSystem`** - Enhanced RAG system class
  - **File**: `src/rag_enhanced.py`
  - **Purpose**: Advanced RAG with vector embeddings
  - **Key Features**: Semantic search, vector similarity, context retrieval

### Vector Database (`src/vector_db.py`)

#### Vector Database Management
- **`GameCockVectorDB`** - Vector database system class
  - **File**: `src/vector_db.py:23`
  - **Purpose**: Hybrid vector database (ChromaDB + FAISS)
  - **Key Methods**: create_collection, add_documents, search, get_stats

- **`create_collection(name, description, embedding_function)`** - Create vector collection
  - **File**: `src/vector_db.py:100`
  - **Purpose**: Create new vector collection
  - **Parameters**: 
    - `name` (str) - Collection name
    - `description` (str) - Collection description
    - `embedding_function` (str) - Embedding function name
  - **Returns**: Collection object

- **`add_documents(collection_name, documents, metadatas, ids)`** - Add documents to collection
  - **File**: `src/vector_db.py:120`
  - **Purpose**: Add documents to vector collection
  - **Parameters**: Document data and metadata
  - **Returns**: None (adds to collection)

- **`search(collection_name, query, n_results=10)`** - Search vector collection
  - **File**: `src/vector_db.py:150`
  - **Purpose**: Semantic search in vector collection
  - **Parameters**: 
    - `collection_name` (str) - Collection to search
    - `query` (str) - Search query
    - `n_results` (int) - Number of results
  - **Returns**: Search results

## Analytics Tools (`tools.py`)

### Core Analytics Functions
- **`search_companies(company_name)`** - Company search
  - **File**: `tools.py:159`
  - **Purpose**: Search for companies by name or ticker
  - **Parameters**: `company_name` (str) - Company name or ticker
  - **Returns**: str - JSON string with search results

- **`add_to_target_list(cik, ticker, title)`** - Add company to targets
  - **File**: `tools.py:211`
  - **Purpose**: Add company to target list
  - **Parameters**: 
    - `cik` (str) - Company CIK
    - `ticker` (str) - Ticker symbol
    - `title` (str) - Company name
  - **Returns**: str - JSON confirmation

- **`view_target_list()`** - View target companies
  - **File**: `tools.py:264`
  - **Purpose**: Display current target companies
  - **Returns**: str - JSON string with target list

- **`download_data(source, data_type)`** - Download data
  - **File**: `tools.py:299`
  - **Purpose**: Queue data download task
  - **Parameters**: 
    - `source` (str) - Data source (cftc/sec)
    - `data_type` (str) - Type of data to download
  - **Returns**: str - JSON string with task ID

- **`process_data(source_dir_name)`** - Process data
  - **File**: `tools.py:406`
  - **Purpose**: Queue data processing task
  - **Parameters**: `source_dir_name` (str) - Data category to process
  - **Returns**: str - JSON string with task ID

- **`get_database_statistics()`** - Get database stats
  - **File**: `tools.py:466`
  - **Purpose**: Retrieve database statistics
  - **Returns**: str - JSON string with statistics

- **`check_task_status(task_id)`** - Check task status
  - **File**: `tools.py:498`
  - **Purpose**: Check background task status
  - **Parameters**: `task_id` (str) - Task identifier
  - **Returns**: str - JSON string with task status

### Enhanced Analytics Functions
- **`create_resilient_analytics_tools()`** - Create analytics tools
  - **File**: `tools.py:537`
  - **Purpose**: Create analytics tools with error handling
  - **Returns**: dict - Analytics tools dictionary

- **`create_resilient_enhanced_analytics_tools()`** - Create enhanced analytics
  - **File**: `tools.py:563`
  - **Purpose**: Create enhanced analytics tools
  - **Returns**: dict - Enhanced analytics tools

- **`create_temporal_analysis_tools()`** - Create temporal analysis tools
  - **File**: `tools.py:591`
  - **Purpose**: Create temporal analysis tools
  - **Returns**: dict - Temporal analysis tools

- **`create_enhanced_entity_tools()`** - Create entity resolution tools
  - **File**: `tools.py:660`
  - **Purpose**: Create enhanced entity resolution tools
  - **Returns**: dict - Entity resolution tools

## Company Management Functions (`company_manager.py`)

### SEC API Integration
- **`get_company_map()`** - Get company data from SEC API
  - **File**: `company_manager.py:9`
  - **Purpose**: Download and process SEC company ticker to CIK mapping
  - **Returns**: pandas.DataFrame - Company data from SEC API
  - **Data Source**: https://www.sec.gov/files/company_tickers.json

- **`find_company(df, search_term)`** - Search companies using SEC data
  - **File**: `company_manager.py:30`
  - **Purpose**: Search company data for ticker, name, or CIK
  - **Parameters**: 
    - `df` (DataFrame) - Company data from SEC API
    - `search_term` (str) - Search term (ticker, name, or CIK)
  - **Returns**: List[dict] - Matching company records

## Entity Resolution Functions (`src/enhanced_entity_resolver.py`)

### Entity Resolution Core
- **`EnhancedEntityResolver`** - Entity resolution engine class
  - **File**: `src/enhanced_entity_resolver.py:94`
  - **Purpose**: Comprehensive entity resolution using SEC API and database sources
  - **Key Methods**: resolve_entity, search_entities, get_entity_profile

- **`resolve_entity(identifier, identifier_type='auto')`** - Resolve entity by identifier using SEC API
  - **File**: `src/enhanced_entity_resolver.py:119`
  - **Purpose**: Resolve entity using SEC API with any identifier type
  - **Parameters**: 
    - `identifier` (str) - Entity identifier
    - `identifier_type` (str) - Type of identifier
  - **Returns**: EntityProfile object from SEC API

- **`get_entity_profile(entity_id)`** - Get entity profile using SEC API
  - **File**: `src/enhanced_entity_resolver.py:451`
  - **Purpose**: Get comprehensive entity profile from SEC API
  - **Parameters**: `entity_id` (str) - Entity identifier
  - **Returns**: EntityProfile object from SEC API

- **`search_entities(search_term, limit=10)`** - Search entities using SEC API
  - **File**: `src/enhanced_entity_resolver.py:465`
  - **Purpose**: Search entities using SEC API with fuzzy matching
  - **Parameters**: 
    - `search_term` (str) - Search term
    - `limit` (int) - Maximum results
  - **Returns**: List[EntityMatch] - Search results from SEC API

- **`find_related_entities(entity_id)`** - Find related entities
  - **File**: `src/enhanced_entity_resolver.py:300`
  - **Purpose**: Find related entities (subsidiaries, parents) using database
  - **Parameters**: `entity_id` (str) - Entity identifier
  - **Returns**: List[EntityReference] - Related entities

- **`find_related_securities(entity_id)`** - Find related securities
  - **File**: `src/enhanced_entity_resolver.py:350`
  - **Purpose**: Find securities related to entity using database
  - **Parameters**: `entity_id` (str) - Entity identifier
  - **Returns**: List[SecurityInfo] - Related securities

## Swap Analysis Functions (`src/swap_analysis/single_party_risk_analyzer.py`)

### Risk Analysis Core
- **`SinglePartyRiskAnalyzer`** - Single party risk analyzer class
  - **File**: `src/swap_analysis/single_party_risk_analyzer.py:150`
  - **Purpose**: Comprehensive swap risk analysis
  - **Key Methods**: analyze_single_party_risk, detect_risk_triggers, track_obligations

- **`analyze_single_party_risk(entity_id)`** - Analyze single party risk
  - **File**: `src/swap_analysis/single_party_risk_analyzer.py:200`
  - **Purpose**: Analyze risk for single entity
  - **Parameters**: `entity_id` (str) - Entity identifier
  - **Returns**: SinglePartyRiskProfile object

- **`detect_risk_triggers(entity_id)`** - Detect risk triggers
  - **File**: `src/swap_analysis/single_party_risk_analyzer.py:250`
  - **Purpose**: Detect risk trigger events
  - **Parameters**: `entity_id` (str) - Entity identifier
  - **Returns**: List[RiskTrigger] - Risk triggers

- **`track_obligations(entity_id)`** - Track obligations
  - **File**: `src/swap_analysis/single_party_risk_analyzer.py:300`
  - **Purpose**: Track payment and collateral obligations
  - **Parameters**: `entity_id` (str) - Entity identifier
  - **Returns**: ObligationProfile object

## Data Processing Functions

### SEC Processing (`src/processor_*.py`)
- **`process_sec_filings(filing_type, source_dir)`** - Process SEC filings
  - **File**: `src/processor_sec.py`
  - **Purpose**: Process SEC filing data
  - **Parameters**: 
    - `filing_type` (str) - Type of filing
    - `source_dir` (str) - Source directory
  - **Returns**: Processing results

- **`process_10k_filings(source_dir)`** - Process 10-K filings
  - **File**: `src/processor_10k.py`
  - **Purpose**: Process 10-K/10-Q filings
  - **Parameters**: `source_dir` (str) - Source directory
  - **Returns**: Processing results

- **`process_8k_filings(source_dir)`** - Process 8-K filings
  - **File**: `src/processor_8k.py`
  - **Purpose**: Process 8-K filings
  - **Parameters**: `source_dir` (str) - Source directory
  - **Returns**: Processing results

### CFTC Processing (`src/processor_cftc_swaps.py`)
- **`process_cftc_swaps(source_dir)`** - Process CFTC swap data
  - **File**: `src/processor_cftc_swaps.py`
  - **Purpose**: Process CFTC swap data files
  - **Parameters**: `source_dir` (str) - Source directory
  - **Returns**: Processing results

### Form Processing
- **`process_form13f_data(source_dir)`** - Process Form 13F data
  - **File**: `src/processor_form13f.py`
  - **Purpose**: Process Form 13F holdings data
  - **Parameters**: `source_dir` (str) - Source directory
  - **Returns**: Processing results

- **`process_formd_data(source_dir)`** - Process Form D data
  - **File**: `src/processor_formd.py`
  - **Purpose**: Process Form D offering data
  - **Parameters**: `source_dir` (str) - Source directory
  - **Returns**: Processing results

## Data Source Functions (`src/data_sources/`)

### SEC Data Source (`src/data_sources/sec.py`)
- **`download_edgar_filings(target_companies, filing_types, years, max_files_per_company)`** - Download EDGAR filings
  - **File**: `src/data_sources/sec.py`
  - **Purpose**: Download SEC EDGAR filings
  - **Parameters**: Company and filing specifications
  - **Returns**: Download results

- **`download_insider_archives()`** - Download insider data
  - **File**: `src/data_sources/sec.py`
  - **Purpose**: Download SEC insider trading data
  - **Returns**: Download results

- **`download_13F_archives()`** - Download 13F data
  - **File**: `src/data_sources/sec.py`
  - **Purpose**: Download Form 13F data
  - **Returns**: Download results

### CFTC Data Source (`src/data_sources/cftc.py`)
- **`download_cftc_credit_archives()`** - Download CFTC credit data
  - **File**: `src/data_sources/cftc.py`
  - **Purpose**: Download CFTC credit swap data
  - **Returns**: Download results

- **`download_cftc_rates_archives()`** - Download CFTC rates data
  - **File**: `src/data_sources/cftc.py`
  - **Purpose**: Download CFTC interest rate data
  - **Returns**: Download results

- **`download_all_swap_data()`** - Download all CFTC swap data
  - **File**: `src/data_sources/cftc.py`
  - **Purpose**: Download all CFTC swap data types
  - **Returns**: Download results

### FRED Data Source (`src/data_sources/fred.py`)
- **`download_fred_swap_data()`** - Download FRED swap data
  - **File**: `src/data_sources/fred.py`
  - **Purpose**: Download FRED swap rate data
  - **Returns**: Download results

### DTCC Data Source (`src/data_sources/dtcc.py`)
- **`download_dtcc_swap_data(data_type)`** - Download DTCC data
  - **File**: `src/data_sources/dtcc.py`
  - **Purpose**: Download DTCC derivative data
  - **Parameters**: `data_type` (str) - Type of DTCC data
  - **Returns**: Download results

## Temporal Analysis Functions (`src/temporal_analysis_tools.py`)

### Temporal Analysis Core
- **`analyze_risk_evolution(company_cik, years=None)`** - Analyze risk evolution
  - **File**: `src/temporal_analysis_tools.py`
  - **Purpose**: Analyze how risk factors evolve over time
  - **Parameters**: 
    - `company_cik` (str) - Company CIK
    - `years` (List[int], optional) - Years to analyze
  - **Returns**: Risk evolution analysis

- **`analyze_management_view_evolution(company_cik, years=None)`** - Analyze management view evolution
  - **File**: `src/temporal_analysis_tools.py`
  - **Purpose**: Analyze MD&A evolution over time
  - **Parameters**: 
    - `company_cik` (str) - Company CIK
    - `years` (List[int], optional) - Years to analyze
  - **Returns**: Management view evolution analysis

- **`compare_company_risks(company_ciks, year)`** - Compare company risks
  - **File**: `src/temporal_analysis_tools.py`
  - **Purpose**: Compare risk factors across companies
  - **Parameters**: 
    - `company_ciks` (List[str]) - Company CIKs
    - `year` (int) - Year to compare
  - **Returns**: Risk comparison analysis

- **`analyze_company_events(company_cik, months=12)`** - Analyze company events
  - **File**: `src/temporal_analysis_tools.py`
  - **Purpose**: Analyze 8-K event patterns
  - **Parameters**: 
    - `company_cik` (str) - Company CIK
    - `months` (int) - Months to look back
  - **Returns**: Event pattern analysis

## Utility Functions

### Error Handling
- **`handle_tool_errors(func)`** - Error handling decorator
  - **File**: `tools.py:144`
  - **Purpose**: Provide consistent error handling for tools
  - **Parameters**: `func` - Function to decorate
  - **Returns**: Decorated function

### Configuration
- **`load_dotenv()`** - Load environment variables
  - **File**: `config.py:4`
  - **Purpose**: Load environment variables from .env file
  - **Returns**: None (loads environment)

### System Utilities
- **`check_dependencies()`** - Check system dependencies
  - **File**: `startup.py`
  - **Purpose**: Validate system dependencies
  - **Returns**: bool - Dependencies status

- **`check_ollama_service()`** - Check Ollama service
  - **File**: `startup.py`
  - **Purpose**: Validate Ollama service availability
  - **Returns**: bool - Service status

- **`check_cuda_support()`** - Check CUDA support
  - **File**: `startup.py`
  - **Purpose**: Validate CUDA GPU support
  - **Returns**: bool - CUDA status

## Function Categories Summary

### Core Application (15 functions)
- Menu controllers, data download, processing, system management

### Database Management (8 functions)
- Table creation, statistics, export, reset operations

### AI and RAG (12 functions)
- Query processing, vector search, semantic analysis

### Analytics Tools (20 functions)
- Company management, data operations, enhanced analytics

### Entity Resolution (8 functions)
- Entity identification, relationship discovery, profile creation

### Swap Analysis (6 functions)
- Risk analysis, trigger detection, obligation tracking

### Data Processing (15 functions)
- SEC, CFTC, Form data processing and transformation

### Data Sources (12 functions)
- External API integration and data download

### Temporal Analysis (4 functions)
- Time-series analysis and trend detection

### Utility Functions (8 functions)
- Error handling, configuration, system validation

---

*This function index encyclopedia provides a comprehensive reference for all functions in the GameCock AI system. Each function entry includes file location, purpose, parameters, and return values for easy navigation and understanding.*
