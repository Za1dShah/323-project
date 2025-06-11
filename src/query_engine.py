"""
Query engine for the Bank AI Chatbot.
"""



import re
import logging
from typing import List, Dict, Any, Optional
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from src.knowledge_base import KnowledgeBase
from src.config import (
    TOP_K_RESULTS, SIMILARITY_THRESHOLD, 
    MAX_RESPONSE_LENGTH, INCLUDE_SOURCES,
    RESPONSE_TEMPLATE, DEFAULT_RESPONSE
)

logger = logging.getLogger(__name__)

class QueryEngine:
    """Engine for processing queries and generating responses."""

    def __init__(self):
        """Initialize the query engine."""
        self.knowledge_base = KnowledgeBase()
        self.knowledge_base.load()

        # NLP tools
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_query(self, query: str) -> str:
        """Preprocess the query text."""
        query = query.lower()
        query = re.sub(r'[^\w\s]', ' ', query)
        tokens = word_tokenize(query)
        tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words]
        return ' '.join(tokens)

    def extract_query_intent(self, query: str) -> str:
        """Extract the main intent of the query."""
        query = query.lower()
        if any(word in query for word in ['loan', 'borrow', 'mortgage', 'finance']):
            return "loans"
        elif any(word in query for word in ['credit', 'card', 'interest', 'payment']):
            return "credit_cards"
        elif any(word in query for word in ['account', 'balance', 'transfer', 'deposit', 'withdraw']):
            return "account_services"
        elif any(word in query for word in ['score', 'improve', 'rating', 'history']):
            return "credit_improvement"
        else:
            return "general_banking"

    def personalize_response(self, response: str, account_info: Optional[Dict[str, Any]]) -> str:
        """Personalize the response based on account information."""
        if not account_info:
            return response

        personalized = f"Hi {account_info['name']}, {response}"
        personalized = personalized.replace("your account", f"your {account_info['account_type']} account")
        personalized = personalized.replace("your balance", f"your balance of ${account_info['balance']}:")
        return personalized

    def process_query(
        self,
        query_text: str,
        account_info: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Process a user query and return a response."""
        clean_query = self.preprocess_query(query_text)
        intent = self.extract_query_intent(clean_query)
        base_response = f"This is information related to {intent.replace('_', ' ')}."
        response = self.personalize_response(base_response, account_info)

        return {
            "response": response,
            "sources": [],
            "confidence": 0.85,
        }

# Optional test block
if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

    engine = QueryEngine()

    test_query = "Can you help me check my credit card balance?"
    test_account = {
        "name": "Alice",
        "account_type": "Savings",
        "balance": 10350.75
    }

    result = engine.process_query(test_query, account_info=test_account)
    print("Query:", test_query)
    print("Response:", result["response"])
    print("Confidence:", result["confidence"])
