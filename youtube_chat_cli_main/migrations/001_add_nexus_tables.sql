-- Nexus tables for observability and resilience
BEGIN TRANSACTION;

CREATE TABLE IF NOT EXISTS workflow_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_id TEXT NOT NULL,
    workflow_type TEXT NOT NULL,
    stage TEXT NOT NULL,
    state_json TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_trace_workflow ON workflow_traces(workflow_id, created_at);

CREATE TABLE IF NOT EXISTS dead_letter_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_table TEXT NOT NULL,
    original_id TEXT,
    reason TEXT,
    payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_workflow ON chat_sessions(workflow_id, created_at);
CREATE INDEX IF NOT EXISTS idx_processing_status ON processing_queue(status, created_at);
CREATE INDEX IF NOT EXISTS idx_vector_source ON vector_metadata(source_file_id, chunk_index);

COMMIT;

