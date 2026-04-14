"""
Centralized configuration for Natural Language to CloudFormation Generator.
All settings controlled via environment variables with typed defaults.
"""
import os

# LLM Backend
BASE_URL: str = os.getenv("BASE_URL", "http://localhost:11434/v1")
API_KEY: str = os.getenv("API_KEY", "ollama")
MODEL: str = os.getenv("MODEL", "llama3.2")

# Generation settings
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT_SECONDS: int = int(os.getenv("TIMEOUT_SECONDS", "120"))
TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.1"))
MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))
LOOP_DETECTION_THRESHOLD: int = int(os.getenv("LOOP_DETECTION_THRESHOLD", "3"))

# Output
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
OUTPUT_DIR: str = os.getenv("OUTPUT_DIR", "output")

# CloudFormation validation
CFN_TERMINATION_CONDITION: str = "AWSTemplateFormatVersion"
CFN_REQUIRED_KEYS: list[str] = ["AWSTemplateFormatVersion", "Resources"]
