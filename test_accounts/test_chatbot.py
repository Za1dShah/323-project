"""
Test script for validating the Bank AI Chatbot with test accounts.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.query_engine import QueryEngine

def run_test_queries():
    """Run test queries against the chatbot for each test account."""
    # Initialize query engine
    query_engine = QueryEngine()
    
    # Load test accounts
    with open(Path(__file__).parent / 'account_details.md', 'r') as f:
        account_details_content = f.read()
    
    # Test accounts from app.py
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
            "description": "High-income professional with excellent credit history and significant savings."
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
            "description": "Middle-income earner with good credit, minor payment issues in the past."
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
            "description": "Young professional with fair credit, struggling with high credit utilization and some missed payments."
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
            "description": "Recent graduate with limited credit history but good payment behavior."
        },
        "1005": {
            "name": "Global Enterprises LLC",
            "account_type": "Business Checking",
            "balance": 42500.87,
            "last_statement_date": "May 10, 2025",
            "credit_score": 800,
            "annual_income": 750000,
            "debt_to_income_ratio": 18,
            "missed_payments": 0,
            "credit_utilization": 10,
            "account_age_years": 6,
            "has_diverse_credit": True,
            "recent_inquiries": 1,
            "description": "Established small business with excellent credit and stable finances."
        }
    }
    
    # Test queries for each account
    test_queries = [
        "What's my current balance?",
        "What's my credit score?",
        "Am I eligible for a home loan?",
        "How can I improve my credit score?",
        "What are the requirements for a personal loan?"
    ]
    
    # Run tests and save results
    results = {}
    
    print("Running test queries...")
    print("-" * 50)
    
    # First, run queries without account info (general responses)
    print("\nTesting general responses (no account):")
    general_results = []
    for query in test_queries:
        response = query_engine.process_query(query)
        print(f"Query: {query}")
        print(f"Response: {response['response'][:100]}...")
        print()
        general_results.append({
            "query": query,
            "response": response['response'],
            "intent": response['intent']
        })
    
    results["general"] = general_results
    
    # Then, run queries for each account
    for account_id, account_info in test_accounts.items():
        print(f"\nTesting account {account_id}: {account_info['name']}")
        account_results = []
        
        for query in test_queries:
            response = query_engine.process_query(query, account_info)
            print(f"Query: {query}")
            print(f"Response: {response['response'][:100]}...")
            print()
            account_results.append({
                "query": query,
                "response": response['response'],
                "intent": response['intent']
            })
        
        results[account_id] = account_results
    
    # Save results to file
    with open(Path(__file__).parent / 'test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("-" * 50)
    print("Test results saved to test_accounts/test_results.json")

if __name__ == "__main__":
    run_test_queries()
