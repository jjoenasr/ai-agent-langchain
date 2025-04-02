import datasets
from langchain.docstore.document import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
# from langchain_community.retrievers import BM25Retriever
from langchain.tools import Tool
import faiss
import os

FAISS_PATH = "faiss_vector_store"
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

if os.path.exists(FAISS_PATH):
    vector_store = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
else:
    index = faiss.IndexHNSWFlat(768, 10) # (emb_size, n_neighbors)
    vector_store = FAISS(embedding_function=embeddings,
                        index=index, # where to store the vectors
                        docstore=InMemoryDocstore(), # where to store documents metadata
                        index_to_docstore_id={} # how to map index to docstore
                        )

def extract_text(query: str) -> str:
    """Retrieves detailed information about gala guests based on their name or relation."""
    global vector_store
    results = vector_store.similarity_search(query, k=1)
    if results:
        return "\n\n".join([doc.page_content for doc in results])
    else:
        return "No matching guest information found."

guest_info_tool = Tool(
    name="guest_info_retriever",
    func=extract_text,
    description="Retrieves detailed information about gala guests based on their name or relation."
)

def load_guest_dataset() -> Tool:
    if not os.path.exists(FAISS_PATH):
        guest_dataset = datasets.load_dataset("agents-course/unit3-invitees", split="train")
        # Convert dataset entries into Document objects
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
        global vector_store
        vector_store.add_documents(documents=docs)
        vector_store.save_local(FAISS_PATH)
    return guest_info_tool

# guest_info_tool = load_guest_dataset()
# print(guest_info_tool.invoke('Who is Marie Curie?'))



