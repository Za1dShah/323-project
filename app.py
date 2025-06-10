"""
Main application for the Bank AI Chatbot.
"""

import os
import random
from flask import Flask, request, jsonify, render_template, session
from pathlib import Path
import nltk
import logging

from src.document_processor import DocumentProcessor
from src.knowledge_base import KnowledgeBase
from src.query_engine import QueryEngine
from src.config import (
    FLASK_HOST,
    FLASK_PORT,
    FLASK_DEBUG,
    GREETING_MESSAGES,
    DEFAULT_RESPONSE,
)

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Download NLTK data if not already present
try:
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)
    nltk.download("wordnet", quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {e}")

app = Flask(__name__)
app.secret_key = os.urandom(24)  # For session management

# Initialize components
document_processor = DocumentProcessor()
knowledge_base = KnowledgeBase()
query_engine = QueryEngine()

# Test accounts data
test_accounts = {
    "1001": {
        "name": "John Smith",
        "account_type": "Premium Checking",
        "balance": 15750.42,
        "last_statement_date": "May 15, 2025",
        "credit_score": 785,
        "annual_income": 95000,
        "debt_to_income_ratio": 22,
        "missed_payments": 0,
        "credit_utilization": 15,
        "account_age_years": 8,
        "has_diverse_credit": True,
        "recent_inquiries": 1,
        "description": "High-income professional with excellent credit history and significant savings.",
    },
    "1002": {
        "name": "Sarah Johnson",
        "account_type": "Standard Checking",
        "balance": 3250.18,
        "last_statement_date": "May 20, 2025",
        "credit_score": 710,
        "annual_income": 65000,
        "debt_to_income_ratio": 28,
        "missed_payments": 1,
        "credit_utilization": 25,
        "account_age_years": 5,
        "has_diverse_credit": True,
        "recent_inquiries": 2,
        "description": "Middle-income earner with good credit, minor payment issues in the past.",
    },
    "1003": {
        "name": "Miguel Rodriguez",
        "account_type": "Basic Checking",
        "balance": 850.75,
        "last_statement_date": "May 18, 2025",
        "credit_score": 620,
        "annual_income": 42000,
        "debt_to_income_ratio": 35,
        "missed_payments": 3,
        "credit_utilization": 60,
        "account_age_years": 3,
        "has_diverse_credit": False,
        "recent_inquiries": 4,
        "description": "Young professional with fair credit, struggling with high credit utilization and some missed payments.",
    },
    "1004": {
        "name": "Emily Chen",
        "account_type": "Student Checking",
        "balance": 450.32,
        "last_statement_date": "May 22, 2025",
        "credit_score": 680,
        "annual_income": 25000,
        "debt_to_income_ratio": 15,
        "missed_payments": 0,
        "credit_utilization": 20,
        "account_age_years": 1,
        "has_diverse_credit": False,
        "recent_inquiries": 2,
        "description": "Recent graduate with limited credit history but good payment behavior.",
    },
    "1005": {
        "name": "Global Enterprises LLC",
        "account_type": "Business Checking",
        "balance": 42500.87,
        "last_statement_date": "May 10, 2025",
        "credit_score": 800,  # Business credit score
        "annual_income": 750000,  # Annual revenue
        "debt_to_income_ratio": 18,
        "missed_payments": 0,
        "credit_utilization": 10,
        "account_age_years": 6,
        "has_diverse_credit": True,
        "recent_inquiries": 1,
        "description": "Established small business with excellent credit and stable finances.",
    },
}


@app.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")


@app.route("/process_documents", methods=["POST"])
def process_documents():
    """Process all documents in the knowledge base."""
    try:
        stats = document_processor.process_all_documents()
        knowledge_base.load()  # Reload knowledge base with new documents
        return jsonify(
            {
                "success": True,
                "message": "Documents processed successfully",
                "stats": stats,
            }
        )
    except Exception as e:
        logger.error(f"Error processing documents: {e}", exc_info=True)
        return (
            jsonify(
                {"success": False, "message": f"Error processing documents: {str(e)}"}
            ),
            500,
        )


@app.route("/query", methods=["POST"])
def query():
    """Process a query and return a response."""
    data = request.json
    query_text = data.get("query", "").strip()
    account_id = data.get("account_id")
    conversation_id = data.get("conversation_id", "default")

    # Check if query is empty
    if not query_text:
        return jsonify(
            {
                "response": random.choice(GREETING_MESSAGES),
                "sources": [],
                "confidence": 1.0,
            }
        )

    # Get account info if account_id is provided
    account_info = test_accounts.get(account_id) if account_id else None

    # Get conversation history from session
    if "conversations" not in session:
        session["conversations"] = {}

    if conversation_id not in session["conversations"]:
        session["conversations"][conversation_id] = []

    conversation_history = session["conversations"][conversation_id]

    # Process query
    try:
        result = query_engine.process_query(
            query_text,
            account_info=account_info,
            conversation_history=conversation_history,
        )

        # Update conversation history
        conversation_history.append(
            {"query": query_text, "response": result["response"]}
        )
        session["conversations"][conversation_id] = conversation_history[
            -5:
        ]  # Keep last 5 exchanges
        session.modified = True

        return jsonify(result)
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return jsonify(
            {
                "response": DEFAULT_RESPONSE,
                "sources": [],
                "confidence": 0.0,
                "error": str(e),
            }
        )


@app.route("/accounts")
def get_accounts():
    """Get all test accounts."""
    return jsonify(
        {
            "accounts": [
                {
                    "id": account_id,
                    "name": account_info["name"],
                    "type": account_info["account_type"],
                    "description": account_info["description"],
                }
                for account_id, account_info in test_accounts.items()
            ]
        }
    )


@app.route("/account/<account_id>")
def get_account(account_id):
    """Get a specific test account."""
    account_info = test_accounts.get(account_id)
    if account_info:
        return jsonify({"id": account_id, "account_info": account_info})
    else:
        return jsonify({"error": "Account not found"}), 404


@app.route("/status")
def status():
    """Get the status of the knowledge base."""
    doc_count = knowledge_base.get_document_count()
    categories = knowledge_base.get_categories()

    return jsonify(
        {
            "document_count": doc_count,
            "categories": categories,
            "knowledge_base_loaded": knowledge_base.is_loaded,
            "test_accounts": len(test_accounts),
        }
    )


@app.route("/reset_conversation", methods=["POST"])
def reset_conversation():
    """Reset a conversation history."""
    data = request.json
    conversation_id = data.get("conversation_id", "default")

    if "conversations" in session and conversation_id in session["conversations"]:
        session["conversations"][conversation_id] = []
        session.modified = True

    return jsonify({"success": True, "message": "Conversation reset successfully"})


if __name__ == "__main__":
    # Ensure knowledge base is loaded
    try:
        knowledge_base.load()
        logger.info("Knowledge base loaded successfully")
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}", exc_info=True)

    # Start the Flask app
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
