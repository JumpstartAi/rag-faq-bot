from fastapi import FastAPI
from routers.ask import router as ask_router

app = FastAPI(title="RAG-FAQ Bot")

# monta le rotte /ask  (GET e POST)
app.include_router(ask_router)
