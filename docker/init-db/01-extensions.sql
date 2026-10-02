-- Enable UUID extension for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for additional crypto functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";