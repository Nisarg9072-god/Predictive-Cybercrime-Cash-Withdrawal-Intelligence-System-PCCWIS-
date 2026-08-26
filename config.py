import os
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

class Config:
    LLM_API_KEY = os.getenv("LLM_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
    ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://localhost:8000")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))
    MAX_TOOL_CALLS = int(os.getenv("MAX_TOOL_CALLS", "20"))
    MAX_GRAPH_DEPTH = int(os.getenv("MAX_GRAPH_DEPTH", "15"))
    MAX_ACCOUNTS_INVESTIGATED = int(os.getenv("MAX_ACCOUNTS_INVESTIGATED", "10"))
    MAX_EXECUTION_TIME = int(os.getenv("MAX_EXECUTION_TIME", "300"))

config = Config()
