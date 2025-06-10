"""
Configuration settings for the Bank AI Chatbot.
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
DOCUMENTS_DIR = DATA_DIR / "documents"
PROCESSED_DIR = DATA_DIR / "processed"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"

# Document categories
DOCUMENT_CATEGORIES = [
    "general_banking",
    "account_services",
    "loans",
    "credit_cards",
    "credit_improvement"
]

# Test accounts directory
TEST_ACCOUNTS_DIR = BASE_DIR / "test_accounts"

# Model settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Sentence transformer model
CHUNK_SIZE = 300  # Number of characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks

# Search settings
TOP_K_RESULTS = 3  # Increased from 2 to get more context
SIMILARITY_THRESHOLD = 0.6  # Minimum similarity score to consider a result relevant

# Response settings
MAX_RESPONSE_LENGTH = 500  # Maximum length of response in characters
INCLUDE_SOURCES = True  # Whether to include sources in response
RESPONSE_TEMPLATE = """
I understand you're asking about {query_topic}. Here's what I can tell you:

{response_content}

{sources}

Is there anything else you'd like to know about this topic?
"""

# Conversation settings
GREETING_MESSAGES = [
    "Hello! I'm your banking assistant. How can I help you today?",
    "Welcome to our banking service! What can I assist you with?",
    "Hi there! I'm here to answer your banking questions. What would you like to know?"
]
DEFAULT_RESPONSE = "I'm sorry, I don't have enough information to answer that question. Could you please rephrase or ask something else about our banking services?"

# Flask settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Create directories if they don't exist
for directory in [DOCUMENTS_DIR, PROCESSED_DIR, EMBEDDINGS_DIR]:
    os.makedirs(directory, exist_ok=True)

for category in DOCUMENT_CATEGORIES:
    os.makedirs(DOCUMENTS_DIR / category, exist_ok=True)