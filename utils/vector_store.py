from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import json

class VectorStore:
    """Utility for managing vector storage operations"""
    
    def __init__(self, embeddings, persist_directory="./chroma_db", collection_name="default"):
        """
        Initialize the vector store
        
        Args:
            embeddings: Embedding model to use
            persist_directory (str): Directory to persist vector database
            collection_name (str): Name of the collection
        """
        self.embeddings = embeddings
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize vector store
        self.vector_store = Chroma(
            collection_name=collection_name,
            persist_directory=persist_directory,
            embedding_function=embeddings
        )
    
    def add_documents(self, documents, ids=None):
        """
        Add documents to the vector store
        
        Args:
            documents (List[Document]): Documents to add
            ids (List[str], optional): IDs for the documents
            
        Returns:
            bool: Success status
        """
        try:
            self.vector_store.add_documents(documents=documents, ids=ids)
            return True
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
    
    def add_texts(self, texts, metadatas=None, ids=None):
        """
        Add texts to the vector store
        
        Args:
            texts (List[str]): Texts to add
            metadatas (List[dict], optional): Metadata for each text
            ids (List[str], optional): IDs for the texts
            
        Returns:
            bool: Success status
        """
        try:
            self.vector_store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
            return True
        except Exception as e:
            print(f"Error adding texts: {e}")
            return False
    
    def get_retriever(self, search_kwargs=None):
        """
        Get a retriever from the vector store
        
        Args:
            search_kwargs (dict, optional): Search parameters
            
        Returns:
            retriever: A LangChain retriever
        """
        search_kwargs = search_kwargs or {"k": 5}
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)
    
    def similarity_search(self, query, k=5):
        """
        Perform similarity search
        
        Args:
            query (str): Query string
            k (int): Number of results to return
            
        Returns:
            List[Document]: Similar documents
        """
        return self.vector_store.similarity_search(query, k=k)
