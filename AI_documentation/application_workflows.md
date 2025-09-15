# GameCock AI Application Workflows

## Overview
This document describes the key workflows and data flow patterns in the GameCock AI system, including data ingestion, processing, analysis, and user interaction workflows.

## 1. Application Startup Workflow

### System Initialization Process
```
Application Start → Dependency Check → Database Init → Worker Start → Main Menu
       ↓                ↓                ↓              ↓            ↓
   app.py          startup.py       database.py    worker.py    User Interface
```

### Detailed Startup Steps
1. **Dependency Validation** (`startup.py`)
   - Check Python package dependencies
   - Verify Ollama service availability
   - Test CUDA support (optional)
   - Validate API keys and configuration

2. **Database Initialization** (`database.py`)
   - Create database tables if not exist
   - Verify database connectivity
   - Initialize database statistics
   - Set up connection pooling

3. **Worker System Startup** (`worker.py`)
   - Initialize background task queue
   - Start worker threads
   - Set up task monitoring
   - Enable background processing

4. **Main Menu Launch** (`app.py`)
   - Display ASCII art and welcome message
   - Present main menu options
   - Initialize user session
   - Enable interactive features

## 2. Data Download Workflow

### Multi-Source Data Download Process
```
User Selection → Source Validation → API Calls → Data Storage → Processing Queue
       ↓              ↓                ↓            ↓              ↓
   Menu Choice    Source Check    Downloader    File System    Background Task
```

### SEC Data Download Workflow
```
SEC Menu → Filing Type Selection → Company Filtering → EDGAR API → File Storage
    ↓              ↓                    ↓               ↓            ↓
  Menu        8-K/10-K/10-Q        Target Companies   API Calls   Downloads/SEC/
```

### CFTC Data Download Workflow
```
CFTC Menu → Asset Class Selection → Archive Download → ZIP Processing → Data Storage
    ↓              ↓                    ↓               ↓              ↓
  Menu        Credit/Rates/Equity   CFTC Archives   Extract Files   Downloads/CFTC/
```

### FRED Data Download Workflow
```
FRED Menu → API Key Validation → Series Selection → Data Download → CSV Storage
    ↓              ↓                ↓               ↓            ↓
  Menu         Environment       Swap Rates      FRED API    Downloads/FRED/
```

## 3. Data Processing Workflow

### Comprehensive Data Processing Pipeline
```
Raw Data → Validation → Cleaning → Transformation → Database Load → Vector Indexing
    ↓          ↓          ↓            ↓              ↓              ↓
  Files    Format      HTML/XML    Normalization   SQLAlchemy    ChromaDB/FAISS
           Check       Cleaning    & Mapping       ORM           Vector Store
```

### SEC Filing Processing Workflow
```
EDGAR Files → Section Extraction → Content Cleaning → Database Storage → Vector Embedding
     ↓              ↓                  ↓                ↓                ↓
  .txt Files    Item 1/1A/7/8/9A   HTML Removal    sec_10k_documents   FinBERT/E5
```

### CFTC Data Processing Workflow
```
ZIP Archives → CSV Extraction → Data Validation → Entity Resolution → Database Load
     ↓              ↓              ↓                ↓                ↓
  Archives      CSV Files      Format Check     CIK/LEI Mapping   cftc_swap_data
```

### Form 13F Processing Workflow
```
13F Files → XML Parsing → Holdings Extraction → Entity Matching → Database Storage
    ↓           ↓              ↓                  ↓                ↓
  .xml       BeautifulSoup   Position Data    Company Lookup    form13f_* tables
```

## 4. AI Query Processing Workflow

### Raven AI Query Processing Pipeline
```
User Query → Intent Analysis → Tool Selection → Data Retrieval → AI Analysis → Response
     ↓            ↓              ↓              ↓              ↓            ↓
  Natural     Unified RAG    TOOL_MAP       Database/      Vector       Formatted
  Language    System         Selection      Vector DB      Search       Output
```

### Enhanced RAG Query Workflow
```
Query → Semantic Analysis → Vector Search → Context Retrieval → LLM Processing → Response
  ↓           ↓                ↓              ↓                ↓              ↓
Text      FinBERT/E5      ChromaDB/FAISS   Document         Ollama        Natural
Input     Embedding       Similarity       Context          LLM          Language
```

### Tool-Enabled Query Workflow
```
Query → Function Detection → Parameter Extraction → Tool Execution → Result Integration
  ↓           ↓                  ↓                    ↓              ↓
Text      Tool Mapping       JSON Schema         Analytics      AI
Input     Analysis           Validation          Functions      Interpretation
```

## 5. Entity Resolution Workflow

### Multi-Identifier Entity Resolution Process
```
Entity Query → Identifier Detection → SEC API Search → Match Scoring → Profile Creation
     ↓              ↓                    ↓              ↓              ↓
  Natural       CIK/CUSIP/ISIN      SEC Company      Confidence     Entity
  Language      LEI/Ticker/Name     Tickers API      Scoring        Profile
```

### Enhanced Entity Resolution Workflow
```
Query → Identifier Type Detection → SEC API Lookup → Database Fallback → Comprehensive Profile
  ↓           ↓                      ↓                ↓                  ↓
Text      Auto-Detection         Real-time SEC      Additional Data    Multi-Source
Input     CIK/CUSIP/LEI/etc      Company Data       from Database      Entity Profile
```

### SEC API Integration Workflow
```
Entity Search → SEC API Call → Company Data Retrieval → Data Processing → Entity Profile
     ↓              ↓                ↓                    ↓              ↓
  User Query    company_tickers    JSON Response      Pandas DF        Structured
  (Name/Ticker) .json endpoint     Company List       Processing       Profile
```

## 6. Swap Risk Analysis Workflow

### Single Party Risk Analysis Process
```
Entity Selection → Data Aggregation → Risk Calculation → Trigger Detection → Report Generation
       ↓              ↓                ↓                 ↓                  ↓
   CIK/LEI        CFTC/DTCC/SEC    Exposure Calc    Margin Calls        Risk Report
   Input          Data Sources     Net/Gross        Credit Events       Dashboard
```

### Cross-Filing Correlation Workflow
```
Entity Query → Filing Collection → Content Analysis → Correlation Detection → Risk Aggregation
     ↓              ↓                ↓                  ↓                    ↓
  Company       10-K/10-Q/8-K     Section Extract    Pattern Matching     Consolidated
  Selection     SEC Filings       Risk Factors       Cross-Reference      Risk Profile
```

## 7. Temporal Analysis Workflow

### Risk Evolution Analysis Process
```
Company Selection → Historical Data → Trend Analysis → Change Detection → Evolution Report
       ↓              ↓                ↓               ↓                ↓
   CIK Input      Multi-Year        Time Series     Pattern Change    Temporal
   Company        SEC Filings       Analysis        Detection         Insights
```

### Management View Evolution Workflow
```
Company → MD&A Extraction → Content Analysis → Change Tracking → Evolution Summary
   ↓           ↓                ↓               ↓                ↓
 CIK       10-K/10-Q         Text Analysis    Year-over-Year    Management
Input      Filings           NLP Processing   Comparison        View Changes
```

## 8. Vector Database Workflow

### Document Indexing Workflow
```
Raw Documents → Text Extraction → Chunking → Embedding → Vector Storage → Index Creation
      ↓              ↓              ↓          ↓            ↓              ↓
   SEC/CFTC      BeautifulSoup    Smart      FinBERT      ChromaDB      FAISS
   Filings       HTML Parser      Chunking   E5-Large     Document      Numerical
```

### Semantic Search Workflow
```
Query → Embedding Generation → Vector Search → Similarity Scoring → Result Ranking → Context Retrieval
  ↓           ↓                  ↓              ↓                  ↓              ↓
Text      FinBERT/E5         ChromaDB        Cosine/Inner        Top-K          Document
Input     Embedding          FAISS Search    Product             Selection      Context
```

## 9. Background Task Processing Workflow

### Task Queue Management Process
```
Task Creation → Queue Addition → Worker Assignment → Task Execution → Result Storage → Status Update
      ↓              ↓              ↓                ↓              ↓              ↓
  User Action    Background      Worker Pool      Function        Database       User
  (Download/     Task Queue      Assignment       Execution       Storage        Notification
   Process)
```

### Worker Task Execution Workflow
```
Task Dequeue → Parameter Validation → Function Execution → Error Handling → Result Storage
     ↓              ↓                    ↓                 ↓              ↓
  Task Queue    Input Validation    Download/Process    Try/Catch      Database
  Management    JSON Schema         Function Call       Error Log      Update
```

## 10. Error Handling and Recovery Workflows

### Graceful Degradation Process
```
Error Detection → Error Classification → Fallback Selection → Service Continuation → User Notification
       ↓              ↓                   ↓                  ↓                    ↓
   Exception      Import/API/DB        Dummy Functions     Reduced              Error
   Occurrence     Data/Network         Service Fallback    Functionality        Message
```

### Service Recovery Workflow
```
Service Failure → Health Check → Automatic Retry → Manual Intervention → Service Restoration
       ↓              ↓             ↓                ↓                  ↓
   Error Log      Service Test    Exponential      Admin Alert        Full
   Detection      Connectivity    Backoff          Notification       Recovery
```

## 11. Data Export and Reporting Workflow

### Database Export Process
```
Export Request → Table Selection → Data Extraction → Format Conversion → File Generation
       ↓              ↓               ↓                ↓                ↓
   User Menu      Table List       SQL Query        CSV/JSON         Downloads/
   Selection      Selection        Execution        Conversion       Export Files
```

### Report Generation Workflow
```
Report Request → Data Aggregation → Analysis Processing → Template Application → Report Output
       ↓              ↓                ↓                  ↓                    ↓
   User Query      Multi-Table      Statistical        Report Template      PDF/HTML
   Selection       JOIN Queries     Analysis           Rendering            Output
```

## 12. Configuration Management Workflow

### Configuration Loading Process
```
Application Start → Config File Reading → Environment Variable Override → Validation → Service Initialization
       ↓                ↓                      ↓                          ↓              ↓
   Startup         config.py              .env File                    Schema         Database/
   Process         Reading                Override                     Validation     API Setup
```

### Dynamic Configuration Update Workflow
```
Config Change → Validation → Service Notification → Graceful Restart → Service Continuation
       ↓            ↓              ↓                  ↓                ↓
   File Edit    Schema Check    Service Alert      Hot Reload       Updated
   Detection    Format Valid    Notification       Process          Configuration
```

## Workflow Integration Points

### Cross-Workflow Dependencies
- Data Download → Data Processing → Vector Indexing
- Entity Resolution → Risk Analysis → Reporting
- Query Processing → Tool Execution → Result Integration
- Error Handling → Service Recovery → Workflow Continuation

### Performance Optimization Points
- Parallel processing in data download workflows
- Caching in query processing workflows
- Batch processing in vector indexing workflows
- Connection pooling in database workflows

---

*This workflow documentation provides a comprehensive overview of the key processes and data flows in the GameCock AI system. Each workflow is designed for reliability, performance, and user experience optimization.*
