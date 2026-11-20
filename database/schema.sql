-- ROSE V1 schema. This creates only the dedicated rose_db database.
CREATE DATABASE IF NOT EXISTS rose_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_0900_ai_ci;

USE rose_db;

CREATE TABLE IF NOT EXISTS assistants (
  id VARCHAR(80) PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  description VARCHAR(500) NOT NULL,
  system_instructions TEXT NOT NULL,
  capabilities JSON NOT NULL,
  availability ENUM('available', 'planned') NOT NULL DEFAULT 'planned',
  provider VARCHAR(40) NOT NULL DEFAULT 'gemini',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS conversations (
  id CHAR(36) PRIMARY KEY,
  assistant_id VARCHAR(80) NOT NULL,
  title VARCHAR(255) NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_conversations_assistant
    FOREIGN KEY (assistant_id) REFERENCES assistants(id)
    ON UPDATE CASCADE ON DELETE RESTRICT,
  INDEX idx_conversations_updated_at (updated_at),
  INDEX idx_conversations_assistant (assistant_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS messages (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  conversation_id CHAR(36) NOT NULL,
  role ENUM('user', 'assistant') NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_messages_conversation
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
    ON UPDATE CASCADE ON DELETE CASCADE,
  INDEX idx_messages_conversation_created (conversation_id, created_at, id)
) ENGINE=InnoDB;

INSERT INTO assistants (
    id,
    name,
    description,
    system_instructions,
    capabilities,
    availability,
    provider
)
VALUES
    (
        'general',
        'General Assistant',
        'Everyday questions, clear explanations, and practical help.',
        'Give clear, accurate, friendly help for everyday questions, explanations, and practical tasks.',
        JSON_ARRAY('Everyday questions', 'Explanations', 'General tasks', 'Conversation'),
        'available',
        'gemini'
    ),
    (
        'coding',
        'Coding Assistant',
        'Understand code, work through errors, and build better solutions.',
        'Explain programming concepts, review code, debug errors, and generate readable solutions. Never execute user-provided code.',
        JSON_ARRAY('Programming help', 'Debugging', 'Code review', 'Learning'),
        'available',
        'gemini'
    ),
    (
        'research',
        'Research Assistant',
        'A future space for guided research and source discovery.',
        'Planned capability. Not active in ROSE V1.',
        JSON_ARRAY('Research planning', 'Source discovery'),
        'planned',
        'gemini'
    ),
    (
        'document',
        'Document Assistant',
        'A future space for understanding and summarizing documents.',
        'Planned capability. Not active in ROSE V1.',
        JSON_ARRAY('Document understanding', 'Summaries'),
        'planned',
        'gemini'
    ) AS new
ON DUPLICATE KEY UPDATE
    name = new.name,
    description = new.description,
    system_instructions = new.system_instructions,
    capabilities = new.capabilities,
    availability = new.availability,
    provider = new.provider;