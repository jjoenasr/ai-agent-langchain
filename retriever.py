from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from markdownify import markdownify
from langchain_text_splitters import MarkdownHeaderTextSplitter
from logger_config import logger
from typing import Literal
import faiss
import re
import os

FAISS_PATH = "faiss_vector_store"

class RAGManager:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.vector_store = None
        self.vector_store_path = FAISS_PATH
        self.load_vector_store()

    def load_vector_store(self):
        """Loads the vector store from disk if it exists, otherwise creates a new one."""
        if os.path.exists(self.vector_store_path):
            try:
                self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
                logger.info("Vector store loaded successfully.")
            except Exception as e:
                self.vector_store = None
        else:
            index = faiss.IndexHNSWFlat(768, 10)  # (emb_size, n_neighbors)
            self.vector_store = FAISS(embedding_function=self.embeddings,
                                      index=index,  # where to store the vectors
                                      docstore=InMemoryDocstore(),  # where to store documents metadata
                                      index_to_docstore_id={}  # how to map index to docstore
                                      )
            logger.info("Initializing new vector store.")

    def clear_vector_store(self):
        """Delete all docs from vector store"""
        self.vector_store.delete()
        
    def ingest_documents_from_html(self, html: str):
        """Load documents from HTML to the vector store."""
        # Convert the HTML content to Markdown
        markdown_content = markdownify(html).strip()

        # Remove multiple line breaks
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)[:40000]

        # Split markdown based on sections
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=False)
        docs = markdown_splitter.split_text(markdown_content)
        if not docs:
            return "No content could be parsed from the webpage."

        # Reset vector store
        self.vector_store.delete()
        # Ingest documents into vector store
        self.vector_store.add_documents(docs)

    def retrieve_html_section(self, html:str, section: Literal['start', 'middle', 'end']) -> str:
        markdown_content = markdownify(html).strip()
        markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)[:40000]
        # Split markdown based on sections
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on, strip_headers=False)
        docs = markdown_splitter.split_text(markdown_content)
        if not docs:
            return "No content could be parsed from the webpage."
        if len(docs) < 3:
            return "\n\n".join([doc.page_content for doc in docs])
        
        third = len(docs) // 3
        if section == "start":
            return "\n\n".join([doc.page_content for doc in docs[:third]])
        elif section == "middle":
            return "\n\n".join([doc.page_content for doc in docs[third:-third]])
        elif section == "end":
            return "\n\n".join([doc.page_content for doc in docs[-third:]])

    
    def retrieve_documents(self, query: str, k:int=3):
        """Retrieves most similar documents"""
        results = self.vector_store.similarity_search(query, k=k)
        if results:
            return "\n\n".join([doc.page_content for doc in results])
        else:
            return "No matching sections"
     

