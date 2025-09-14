# Raven Financial Analytics

Raven is an advanced financial data analysis platform designed to download, process, and analyze financial data from multiple public sources including the Securities and Exchange Commission (SEC), Commodity Futures Trading Commission (CFTC), and Federal Reserve Economic Data (FRED). The platform features a powerful Retrieval-Augmented Generation (RAG) pipeline with an AI assistant that provides intelligent, context-aware responses to your financial data queries.

## Features

- **Multi-Source Data Integration**: Seamlessly aggregates data from multiple authoritative financial sources
- **Raven AI Assistant**: A sophisticated RAG-based chatbot that understands complex financial queries and provides accurate, data-driven insights
- **Comprehensive Data Processing**: Automated pipelines for downloading, cleaning, and structuring financial data
- **Advanced Analytics**: Built-in tools for time series analysis, trend detection, and financial modeling

### Data Sources

- **SEC EDGAR**: Comprehensive access to corporate filings, including:
  - 10-K, 10-Q, 8-K reports
  - Form 13F institutional holdings
  - N-CEN and N-PORT fund disclosures
  - Insider trading reports

- **CFTC Data**: Detailed swap dealer and major swap participant information
  - Swap dealer registrations
  - SEF (Swap Execution Facility) information
  - Historical swap data reporting

- **FRED Economic Data**: Extensive economic indicators including:
  - Interest rates (EFFR, SOFR, Treasury yields)
  - Market indicators (VIX, credit spreads)
  - Economic indicators (GDP, unemployment, inflation)
  - Financial conditions indices

- **AI-Powered Analysis**: Raven's advanced capabilities include:
  - Natural language query processing
  - Context-aware financial analysis
  - Automated report generation
  - Anomaly detection in financial data
  - Predictive analytics and forecasting

## Key Capabilities

### 1. Data Ingestion and Processing Pipeline

1. **Targeted Data Collection**
   - Create custom watchlists of companies and financial instruments
   - Schedule automated data refreshes
   - Filter and preprocess data during download

2. **Comprehensive Data Processing**
   - Automated data validation and cleaning
   - Normalization across different data sources
   - Time-series alignment for cross-dataset analysis
   - Handling of missing and incomplete data

3. **Advanced Database Management**
   - SQLite-based storage with optimized schemas
   - Efficient indexing for fast query performance
   - Data versioning and history tracking
   - Secure storage of sensitive information

### 2. Interacting with Raven AI

Raven's AI assistant provides a natural language interface to your financial data. Access it by selecting the chat option from the main menu.

#### Example Queries

**Market Analysis**
> "Show me the correlation between VIX and S&P 500 returns"
> "Analyze recent insider trading activity in the tech sector"
> "Compare interest rate swap trends between US and EU markets"

**Regulatory Research**
> "Find all 13F filings mentioning AI investments in Q2 2023"
> "Show me the latest N-PORT filings for BlackRock funds"
> "Analyze changes in CFTC swap dealer positions over the last quarter"

**Economic Indicators**
> "Plot the yield curve using the latest Treasury data"
> "Compare current inflation metrics with historical averages"
> "Show me the relationship between unemployment and consumer sentiment"

**Data Management**
> "Update all SEC filings for my watchlist companies"
> "Process the latest FRED economic indicators"
> "Generate a report on data completeness and quality"

### 3. Database Management

- **View Statistics**: Get a summary of the data stored in the database.
- **Export Data**: Export data from the database to a CSV file for external analysis.
- **Reset Database**: Clear all data from the database to start fresh.

## License

Raven Financial Analytics is dual-licensed under the following terms:

1. **Non-Commercial Use**: Licensed under the [GNU Affero General Public License v3.0](LICENSE)
   - Free for personal, educational, and non-commercial use
   - Must include original copyright notice and license
   - Source code must be made available for any network use
   - No warranty or liability

2. **Commercial Use**: Requires a commercial license
   - For businesses, financial institutions, and professional services
   - Includes priority support and additional features
   - Contact [Your Contact Email] for pricing and terms
   - See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) for details

By using this software, you agree to the terms of the appropriate license.

## Getting Started

### Option 1: Windows Installer (Recommended for Most Users)

1. **Download the Installer**:
   - Download the latest `RavenAnalytics.msi` from the [Releases](https://github.com/yourusername/GameCockAI/releases) page

2. **Run the Installer**:
   - Double-click the `.msi` file and follow the installation wizard
   - The installer will create a Start Menu shortcut and desktop icon

3. **First Run**:
   - Launch Raven Analytics from the Start Menu or desktop shortcut
   - The application will guide you through the initial setup
   - Enter your FRED API key (get one from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html))
   - Configure your preferred data sources and update frequencies

### Option 2: Manual Installation (For Developers)

1. **Prerequisites**
   - Python 3.9 or higher
   - FRED API key (free) from [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html)
   - Git (for version control)

2. **Setup**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/GameCockAI.git
   cd GameCockAI
   
   # Create and activate virtual environment
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Configure environment
   copy .env_template .env
   # Edit .env to add your FRED API key and other settings
   
   # Initialize the database
   python -c "from GameCockAI.database import create_db_and_tables; create_db_and_tables()"
   ```

3. **Run the application**:
   ```bash
   # Start the application
   python main.py
   ```

4. **Development Mode**:
   ```bash
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Run tests
   python -m pytest
   
   # Run with hot-reload for development
   python -m uvicorn main:app --reload
   ```

## Advanced Configuration

### Data Source Configuration

Raven supports configuration of various data sources through the `config.py` file or environment variables:

```python
# FRED API Configuration
FRED_API_KEY = "your_api_key_here"
FRED_UPDATE_FREQUENCY = "daily"  # or "weekly", "monthly"

# SEC EDGAR Configuration
SEC_RATE_LIMIT = 10  # Requests per second
SEC_USER_AGENT = "Your Company Name - Your Email"

# CFTC Configuration
CFTC_UPDATE_FREQUENCY = "weekly"

# Database Configuration
DATABASE_URI = "sqlite:///raven.db"
MAX_DB_CONNECTIONS = 10
```

### Building the Installer (For Developers)

To create a Windows installer for Raven:

1. Install NSIS (Nullsoft Scriptable Install System)
2. Run the build script:
   ```bash
   cd Installer
   .\build_installer.bat
   ```
3. The installer will be created in the `dist` directory

For detailed instructions, see the [Installer/README.md](Installer/README.md) file.

## Advanced Features

### Raven AI Engine

Raven's AI capabilities are powered by state-of-the-art machine learning models and include:

- **Natural Language Understanding**: Process complex financial queries with industry-specific terminology
- **Contextual Awareness**: Maintains conversation context and remembers previous interactions
- **Multi-modal Analysis**: Correlates data across different sources and formats
- **Anomaly Detection**: Identifies unusual patterns and potential market-moving events
- **Predictive Analytics**: Projects trends and forecasts based on historical data

### FRED Data Integration

Raven provides comprehensive access to FRED's economic data, including:

- **Interest Rates**: EFFR, SOFR, Treasury yields across maturities
- **Market Indicators**: VIX, credit spreads, volatility measures
- **Economic Indicators**: GDP, unemployment, inflation metrics (CPI, PCE)
- **Financial Conditions**: Various financial conditions indices

### SEC and CFTC Data Processing

- **Form 13F**: Institutional investment holdings with historical tracking
- **N-CEN/N-PORT**: Detailed fund holdings and risk metrics
- **CFTC Reports**: Swap dealer positions and market participation
- **SEC Filings**: 10-K, 10-Q, 8-K, and other corporate disclosures
