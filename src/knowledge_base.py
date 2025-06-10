"""
Knowledge base management for the Bank AI Chatbot.
This module handles the storage, retrieval, and querying of banking information.
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

import faiss
from sentence_transformers import SentenceTransformer

from src.config import (
    PROCESSED_DIR,
    EMBEDDINGS_DIR,
    TOP_K_RESULTS,
    EMBEDDING_MODEL
)

class KnowledgeBase:
    """Knowledge base for storing and retrieving banking information."""
    
    def __init__(self):
        """Initialize the knowledge base."""
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.index = None
        self.documents = []
        self.is_loaded = False
    
    def load(self) -> bool:
        """
        Load all processed documents and embeddings into memory.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            self.documents = []
            all_embeddings = []
            
            # Check if processed and embeddings directories exist
            if not os.path.exists(PROCESSED_DIR) or not os.path.exists(EMBEDDINGS_DIR):
                print("Warning: Processed or embeddings directories do not exist.")
                return False
            
            # Load each category
            for category_dir in PROCESSED_DIR.iterdir():
                if category_dir.is_dir():
                    category_name = category_dir.name
                    embeddings_category_dir = EMBEDDINGS_DIR / category_name
                    
                    # Skip if embeddings directory doesn't exist
                    if not embeddings_category_dir.exists():
                        continue
                    
                    # Load each document in the category
                    for processed_file in category_dir.glob('*.json'):
                        doc_name = processed_file.stem
                        embeddings_file = embeddings_category_dir / f"{doc_name}.json"
                        
                        # Skip if embeddings file doesn't exist
                        if not embeddings_file.exists():
                            continue
                        
                        # Load processed document
                        with open(processed_file, 'r') as f:
                            doc_data = json.load(f)
                        
                        # Load embeddings
                        with open(embeddings_file, 'r') as f:
                            embeddings_data = json.load(f)
                        
                        # Add document chunks to documents list
                        for i, chunk in enumerate(doc_data['chunks']):
                            self.documents.append({
                                'category': category_name,
                                'document': doc_name,
                                'source': doc_data['source'],
                                'chunk_index': i,
                                'text': chunk['text']
                            })
                        
                        # Add embeddings to list
                        all_embeddings.extend(embeddings_data['embeddings'])
            
            # Create FAISS index if documents were loaded
            if self.documents:
                dimension = len(all_embeddings[0])
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(np.array(all_embeddings).astype('float32'))
                self.is_loaded = True
                return True
            else:
                print("Warning: No documents were loaded.")
                return False
                
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return False
    
    def query(self, query_text: str) -> List[Dict[str, Any]]:
        """
        Query the knowledge base for relevant information.
        
        Args:
            query_text (str): The query text.
            
        Returns:
            List[Dict[str, Any]]: List of relevant document chunks.
        """
        if not self.is_loaded:
            if not self.load():
                return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query_text])[0]
        
        # Search for similar documents
        distances, indices = self.index.search(
            np.array([query_embedding]).astype('float32'), 
            min(TOP_K_RESULTS, len(self.documents))
        )
        
        # Get relevant documents
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):  # Ensure index is valid
                doc = self.documents[idx]
                results.append({
                    'text': doc['text'],
                    'source': doc['source'],
                    'category': doc['category'],
                    'document': doc['document'],
                    'relevance_score': float(1.0 / (1.0 + distances[0][i]))  # Convert distance to score
                })
        
        return results
    
    def get_document_count(self) -> Dict[str, int]:
        """
        Get the number of documents in each category.
        
        Returns:
            Dict[str, int]: Dictionary with categories as keys and document counts as values.
        """
        counts = {}
        
        if not PROCESSED_DIR.exists():
            return counts
        
        for category_dir in PROCESSED_DIR.iterdir():
            if category_dir.is_dir():
                category_name = category_dir.name
                doc_count = len(list(category_dir.glob('*.json')))
                counts[category_name] = doc_count
        
        return counts
    
    def get_categories(self) -> List[str]:
        """
        Get all available categories.
        
        Returns:
            List[str]: List of category names.
        """
        if not PROCESSED_DIR.exists():
            return []
        
        return [d.name for d in PROCESSED_DIR.iterdir() if d.is_dir()]


if __name__ == "__main__":
    kb = KnowledgeBase()
    if kb.load():
        print(f"Knowledge base loaded with {len(kb.documents)} chunks.")
        print(f"Document counts: {kb.get_document_count()}")
        print(f"Categories: {kb.get_categories()}")
    else:
        print("Failed to load knowledge base.")
