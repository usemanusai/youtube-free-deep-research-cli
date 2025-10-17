# Personal Research Insight CLI - Development Checklist

## Document Information

*   **Version**: 1.0

*   **Date**: 2025-09-24

*   **Status**: Final

*   **Prepared for**: Development Team Handoff

## Overview

This checklist provides a comprehensive guide for developing the Personal Research Insight CLI from initial setup through deployment. Each section contains specific, actionable tasks that should be completed in order.

## Pre-Development Setup

### Environment Setup

*   [ ] Initialize a new Git repository.

*   [ ] Create and activate a Python virtual environment (e.g., `python -m venv venv`).

*   [ ] Create a `requirements.txt` file and add initial dependencies: `click`, `python-dotenv`, `requests`, `halo`, `youtube-transcript-api`, `beautifulsoup4`, `deepmultilingualpunctuation`, `langchain-huggingface`.

*   [ ] Install dependencies (`pip install -r requirements.txt`).

*   [ ] Create the `.env` file from the `.env.template` and populate it with the OpenRouter API key and correct URLs for MaryTTS and the n8n webhook.

*   [ ] Set up code linting and formatting tools (e.g., Black, Flake8).

### Project Initialization

*   [ ] Create the project structure with the specified module files: `cli.py`, `session_manager.py`, `source_processor.py`, `llm_service.py`, `tts_service.py`, `n8n_client.py`.

*   [ ] In `cli.py`, create the main Click command group.

*   [ ] In `session_manager.py`, implement the initial logic to create `session.json` in a user-appropriate directory if it doesn't exist.

*   [ ] Add a `.gitignore` file to exclude the virtual environment, `.env`, `__pycache__`, and other unnecessary files.

## Phase 1: Core Infrastructure

### Backend Foundation (CLI Modules)

*   [ ] **`session_manager.py`**: Implement functions to `load_session`, `save_session`, `get_session_id` (generating and saving a UUID if none exists), `get_active_source`, `set_active_source`, `get_chat_history`, `add_to_chat_history`, and `clear_chat_history`.

*   [ ] **`cli.py`**: Implement the `session` command group with subcommands: `view`, `clear-history`, `clear-all`, and `new-id`. Hook these commands to the `session_manager.py` functions.

*   [ ] **`llm_service.py`**: Implement a class or function to initialize the `langchain` client with the API key from the `.env` file. Create a core function to send a prompt and context to the OpenRouter API.

*   [ ] **Error Handling**: Establish a consistent error handling and logging strategy for API failures and file I/O issues.

### Testing Infrastructure

*   [ ] Set up a testing framework (e.g., `pytest`).

*   [ ] Create initial unit tests for `session_manager.py` to verify file creation, loading, and saving logic.

## Phase 2: Core Features Implementation

### Feature: Source Processing

*   [ ] **`source_processor.py`**: Implement the `get_youtube_transcript` function using `youtube-transcript-api`.

*   [ ] **`source_processor.py`**: Implement the `scrape_website_text` function using `requests` and `BeautifulSoup4`.

*   [ ] **`source_processor.py`**: Implement the `restore_punctuation` function using the `deepmultilingualpunctuation` library.

*   [ ] **`cli.py`**: Implement the `set-source <URL>` command to fetch content using the `source_processor`, process it, and save the URL as the `active_source_url` in the session.

*   [ ] **`cli.py`**: Implement the `print-text` command to display the processed text of the currently active source.

### Feature: LLM Interactions

*   [ ] **`cli.py`**: Implement the `summarize` command. It should load the active source's text, pass it to `llm_service.py` with a summarization prompt, and print the result.

*   [ ] **`cli.py`**: Implement the `faq` command, instructing the LLM to generate a list of questions and answers.

*   [ ] **`cli.py`**: Implement the `toc` command, instructing the LLM to generate a table of contents.

*   [ ] **`cli.py`**: Implement the `chat` command. This will start an interactive loop that takes user input, adds it to the chat history, sends the full history and context to the LLM, prints the response, and saves the updated history to `session.json`.

## Phase 3: Advanced Features

### Feature: Audio Overview (Podcast)

*   [ ] **`tts_service.py`**: Implement a function to send a text payload to the MaryTTS server endpoint and save the resulting audio stream to a file (e.g., `overview.wav`).

*   [ ] **`cli.py`**: Implement the `podcast` command. This command will:

    *   [ ] Use `llm_service.py` to generate the two-speaker script based on the source text.

    *   [ ] Pass the generated script to `tts_service.py` to create the audio file.

    *   [ ] Print a confirmation message with the location of the saved audio file.

## Phase 4: Integration and Testing

### Third-Party Integrations

*   [ ] **`n8n_client.py`**: Implement a function to send a POST request to the n8n webhook URL with the required JSON payload (`chatInput`, `sessionId`).

*   [ ] **`cli.py`**: Implement the `invoke-n8n` command that takes a text prompt, retrieves the persistent `sessionId`, and calls the function in `n8n_client.py`.

*   [ ] Verify successful communication with OpenRouter, MaryTTS, and the n8n webhook.

### Comprehensive Testing

*   [ ] Create unit tests for `source_processor.py` logic (mocking the API calls).

*   [ ] Create unit tests for the prompt construction logic in `llm_service.py`.

*   [ ] Create integration tests for the full flow of at least two commands (e.g., `summarize` and `chat`).

## Phase 5: Deployment Preparation

### Final Touches

*   [ ] Enhance the CLI with user-friendly feedback using the `halo` library for long-running operations (e.g., "Processing text...", "Generating summary...").

*   [ ] Implement robust command-line argument parsing and validation for all commands.

*   [ ] Create a final, comprehensive `README.md` detailing setup, configuration, and usage of all commands.

### Packaging

*   [ ] Prepare a `setup.py` or `pyproject.toml` file to make the CLI tool installable via `pip`.

*   [ ] Test the installation process in a clean virtual environment.

## Success Criteria

### Technical Success Criteria

*   [ ] All features from the PRD are implemented and functional.

*   [ ] The application handles common errors (e.g., invalid URL, API downtime) gracefully.

*   [ ] Session state is correctly persisted in `session.json`.

*   [ ] The n8n webhook integration sends data in the correct format.

*   [ ] The CLI is installable and runs as a standalone command.
