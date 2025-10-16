from dotenv import load_dotenv
import os, re, pathlib

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


# --- New Helpers --------------------------------------------------------

def upsert_env_var(key: str, value: str, env_path: str | pathlib.Path = None):
    """
    Add or update an environment variable in the .env file.
    Creates the file if it doesn't exist.
    """
    path = pathlib.Path(env_path or ".env").resolve()
    txt = ""
    if path.exists():
        txt = path.read_text()
        pattern = re.compile(rf"^(?:\s*#.*\n)*{re.escape(key)}=.*$", re.MULTILINE)
        if pattern.search(txt):
            txt = re.sub(pattern, f"{key}={value}", txt, count=1)
        else:
            if not txt.endswith("\n"):
                txt += "\n"
            txt += f"{key}={value}\n"
    else:
        txt = f"{key}={value}\n"
    path.write_text(txt)


def write_instance_manifest(data: dict, manifest_path: str | pathlib.Path = None):
    """Write instance metadata to a JSON manifest for later use."""
    import json
    path = pathlib.Path(manifest_path or "last_instance.json").resolve()
    path.write_text(json.dumps(data, indent=2))
    return path
