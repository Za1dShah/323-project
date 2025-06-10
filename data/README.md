# Banking Information Documents

This directory is where you should place all the banking information documents that you want the AI chatbot to learn from. The chatbot will only use information contained in these documents to answer customer inquiries.

## Document Structure

Please organize your documents in the following subdirectories:

### `/data/documents/general_banking/`
Place general banking information, policies, and procedures here.

### `/data/documents/account_services/`
Place information about account types, features, and services here.

### `/data/documents/loans/`
Place loan products, eligibility criteria, and application processes here.

### `/data/documents/credit_cards/`
Place credit card offerings, benefits, and terms here.

### `/data/documents/credit_improvement/`
Place credit score improvement guidelines and best practices here.

## Supported Document Formats

The system can process the following document formats:
- PDF (.pdf)
- Word Documents (.docx)
- Text Files (.txt)
- Markdown Files (.md)

## Document Guidelines

For optimal performance of the chatbot:

1. Ensure documents are clearly written and well-structured
2. Use headings and subheadings to organize information
3. Include specific details about policies, procedures, and requirements
4. Avoid ambiguous language or undefined terms
5. Include frequently asked questions and their answers when possible

## Example Document Structure

A well-structured document might include:

```
# Credit Card Application Process

## Eligibility Requirements
- Minimum credit score: 650
- Minimum annual income: $30,000
- Maximum debt-to-income ratio: 40%

## Application Steps
1. Complete online application form
2. Provide identification documents
3. Submit proof of income
4. Wait for credit check (typically 2-3 business days)
5. Receive decision by email

## Approval Process
...

## Frequently Asked Questions
...
```

The chatbot will learn from these documents and use this information to respond to customer inquiries accurately.
