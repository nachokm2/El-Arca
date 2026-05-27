import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "claude-opus-4-7")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "4096"))

LOG_LEVEL = os.getenv("SIMULATION_LOG_LEVEL", "INFO")
DB_PATH = BASE_DIR / os.getenv("DB_PATH", "data/elarca.db")

MAX_AGENTS = int(os.getenv("MAX_AGENTS", "200"))
DEBATE_ROUNDS = int(os.getenv("DEBATE_ROUNDS", "3"))

DATA_DIR = BASE_DIR / "data"
SIMULATIONS_DIR = DATA_DIR / "simulations"
PROFILES_DIR = DATA_DIR / "agent_profiles"

DATA_DIR.mkdir(exist_ok=True)
SIMULATIONS_DIR.mkdir(exist_ok=True)
PROFILES_DIR.mkdir(exist_ok=True)
