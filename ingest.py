
import os
import json
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv("XAI_API_KEY") # Using the same key if valid for Google or assuming user has GOOGLE_API_KEY
if not os.getenv("GOOGLE_API_KEY"):
    # If GOOGLE_API_KEY is not set, try to use XAI_API_KEY if that was the intention, 
    # but the prompt specifically mentioned Gemini API.
    # User previously used XAI_API_KEY for Grok. Gemini needs its own key usually.
    # I will assume the environment might have GOOGLE_API_KEY.
    pass

genai.configure(api_key=os.getenv("GOOGLE_API_KEY") or os.getenv("XAI_API_KEY"))

# Check for dataset file. Defaults to the output of whatsapp_parser.py
DATA_FILE = "newwp.jsonl"
if not os.path.exists(DATA_FILE) and os.path.exists("gero.jsonl"):
    DATA_FILE = "gero.jsonl"

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "twin_messages"

def get_embedding(text):
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_document",
        title="Chat Context"
    )
    return result['embedding']

def ingest_data():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return

    # Initialize ChromaDB (Older API)
    client = chromadb.Client(Settings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=CHROMA_PATH
    ))
    # We set embedding_function to None because we provide them manually
    collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=lambda x: None)

    print(f"Reading {DATA_FILE}...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    print(f"Total lines to process: {len(lines)}")
    
    # Process in batches to avoid overwhelming or for better progress tracking
    batch_size = 50
    for i in tqdm(range(0, len(lines), batch_size)):
        batch = lines[i:i+batch_size]
        ids = []
        embeddings = []
        metadatas = []
        documents = []
        
        texts_to_embed = []
        metadatas_to_add = []
        ids_to_add = []
        
        for idx, line in enumerate(batch):
            try:
                data = json.loads(line)
                context = data.get("context", "")
                response = data.get("response", "")
                
                if not context or not response:
                    continue
                
                texts_to_embed.append(context)
                metadatas_to_add.append({"response": response})
                ids_to_add.append(f"id_{i+idx}")
            except Exception as e:
                print(f"Error parsing line {i+idx}: {e}")
                continue
        
        if texts_to_embed:
            try:
                # Batch embedding call
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=texts_to_embed,
                    task_type="retrieval_document"
                )
                embeddings = result['embedding']
                
                collection.add(
                    embeddings=embeddings,
                    metadatas=metadatas_to_add,
                    documents=texts_to_embed,
                    ids=ids_to_add
                )
            except Exception as e:
                print(f"Error in batch embedding/adding {i}: {e}")

    print(f"Ingestion complete. Collections size: {collection.count()}")
    client.persist()

if __name__ == "__main__":
    ingest_data()
