CREATE SCHEMA IF NOT EXISTS nsdf;

CREATE TABLE IF NOT EXISTS nsdf.source_config (
  source_config_id INT PRIMARY KEY,
  source TEXT NOT NULL,
  x DOUBLE PRECISION NOT NULL,
  y DOUBLE PRECISION NOT NULL,
  description TEXT,
  configuration TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nsdf.shield_config (
  shield_config_id INT PRIMARY KEY,
  configuration TEXT NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS nsdf.trigger_config (
  trigger_config_id INT PRIMARY KEY,
  configuration TEXT NOT NULL,
  description TEXT
);

CREATE TABLE IF NOT EXISTS nsdf.run_context (
  run_number INT PRIMARY KEY,
  run_summary TEXT NOT NULL,
  image_links TEXT[] NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS nsdf.metadata (
  series TEXT PRIMARY KEY,
  run_number INT NOT NULL,
  source_config_id INT NOT NULL,
  shield_config_id INT NOT NULL,
  trigger_config_id INT NOT NULL,
  duration_minutes INT NOT NULL,
  bias INT NOT NULL,
  notes TEXT,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  trigger_rate DOUBLE PRECISION,
  run_diary TEXT,

  CONSTRAINT fk_metadata_run_number
    FOREIGN KEY (run_number)
    REFERENCES nsdf.run_context (run_number)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_metadata_source_config_id
    FOREIGN KEY (source_config_id)
    REFERENCES nsdf.source_config (source_config_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_metadata_shield_config_id
    FOREIGN KEY (shield_config_id)
    REFERENCES nsdf.shield_config (shield_config_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  CONSTRAINT fk_metadata_trigger_config_id
    FOREIGN KEY (trigger_config_id)
    REFERENCES nsdf.trigger_config (trigger_config_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
);

-- Create indexes for foreign keys
CREATE INDEX IF NOT EXISTS idx_metadata_run_number ON nsdf.metadata(run_number);
CREATE INDEX IF NOT EXISTS idx_metadata_source_config_id ON nsdf.metadata(source_config_id);
CREATE INDEX IF NOT EXISTS idx_metadata_shield_config_id ON nsdf.metadata(shield_config_id);
CREATE INDEX IF NOT EXISTS idx_metadata_trigger_config_id ON nsdf.metadata(trigger_config_id);
CREATE INDEX IF NOT EXISTS idx_run_context_run_number ON nsdf.run_context(run_number);

-- for local-test: CREATE ROLE nsdf_readonly LOGIN PASSWORD 'local_password';

-- Allow the readonly role to access the nsdf schema.
GRANT USAGE ON SCHEMA nsdf TO nsdf_readonly;
-- Allow the readonly role to read all existing tables.
GRANT SELECT ON ALL TABLES IN SCHEMA nsdf TO nsdf_readonly;

ALTER DEFAULT PRIVILEGES FOR ROLE postgres
IN SCHEMA nsdf 
GRANT SELECT ON TABLES TO nsdf_readonly;