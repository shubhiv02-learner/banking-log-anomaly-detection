-- =============================================================================
-- drop_rag_tables.sql
--
-- Purpose: Tear down the RAG knowledge schema (tables, indexes, enum type).
-- WARNING: DESTRUCTIVE — permanently deletes all RAG document/chunk/ingestion
--          data. Does NOT drop extensions (uuid-ossp, vector).
-- =============================================================================

-- Child table first (FK to knowledge_documents); CASCADE removes indexes/constraints
DROP TABLE IF EXISTS knowledge_chunks CASCADE;

DROP TABLE IF EXISTS knowledge_documents CASCADE;

DROP TABLE IF EXISTS ingestion_history CASCADE;

-- Enum type last (may be referenced by dropped tables)
DROP TYPE IF EXISTS document_type_enum CASCADE;
