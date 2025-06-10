"""
Query engine for the Bank AI Chatbot.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
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

logger = logging.getLogger(__name__)


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
        """
        Preprocess the query text.

        Args:
            query: The raw query text

        Returns:
            Preprocessed query text
        """
        # Convert to lowercase
        query = query.lower()

        # Remove special characters
        query = re.sub(r"[^\w\s]", " ", query)

        # Tokenize
        tokens = word_tokenize(query)

        # Remove stop words and lemmatize
        tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]

        # Join back into a string
        return " ".join(tokens)

    def extract_query_intent(self, query: str) -> str:
        """
        Extract the main intent of the query.

        Args:
            query: The query text

        Returns:
            The main intent category
        """
        # This is a simple implementation - could be enhanced with a classifier
        query = query.lower()

        if any(word in query for word in ["loan", "borrow", "mortgage", "finance"]):
            return "loans"
        elif any(word in query for word in ["credit", "card", "interest", "payment"]):
            return "credit_cards"
        elif any(
            word in query
            for word in ["account", "balance", "transfer", "deposit", "withdraw"]
        ):
            return "account_services"
        elif any(word in query for word in ["score", "improve", "rating", "history"]):
            return "credit_improvement"
        else:
            return "general_banking"

    def personalize_response(
        self, response: str, account_info: Optional[Dict[str, Any]]
    ) -> str:
        """
        Personalize the response based on account information.

        Args:
            response: The base response
            account_info: Account information dictionary

        Returns:
            Personalized response
        """
        if not account_info:
            return response

        # Replace placeholders with actual account info
        personalized = response

        # Add personalized greeting
        personalized = f"Hi {account_info['name']}, " + personalized

        # Replace generic terms with specific account details
        personalized = personalized.replace(
            "your account", f"your {account_info['account_type']} account"
        )
        personalized = personalized.replace(
            "your balance", f"your balance of ${account_info['balance']}"
        )

        return personalized

    def process_query(self, query_text, account_info=None, conversation_history=None):
        """
        Process a user query and return a response.

        Args:
            query_text: The user's query text
            account_info: Optional account information for personalization
            conversation_history: Optional conversation history for context

        Returns:
            Dictionary containing response, sources, and confidence
        """
        try:
            # Preprocess the query
            preprocessed_query = self.preprocess_query(query_text)

            # Check for account-specific queries first
            if account_info:
                # Balance inquiry
                if any(
                    word in preprocessed_query
                    for word in ["balance", "money", "funds", "account"]
                ):
                    response = (
                        f"Your current balance is ${account_info['balance']:.2f}."
                    )
                    return {
                        "response": self.personalize_response(response, account_info),
                        "sources": [],
                        "confidence": 0.95,
                    }

                # Credit score inquiry
                if any(
                    word in preprocessed_query for word in ["credit", "score", "rating"]
                ):
                    response = f"Your credit score is {account_info['credit_score']}."
                    if account_info["credit_score"] >= 740:
                        response += " This is considered excellent."
                    elif account_info["credit_score"] >= 670:
                        response += " This is considered good."
                    elif account_info["credit_score"] >= 580:
                        response += " This is considered fair."
                    else:
                        response += " This is considered poor."
                    return {
                        "response": self.personalize_response(response, account_info),
                        "sources": [],
                        "confidence": 0.95,
                    }

            # For non-account specific queries, search the knowledge base
            intent = self.extract_query_intent(query_text)
            results = self.knowledge_base.search(
                preprocessed_query, intent, top_k=TOP_K_RESULTS
            )

            if results and results[0]["score"] >= SIMILARITY_THRESHOLD:
                # Use the top result to generate a response
                response = results[0]["content"]

                # Truncate if too long
                if len(response) > MAX_RESPONSE_LENGTH:
                    response = response[:MAX_RESPONSE_LENGTH] + "..."

                # Format sources if needed
                sources = []
                if INCLUDE_SOURCES:
                    sources = [
                        {"title": r["title"], "url": r.get("url", "")}
                        for r in results[:3]
                    ]

                return {
                    "response": self.personalize_response(response, account_info),
                    "sources": sources,
                    "confidence": results[0]["score"],
                }
            else:
                # No good match found
                return {"response": DEFAULT_RESPONSE, "sources": [], "confidence": 0.0}
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return {
                "response": DEFAULT_RESPONSE,
                "sources": [],
                "confidence": 0.0,
                "error": str(e),
            }
