Development & Deployment Checklist: JAEGIS NexusSync
This checklist outlines the key tasks and milestones required to successfully decommission the 'Local RAG AI Agent' n8n workflow and deploy the new code-based JAEGIS NexusSync CLI application. This list covers initial setup, core feature development, testing, documentation, and final deployment.
Phase 1: Project Setup & Foundational Work
• [ ] 1.1. Fork & Rebrand youtube-free-deep-research-cli:
    ◦ [ ] Fork the usemanusai/youtube-free-deep-research-cli repository to create the new project base [1, 2].
    ◦ [ ] Rename the project to jaegis-nexus-sync and update all relevant package files (pyproject.toml, setup.py) and branding [3, 4].
    ◦ [ ] Set up a new virtual environment and install dependencies in development mode (pip install -e .) [5].
• [ ] 1.2. Configuration & Environment Setup:
    ◦ [ ] Create a .env.template file consolidating all required API keys and configuration variables (YouTube, OpenRouter, Google Drive, Ollama, Qdrant, Tavily) [6].
    ◦ [ ] Implement a robust configuration management module (src/jaegis_nexus_sync/core/config.py) to load these variables securely [7].
    ◦ [ ] Update the CLI to include a command for initializing the .env file from the template.
• [ ] 1.3. Google Drive API Integration Setup:
    ◦ [ ] Create OAuth 2.0 Credentials: Guide the user on how to create a new project in the Google Cloud Console, enable the Drive API, and generate OAuth 2.0 credentials (client_secret.json) [8, 9].
    ◦ [ ] Define Scopes: Identify the most narrowly focused scopes needed. Start with non-sensitive scopes like https://www.googleapis.com/auth/drive.file or https://www.googleapis.com/auth/drive.readonly to ensure a streamlined user consent process [10-12].
    ◦ [ ] Implement OAuth 2.0 Flow: Develop a secure, code-based OAuth 2.0 flow that allows the CLI to request user consent, exchange the authorization code for an access token and a refresh token, and securely store the refresh token for offline access [13-15].
Phase 2: Decommissioning n8n - Core Functionality Replacement
• [ ] 2.1. Replace Google Drive Triggers (File Created/File Updated):
    ◦ [ ] Implement a GoogleDriveWatcher module within the background service (APScheduler) [16].
    ◦ [ ] This service will periodically poll a specified Google Drive folder for new or modified files, replicating the trigger functionality from the n8n workflow [17, 18].
    ◦ [ ] Implement a SQLite-backed processing queue to add jobs for detected file changes, ensuring robust and sequential processing [19].
• [ ] 2.2. Replace Document Ingestion Pipeline:
    ◦ [ ] File Download & Conversion: Create a ContentProcessor service that downloads files from Google Drive using the file ID [20].
    ◦ [ ] For Google Docs, convert to clean markdown, preserving structure [21, 22].
    ◦ [ ] For PDFs and images, integrate an OCR service (e.g., Mistral OCR) to extract structured markdown, replacing the n8n workflow's plain text extraction [23, 24].
    ◦ [ ] For other file types (20+ supported by the base CLI), implement appropriate conversion-to-markdown logic [25].
• [ ] 2.3. Replace Text Splitting (RecursiveCharacterTextSplitter):
    ◦ [ ] Implement Markdown-Aware Splitting: Configure the text splitter to explicitly split documents by markdown headings. This is the "one fix" that dramatically improves RAG quality by preserving logical context and avoiding the "sliding window problem" of the default n8n splitter [26-28].
    ◦ [ ] Ensure the splitter prioritizes headings to create coherent, context-rich chunks [29, 30]. This replaces the arbitrary chunkSize: 100 setting from the n8n workflow [31].
• [ ] 2.4. Replace Vectorization & Storage Nodes:
    ◦ [ ] Create a pluggable service for vectorization that supports multiple embedding models (Ollama, OpenAI) via configuration [31, 32].
    ◦ [ ] Implement a generic vector store interface that supports Qdrant and Chroma, allowing the user to select their preferred store in the .env file [33].
    ◦ [ ] Ensure the ingestion pipeline correctly upserts the markdown-split chunks and their metadata (file ID, folder ID) into the selected vector store [34].
Phase 3: Implementing Advanced RAG & User Interface
• [ ] 3.1. Develop the Adaptive RAG Engine (LangGraph):
    ◦ [ ] Define Graph State: Create a GraphState TypedDict to manage question, documents, and generation throughout the flow [35].
    ◦ [ ] Implement Core Nodes: Create functions for each state in the graph: retrieve, grade_documents, transform_query, generate, and web_search [36].
    ◦ [ ] Build LLM Graders: * [ ] Query Router: Routes questions to vectorstore or web_search (using Tavily) [35, 37]. * [ ] Retrieval Grader: Assigns a binary 'yes'/'no' score to filter out irrelevant documents [38]. * [ ] Hallucination Grader: Verifies that the answer is grounded in the retrieved facts [39]. * [ ] Answer Grader: Checks if the answer resolves the user's question [40].
    ◦ [ ] Implement Self-Correction Loop: Develop the transform_query node to rewrite questions when retrieval fails, creating a self-correcting RAG pipeline [41].
    ◦ [ ] Compile the Graph: Define the conditional edges (route_question, decide_to_generate, grade_generation) and compile the final LangGraph app [42].
• [ ] 3.2. Enhance the User Interface:
    ◦ [ ] Interactive Chat: Adapt the existing youtube-chat chat command to use the new Adaptive RAG engine as its backend. Ensure it supports real-time streaming, session management, and markdown rendering [43, 44].
    ◦ [ ] Integrate Content Generation: Connect the podcast-create-multi and blueprint-create commands so they can use the RAG knowledge base as a source for content synthesis [25, 45, 46].
• [ ] 3.3. Build the MCP Server:
    ◦ [ ] Expose 35+ Tools: Expand the MCP server from the youtube-chat-cli to expose the full functionality of the new application as tools [19, 47].
    ◦ [ ] Implement RAG-Specific Tools: Add new MCP tools for gdrive-add-file, rag-ask-question, and managing the ingestion pipeline.
    ◦ [ ] Ensure MCP Compliance: Adhere to MCP security principles, including explicit user consent for all data access and tool execution [48, 49].
    ◦ [ ] Test with AI Assistants: Verify that the MCP server works seamlessly with clients like Claude Desktop by configuring the mcpServers JSON [5, 45].
Phase 4: Testing, Documentation, and Deployment
• [ ] 4.1. Unit & Integration Testing:
    ◦ [ ] Write unit tests for individual services (Google Drive client, content processor, RAG graders).
    ◦ [ ] Write integration tests for the full data ingestion pipeline (from Drive change detection to vector store insertion).
    ◦ [ ] Test the complete Adaptive RAG flow with various queries to validate routing, grading, and self-correction logic [50, 51].
    ◦ [ ] Perform end-to-end testing of the CLI commands and the MCP server.
• [ ] 4.2. Documentation:
    ◦ [ ] Update README.md: Thoroughly document all new features, installation steps (including OAuth setup), and usage examples for both CLI and MCP.
    ◦ [ ] CLI Help Text: Ensure all Click commands have comprehensive --help messages.
    ◦ [ ] Create User Guides: Write guides on "Connecting to Google Drive", "Understanding Adaptive RAG", and "Using the MCP Server with Claude".
• [ ] 4.3. Packaging & Deployment:
    ◦ [ ] PyPI Package: Update pyproject.toml and build/test the Python package for distribution on PyPI [3, 52].
    ◦ [ ] npm Package: Update and package the jaegis-youtube-chat-mcp wrapper for npm distribution [3, 5].
    ◦ [ ] Release: Draft release notes, tag a new version, and publish the packages to PyPI and npm.
--------------------------------------------------------------------------------
JAEGIS NexusSync Architecture and Components
Of course. Based on our ongoing conversation and the 11 sources provided, here is the detailed architecture.md document for JAEGIS NexusSync.
--------------------------------------------------------------------------------
Architecture: JAEGIS NexusSync
1. Overview
This document describes the architecture for JAEGIS NexusSync, a code-based, CLI-first application that replaces the 'Local RAG AI Agent' n8n workflow [1]. The system is designed as a modular extension of the JAEGIS YouTube Chat CLI, inheriting its professional package structure, background service capabilities, and comprehensive feature set [2, 3].
The architecture is centered around a clear separation of concerns, ensuring maintainability, scalability, and extensibility. It combines a robust data ingestion pipeline, a sophisticated self-correcting RAG engine, a persistent background service for automation, and a versatile user interface layer that serves both direct CLI users and external AI assistants via the Model Context Protocol (MCP) [4].
The design is heavily influenced by the modular structure seen in both the youtube-free-deep-research-cli and jaegis-nexus-sync repositories [2, 5], and its core intelligence is powered by the Adaptive RAG state machine pattern described in the LangGraph documentation [6].
2. High-Level Architectural Diagram
The following diagram illustrates the major components and their interactions:
graph TD
    subgraph "User Interface Layer"
        CLI[CLI Interface (Click)]
        MCP[MCP Server (npx wrapper)]
    end

    subgraph "Core Application Services (Python)"
        CoreServices[Core Services]
        AdaptiveRAG[Adaptive RAG Engine (LangGraph)]
        ContentProc[Multi-Source Content Processing Engine]
        GoogleDriveClient[Google Drive API Client]
    end

    subgraph "Background Service (APScheduler)"
        BGService[Background Service]
        GDWatcher[Google Drive Watcher]
        QueueProc[Processing Queue Manager]
    end

    subgraph "Data &amp; State Management"
        VectorStore[(Vector Store - Qdrant/Chroma)]
        DB[(SQLite Database)]
    end

    subgraph "External Services"
        GD_API[Google Drive API]
        LLM_API[LLM APIs (Ollama/OpenAI)]
        SearchAPI[Web Search API (Tavily)]
    end

    CLI --&gt; CoreServices
    MCP --&gt; CoreServices

    CoreServices --&gt; AdaptiveRAG
    CoreServices --&gt; ContentProc
    CoreServices --&gt; VectorStore
    CoreServices --&gt; DB

    AdaptiveRAG --&gt; LLM_API
    AdaptiveRAG --&gt; SearchAPI
    AdaptiveRAG --&gt; VectorStore

    BGService --&gt; GDWatcher
    BGService --&gt; QueueProc

    GDWatcher --&gt; GoogleDriveClient
    GoogleDriveClient --&gt; GD_API

    QueueProc --&gt; ContentProc
    ContentProc --&gt; VectorStore
    ContentProc --&gt; DB

3. Component Breakdown
3.1. User Interface Layer
This layer provides the primary entry points for user interaction.
• CLI Interface (Click): The main user-facing component, built using the Python Click library [7]. It exposes all functionalities through a structured command system, including interactive chat, content generation, and system management [8, 9]. This is the direct replacement for interacting with the n8n agent via its chat trigger or webhook [10, 11].
• MCP Server: An integrated Model Context Protocol (MCP) server, packaged for easy execution via npx [12, 13]. It exposes over 35 tools, translating MCP requests into internal CLI command executions [14, 15]. This is a vast improvement over the simple Google Drive search tool exposed by the n8n MCP server [16], enabling full control over the RAG pipeline from AI assistants like Claude [4, 17].
3.2. Core Application Services
This layer contains the main business logic of the application, building upon the src/youtube_chat_cli/services/ structure [18].
• Google Drive API Client: A dedicated module for interacting with the Google Drive API v3.
    ◦ Authentication: It will manage the OAuth 2.0 flow, handling user consent, storing refresh tokens securely for offline access, and making authorized API calls [19-21]. It will request the most narrowly focused scopes possible, such as drive.file or drive.readonly, as recommended for security and user trust [22, 23].
    ◦ Operations: Provides functions to list, download, and get metadata for files, replacing the functionality of the Google Drive nodes in the n8n workflow [24].
• Multi-Source Content Processing Engine: This engine is responsible for the ingestion pipeline.
    ◦ Format Conversion: It converts over 20+ file types (Google Docs, PDFs, HTML, etc.) into clean, structured markdown [25, 26]. For PDFs, it will use an OCR API (like Mistral OCR) to preserve structure, a significant upgrade from the n8n workflow's plain text extraction [27, 28].
    ◦ Intelligent Chunking: It utilizes a markdown-aware text splitter to chunk documents by headings. This is a critical architectural decision that solves the "sliding window problem" inherent in the n8n workflow's RecursiveCharacterTextSplitter, which splits text arbitrarily without regard for logical structure [29-32].
    ◦ Vectorization & Storage: It manages embedding generation (via Ollama or OpenAI) and upserts the resulting vectors and metadata into a configured vector store (Qdrant or Chroma) [33, 34].
• Adaptive RAG Engine (LangGraph): This is the intelligent core of the application, replacing the static AI Agent node from the n8n workflow [35]. It is implemented as a stateful graph using LangGraph, reflecting the Adaptive RAG pattern [6, 36].
    ◦ Graph State: A defined state object (GraphState) tracks the question, retrieved documents, and generated answer throughout the process [37].
    ◦ Nodes: Each step in the process is a distinct node in the graph: retrieve, grade_documents, transform_query, generate, and web_search [38].
    ◦ Conditional Edges: The graph uses LLM-powered graders to make decisions and route the flow. Key decision points include: 1. route_question: Decides whether to use the vector store or web search [38, 39]. 2. decide_to_generate: Checks if retrieved documents are relevant; if not, triggers a transform_query node to rewrite the question [38, 40, 41]. 3. grade_generation: Performs hallucination and answer relevance checks, looping back to generate or transform_query if the answer is unsatisfactory [42-44].
3.3. Background Service (APScheduler)
This component, inherited from the youtube-chat-cli architecture, runs persistently to handle automated tasks, replacing the n8n trigger nodes [2, 45, 46].
• Google Drive Watcher: This module periodically queries the Google Drive API for new or updated files in the specified folder, mimicking the File Created and File Updated triggers from the n8n workflow [47, 48]. Instead of polling, it could potentially use the Google Workspace Events API for more efficient push notifications in a future version [49].
• Processing Queue Manager: When the watcher detects a change, it adds a job to a processing queue managed by the SQLite database. The queue manager ensures that documents are processed sequentially and robustly, with retry logic for transient failures [14].
3.4. Data & State Management
• SQLite Database: A local SQLite database is used for storing application state, including monitored Google Drive folders, the processing queue, chat session history, and workflow configurations [14]. This provides a lightweight and persistent storage solution.
• Vector Store (Qdrant/Chroma): This is the knowledge base of the RAG system, storing document chunks as vector embeddings for semantic search [50, 51]. The architecture allows for pluggable support for different vector stores, configured via environment variables.
3.5. External Services
• Google Drive API: Used for monitoring and downloading files [24, 52].
• LLM APIs (Ollama/OpenAI): Used for all generation, grading, and routing tasks within the Adaptive RAG engine [53, 54].
• Web Search API (Tavily): Integrated as a tool within the RAG graph to answer questions about recent events that are not in the local knowledge base [37, 55].
4. Code & Directory Structure
The project will follow the professional package structure of youtube-free-deep-research-cli to ensure modularity and maintainability [18, 56].
src/jaegis_nexus_sync/
├── cli/              # Click-based CLI commands and entry points
│   └── main.py
├── core/             # Core business logic and shared utilities
│   ├── config.py     # Configuration management (.env loading)
│   └── database.py   # SQLite database models and session management
├── services/         # High-level service implementations
│   ├── gdrive_service.py     # Google Drive API client and watcher
│   ├── content_processor.py  # Document conversion and chunking
│   ├── rag_engine.py         # Adaptive RAG LangGraph implementation
│   ├── background_service.py # APScheduler setup and job definitions
│   └── chat_interface.py     # Interactive terminal UI
└── mcp/              # MCP server logic and tool definitions
    └── server.py

--------------------------------------------------------------------------------
JAEGIS NexusSync: Adaptive RAG Product Requirements
Of course. Based on our conversation and the 11 sources provided, here is the detailed Product Requirements Document (prd.md) for JAEGIS NexusSync.
--------------------------------------------------------------------------------
Product Requirements Document (PRD): JAEGIS NexusSync
1. Introduction
This document outlines the product requirements for JAEGIS NexusSync, a command-line interface (CLI) application designed to be the ultimate Retrieval-Augmented Generation (RAG) service. This project will replace and significantly enhance the functionality of the existing 'Local RAG AI Agent' n8n workflow [1, 2].
The primary goal is to create a robust, code-based application by extending the existing 'JAEGIS YouTube Chat CLI' [3]. This new tool will integrate advanced RAG techniques, automated data ingestion from Google Drive, and seamless connectivity with AI assistants via the Model Context Protocol (MCP) [4, 5]. JAEGIS NexusSync is intended for researchers, developers, and knowledge workers who require a powerful, scalable, and customizable RAG solution [3].
2. Target Audience & Personas
• Persona 1: The AI-Powered Researcher (Alex)
    ◦ Needs: A reliable system to automatically ingest and index research papers, articles, and meeting notes from a shared Google Drive. Alex needs to ask complex questions and receive accurate, well-cited answers grounded in the provided documents. They need to interact with this system via both a CLI and their preferred AI assistant (like Claude) [6, 7].
    ◦ Pain Points with n8n: Limited scalability, difficult to customize complex logic (like self-correction), and potential for brittleness in a low-code environment [8, 9].
• Persona 2: The Content Creator (Casey)
    ◦ Needs: A tool to process diverse content types (videos, PDFs, web pages) into a unified knowledge base [10]. Casey wants to use this knowledge base to generate structured content like blueprints, summaries, and professional-quality podcasts with different styles and voices [10-12].
    ◦ Pain Points with n8n: Manual data preparation is tedious. The simple text extraction in the n8n workflow loses critical document structure (headings, tables), leading to poor-quality RAG results [13, 14].
• Persona 3: The Developer / Automator (Devan)
    ◦ Needs: A scriptable, CLI-first application with a modular architecture that can be integrated into larger automated workflows [15]. Devan requires robust configuration, clear API endpoints, and the ability to expose the tool's functions to other services, including AI agents via a standardized protocol like MCP [5, 11].
    ◦ Pain Points with n8n: "Black box" nature of low-code tools makes debugging difficult. Dependency on the n8n platform creates limitations; a pure code solution offers more control and transparency [9, 16].
3. Functional Requirements
FR-1: Decommission n8n Workflow & Replicate Core Functionality in Code
• FR-1.1: Google Drive Integration: The system MUST provide automated, real-time ingestion of documents from a specified Google Drive folder [17-19].
    ◦ FR-1.1.1: Authentication: The application MUST use OAuth 2.0 for secure, user-consented access to Google Drive [20, 21]. It MUST request the most narrowly focused scopes possible (e.g., drive.file or drive.readonly) and securely store refresh tokens for offline access [22-24].
    ◦ FR-1.1.2: File Monitoring: A persistent background service MUST monitor for file creation and updates in the target folder, replacing the n8n polling triggers [17, 18, 25].
• FR-1.2: Advanced Document Processing: The system MUST process and convert various document formats into clean, structured markdown before chunking [19, 26].
    ◦ FR-1.2.1: Multi-Format Support: The system MUST support the 20+ file types from the base youtube-chat-cli, including Google Docs, PDFs, HTML, and media files [10, 14, 27, 28]. For PDFs and images, OCR MUST be used to extract structured markdown, which is a significant improvement over the n8n workflow's plain text extraction [13, 14, 28].
    ◦ FR-1.2.2: Intelligent Chunking: The system MUST implement markdown-aware text splitting, chunking documents by headings to preserve logical context. This explicitly replaces the RecursiveCharacterTextSplitter from the n8n workflow, which suffers from the "sliding window problem" [29-32].
• FR-1.3: Pluggable Vectorization & Storage: The system MUST support multiple embedding models (Ollama, OpenAI) and vector stores (Qdrant, Chroma) through configuration, replacing the hard-coded n8n nodes [2, 33-35].
FR-2: Implement Adaptive RAG for Self-Correction and Intelligence
• FR-2.1: LangGraph-based State Machine: The core RAG logic MUST be implemented as a stateful graph that follows the Adaptive RAG pattern [36, 37].
• FR-2.2: Query Routing: The system MUST analyze incoming questions and route them to the most appropriate data source: the local vector store for indexed knowledge or a web search tool (e.g., Tavily) for recent events [38-40].
• FR-2.3: Document Relevance Grading: After retrieval, an LLM-based grader MUST assess if the retrieved documents are relevant to the question, filtering out erroneous results [40, 41].
• FR-2.4: Query Transformation: If the initial retrieval yields no relevant documents, the system MUST automatically rewrite the user's question to be better optimized for vector search and retry the retrieval process [40, 42, 43].
• FR-2.5: Groundedness and Answer Grading:
    ◦ FR-2.5.1: Hallucination Check: The system MUST use an LLM grader to verify that the generated answer is grounded in and supported by the retrieved documents [43, 44].
    ◦ FR-2.5.2: Answer Check: The system MUST use an LLM grader to confirm that the generated answer correctly addresses the user's original question [43, 45]. If checks fail, the system MUST loop back to generate a new answer or transform the query again [43].
FR-3: Integration with JAEGIS YouTube Chat CLI Features
• FR-3.1: Interactive CLI: The system MUST provide a rich interactive terminal UI for conversations, including session management (save, load, export) and markdown rendering [46, 47].
• FR-3.2: Content Generation: The application MUST be able to generate structured blueprints (5 styles) and professional podcasts (14 styles) from the knowledge stored in the RAG pipeline [10, 11, 48, 49].
• FR-3.3: Workflow Management: The system MUST allow users to configure and manage connections to different RAG workflows and external services [46, 50].
FR-4: Model Context Protocol (MCP) Server
• FR-4.1: Comprehensive Tool Exposure: The application MUST expose its full range of functionalities (35+ tools) via a built-in MCP server [7, 11]. This replaces the simple search-and-get MCP server from the n8n template [51, 52].
• FR-4.2: AI Assistant Compatibility: The MCP server MUST be compatible with clients like Claude and ChatGPT, allowing users to manage the entire RAG service (from adding Drive files to generating podcasts) directly from their AI assistant [7, 53, 54].
• FR-4.3: Secure and Standardized: The MCP implementation MUST adhere to the MCP specification, including principles of user consent and control for executing tools and accessing data [4, 55].
4. Non-Functional Requirements
• NFR-1: Performance: The system must provide real-time, streaming responses in the interactive chat. Document ingestion and indexing should be handled efficiently in the background without blocking the user interface.
• NFR-2: Scalability: The architecture must be able to handle a large corpus of documents (thousands of files) and concurrent user queries without significant degradation in performance.
• NFR-3: Usability: The CLI must be intuitive, with clear commands, helpful documentation (--help), and robust error handling [56]. The MCP server should be easy to set up with standard clients [54, 57].
• NFR-4: Modularity & Maintainability: The codebase must follow the professional, modular architecture of the youtube-free-deep-research-cli, ensuring a clear separation of concerns that makes it easy to maintain and extend [15, 58].
• NFR-5: Security: All sensitive information, such as API keys and OAuth tokens, MUST be managed through secure environment variables (.env files) and MUST NOT be hardcoded [59, 60]. The application must follow security best practices for handling user data and executing tools via MCP [55].
• NFR-6: Reliability: The background service for Google Drive monitoring must be persistent and automatically recover from transient errors. The RAG pipeline should include retry logic for external API calls [25].
5. Assumptions & Constraints
• Assumption-1: Users will have a Google account and will be able to generate the necessary OAuth 2.0 credentials and API keys for services like Google Drive and LLM providers [21, 61].
• Assumption-2: Users have a basic understanding of command-line tools.
• Constraint-1: The initial version will be built on the Python-based youtube-free-deep-research-cli project. The MCP server will use the existing npx wrapper for ease of use [11, 56].
• Constraint-2: The system relies on third-party APIs (Google Drive, LLM providers, search tools), and their availability and rate limits will affect the system's performance and reliability [62].
6. Future Work / Out of Scope for v1.0
• Web UI Dashboard: A web-based interface for managing the RAG service, visualizing the knowledge base, and reviewing chat history (inspired by JAEGIS NexusSync) is out of scope for the initial release [63, 64].
• Advanced User/Permission Management: Multi-user support with role-based access control is not included in v1.0.
• Automated Maintenance & GitHub Integration: Features like automated dependency maintenance and pull request creation from the NexusSync project are out of scope [63].
• Support for Other Cloud Storage: Integration with cloud storage providers other than Google Drive (e.g., Dropbox, OneDrive) will be considered for future versions.
--------------------------------------------------------------------------------
JAEGIS NexusSync: Blueprint for an Adaptive RAG Service
Of course. Based on the 11 sources provided, here is the detailed blueprint.md document for transforming the 'Local RAG AI Agent Workflow' into a fully functional, code-based CLI application, built upon the 'JAEGIS YouTube Chat CLI'.
--------------------------------------------------------------------------------
Blueprint: JAEGIS NexusSync - The Ultimate R.A.G. Service
1. Introduction
This document outlines the blueprint for JAEGIS NexusSync, a next-generation, code-based Retrieval-Augmented Generation (RAG) service. The project's core objective is to decommission the 'Local RAG AI Agent' n8n workflow [1-3] and replace it with a robust, scalable, and fully-featured Command Line Interface (CLI) application.
The new system will be built as an extension of the existing 'JAEGIS YouTube Chat CLI - Professional Podcast Generation Platform' [4, 5], inheriting its modular architecture, rich feature set, and MCP (Model Context Protocol) server capabilities [4, 6]. By integrating advanced concepts from Adaptive RAG [7], automated maintenance [8], and seamless Google Drive integration [9], JAEGIS NexusSync will serve as a comprehensive, production-grade RAG solution.
The n8n workflow provided a foundational structure for document ingestion from Google Drive and an AI agent interface [3, 10, 11]. However, a code-based CLI approach offers superior performance, scalability, customization, and maintainability, eliminating the constraints of a low-code platform [12].
2. Core Vision & Principles
JAEGIS NexusSync is envisioned as a unified system that integrates:
• Research-Driven RAG: Automated ingestion and processing of content from diverse sources into a sophisticated RAG pipeline [8, 13].
• Adaptive Intelligence: A self-corrective and analytical RAG process that intelligently routes queries, grades document relevance, and rewrites questions for optimal retrieval [7, 14, 15].
• Seamless Integration: Deep integration with Google Drive for real-time document synchronization [9, 11] and exposure of all functionalities through a Model Context Protocol (MCP) server for AI assistants like Claude and ChatGPT [4, 6, 16].
• Developer-Centric Experience: A fully scriptable, CLI-first application with a modular architecture, robust configuration management, and clear separation of concerns [5, 8].
3. Decommissioning the n8n Workflow
The entire 'Local RAG AI Agent' n8n workflow will be systematically replaced with code-based modules. The following table maps the n8n nodes to their new CLI-based counterparts:
n8n Node / Functionality [1-3, 10, 11, 17-34]
New CLI Module / Feature
Justification & Enhancement
Google Drive Triggers (File Created/Updated) [11, 17]
Background Service with Google Drive Watcher
Will use the Google Drive API with OAuth 2.0 [35, 36] for robust, real-time monitoring, replacing polling-based triggers [11]. This provides more reliable and immediate event handling.
Document Processing Pipeline (Download, Extract Text) [18, 19]
Multi-Source Content Processing Engine
Extends beyond simple text extraction to support 20+ file types (PDF, DOCX, MP4, etc.) [13]. For PDFs and images, OCR will be used to extract structured markdown [37, 38], a significant improvement over plain text extraction [19, 37].
Text Splitter (Recursive Character) [20]
Advanced Markdown-Aware Text Splitter
Implements the best practice of splitting documents by markdown headings to preserve logical structure and context, avoiding the "sliding window problem" of arbitrary character splits [39-41].
Embeddings & Vector Store (Ollama, Qdrant) [21, 24, 25]
Pluggable Vectorization & Storage Service
Will support multiple embedding models (Ollama, OpenAI) and vector stores (Qdrant, Chroma, Supabase) [42-44] managed through configuration, providing greater flexibility than the hard-wired n8n connections [21, 24].
AI Agent & Chat (Webhook, Chat Trigger, Ollama Model) [3, 27]
Adaptive RAG Engine & Interactive Chat Interface
Replaces the static agent prompt [27] with a dynamic, stateful graph based on Adaptive RAG [7, 45]. This includes query routing, document grading, hallucination checks, and question rewriting [46-49]. The chat interface will be a rich terminal UI [50].
MCP Integration [9, 51]
Native MCP Server with 35+ Tools
Greatly expands on the simple n8n MCP server [9] by exposing the entire CLI functionality (35+ tools) via a standards-compliant MCP server, making it a powerful backend for any compatible AI assistant [6, 52, 53].
4. Key Features & Capabilities
The new CLI application will incorporate and expand upon features from the base 'YouTube Chat CLI' and other source materials.
4.1. Data Ingestion & Processing
• Google Drive Integration:
    ◦ Automated Sync: A background service will monitor specified Google Drive folders for new and updated files [11, 17, 54].
    ◦ Secure Authentication: Implements OAuth 2.0 for secure, user-consented access to Google Drive, requesting the most narrowly focused scopes possible (e.g., drive.file or drive.readonly) [55-57]. Refresh tokens will be securely stored for offline access [58, 59].
    ◦ Multi-Format Handling: Converts various file formats (Google Docs, PDF, HTML) into clean markdown to preserve structural integrity for optimal chunking [37, 54, 60].
• Multi-Source Support: Inherits the ability to process over 20 file types, including local files, URLs, and YouTube content, creating a unified knowledge base [13].
4.2. Advanced RAG Pipeline (Adaptive RAG)
The core of the service will be a LangGraph-based state machine that implements the Adaptive RAG strategy [7, 45].
1. Query Analysis & Routing: The system will first analyze the user's question to determine the best path [46, 61]. It will route the query to either the local vector store for indexed knowledge or to a web search tool (like Tavily) for recent events [14, 62].
2. Retrieval & Document Grading: After retrieving documents from the vector store, an LLM-based grader will assess each document's relevance to the question, filtering out erroneous retrievals [14, 47].
3. Self-Correction & Query Transformation: If retrieved documents are irrelevant, the system will automatically rewrite the user's question to be more optimized for vector search and re-attempt retrieval [14, 49]. This is a critical self-corrective loop [7].
4. Generation & Groundedness Checking:
    ◦ The final set of relevant documents is passed to an LLM to generate an answer [63].
    ◦ A Hallucination Grader will verify that the generated answer is grounded in the provided documents [15, 48].
    ◦ An Answer Grader will check if the generation actually addresses the user's question [15, 64].
    ◦ If generation fails these checks, the system can re-generate or re-transform the query, creating another corrective loop [15].
4.3. User Interface & Interaction
• Interactive CLI Chat: A rich terminal UI for real-time, streaming conversations with the RAG agent, including session management (save, load, export) and markdown rendering [50, 65].
• MCP Server for AI Assistants: Exposes all CLI functions as over 35 MCP tools, enabling seamless integration with assistants like Claude [6, 52, 53]. Users can manage the entire RAG pipeline—from adding sources to generating podcasts—directly from their AI assistant [66].
• Blueprint & Podcast Generation: Leverages the powerful content synthesis capabilities of the base CLI to create structured documentation (blueprint-create) or audio summaries (podcast-create-multi) from the RAG knowledge base [13, 67, 68].
4.4. System & Architecture
• Modular Codebase: Built on the professional, modular architecture of the youtube-free-deep-research-cli project, ensuring a clear separation of concerns between services like the CLI, core services, database, and external API clients [5, 69].
• Background Service: A persistent background service using APScheduler will manage automated tasks like Google Drive monitoring and queue processing, ensuring continuous operation [70].
• Robust Configuration: Centralized configuration management via .env files for API keys, database connections, and workflow URLs [71].
5. Technology Stack
• Primary Language: Python 3.8+ [72]
• CLI Framework: Click [73]
• RAG Orchestration: LangGraph [45, 62]
• LLM Integration: LangChain, supporting models from OpenAI and Ollama [2, 62]
• Vector Stores: ChromaDB, Qdrant [24, 42]
• Database: SQLite for local metadata and state management [6]
• Background Jobs: APScheduler [70]
• APIs: Google Drive API v3 [74], Tavily Search API [75], various LLM and OCR APIs [37].
• Packaging: PyPI for the core CLI package, npm for the MCP server wrapper [76, 77].
--------------------------------------------------------------------------------
