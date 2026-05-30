import chromadb
from chromadb.utils import embedding_functions
from pipeline import process_all_documents

def build_vector_store():
    # 1. Grab our beautifully cleaned chunks
    chunks = process_all_documents()
    
    # 2. Initialize local ChromaDB 
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    
    # 3. Load the specific embedding model from our planning.md spec
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # (Optional cleanup: delete the collection if it exists so we don't duplicate data on re-runs)
    try:
        chroma_client.delete_collection(name="mcit_reviews")
    except:
        pass
        
    # 4. Create the collection
    collection = chroma_client.create_collection(name="mcit_reviews", embedding_function=sentence_transformer_ef)
    
    # 5. Format data for Chroma
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    print(f"\nEmbedding {len(documents)} chunks and saving to ChromaDB...")
    print("This might take a minute on the first run as it downloads the model...")
    
    # 6. Insert into database
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )
    print("✅ Vector store built successfully in the './chroma_db' directory!")

if __name__ == "__main__":
    build_vector_store()