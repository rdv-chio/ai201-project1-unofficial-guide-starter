import chromadb
from chromadb.utils import embedding_functions

def retrieve_chunks(query_text, n_results=4):
    """
    Connects to the local ChromaDB and retrieves the top-k semantic matches.
    """
    chroma_client = chromadb.PersistentClient(path="./chroma_db")
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    collection = chroma_client.get_collection(name="mcit_reviews", embedding_function=sentence_transformer_ef)
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    return results

if __name__ == "__main__":
    # Testing Evaluation Question #1 from our planning.md
    test_query = "What is the primary difficulty students face in the second half of CIT-591?"
    print(f"Testing Retrieval for: '{test_query}'\n")
    
    n_results = 4 #The embedding model over-indexed on the semantic concept of 'late-semester difficulty' rather than the keyword 'CIT-591', pulling irrelevant courses into the top-k results.

    results = retrieve_chunks(test_query, n_results=n_results)
    
    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        meta = results['metadatas'][0][i]
        dist = results['distances'][0][i]  # Lower distance = better semantic match
        
        print(f"Result {i+1} | Source: {meta['source']} | Distance: {dist:.4f}")
        print(f"Text: {doc}")
        print("-" * 60)