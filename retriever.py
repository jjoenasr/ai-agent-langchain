import datasets
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.retrievers import BM25Retriever
from langchain.tools import Tool
from langchain_core.tools import tool
import faiss
import os

FAISS_PATH = "faiss_vector_store"

class RAGManager:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        self.vector_store = None
        self.load_vector_store()

    def load_vector_store(self, faiss_path=FAISS_PATH):
        """Loads the vector store from disk if it exists, otherwise creates a new one."""
        if os.path.exists(faiss_path):
            try:
                self.vector_store = FAISS.load_local(faiss_path, self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                self.vector_store = None
        else:
            index = faiss.IndexHNSWFlat(768, 10)  # (emb_size, n_neighbors)
            self.vector_store = FAISS(embedding_function=self.embeddings,
                                      index=index,  # where to store the vectors
                                      docstore=InMemoryDocstore(),  # where to store documents metadata
                                      index_to_docstore_id={}  # how to map index to docstore
                                      )
            self.ingest_guest_dataset()

    def ingest_guest_dataset(self, faiss_path=FAISS_PATH):
        """Load the dataset and add the documents to the vector store."""
        guest_dataset = datasets.load_dataset("agents-course/unit3-invitees", split="train")
        docs = [
            Document(
                page_content="\n".join([
                    f"Name: {guest['name']}",
                    f"Relation: {guest['relation']}",
                    f"Description: {guest['description']}",
                    f"Email: {guest['email']}"
                ]),
                metadata={"name": guest["name"]}
            )
            for guest in guest_dataset
        ]
        self.vector_store.add_documents(documents=docs)
        self.vector_store.save_local(faiss_path)

    def retrieve_guests(self, query: str) -> str:
        """Retrieves detailed information about gala guests based on their name or relation."""
        results = self.vector_store.similarity_search(query, k=1)
        if results:
            return "\n\n".join([doc.page_content for doc in results])
        else:
            return "No matching guest information found."


# Initialize the RAG manager
vector_store_manager = RAGManager()

@tool
def guest_info_tool(query: str) -> str:
    """Retrieves detailed information about gala guests based on their name or relation."""
    return vector_store_manager.retrieve_guests(query)


