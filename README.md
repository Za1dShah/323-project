# Bank AI Chatbot Project

## Project Overview
This project implements an AI chatbot for a bank that learns from user-provided information documents and answers customer inquiries about bank statements, credit information, loan eligibility, and credit improvement strategies. The chatbot is designed to only use the information it has been trained on, ensuring that responses are based solely on the provided banking documents.

## Features
- Document processing system that extracts information from banking documents
- Knowledge base that stores and indexes the extracted information
- Query engine that understands customer inquiries and generates relevant responses
- Personalized responses based on account information
- Web interface for interacting with the chatbot
- Five test accounts with different financial profiles for demonstration

## Project Structure
```
bank_chatbot/
├── app.py                  # Main Flask application
├── data/                   # Knowledge base storage
│   ├── documents/          # Place your banking information documents here
│   │   ├── general_banking/
│   │   ├── account_services/
│   │   ├── loans/
│   │   ├── credit_cards/
│   │   └── credit_improvement/
│   ├── processed/          # Processed information (generated)
│   └── embeddings/         # Vector embeddings (generated)
├── src/                    # Source code
│   ├── config.py           # Configuration settings
│   ├── document_processor.py # Document processing utilities
│   ├── knowledge_base.py   # Knowledge base management
│   └── query_engine.py     # Query processing and response generation
├── templates/              # HTML templates
│   └── index.html          # Web interface
├── test_accounts/          # Test account data and validation scripts
│   ├── account_details.md  # Detailed information about test accounts
│   └── test_chatbot.py     # Script for testing the chatbot
└── docs/                   # Documentation
    └── architecture.md     # System architecture documentation
```

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation Steps

1. Clone the repository or extract the provided files to your desired location.

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```
   pip install flask nltk sentence-transformers faiss-cpu python-docx
   ```5

4. Download NLTK data:
   ```
   python -c "import nltk; nltk.download('punkt')"
   ```

5. Add your banking information documents to the appropriate subdirectories in `data/documents/`:
   - General banking information: `data/documents/general_banking/`
   - Account services information: `data/documents/account_services/`
   - Loan information: `data/documents/loans/`
   - Credit card information: `data/documents/credit_cards/`
   - Credit improvement guidelines: `data/documents/credit_improvement/`

   Supported document formats: PDF, DOCX, TXT, MD

6. Process the documents:
   - Run the application (see below)
   - Click on "Process Documents" in the web interface

7. Start using the chatbot!

## Running the Application

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open a web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. The chatbot interface will be displayed. You can:
   - Select a test account to see personalized responses
   - Ask questions about banking services, credit scores, loan eligibility, etc.
   - Process documents if you've added new ones

## Test Accounts

The system includes five test accounts with different financial profiles:

1. **John Smith (ID: 1001)**: High-income professional with excellent credit
2. **Sarah Johnson (ID: 1002)**: Middle-income earner with good credit
3. **Miguel Rodriguez (ID: 1003)**: Young professional with fair credit
4. **Emily Chen (ID: 1004)**: Recent graduate with limited credit history
5. **Global Enterprises LLC (ID: 1005)**: Established small business

Detailed information about each account can be found in `test_accounts/account_details.md`.

## Testing the Chatbot

A test script is provided to validate the chatbot's responses for each test account:

```
python test_accounts/test_chatbot.py
```

This script runs a set of test queries against each account and saves the results to `test_accounts/test_results.json`.

## Customization

### Adding Your Own Documents

1. Prepare your banking information documents in PDF, DOCX, TXT, or MD format.
2. Place them in the appropriate subdirectories under `data/documents/`.
3. Run the application and click "Process Documents" in the web interface.

### Modifying Test Accounts

Test account data is defined in `app.py`. You can modify the existing accounts or add new ones by editing the `test_accounts` dictionary.

### Extending the Chatbot

To extend the chatbot's capabilities:

1. Add new intent patterns in `src/query_engine.py`
2. Enhance the response generation logic in the `_generate_general_response` and `_generate_personalized_response` methods
3. Add new document categories by updating the `DOCUMENT_CATEGORIES` list in `src/config.py`

## Limitations

- The chatbot can only answer questions based on information in the provided documents
- Complex reasoning beyond the scope of provided information will be limited
- The system will acknowledge when it doesn't have sufficient information to answer a query

## Troubleshooting

- **Issue**: Knowledge base not loading
  **Solution**: Ensure you've processed documents by clicking "Process Documents" in the web interface

- **Issue**: Document processing fails
  **Solution**: Check that your documents are in supported formats (PDF, DOCX, TXT, MD) and are not corrupted

- **Issue**: Chatbot gives generic responses
  **Solution**: Make sure you've added relevant banking documents to the knowledge base

- **Issue**: Web interface not loading
  **Solution**: Check that the Flask application is running and you're using the correct URL

## Future Enhancements

- Improved document processing for more complex document types
- Enhanced context management for more natural conversations
- Integration with bank systems for real-time data access (if desired)
- Multi-language support
- Voice interface for accessibility
