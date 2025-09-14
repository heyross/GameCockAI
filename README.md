# GamecockAI

GamecockAI is a Python-based application designed to download, process, and analyze financial data from public sources like the Securities and Exchange Commission (SEC) and the Commodity Futures Trading Commission (CFTC). It features a Retrieval-Augmented Generation (RAG) pipeline with an AI assistant named Raven that allows users to ask natural language questions about the collected data and get intelligent, context-aware responses.

## Features

- **Data Downloader**: Fetches bulk data from SEC, CFTC, and FRED (Federal Reserve Economic Data) websites.
- **Raven AI Assistant**: A powerful RAG-based chatbot that provides intelligent, context-aware responses about your financial data. Ask questions in natural language and get accurate, data-driven answers.
- **Data Sources**

- **SEC EDGAR**: Company filings, insider trades, and more
- **CFTC**: Swap Dealer and Major Swap Participant data
- **FRED (Federal Reserve Economic Data)**: Interest rate swaps, credit default swaps, and other economic indicators
- **AI Agent (SwapBot)**: A conversational AI that can perform tasks on your behalf. It can search for companies, manage watchlists, download and process data, and check the status of background jobs.
- **Company Watchlist**: Allows users to specify companies of interest to filter the data.
- **Database Management**: Provides tools for inspecting, exporting, and managing the local database.

## Workflows

### 1. Data Ingestion and Processing

1.  **Select Target Companies**: Users can search for and select specific companies to create a watchlist. This focuses the data processing on relevant entities.
2.  **Download Data**: Download data from various sources (SEC, CFTC, FRED)
- **Process Data**: Process downloaded data into the database, filtered according to the watchlist, and loaded into a SQLite database.

### 2. Interacting with the AI Agent

The application features a powerful AI agent named SwapBot that can perform a variety of tasks through a conversational interface. To chat with SwapBot, select option 4 from the main menu.

The AI is designed to be interactive. If your request is ambiguous, it will ask clarifying questions to ensure it understands your intent before taking action.

Here are some examples of what you can ask SwapBot to do:

- **Search for a company:**
  > `Find companies related to 'morgan'`

- **Add a company to your target list:**
  > `Add JP Morgan Chase to my target list.`
  *(Note: The AI may ask you to confirm which company if multiple matches are found.)*

- **View your target list:**
  > `Show me my target list.`

- **Start a background download:**
  > `Download the latest CFTC credit data.`
  
  The AI will queue the task and respond with a `task_id`.

- **Start a data processing job:**
  > `Process the downloaded credit data.`

- **Check the status of a background task:**
  > `What is the status of task [paste task_id here]?`

- **Get database statistics:**
  > `How many records are in the database?`

### 3. Database Management

- **View Statistics**: Get a summary of the data stored in the database.
- **Export Data**: Export data from the database to a CSV file for external analysis.
- **Reset Database**: Clear all data from the database to start fresh.

## License

GamecockAI is dual-licensed under the following terms:

1. **Non-Commercial Use**: Licensed under the [GNU Affero General Public License v3.0](LICENSE)
   - Free for personal, educational, and non-commercial use
   - Must include original copyright notice and license
   - Source code must be made available for any network use
   - No warranty or liability

2. **Commercial Use**: Requires a commercial license
   - For businesses, cloud providers, and SaaS offerings
   - Contact [Your Contact Email] for pricing and terms
   - See [COMMERCIAL_LICENSE.md](COMMERCIAL_LICENSE.md) for details

By using this software, you agree to the terms of the appropriate license.

## Getting Started

### Option 1: Windows Installer (Recommended for Most Users)

1. **Download the Installer**:
   - Download the latest `GamecockAI.msi` from the [Releases](https://github.com/yourusername/GameCockAI/releases) page

2. **Run the Installer**:
   - Double-click the `.msi` file and follow the installation wizard
   - The installer will create a Start Menu shortcut and desktop icon

3. **First Run**:
   - Launch GamecockAI from the Start Menu or desktop shortcut
   - The application will guide you through the initial setup
   - Enter your FRED API key when prompted

### Option 2: Manual Installation (For Developers)

1. **Prerequisites**
   - Python 3.7 or higher
   - FRED API key (free) from [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html)

2. **Automatic Setup**:
   - The application will automatically create and configure a virtual environment
   - All required Python packages will be installed automatically
   - First-time setup will guide you through the configuration process

3. **Configuration**:
   - On first run, the application will create a `.env` file from the template
   - Add your FRED API key to the `.env` file when prompted
   - (Optional) Configure other settings as needed

4. **Run the application**:
   - On Windows:
     ```bash
     launcher.bat
     ```
   - On macOS/Linux:
     ```bash
     python main.py
     ```

### Building the Installer (For Developers)

If you want to build the Windows installer yourself, see the [Installer/README.md](Installer/README.md) file for detailed instructions.

This will launch the command-line interface, where you can navigate through the different menus to use the application.

## Interacting with Raven AI

Raven is your intelligent assistant that can help you analyze financial data using natural language. To start a conversation with Raven:

1. From the main menu, select the option to chat with Raven
2. Ask questions in plain English, such as:
   - "What are the latest SEC filings for Apple?"
   - "Show me the trend for interest rate swaps over the past year"
   - "Compare the CFTC data between these two companies"
   - "What insights can you find about [company name]?"

Raven uses advanced RAG (Retrieval-Augmented Generation) technology to provide accurate, up-to-date answers based on the financial data in your database.
