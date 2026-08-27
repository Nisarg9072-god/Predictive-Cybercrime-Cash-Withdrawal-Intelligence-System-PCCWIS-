import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    # Mistral LLM (primary provider)
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

    # Legacy LLM slot
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    
    # Database Configuration
    DATASET_DB_PATH = os.getenv("DATASET_DB_PATH", "data/synthetic/CYBER_INTERCEPT_FULL_DATASET/cyber_intercept.db")
    OPERATIONAL_DB_PATH = os.getenv("OPERATIONAL_DB_PATH", "data/agent/agent.db")
    
    ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
    MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "20"))
    MAX_GRAPH_DEPTH = int(os.getenv("MAX_GRAPH_DEPTH", "15"))
    MAX_ACCOUNTS_INVESTIGATED = int(os.getenv("MAX_ACCOUNTS_INVESTIGATED", "10"))
    MAX_EXECUTION_TIME = int(os.getenv("MAX_EXECUTION_TIME", "300"))

config = Config()
