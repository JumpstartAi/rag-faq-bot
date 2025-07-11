from fastapi import APIRouter, Body
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import glob, os

# ⇢  ROUTER senza prefisso: le rotte si dichiarano esplicitamente 
router = APIRouter()

# ---------- indicizzazione ----------
DOC_PATH = "data"
DB_PATH  = "data/chroma"
emb = OpenAIEmbeddings(model="text-embedding-ada-002")

docs = []
for pdf in glob.glob(f"{DOC_PATH}/*.pdf"):
    docs.extend(PyPDFLoader(pdf).load())

if docs and not os.path.exists(DB_PATH):
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50
    ).split_documents(docs)
    vectordb = Chroma.from_documents(
        chunks, emb, persist_directory=DB_PATH
    )
    vectordb.persist()
else:
    vectordb = Chroma(
        persist_directory=DB_PATH,
        embedding_function=emb
    )
# ---------- chain ----------
retriever = vectordb.as_retriever(search_k=3)
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0),
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)
# ------------------------------------

@router.post("/ask")
@router.get("/ask")
async def ask(question: str = Body(..., embed=True)):
    """
    Fai una domanda e ottieni risposta + fonti.
    """
    resp = qa(question)
    return {
        "answer": resp["result"],
        "sources": [d.metadata.get("source", "") for d in resp["source_documents"]],
    }
