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

from .knowledge_base import KnowledgeBase
from .config import (
    TOP_K_RESULTS,
    SIMILARITY_THRESHOLD,
    MAX_RESPONSE_LENGTH,
    INCLUDE_SOURCES,
    RESPONSE_TEMPLATE,
    DEFAULT_RESPONSE,
)

# Download required NLTK corpora (run once)
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

logger = logging.getLogger(__name__)


def check_home_loan_eligibility(user_data: dict) -> str:
    """Check if the user is eligible for a home loan based on credit score and income."""
    income = user_data.get("monthly_income", 0)
    credit_score = user_data.get("credit_score", 0)

    if credit_score >= 700:
        return "Yes, based on your credit score and income, you may be eligible for a home loan."
    else:
        return "Based on your credit score, you might not currently qualify for a home loan."
    


class QueryEngine:
    """Engine for processing queries and generating responses."""

    def __init__(self):
        """Initialize the query engine."""
        self.knowledge_base = KnowledgeBase()
        self.knowledge_base.load()

        # NLP tools
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_query(self, query: str) -> str:
        """Preprocess the query text."""
        query = query.lower()
        query = re.sub(r"[^\w\s]", " ", query)
        tokens = word_tokenize(query)
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]
        return " ".join(tokens)

    def extract_query_intent(self, query: str) -> str:
        """Extract the main intent of the query."""
        query = query.lower()
        if any(word in query for word in ["loan", "borrow", "mortgage", "finance"]):
            return "loans"
        elif any(word in query for word in ["credit", "card", "interest", "payment"]):
            return "credit_cards"
        elif any(word in query for word in ["account", "balance", "transfer", "deposit", "withdraw"]):
            return "account_services"
        elif any(word in query for word in ["score", "improve", "rating", "history"]):
            return "credit_improvement"
        else:
            return "general_banking"

    def personalize_response(self, response: str, account_info: Optional[Dict[str, Any]]) -> str:
        """Personalize the response based on account information."""
        if not account_info:
            return response

        personalized = response
        personalized = f"Hi {account_info['name']}, " + personalized
        personalized = personalized.replace(
            "your account", f"your {account_info['account_type']} account"
        )
        personalized = personalized.replace(
            "your balance", f"your balance of ${account_info['balance']}"
        )
        return personalized

    def process_query(
        self,
        query_text: str,
        account_info: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Process a user query and return a response."""
        try:
            preprocessed_query = self.preprocess_query(query_text)

            # Account-specific queries
            if account_info:
                if any(word in preprocessed_query for word in ["balance", "money", "fund", "account"]):
                    response = f"Your current balance is ${account_info['balance']:.2f}."
                    return {
                        "response": self.personalize_response(response, account_info),
                        "sources": [],
                        "confidence": 0.95,
                    }

                if any(word in preprocessed_query for word in ["credit", "score", "rating"]):
                    score = account_info.get("credit_score", 0)
                    response = f"Your credit score is {score}."
                    if score >= 740:
                        response += " This is considered excellent."
                    elif score >= 670:
                        response += " This is considered good."
                    elif score >= 580:
                        response += " This is considered fair."
                    else:
                        response += " This is considered poor."
                    return {
                        "response": self.personalize_response(response, account_info),
                        "sources": [],
                        "confidence": 0.95,
                    }

                if any(phrase in preprocessed_query for phrase in ["home loan", "loan eligibility", "eligible for loan"]):
                    response = check_home_loan_eligibility(account_info)
                    return {
                        "response": self.personalize_response(response, account_info),
                        "sources": [],
                        "confidence": 0.95,
                    }

            # Knowledge base query
            results = self.knowledge_base.query(preprocessed_query)

            if results and results[0]["relevance_score"] >= SIMILARITY_THRESHOLD:
                response = results[0]["text"]
                if len(response) > MAX_RESPONSE_LENGTH:
                    response = response[:MAX_RESPONSE_LENGTH] + "..."

                sources = []
                if INCLUDE_SOURCES:
                    sources = [
                        {"title": r["document"], "url": r.get("source", "")}
                        for r in results[:3]
                    ]

                return {
                    "response": self.personalize_response(response, account_info),
                    "sources": sources,
                    "confidence": results[0]["relevance_score"],
                }
            else:
                return {"response": DEFAULT_RESPONSE, "sources": [], "confidence": 0.0}

        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return {
                "response": DEFAULT_RESPONSE,
                "sources": [],
                "confidence": 0.0,
                "error": str(e),
            }


if __name__ == "__main__":
    engine = QueryEngine()

    while True:
        query = input("\nAsk a banking question (or type 'exit'): ")
        if query.lower() == "exit":
            break

        # Example mock account info
        account_info = {
            "name": "John",
            "account_type": "savings",
            "balance": 1200.50,
            "credit_score": 680,
            "monthly_income": 6000,
        }

        response = engine.process_query(query, account_info=account_info)
        print(f"\n🤖 Response: {response['response']}")
