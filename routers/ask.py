from fastapi import APIRouter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import glob, os

router = APIRouter(prefix="/ask")

# ---------- costruisci / ricarica l'indice ----------
DOC_PATH = "data"            # volume Railway
DB_PATH  = "data/chroma"
emb = OpenAIEmbeddings()

if not os.path.exists(DB_PATH):
    docs = []
    for pdf in glob.glob(f"{DOC_PATH}/*.pdf"):
        docs.extend(PyPDFLoader(pdf).load())
    chunks = RecursiveCharacterTextSplitter(
                chunk_size=500, chunk_overlap=50).split_documents(docs)
    vectordb = Chroma.from_documents(
                chunks, emb, persist_directory=DB_PATH)
    vectordb.persist()
else:
    vectordb = Chroma(persist_directory=DB_PATH, embedding_function=emb)

retriever = vectordb.as_retriever(search_k=3)
qa = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0),
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True)
# -----------------------------------------------------

@router.post("")      #  ← esiste già
@router.get("")       #  ← AGGIUNGI questa sola riga
async def ask(question: str):
    """
    Fai una domanda e ottieni risposta + fonti.
    """
    resp = qa(question)
    return {
        "answer": resp["result"],
        "sources": [d.metadata.get("source", "") for d in resp["source_documents"]]
    }
