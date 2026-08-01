import os
from dotenv import load_dotenv

#load environment variables
load_dotenv()

class Settings:

    # --- GEMINI EMBEDDINGS ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # --- GROQ REASONING ENGINE ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    # GROQ_FALLBACK_API_KEY = os.getenv("GROQ_FALLBACK_API_KEY")
    GROQ_MODEL = "llama-3.3-70b-versatile"

    # --- QDRANT VECTOR DB ---
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_CLUSTER_ENDPOINT = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QDRANT_COLLECTION = "multimodal_agentic_rag"


settings = Settings()