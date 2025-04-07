from langchain_ollama.llms import OllamaLLM
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class OllamaInterface:
    """Interface for interacting with Ollama models"""
    
    def __init__(self, llm_model="llama3.2", embed_model="mxbai-embed-large", base_url="http://localhost:11434"):
        """
        Initialize the Ollama interface
        
        Args:
            llm_model (str): Name of the Ollama LLM model to use
            embed_model (str): Name of the Ollama embedding model to use
            base_url (str): URL where Ollama is running
        """
        self.llm = OllamaLLM(model=llm_model, base_url=base_url)
        self.embeddings = OllamaEmbeddings(model=embed_model, base_url=base_url)
    
    def create_chain(self, template):
        """
        Create a simple LLM chain with a template
        
        Args:
            template (str): The prompt template string
            
        Returns:
            chain: A runnable LangChain chain
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()
        return chain
    
    def create_rag_chain(self, template, retriever):
        """
        Create a RAG chain with a template and retriever
        
        Args:
            template (str): The prompt template string
            retriever: A LangChain retriever
            
        Returns:
            chain: A runnable RAG chain
        """
        prompt = ChatPromptTemplate.from_template(template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return rag_chain
    
    def get_embeddings(self):
        """
        Get the embeddings model
        
        Returns:
            embeddings: The Ollama embeddings model
        """
        return self.embeddings
