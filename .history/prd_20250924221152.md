---
title: "I have designed a detailed and comprehensive Product Requirements Document (PRD) in markdown format. This document synthesizes the technical components, functionalities, and user goals described across the sources to outline a powerful CLI tool for personal research, aligning with all your specified requirements.  Product Requirements Document: Personal Research Insight CLI  1. Introduction & Vision  This document outlines the product requirements for a Command-Line Interface (CLI) tool designed for personal research purposes. The vision is to create a versatile and powerful tool that empowers a user to efficiently extract, process, and query information from various online sources, primarily YouTube videos and websites.  Inspired by the seamless experience of tools like Google's NotebookLM, this CLI will leverage Large Language Models (LLMs) to summarize, answer questions, and structure information from user-provided sources. The tool will be free to use, rely exclusively on free, open-source models and services, and integrate deeply with an existing n8n-based RAG workflow for more complex, persistent operations. The core purpose is to facilitate personal research by automating the initial, time-consuming steps of information gathering and synthesis.  2. Core Problem & Target Audience  Problem Statement: For personal research, gathering and digesting information from numerous lengthy YouTube videos (e.g., lectures, tutorials) and web articles is a significant bottleneck. Manually watching, reading, and taking notes is inefficient and makes it difficult to quickly cross-reference or query the collected knowledge base.  Target User: An individual researcher or developer who wants to build and interact with a personal knowledge base programmatically. The user is technically proficient and comfortable with the command line and wants a tool that is both powerful and transparent about its inner workings.  Proposed Solution: A CLI application that ingests a bulk list of URLs, processes the content through a Retrieval-Augmented Generation (RAG) pipeline, and provides a suite of AI-powered features for interaction. The CLI will also serve as a control interface for a more robust backend n8n workflow, bridging simple, on-the-fly analysis with persistent, structured knowledge management.  3. Features & Functionality  3.1. Data Ingestion & Management  Bulk URL Import: The application must support ingesting a list of YouTube and website URLs from a plain text file (e.g., input.txt) for batch processing. This is a primary entry point for adding sources to the knowledge base.  Content Extraction:YouTube Videos: The tool will use the youtube-transcript-api Python library to fetch video transcripts without requiring an API key or a headless browser. It will extract the video ID from the full URL to make the API call.  Websites: For website URLs, the tool will employ a web scraping mechanism to extract the main textual content. (This is a necessary feature to fulfill the "website url" requirement).  Source Metadata and Filtering: To support research workflows, the tool must manage metadata for each ingested source.It will automatically store the ingestion date for each URL.  CLI commands must be available to filter the processed sources, for example:--filter-latest-date: To query or process the most recently added content.  --filter-recently-added [N]: To query or process the last N items added.  3.2. Context Preparation Pipeline  Punctuation Restoration: Raw transcripts from YouTube are often unpunctuated. To improve readability and the accuracy of LLM responses, all extracted text will be processed by a punctuation restoration model.Implementation: Use the deepmultilingualpunctuation Python package.  Model: Employ a powerful, multilingual model like oliverguhr/fullstop-punctuation-multilang-large to handle content in English, German, French, and Italian. This ensures the tool is versatile for various sources.  3.3. Core LLM Interaction & RAG Engine  The tool's "engine" is a RAG system that uses the prepared text as context for an LLM to generate responses.  LLM Provider: The implementation will prioritize OpenRouter.ai as the API provider. This choice aligns with the core requirement of using free models, as OpenRouter offers access to various free-tier models like z-ai/glm-4.5-air:free.  Prompt Engineering: A robust prompt template is crucial for controlling the LLM's output. The template will include the context (transcript/text), the user's question, and the chat history.It will contain explicit instructions for the LLM to answer only based on the provided text.  It will include specific guardrails for handling out-of-scope or unanswerable questions, instructing the model to respond with predefined messages like "I'm sorry, I can't answer that...".  Library: The langchain-huggingface package will be used for its convenient wrappers and abstractions for interacting with various Hugging Face models and APIs, simplifying the integration logic.  3.4. User-Facing CLI Features  The CLI will present an interactive menu for easy operation.  1. Summarize Content: Generate a concise summary of the selected source(s).  2. Generate FAQ: Create a list of frequently asked questions and their answers based on the content.  3. Generate Table of Contents: Produce a structured outline of the source material.  4. AI Chat: Launch an interactive chat loop where the user can ask multiple, follow-up questions about a specific source. The chat history will be maintained to provide conversational context.  5. Audio Overview (Podcast Feature): Inspired by a NotebookLM feature, this generates a conversational script between two AI speakers discussing the source material.Backend Prompt: The CLI will send a prompt like: "provide me a podcast with 2 speakers discussing the video content, while keeping a friendly tone with a bit of professionalism...".  Text-to-Speech (TTS): The generated script will be converted into an audio file for on-the-go listening. The tool will use MaryTTS, an open-source, Java-based, client-server TTS system that can be queried via HTTP, making it ideal for integration into a Python CLI.  6. Print Processed Text: Display the cleaned and punctuated text for user review.  7. Change Source: Allow the user to switch the context to a different video or website without restarting the tool.  3.5. n8n Workflow Integration  A key feature is the ability for the CLI to act as a controller for the existing Local RAG AI Agent n8n workflow.  CLI Controllability: The CLI will include commands to trigger the n8n webhook.  JSON Payload: When invoked, the CLI will construct a JSON payload and send it via an HTTP POST request to the n8n webhook endpoint (/invoke_n8n_agent).  Data Format: The JSON payload must match the format expected by the "Edit Fields" node in the n8n workflow, containing the keys chatInput and sessionId. This bridges the lightweight CLI with the more powerful, persistent RAG capabilities of the n8n backend, which handles vectorization, storage in Qdrant, and chat memory in Postgres.  4. Technical Stack & Dependencies  Programming Language: Python 3.x.  Core Libraries:youtube-transcript-api: For fetching YouTube transcripts.  deepmultilingualpunctuation: For restoring punctuation.  langchain-huggingface: For LLM interaction and prompt management.  requests: For making API calls to OpenRouter.ai and the MaryTTS server.  halo: For user-friendly spinners and visual feedback in the CLI.  LLM API: OpenRouter.ai.  TTS Service: A self-hosted MaryTTS server instance.  Dependencies Management: A requirements.txt file will list all Python dependencies, and a .env.template file will guide the setup of API keys and endpoints.  5. Non-Functional Requirements  Free for Personal Use: All core components—OpenRouter's free-tier models, youtube-transcript-api, MaryTTS, and open-source Python libraries—must be free for personal use.  Usability: The CLI must be intuitive with a clear menu, colored output for readability, and loading indicators to enhance the user experience.  Extensibility: The codebase should be modular to allow for future enhancements, such as adding new data source types (e.g., PDFs) or new analysis features.  Error Handling: The application must gracefully handle common errors like invalid URLs, API failures, or unavailable transcripts, providing clear feedback to the user.  6. Out of Scope for Initial Version  Graphical User Interface (GUI): This is a CLI-only tool.  Visual/Audio Content Analysis: The tool will operate exclusively on textual data (transcripts and web page text), not video frames or raw audio.  User Authentication: As a tool for personal use, it will not require user accounts or authentication.  Native Vector Database: All complex RAG operations like document chunking, embedding, and vector storage will be delegated to the n8n workflow rather than being implemented natively in the CLI tool itself."
date: "2025-09-24T22:06:31 (UTC +02:00)"
source: gemini.google.com
# Personal Research Insight CLI

## Product Requirements Document

### 1. Introduction & Vision

This document outlines the product requirements for a Command-Line Interface (CLI) tool designed for personal research purposes. The vision is to create a versatile and powerful tool that empowers a user to efficiently extract, process, and query information from various online sources, primarily YouTube videos and websites.

Inspired by the seamless experience of tools like Google's NotebookLM, this CLI will leverage Large Language Models (LLMs) to summarize, answer questions, and structure information from user-provided sources. The tool will be free to use, rely exclusively on free, open-source models and services, and integrate deeply with an existing n8n-based RAG workflow for more complex, persistent operations. The core purpose is to facilitate personal research by automating the initial, time-consuming steps of information gathering and synthesis.

### 2. Core Problem & Target Audience

**Problem Statement:** For personal research, gathering and digesting information from numerous lengthy YouTube videos (e.g., lectures, tutorials) and web articles is a significant bottleneck. Manually watching, reading, and taking notes is inefficient and makes it difficult to quickly cross-reference or query the collected knowledge base.

**Target User:** An individual researcher or developer who wants to build and interact with a personal knowledge base programmatically. The user is technically proficient and comfortable with the command line and wants a tool that is both powerful and transparent about its inner workings.

**Proposed Solution:** A CLI application that ingests a bulk list of URLs, processes the content through a Retrieval-Augmented Generation (RAG) pipeline, and provides a suite of AI-powered features for interaction. The CLI will also serve as a control interface for a more robust backend n8n workflow, bridging simple, on-the-fly analysis with persistent, structured knowledge management.

### 3. Features & Functionality

#### 3.1. Data Ingestion & Management

**Bulk URL Import:** The application must support ingesting a list of YouTube and website URLs from a plain text file (e.g., input.txt) for batch processing. This is a primary entry point for adding sources to the knowledge base.

**Content Extraction:**
- **YouTube Videos:** The tool will use the youtube-transcript-api Python library to fetch video transcripts without requiring an API key or a headless browser. It will extract the video ID from the full URL to make the API call.
- **Websites:** For website URLs, the tool will employ a web scraping mechanism to extract the main textual content. (This is a necessary feature to fulfill the "website url" requirement).

**Source Metadata and Filtering:** To support research workflows, the tool must manage metadata for each ingested source. It will automatically store the ingestion date for each URL.

CLI commands must be available to filter the processed sources, for example:
- `--filter-latest-date`: To query or process the most recently added content.
- `--filter-recently-added [N]`: To query or process the last N items added.

#### 3.2. Context Preparation Pipeline

**Punctuation Restoration:** Raw transcripts from YouTube are often unpunctuated. To improve readability and the accuracy of LLM responses, all extracted text will be processed by a punctuation restoration model.

- **Implementation:** Use the deepmultilingualpunctuation Python package.
- **Model:** Employ a powerful, multilingual model like oliverguhr/fullstop-punctuation-multilang-large to handle content in English, German, French, and Italian. This ensures the tool is versatile for various sources.

#### 3.3. Core LLM Interaction & RAG Engine

The tool's "engine" is a RAG system that uses the prepared text as context for an LLM to generate responses.

**LLM Provider:** The implementation will prioritize OpenRouter.ai as the API provider. This choice aligns with the core requirement of using free models, as OpenRouter offers access to various free-tier models like z-ai/glm-4.5-air:free.

**Prompt Engineering:** A robust prompt template is crucial for controlling the LLM's output. The template will include the context (transcript/text), the user's question, and the chat history. It will contain explicit instructions for the LLM to answer only based on the provided text.

It will include specific guardrails for handling out-of-scope or unanswerable questions, instructing the model to respond with predefined messages like "I'm sorry, I can't answer that...".

**Library:** The langchain-huggingface package will be used for its convenient wrappers and abstractions for interacting with various Hugging Face models and APIs, simplifying the integration logic.

#### 3.4. User-Facing CLI Features

The CLI will present an interactive menu for easy operation.

1. **Summarize Content:** Generate a concise summary of the selected source(s).
2. **Generate FAQ:** Create a list of frequently asked questions and their answers based on the content.
3. **Generate Table of Contents:** Produce a structured outline of the source material.
4. **AI Chat:** Launch an interactive chat loop where the user can ask multiple, follow-up questions about a specific source. The chat history will be maintained to provide conversational context.
5. **Audio Overview (Podcast Feature):** Inspired by a NotebookLM feature, this generates a conversational script between two AI speakers discussing the source material.

   - **Backend Prompt:** The CLI will send a prompt like: "provide me a podcast with 2 speakers discussing the video content, while keeping a friendly tone with a bit of professionalism...".
   - **Text-to-Speech (TTS):** The generated script will be converted into an audio file for on-the-go listening. The tool will use MaryTTS, an open-source, Java-based, client-server TTS system that can be queried via HTTP, making it ideal for integration into a Python CLI.

6. **Print Processed Text:** Display the cleaned and punctuated text for user review.
7. **Change Source:** Allow the user to switch the context to a different video or website without restarting the tool.

#### 3.5. n8n Workflow Integration

A key feature is the ability for the CLI to act as a controller for the existing Local RAG AI Agent n8n workflow.

**CLI Controllability:** The CLI will include commands to trigger the n8n webhook.

**JSON Payload:** When invoked, the CLI will construct a JSON payload and send it via an HTTP POST request to the n8n webhook endpoint (/invoke_n8n_agent).

**Data Format:** The JSON payload must match the format expected by the "Edit Fields" node in the n8n workflow, containing the keys chatInput and sessionId. This bridges the lightweight CLI with the more powerful, persistent RAG capabilities of the n8n backend, which handles vectorization, storage in Qdrant, and chat memory in Postgres.

### 4. Technical Stack & Dependencies

**Programming Language:** Python 3.x.

**Core Libraries:**
- youtube-transcript-api: For fetching YouTube transcripts.
- deepmultilingualpunctuation: For restoring punctuation.
- langchain-huggingface: For LLM interaction and prompt management.
- requests: For making API calls to OpenRouter.ai and the MaryTTS server.
- halo: For user-friendly spinners and visual feedback in the CLI.
- LLM API: OpenRouter.ai.
- TTS Service: A self-hosted MaryTTS server instance.

**Dependencies Management:** A requirements.txt file will list all Python dependencies, and a .env.template file will guide the setup of API keys and endpoints.

### 5. Non-Functional Requirements

**Free for Personal Use:** All core components—OpenRouter's free-tier models, youtube-transcript-api, MaryTTS, and open-source Python libraries—must be free for personal use.

**Usability:** The CLI must be intuitive with a clear menu, colored output for readability, and loading indicators to enhance the user experience.

**Extensibility:** The codebase should be modular to allow for future enhancements, such as adding new data source types (e.g., PDFs) or new analysis features.

**Error Handling:** The application must gracefully handle common errors like invalid URLs, API failures, or unavailable transcripts, providing clear feedback to the user.

### 6. Out of Scope for Initial Version

- **Graphical User Interface (GUI):** This is a CLI-only tool.
- **Visual/Audio Content Analysis:** The tool will operate exclusively on textual data (transcripts and web page text), not video frames or raw audio.
- **User Authentication:** As a tool for personal use, it will not require user accounts or authentication.
- **Native Vector Database:** All complex RAG operations like document chunking, embedding, and vector storage will be delegated to the n8n workflow rather than being implemented natively in the CLI tool itself.
