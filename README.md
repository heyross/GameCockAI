# GamecockAI

GamecockAI is a Python-based application designed to download, process, and analyze financial data from public sources like the Securities and Exchange Commission (SEC) and the Commodity Futures Trading Commission (CFTC). It features a Retrieval-Augmented Generation (RAG) pipeline that allows users to ask natural language questions about the collected data.

## Features

- **Data Downloader**: Fetches bulk data from SEC and CFTC websites.
- **Data Processor**: Extracts and transforms data from downloaded files and loads it into a local database.
- **AI Agent (SwapBot)**: A conversational AI that can perform tasks on your behalf. It can search for companies, manage watchlists, download and process data, and check the status of background jobs.
- **Company Watchlist**: Allows users to specify companies of interest to filter the data.
- **Database Management**: Provides tools for inspecting, exporting, and managing the local database.

## Workflows

### 1. Data Ingestion and Processing

1.  **Select Target Companies**: Users can search for and select specific companies to create a watchlist. This focuses the data processing on relevant entities.
2.  **Download Data**: The application can download various datasets, including CFTC swap data and SEC filings.
3.  **Process Data**: Downloaded data is processed, filtered according to the watchlist, and loaded into a SQLite database.

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

## Getting Started

1.  **Prerequisites**: Ensure you have Python and pip installed. This project also uses `ollama` to run the language model locally.
2.  **Installation**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Application**:
    ```bash
    python main.py
    ```

This will launch the command-line interface, where you can navigate through the different menus to use the application.
