from string import ascii_uppercase
from fastapi import FastAPI
from app.routes import router

app = FastAPI(
    title="Agentic Security Triage",
    version="1.0.0",
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(router)