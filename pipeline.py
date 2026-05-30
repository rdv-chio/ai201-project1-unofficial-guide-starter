import os
import re

def clean_text(text):
    """
    Cleans out background noise from MCIT Central text.
    Strips inline markers and cleans up excessive spacing.
    """
    # Remove the citations from the raw text completely
    #cleaned = re.sub(r'\', '', text)
    cleaned = re.sub(r'\[[^\]]*\]', '', text)
    
    # Normalize whitespace and strip trailing/leading spaces
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def chunk_document(text, source_name, chunk_size=500, overlap=100):
    """
    Splits text into fixed character chunks with a sliding window overlap.
    Tracks metadata fields for source verification.
    """
    chunks = []
    if len(text) <= chunk_size:
        return [{"text": text, "metadata": {"source": source_name, "start_idx": 0}}]
        
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk_text = text[start:end]
        
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "source": source_name,
                "start_idx": start
            }
        })
        
        # Move the window forward by chunk_size minus overlap
        start += (chunk_size - overlap)
        
        # Break if the remaining window is smaller than the step size
        if start + (chunk_size - overlap) >= len(text) and start < len(text):
            # Capture the final tail end of the text cleanly
            chunks.append({
                "text": text[start:],
                "metadata": {"source": source_name, "start_idx": start}
            })
            break
            
    return chunks

def process_all_documents(docs_dir="documents"):
    """
    Cycles through all files in the target directory and executes processing pipeline.
    """
    all_chunks = []
    if not os.path.exists(docs_dir):
        print(f"Error: Directory '{docs_dir}' not found.")
        return all_chunks
        
    for filename in os.listdir(docs_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(docs_dir, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read()
                
            cleaned_content = clean_text(raw_content)
            file_chunks = chunk_document(cleaned_content, filename)
            all_chunks.extend(file_chunks)
            
    print(f"Successfully processed {len(os.listdir(docs_dir))} documents into {len(all_chunks)} unique chunks.")
    return all_chunks

if __name__ == "__main__":
    # Milestone 3 Validation: Inspect a few random chunks to ensure sanity
    import random
    
    chunks = process_all_documents()
    if chunks:
        print("\n--- INVENTORY INSPECTION: 3 RANDOM CHUNKS ---\n")
        sample_chunks = random.sample(chunks, min(len(chunks), 3))
        for idx, c in enumerate(sample_chunks):
            print(f"Sample #{idx + 1} | Source: {c['metadata']['source']} | Start Pos: {c['metadata']['start_idx']}")
            print(f"Content: {c['text']}")
            print("-" * 50)