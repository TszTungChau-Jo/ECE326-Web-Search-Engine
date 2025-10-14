# env_utils.py
from dotenv import load_dotenv
import os

# Load the .env file automatically when imported
load_dotenv()

def get_env_var(name: str) -> str:
    """Fetch an environment variable or raise a clear error if missing."""
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"Missing required environment variable: {name}\n"
            f"Please define it in your .env file or environment."
        )
    return value.strip()
