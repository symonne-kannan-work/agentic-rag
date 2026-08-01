from langchain_groq import ChatGroq

from app.config import settings


guard_llm = ChatGroq(
    api_key=settings.GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0,
)