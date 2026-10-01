import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")


# ---------------------------------------------------------
# Gemini / Google AI configuration
# ---------------------------------------------------------

GOOGLE_API_KEY = (
    os.getenv("GOOGLE_API_KEY")
    or os.getenv("GEMINI_API_KEY")
    or ""
).strip()

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.0-flash"
).strip()


# ---------------------------------------------------------
# Security configuration
# ---------------------------------------------------------

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "change-this-secret-key-in-production"
).strip()

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("SESSION_MINUTES", "30")
)


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

database_value = os.getenv(
    "DATABASE_PATH",
    str(BASE_DIR / "pocketsmart.db")
)

DATABASE_PATH = Path(database_value)

if not DATABASE_PATH.is_absolute():
    DATABASE_PATH = BASE_DIR / DATABASE_PATH


# ---------------------------------------------------------
# Upload configuration
# ---------------------------------------------------------

UPLOAD_DIR = (
    BASE_DIR
    / "app"
    / "static"
    / "uploads"
)

MAX_UPLOAD_MB = int(
    os.getenv("MAX_UPLOAD_MB", "8")
)