from chatgpt_plugin_fastapi_langchain_chroma import create_app

app = create_app()
from routers.ask import router as ask_router
app.include_router(ask_router)
