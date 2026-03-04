-- Add authentication columns to users table

ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_login_at TIMESTAMP WITH TIME ZONE;

-- Add full-text search index for tasks
CREATE INDEX IF NOT EXISTS idx_tasks_fulltext ON tasks USING gin(to_tsvector('english', title || ' ' || COALESCE(description, '')));

-- Add GIN index for tags array search
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING gin(tags);
