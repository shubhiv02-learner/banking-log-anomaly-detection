-- Login + Salveris acting-principal mapping on user_master.
-- Email is not uniquely indexed: existing sentineliq rows already share emails.

ALTER TABLE user_master ADD COLUMN IF NOT EXISTS external_reference VARCHAR(64);
ALTER TABLE user_master ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255);

CREATE UNIQUE INDEX IF NOT EXISTS ux_user_master_external_reference
  ON user_master (external_reference)
  WHERE external_reference IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_user_master_email ON user_master (email);
