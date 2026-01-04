from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
from pathlib import Path

router = APIRouter()


class ApiKeyUpdate(BaseModel):
    api_key: str


def get_env_file_path() -> Path:
    """Get the path to the .env file in the backend directory."""
    backend_dir = Path(__file__).parent.parent.parent
    return backend_dir / ".env"


def read_env_file() -> dict:
    """Read the .env file and return as a dictionary."""
    env_path = get_env_file_path()
    env_vars = {}

    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

    return env_vars


def write_env_file(env_vars: dict) -> None:
    """Write environment variables to the .env file."""
    env_path = get_env_file_path()

    with open(env_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")


@router.get("/env/kie-api-key")
async def get_kie_api_key():
    """Get the current KIE API key from .env file."""
    env_vars = read_env_file()
    api_key = env_vars.get('KIE_API_KEY', '')

    return {
        "api_key": api_key,
        "is_set": bool(api_key)
    }


@router.put("/env/kie-api-key")
async def update_kie_api_key(update: ApiKeyUpdate):
    """Update the KIE API key in .env file."""
    if not update.api_key.strip():
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    # Read existing env vars
    env_vars = read_env_file()

    # Update the API key
    env_vars['KIE_API_KEY'] = update.api_key.strip()

    # Write back to file
    write_env_file(env_vars)

    # Update the current process environment (optional, for immediate effect)
    os.environ['KIE_API_KEY'] = update.api_key.strip()

    return {
        "message": "API key updated successfully",
        "api_key": update.api_key.strip()
    }
