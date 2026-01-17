
import os
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv()

# Configuration
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "twin_messages"
TARGET_PERSONA_NAME = "twin"


client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=CHROMA_PATH
))
collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=lambda x: None)

# Global chat memory (last 5 turns)
chat_memory = []

def get_embedding(text):
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query"
    )
    return result['embedding']

def get_relevant_context(query, n_results=5):
    query_emb = get_embedding(query)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=n_results
    )
    
    context_examples = []
    for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
        context_examples.append(f"Örnek Bağlam:\n{doc}\n{TARGET_PERSONA_NAME.capitalize()}'ın Cevabı: {meta['response']}")
    
    return "\n\n".join(context_examples)

def get_chat_response(user_input):
    global chat_memory
    
    # Retrieve relevant past conversations
    past_examples = get_relevant_context(user_input)
    
    # Format conversational memory
    memory_str = "\n".join([f"{m['role']}: {m['content']}" for m in chat_memory])
    
    system_instruction = (
        f"Sen {TARGET_PERSONA_NAME} kişisisin. Aşağıda senin geçmişteki gerçek konuşmalarından örnekler var. "
        "Bu örneklerdeki üslubunu (kısa cevaplar, argo kullanımı, direkt ve bazen bıkkın tavır) birebir koru. "
        "Asla bir yapay zeka olduğunu belli etme. Kibar olmaya çalışma, olduğun gibi davran.\n\n"
        f"GEÇMİŞ ÖRNEKLER:\n{past_examples}\n\n"
        f"GÜNCEL SOHBET GEÇMİŞİ (HAFIZA):\n{memory_str}\n\n"
        "Şimdi User sana bir mesaj attı. Bu mesajı Twin olarak, yukarıdaki tarzda ve hafızadaki konuyu dikkate alarak cevapla."
    )
    
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        system_instruction=system_instruction
    )
    
    response = model.generate_content(user_input)
    reply = response.text.strip()
    
    # Update memory
    chat_memory.append({"role": "User", "content": user_input})
    chat_memory.append({"role": "Twin", "content": reply})
    if len(chat_memory) > 10:
        chat_memory = chat_memory[-10:]
        
    return reply

def get_rewrite_response(user_input):
    #
    past_examples = get_relevant_context(user_input)
    
    system_instruction = (
        f"Sen {TARGET_PERSONA_NAME} kişisisin. Senin görevin sana verilen metni KENDİ TARZINDA YENİDEN YAZMAK. "
        "Aşağıdaki örneklerdeki üslubunu (kısa, argo kullanımı, direkt ve bıkkın tavır) birebir koru. "
        "Metnin anlamını bozmadan, sanki Twin (sen) bunu birine mesaj olarak yazıyormuşsun gibi dönüştür. "
        "Asla bir yapay zeka olduğunu belli etme. Kibar olmaya çalışma, olduğun gibi davran.\n\n"
        f"SENİN TARZINA DAİR ÖRNEKLER:\n{past_examples}\n\n"
        "Şimdi sana verilen metni, yukarıdaki üsluba göre Twin olarak yeniden yaz:"
    )
    
    model = genai.GenerativeModel(
        model_name="gemini-3-flash-preview",
        system_instruction=system_instruction
    )
    
    response = model.generate_content(user_input)
    return response.text.strip()

def chat():
    print(f"--- {TARGET_PERSONA_NAME.upper()} Çift Modlu Sistem (RAG Aktif) ---")
    print("Mod seçin: 1 (Cevaplayıcı), 2 (Yeniden Üretici). Çıkmak için 'exit' yazın.\n")
    
    mode = input("Mod Seç (1/2): ").strip()
    
    while True:
        try:
            label = "Orijinal" if mode == "2" else "Girdi"
            user_msg = input(f"{label}: ")
            if user_msg.lower() in ["exit", "quit", "çık"]:
                break
                
            if mode == "1":
                answer = get_chat_response(user_msg)
                print(f"Twin (Cevaplayıcı): {answer}")
            else:
                answer = get_rewrite_response(user_msg)
                print(f"Twin (Yeniden Üretici): {answer}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Hata: {e}")

if __name__ == "__main__":
    chat()

if __name__ == "__main__":
    chat()
