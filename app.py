import os
import gradio as gr
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq
from dotenv import load_dotenv

# Load API key
load_dotenv()
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path="./chroma_db")
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = chroma_client.get_collection(name="mcit_reviews", embedding_function=sentence_transformer_ef)

def ask_unofficial_guide(query_text):
    """Retrieves context and generates a grounded response."""
    
    # 1. Retrieve the top 4 chunks
    results = collection.query(query_texts=[query_text], n_results=4)
    
    retrieved_docs = results['documents'][0]
    retrieved_sources = results['metadatas'][0]
    
    # 2. Format the context for the LLM
    context_blocks = []
    unique_sources = set()
    
    for i in range(len(retrieved_docs)):
        doc = retrieved_docs[i]
        source = retrieved_sources[i]['source']
        context_blocks.append(f"[{source}]: {doc}")
        unique_sources.add(source)
        
    compiled_context = "\n\n".join(context_blocks)
    formatted_sources = "\n".join([f"• {s}" for s in unique_sources])
    
    # 3. System Prompt enforcing Strict Grounding
    system_prompt = """
    You are an assistant for the MCIT Unofficial Guide. 
    You must answer the user's question USING ONLY the provided context documents.
    If the provided documents do not contain enough information to answer the question, 
    you must explicitly say "I don't have enough information on that."
    Do NOT use your general knowledge.
    """
    
    # 4. Generate the response
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context Documents:\n{compiled_context}\n\nQuestion: {query_text}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1, # Keep it strictly factual
        )
        answer = chat_completion.choices[0].message.content
        return answer, formatted_sources
        
    except Exception as e:
        return f"Error communicating with LLM: {e}", ""

# 5. Gradio Interface
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎓 The Unofficial Guide: MCIT Central")
    gr.Markdown("Ask a question about MCIT courses, workload, or difficulty. Answers are grounded purely in student reviews.")
    
    with gr.Row():
        inp = gr.Textbox(label="Your question", placeholder="e.g., Which class is harder: CIT-592 or CIT-596?")
    
    btn = gr.Button("Ask")
    
    with gr.Row():
        answer_box = gr.Textbox(label="Answer", lines=6)
        source_box = gr.Textbox(label="Retrieved from", lines=3)
        
    btn.click(ask_unofficial_guide, inputs=inp, outputs=[answer_box, source_box])
    inp.submit(ask_unofficial_guide, inputs=inp, outputs=[answer_box, source_box])

if __name__ == "__main__":
    demo.launch()