
from pathlib import Path
import os
from dotenv import load_dotenv

# Locate the .env file in the project root
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

# Load private environment variables
load_dotenv(ENV_FILE)

# Database configuration
DATABASE_MODE = os.getenv("DATABASE_MODE", "sqlite").lower()
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_MODE not in ("sqlite", "postgresql"):
    raise RuntimeError("DATABASE_MODE must be sqlite or postgresql")

if DATABASE_MODE == "postgresql" and not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing from .env")

# Control session cookie security by environment
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"

# Read authentication settings
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY")
OWNER_PASSWORD_HASH = os.getenv("OWNER_PASSWORD_HASH")

# Ensure required secrets exist
if not SESSION_SECRET_KEY:
    raise RuntimeError("SESSION_SECRET_KEY is missing from .env")

if not OWNER_PASSWORD_HASH:
    raise RuntimeError("OWNER_PASSWORD_HASH is missing from .env")
