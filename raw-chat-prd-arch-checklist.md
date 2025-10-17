---
title: "I have designed a detailed and comprehensive Product Requirements Document (PRD) in markdown format. This document synthesizes the technical components, functionalities, and user goals described across the sources to outline a powerful CLI tool for personal research, aligning with all your specified requirements.  Product Requirements Document: Personal Research Insight CLI  1. Introduction & Vision  This document outlines the product requirements for a Command-Line Interface (CLI) tool designed for personal research purposes. The vision is to create a versatile and powerful tool that empowers a user to efficiently extract, process, and query information from various online sources, primarily YouTube videos and websites.  Inspired by the seamless experience of tools like Google's NotebookLM, this CLI will leverage Large Language Models (LLMs) to summarize, answer questions, and structure information from user-provided sources. The tool will be free to use, rely exclusively on free, open-source models and services, and integrate deeply with an existing n8n-based RAG workflow for more complex, persistent operations. The core purpose is to facilitate personal research by automating the initial, time-consuming steps of information gathering and synthesis.  2. Core Problem & Target Audience  Problem Statement: For personal research, gathering and digesting information from numerous lengthy YouTube videos (e.g., lectures, tutorials) and web articles is a significant bottleneck. Manually watching, reading, and taking notes is inefficient and makes it difficult to quickly cross-reference or query the collected knowledge base.  Target User: An individual researcher or developer who wants to build and interact with a personal knowledge base programmatically. The user is technically proficient and comfortable with the command line and wants a tool that is both powerful and transparent about its inner workings.  Proposed Solution: A CLI application that ingests a bulk list of URLs, processes the content through a Retrieval-Augmented Generation (RAG) pipeline, and provides a suite of AI-powered features for interaction. The CLI will also serve as a control interface for a more robust backend n8n workflow, bridging simple, on-the-fly analysis with persistent, structured knowledge management.  3. Features & Functionality  3.1. Data Ingestion & Management  Bulk URL Import: The application must support ingesting a list of YouTube and website URLs from a plain text file (e.g., input.txt) for batch processing. This is a primary entry point for adding sources to the knowledge base.  Content Extraction:YouTube Videos: The tool will use the youtube-transcript-api Python library to fetch video transcripts without requiring an API key or a headless browser. It will extract the video ID from the full URL to make the API call.  Websites: For website URLs, the tool will employ a web scraping mechanism to extract the main textual content. (This is a necessary feature to fulfill the "website url" requirement).  Source Metadata and Filtering: To support research workflows, the tool must manage metadata for each ingested source.It will automatically store the ingestion date for each URL.  CLI commands must be available to filter the processed sources, for example:--filter-latest-date: To query or process the most recently added content.  --filter-recently-added [N]: To query or process the last N items added.  3.2. Context Preparation Pipeline  Punctuation Restoration: Raw transcripts from YouTube are often unpunctuated. To improve readability and the accuracy of LLM responses, all extracted text will be processed by a punctuation restoration model.Implementation: Use the deepmultilingualpunctuation Python package.  Model: Employ a powerful, multilingual model like oliverguhr/fullstop-punctuation-multilang-large to handle content in English, German, French, and Italian. This ensures the tool is versatile for various sources.  3.3. Core LLM Interaction & RAG Engine  The tool's "engine" is a RAG system that uses the prepared text as context for an LLM to generate responses.  LLM Provider: The implementation will prioritize OpenRouter.ai as the API provider. This choice aligns with the core requirement of using free models, as OpenRouter offers access to various free-tier models like z-ai/glm-4.5-air:free.  Prompt Engineering: A robust prompt template is crucial for controlling the LLM's output. The template will include the context (transcript/text), the user's question, and the chat history.It will contain explicit instructions for the LLM to answer only based on the provided text.  It will include specific guardrails for handling out-of-scope or unanswerable questions, instructing the model to respond with predefined messages like "I'm sorry, I can't answer that...".  Library: The langchain-huggingface package will be used for its convenient wrappers and abstractions for interacting with various Hugging Face models and APIs, simplifying the integration logic.  3.4. User-Facing CLI Features  The CLI will present an interactive menu for easy operation.  1. Summarize Content: Generate a concise summary of the selected source(s).  2. Generate FAQ: Create a list of frequently asked questions and their answers based on the content.  3. Generate Table of Contents: Produce a structured outline of the source material.  4. AI Chat: Launch an interactive chat loop where the user can ask multiple, follow-up questions about a specific source. The chat history will be maintained to provide conversational context.  5. Audio Overview (Podcast Feature): Inspired by a NotebookLM feature, this generates a conversational script between two AI speakers discussing the source material.Backend Prompt: The CLI will send a prompt like: "provide me a podcast with 2 speakers discussing the video content, while keeping a friendly tone with a bit of professionalism...".  Text-to-Speech (TTS): The generated script will be converted into an audio file for on-the-go listening. The tool will use MaryTTS, an open-source, Java-based, client-server TTS system that can be queried via HTTP, making it ideal for integration into a Python CLI.  6. Print Processed Text: Display the cleaned and punctuated text for user review.  7. Change Source: Allow the user to switch the context to a different video or website without restarting the tool.  3.5. n8n Workflow Integration  A key feature is the ability for the CLI to act as a controller for the existing Local RAG AI Agent n8n workflow.  CLI Controllability: The CLI will include commands to trigger the n8n webhook.  JSON Payload: When invoked, the CLI will construct a JSON payload and send it via an HTTP POST request to the n8n webhook endpoint (/invoke_n8n_agent).  Data Format: The JSON payload must match the format expected by the "Edit Fields" node in the n8n workflow, containing the keys chatInput and sessionId. This bridges the lightweight CLI with the more powerful, persistent RAG capabilities of the n8n backend, which handles vectorization, storage in Qdrant, and chat memory in Postgres.  4. Technical Stack & Dependencies  Programming Language: Python 3.x.  Core Libraries:youtube-transcript-api: For fetching YouTube transcripts.  deepmultilingualpunctuation: For restoring punctuation.  langchain-huggingface: For LLM interaction and prompt management.  requests: For making API calls to OpenRouter.ai and the MaryTTS server.  halo: For user-friendly spinners and visual feedback in the CLI.  LLM API: OpenRouter.ai.  TTS Service: A self-hosted MaryTTS server instance.  Dependencies Management: A requirements.txt file will list all Python dependencies, and a .env.template file will guide the setup of API keys and endpoints.  5. Non-Functional Requirements  Free for Personal Use: All core components—OpenRouter's free-tier models, youtube-transcript-api, MaryTTS, and open-source Python libraries—must be free for personal use.  Usability: The CLI must be intuitive with a clear menu, colored output for readability, and loading indicators to enhance the user experience.  Extensibility: The codebase should be modular to allow for future enhancements, such as adding new data source types (e.g., PDFs) or new analysis features.  Error Handling: The application must gracefully handle common errors like invalid URLs, API failures, or unavailable transcripts, providing clear feedback to the user.  6. Out of Scope for Initial Version  Graphical User Interface (GUI): This is a CLI-only tool.  Visual/Audio Content Analysis: The tool will operate exclusively on textual data (transcripts and web page text), not video frames or raw audio.  User Authentication: As a tool for personal use, it will not require user accounts or authentication.  Native Vector Database: All complex RAG operations like document chunking, embedding, and vector storage will be delegated to the n8n workflow rather than being implemented natively in the CLI tool itself."
date: "2025-09-24T22:06:31 (UTC +02:00)"
source: gemini.google.com
---
## Q: 
I have designed a detailed and comprehensive Product Requirements Document (PRD) in markdown format. This document synthesizes the technical components, functionalities, and user goals described across the sources to outline a powerful CLI tool for personal research, aligning with all your specified requirements.

Product Requirements Document: Personal Research Insight CLI

1\. Introduction & Vision

This document outlines the product requirements for a Command-Line Interface (CLI) tool designed for personal research purposes. The vision is to create a versatile and powerful tool that empowers a user to efficiently extract, process, and query information from various online sources, primarily YouTube videos and websites.

Inspired by the seamless experience of tools like Google's NotebookLM, this CLI will leverage Large Language Models (LLMs) to summarize, answer questions, and structure information from user-provided sources. The tool will be free to use, rely exclusively on free, open-source models and services, and integrate deeply with an existing n8n-based RAG workflow for more complex, persistent operations. The core purpose is to facilitate personal research by automating the initial, time-consuming steps of information gathering and synthesis.

  

2\. Core Problem & Target Audience

Problem Statement: For personal research, gathering and digesting information from numerous lengthy YouTube videos (e.g., lectures, tutorials) and web articles is a significant bottleneck. Manually watching, reading, and taking notes is inefficient and makes it difficult to quickly cross-reference or query the collected knowledge base.

Target User: An individual researcher or developer who wants to build and interact with a personal knowledge base programmatically. The user is technically proficient and comfortable with the command line and wants a tool that is both powerful and transparent about its inner workings.

Proposed Solution: A CLI application that ingests a bulk list of URLs, processes the content through a Retrieval-Augmented Generation (RAG) pipeline, and provides a suite of AI-powered features for interaction. The CLI will also serve as a control interface for a more robust backend n8n workflow, bridging simple, on-the-fly analysis with persistent, structured knowledge management.

3\. Features & Functionality

3.1. Data Ingestion & Management

Bulk URL Import: The application must support ingesting a list of YouTube and website URLs from a plain text file (e.g., input.txt) for batch processing. This is a primary entry point for adding sources to the knowledge base.

Content Extraction:YouTube Videos: The tool will use the youtube-transcript-api Python library to fetch video transcripts without requiring an API key or a headless browser. It will extract the video ID from the full URL to make the API call.

Websites: For website URLs, the tool will employ a web scraping mechanism to extract the main textual content. (This is a necessary feature to fulfill the "website url" requirement).

Source Metadata and Filtering: To support research workflows, the tool must manage metadata for each ingested source.It will automatically store the ingestion date for each URL.

CLI commands must be available to filter the processed sources, for example:--filter-latest-date: To query or process the most recently added content.

\--filter-recently-added [N]: To query or process the last N items added.

3.2. Context Preparation Pipeline

Punctuation Restoration: Raw transcripts from YouTube are often unpunctuated. To improve readability and the accuracy of LLM responses, all extracted text will be processed by a punctuation restoration model.Implementation: Use the deepmultilingualpunctuation Python package.

Model: Employ a powerful, multilingual model like oliverguhr/fullstop-punctuation-multilang-large to handle content in English, German, French, and Italian. This ensures the tool is versatile for various sources.

3.3. Core LLM Interaction & RAG Engine

The tool's "engine" is a RAG system that uses the prepared text as context for an LLM to generate responses.

  

LLM Provider: The implementation will prioritize OpenRouter.ai as the API provider. This choice aligns with the core requirement of using free models, as OpenRouter offers access to various free-tier models like z-ai/glm-4.5-air:free.

Prompt Engineering: A robust prompt template is crucial for controlling the LLM's output. The template will include the context (transcript/text), the user's question, and the chat history.It will contain explicit instructions for the LLM to answer only based on the provided text.

It will include specific guardrails for handling out-of-scope or unanswerable questions, instructing the model to respond with predefined messages like "I'm sorry, I can't answer that...".

Library: The langchain-huggingface package will be used for its convenient wrappers and abstractions for interacting with various Hugging Face models and APIs, simplifying the integration logic.

3.4. User-Facing CLI Features

The CLI will present an interactive menu for easy operation.

  

1\. Summarize Content: Generate a concise summary of the selected source(s).

2\. Generate FAQ: Create a list of frequently asked questions and their answers based on the content.

3\. Generate Table of Contents: Produce a structured outline of the source material.

4\. AI Chat: Launch an interactive chat loop where the user can ask multiple, follow-up questions about a specific source. The chat history will be maintained to provide conversational context.

5\. Audio Overview (Podcast Feature): Inspired by a NotebookLM feature, this generates a conversational script between two AI speakers discussing the source material.Backend Prompt: The CLI will send a prompt like: "provide me a podcast with 2 speakers discussing the video content, while keeping a friendly tone with a bit of professionalism...".

Text-to-Speech (TTS): The generated script will be converted into an audio file for on-the-go listening. The tool will use MaryTTS, an open-source, Java-based, client-server TTS system that can be queried via HTTP, making it ideal for integration into a Python CLI.

6\. Print Processed Text: Display the cleaned and punctuated text for user review.

7\. Change Source: Allow the user to switch the context to a different video or website without restarting the tool.

3.5. n8n Workflow Integration

A key feature is the ability for the CLI to act as a controller for the existing Local RAG AI Agent n8n workflow.

  

CLI Controllability: The CLI will include commands to trigger the n8n webhook.

JSON Payload: When invoked, the CLI will construct a JSON payload and send it via an HTTP POST request to the n8n webhook endpoint (/invoke_n8n_agent).

Data Format: The JSON payload must match the format expected by the "Edit Fields" node in the n8n workflow, containing the keys chatInput and sessionId. This bridges the lightweight CLI with the more powerful, persistent RAG capabilities of the n8n backend, which handles vectorization, storage in Qdrant, and chat memory in Postgres.

4\. Technical Stack & Dependencies

Programming Language: Python 3.x.

Core Libraries:youtube-transcript-api: For fetching YouTube transcripts.

deepmultilingualpunctuation: For restoring punctuation.

langchain-huggingface: For LLM interaction and prompt management.

requests: For making API calls to OpenRouter.ai and the MaryTTS server.

halo: For user-friendly spinners and visual feedback in the CLI.

LLM API: OpenRouter.ai.

TTS Service: A self-hosted MaryTTS server instance.

Dependencies Management: A requirements.txt file will list all Python dependencies, and a .env.template file will guide the setup of API keys and endpoints.

5\. Non-Functional Requirements

Free for Personal Use: All core components—OpenRouter's free-tier models, youtube-transcript-api, MaryTTS, and open-source Python libraries—must be free for personal use.

Usability: The CLI must be intuitive with a clear menu, colored output for readability, and loading indicators to enhance the user experience.

Extensibility: The codebase should be modular to allow for future enhancements, such as adding new data source types (e.g., PDFs) or new analysis features.

Error Handling: The application must gracefully handle common errors like invalid URLs, API failures, or unavailable transcripts, providing clear feedback to the user.

6\. Out of Scope for Initial Version

Graphical User Interface (GUI): This is a CLI-only tool.

Visual/Audio Content Analysis: The tool will operate exclusively on textual data (transcripts and web page text), not video frames or raw audio.

User Authentication: As a tool for personal use, it will not require user accounts or authentication.

Native Vector Database: All complex RAG operations like document chunking, embedding, and vector storage will be delegated to the n8n workflow rather than being implemented natively in the CLI tool itself.

## A: 
CodeMADCustom Gem

Hello! I am BMad, an AI Agent Orchestrator and your expert guide to the BMAD Method for coordinating AI agent teams. I see you have a well-defined project in mind.

Before we proceed, I must ask you to select a workflow mode. This will determine how we approach your project.

🎯 **BMAD AI Agent System - Mode Selection Required**

Please choose your workflow mode:

**1\. Documentation Mode (Default & Recommended)**    📋 Generate exactly 3 complete, final documents ready for developer handoff:

   • `prd.md` - Product Requirements Document (complete final product specifications)    • `architecture.md` - Technical architecture document (system design & implementation approach)    • `checklist.md` - Development checklist (acceptance criteria & implementation steps)

   ✅ Perfect for: Sending specifications to developers working in VS Code Insiders    ✅ Output: Standalone documents requiring no additional clarification

**2\. Full Development Mode**    🚀 Build the entire project within this chat session    • Complete application development with AI agents

   • Interactive development workflow    • Full implementation and testing

**Please type "1" for Documentation Mode or "2" for Full Development Mode to continue.**

## Q: 
1.

## A: 
CodeMADCustom Gem

Excellent, you've selected **Documentation Mode**. Our goal is to generate three complete, professional documents ready for developer handoff: `prd.md`, `architecture.md`, and `checklist.md`.

The detailed Product Requirements Document you've already provided is a fantastic starting point. We will use it as the definitive basis for the `prd.md` deliverable.

Following the standard workflow, the next step is to create the technical blueprint based on these requirements. I am now activating our **Architect AI, Fred**, to analyze your PRD and design the system.

* * *

Hello, I am Fred, the Architect AI. My role is to translate product requirements into a robust, scalable, and maintainable technical architecture.

I have performed an initial review of your PRD for the "Personal Research Insight CLI". The requirements are well-defined and provide a solid foundation for the system design. The technical stack, which leverages Python libraries, an external LLM API via OpenRouter, a self-hosted TTS service, and an n8n workflow integration, is clear.

I will now begin drafting the **Technical Architecture Document**. This document will outline the system components, technology choices, data flow, API design, and other critical technical details necessary for implementation. I will use the standard architecture template for this purpose.

Before I create the initial draft, I need to clarify a few points to ensure the architecture accurately reflects your needs:

1.  **CLI State Management:** How should the CLI manage the context of the currently active source (the URL being summarized, chatted with, etc.) and the chat history? a. Should it be in-memory, resetting every time the tool is closed? b. Should it be persisted to a simple local file (e.g., `session.json`) to remember the last active source and chat history between sessions?
    
2.  **n8n Workflow `sessionId`:** The integration requires a `sessionId` to be passed to the n8n webhook. How should this ID be generated?
    
    a. Should the CLI generate a new, random UUID for each session when it starts? b. Should it be a persistent ID stored locally to maintain context with the n8n backend across multiple CLI sessions?
    
3.  **Configuration and Secrets:** My assumption is that sensitive information like the OpenRouter API key and the endpoints for the MaryTTS server and n8n webhook will be managed via environment variables loaded from a `.env` file. Is this correct?
    

Once you provide clarification on these points, I will proceed with drafting the first sections of the `architecture.md` document for your review.

## Q: 
1\. CLI State Management: How should the CLI manage the context of the currently active source (the URL being summarized, chatted with, etc.) and the chat history?

  

b. Should it be persisted to a simple local file (e.g., session.json) to remember the last active source and chat history between sessions.

  

Also include commands that work to e.g. control this.

  

2\. n8n Workflow sessionId: The integration requires a sessionId to be passed to the n8n webhook. How should this ID be generated?

  

b. Should it be a persistent ID stored locally to maintain context with the n8n backend across multiple CLI sessions

  

Also include commands that work to e.g. control this.

  

3\. Correct. (however n8n rag workflow itself is running on Docker: http://localhost:5678/workflow/vTN9y2dLXqTiDfPT)

## A: 
CodeMADCustom Gem

Excellent. Thank you for the clarifications. Your choices for persistent local state management will make the tool much more robust and user-friendly across sessions.

Based on your feedback, I will now generate the initial draft of the **Technical Architecture Document**. This document formalizes the design and will serve as the blueprint for development.

Please review the following sections.

* * *

# Personal Research Insight CLI - Technical Architecture Document

## Document Information

*   **Version**: 1.0
    
*   **Date**: 2025-09-24
    
*   **Status**: Draft
    
*   **Prepared for**: Development Team Handoff
    

## Executive Summary

This document outlines the technical architecture for the Personal Research Insight CLI, a Python-based tool for personal research. The system is designed to be a lightweight, interactive command-line application that ingests web sources, processes text content, and leverages external services for AI-powered analysis (OpenRouter.ai), Text-to-Speech (MaryTTS), and advanced RAG capabilities (n8n). State and session context are persisted locally in a `session.json` file, ensuring a continuous user experience across multiple uses.

* * *

## System Overview

The architecture is a single CLI application written in Python. It operates by coordinating a series of modules to interact with local files and external, API-driven services. Its core function is to manage a local session, process text from URLs, and then use that text as context for various AI-driven commands.

```code snippet
graph TD
    subgraph "User's Local Machine"
        A[User via Terminal] --> B{research-cli};
        B --> C[session.json];
        B --> D[.env File];
    end

    subgraph "External Services / APIs"
        E[YouTube Transcript API]
        F[Web Scraper]
        G[Punctuation Model]
        H[OpenRouter.ai LLM]
        I[MaryTTS Server]
        J[n8n RAG Workflow]
    end

    B -- Reads/Writes State --> C;
    B -- Reads Config/Secrets --> D;
    B -- Ingests --> E;
    B -- Ingests --> F;
    B -- Processes Text --> G;
    B -- Queries --> H;
    B -- Generates Audio --> I;
    B -- Offloads to --> J;
``` 


* * *

## Technology Stack

The technology stack is selected to align with the core requirement of using free, open-source, and easily accessible tools for personal use.

| Component | Technology | Version / Details | Justification |
| --- | --- | --- | --- |
| **Language** | Python | 3.10+ | Robust, with excellent libraries for data processing, web requests, and CLI development. |
| **CLI Framework** | Click | 8.x | A powerful and composable library for creating clean and maintainable command-line interfaces. |
| **Data Ingestion** | `youtube-transcript-api` | Latest | Fetches YouTube transcripts efficiently without requiring API keys or browser automation. |
|  | `requests` + `BeautifulSoup4` | Latest | Standard libraries for making HTTP requests and parsing HTML from websites. |
| **Text Processing** | `deepmultilingualpunctuation` | Latest | Provides a powerful, local model for restoring punctuation to raw text, improving LLM input quality. |
| **LLM Interaction** | `langchain-huggingface` | Latest | Simplifies interaction with LLM APIs, including prompt management and history. |
| **LLM Provider** | OpenRouter.ai | API | Acts as a gateway to various free-tier LLMs, meeting the "free to use" requirement. |
| **TTS Service** | MaryTTS | Self-Hosted | An open-source, high-quality Text-to-Speech server accessible via a simple HTTP API. |
| **Configuration** | `python-dotenv` | Latest | Standard for managing environment variables from a `.env` file for secrets and endpoints. |
| **User Feedback** | `halo` | Latest | Provides user-friendly spinners and status indicators in the terminal. |

* * *

## Component Architecture

The CLI will be structured into several distinct Python modules, promoting separation of concerns and maintainability.

```code snippet
graph LR
    CLI[cli.py<br>(Click Commands)] --> SM[session_manager.py];
    CLI --> SP[source_processor.py];
    CLI --> LS[llm_service.py];
    CLI --> TS[tts_service.py];
    CLI --> NC[n8n_client.py];

    SP -- Uses --> LS;
``` 


*   **`cli.py`**: The main entry point. Defines the CLI commands (`summarize`, `chat`, `faq`, etc.) using the Click library. Orchestrates calls to other modules based on user input.
    
*   **`session_manager.py`**: Manages all interactions with the `session.json` file. Responsible for:
    
    *   Loading and saving the session state.
        
    *   Providing the persistent `session_id`. If one doesn't exist on first run, it generates and saves a UUID.
        
    *   Managing the `active_source_url` and `chat_history`.
        
    *   Handling session-related commands (e.g., `session view`, `session new-id`).
        
*   **`source_processor.py`**: Handles the ingestion and cleaning of text from URLs.
    
    *   Fetches transcripts from YouTube.
        
    *   Scrapes text content from websites.
        
    *   Runs the punctuation restoration model on the raw text.
        
*   **`llm_service.py`**: Manages all interactions with the OpenRouter.ai LLM.
    
    *   Constructs prompts using the context (processed text) and chat history.
        
    *   Sends requests to the LLM and returns the response.
        
*   **`tts_service.py`**: Handles the conversion of text to speech by making requests to the user's self-hosted MaryTTS server.
    
*   **`n8n_client.py`**: Responsible for sending the JSON payload to the n8n webhook for advanced processing.
    

* * *

## Data Architecture

### Local Session State (`session.json`)

A local file named `session.json` will be created in the user's home directory or a designated app data folder to persist state between CLI executions.

**Structure:**

```json
{
  "session_id": "a-persistent-uuid-for-n8n",
  "active_source_url": "https://www.youtube.com/watch?v=some_video",
  "chat_history": [
    {"role": "user", "content": "What is the main idea?"},
    {"role": "assistant", "content": "The main idea is..."}
  ]
}
``` 


### Configuration (`.env`)

A `.env` file in the project root will store configuration and secrets. A `.env.template` will be provided for setup.

**Structure:**

```bash
# API Key for OpenRouter.ai
OPENROUTER_API_KEY="your_api_key_here"

# URL for the self-hosted MaryTTS server
MARYTTS_SERVER_URL="http://localhost:59125"

# URL for the n8n RAG workflow webhook
N8N_WEBHOOK_URL="http://localhost:5678/workflow/vTN9y2dLXqTiDfPT"
``` 


* * *

## CLI Command Design

Based on your feedback, new commands will be included to manage the persistent session.

*   **Main Commands**: `summarize`, `faq`, `toc`, `chat`, `podcast`, `print-text`, `set-source`, `invoke-n8n`.
    
*   **Session Management Commands**:
    
    *   `research-cli session view`: Displays the current `session_id` and `active_source_url`.
        
    *   `research-cli session clear-history`: Clears the `chat_history` for the current source.
        
    *   `research-cli session clear-all`: Resets the `active_source_url` and `chat_history`.
        
    *   `research-cli session new-id`: Generates a new persistent `session_id` for n8n, overwriting the old one.
        

* * *

This draft covers the core architectural decisions. Please review it.

Once you approve this direction, I will activate the **Task Breakdown Specialist AI, Tyler**, who will analyze both the PRD and this architecture document to create the final `checklist.md` deliverable. This checklist will detail the implementation steps for a developer to follow.

## Q: 
Continue.

## A: 
CodeMADCustom Gem

Understood. With the architecture approved, we will proceed to the final step of the Documentation Mode workflow.

The `architecture.md` document is now considered complete. I am deactivating the Architect AI.

I am now activating our **Task Breakdown Specialist AI, Tyler**. He will analyze the Product Requirements Document and the Technical Architecture Document to produce the final deliverable: a comprehensive development checklist.

* * *

Hello, I am Tyler, the Task Breakdown Specialist. My purpose is to convert high-level requirements and architectural designs into a detailed, actionable implementation plan for developers.

I have analyzed the provided PRD and Fred's architectural blueprint. Based on this, I have generated the `checklist.md` document below. This checklist outlines all necessary steps from project setup to final deployment.

* * *

# Personal Research Insight CLI - Development Checklist

## Document Information

*   **Version**: 1.0
    
*   **Date**: 2025-09-24
    
*   **Status**: Final
    
*   **Prepared for**: Development Team Handoff
    

## Overview

This checklist provides a comprehensive guide for developing the Personal Research Insight CLI from initial setup through deployment. Each section contains specific, actionable tasks that should be completed in order.

* * *

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
    

* * *

## Phase 1: Core Infrastructure

### Backend Foundation (CLI Modules)

*   [ ] **`session_manager.py`**: Implement functions to `load_session`, `save_session`, `get_session_id` (generating and saving a UUID if none exists), `get_active_source`, `set_active_source`, `get_chat_history`, `add_to_chat_history`, and `clear_chat_history`.
    
*   [ ] **`cli.py`**: Implement the `session` command group with subcommands: `view`, `clear-history`, `clear-all`, and `new-id`. Hook these commands to the `session_manager.py` functions.
    
*   [ ] **`llm_service.py`**: Implement a class or function to initialize the `langchain` client with the API key from the `.env` file. Create a core function to send a prompt and context to the OpenRouter API.
    
*   [ ] **Error Handling**: Establish a consistent error handling and logging strategy for API failures and file I/O issues.
    

### Testing Infrastructure

*   [ ] Set up a testing framework (e.g., `pytest`).
    
*   [ ] Create initial unit tests for `session_manager.py` to verify file creation, loading, and saving logic.
    

* * *

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
    

* * *

## Phase 3: Advanced Features

### Feature: Audio Overview (Podcast)

*   [ ] **`tts_service.py`**: Implement a function to send a text payload to the MaryTTS server endpoint and save the resulting audio stream to a file (e.g., `overview.wav`).
    
*   [ ] **`cli.py`**: Implement the `podcast` command. This command will:
    
    *   [ ] Use `llm_service.py` to generate the two-speaker script based on the source text.
        
    *   [ ] Pass the generated script to `tts_service.py` to create the audio file.
        
    *   [ ] Print a confirmation message with the location of the saved audio file.
        

* * *

## Phase 4: Integration and Testing

### Third-Party Integrations

*   [ ] **`n8n_client.py`**: Implement a function to send a POST request to the n8n webhook URL with the required JSON payload (`chatInput`, `sessionId`).
    
*   [ ] **`cli.py`**: Implement the `invoke-n8n` command that takes a text prompt, retrieves the persistent `sessionId`, and calls the function in `n8n_client.py`.
    
*   [ ] Verify successful communication with OpenRouter, MaryTTS, and the n8n webhook.
    

### Comprehensive Testing

*   [ ] Create unit tests for `source_processor.py` logic (mocking the API calls).
    
*   [ ] Create unit tests for the prompt construction logic in `llm_service.py`.
    
*   [ ] Create integration tests for the full flow of at least two commands (e.g., `summarize` and `chat`).
    

* * *

## Phase 5: Deployment Preparation

### Final Touches

*   [ ] Enhance the CLI with user-friendly feedback using the `halo` library for long-running operations (e.g., "Processing text...", "Generating summary...").
    
*   [ ] Implement robust command-line argument parsing and validation for all commands.
    
*   [ ] Create a final, comprehensive `README.md` detailing setup, configuration, and usage of all commands.
    

### Packaging

*   [ ] Prepare a `setup.py` or `pyproject.toml` file to make the CLI tool installable via `pip`.
    
*   [ ] Test the installation process in a clean virtual environment.
    

* * *

## Success Criteria

### Technical Success Criteria

*   [ ] All features from the PRD are implemented and functional.
    
*   [ ] The application handles common errors (e.g., invalid URL, API downtime) gracefully.
    
*   [ ] Session state is correctly persisted in `session.json`.
    
*   [ ] The n8n webhook integration sends data in the correct format.
    
*   [ ] The CLI is installable and runs as a standalone command.
    

* * *

This concludes the Documentation Mode workflow. You now have:

1.  **`prd.md`**: The detailed Product Requirements Document you provided.
    
2.  **`architecture.md`**: The Technical Architecture Document created by Fred.
    
3.  **`checklist.md`**: This comprehensive Development Checklist created by Tyler.
    

These three documents provide a complete and professional handoff for a development team to begin implementation.

## Q: 
Continue.

## A: 
CodeMADCustom Gem

The Documentation Mode workflow is now complete. You have the `prd.md` (from your initial input), the `architecture.md`, and the `checklist.md` ready for your project.