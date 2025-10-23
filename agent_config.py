import os
import time
import asyncio
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.models.google import Gemini
from agno.vectordb.chroma import ChromaDb
from dotenv import load_dotenv

# 🔹 Load environment variables
load_dotenv()
os.getenv("GOOGLE_API_KEY")
os.getenv("EXA_API_KEY")

# ⚙️ ChromaDB setup (local persistent directory)
CHROMA_DIR = "./legal_chromadb"

# 🧠 Initialize Chroma knowledge base safely
def init_knowledge():
    print("🧠 Initializing ChromaDB knowledge store...")
    start = time.time()

    # ✅ Ensure the ChromaDB directory exists
    if not os.path.exists(CHROMA_DIR):
        os.makedirs(CHROMA_DIR)
        print(f"📁 Created local Chroma directory: {CHROMA_DIR}")

    try:
        knowledge = Knowledge(
            vector_db=ChromaDb(
                collection="indian_laws",
                path=CHROMA_DIR,
            ),
        )
        print(f"✅ Knowledge base initialized successfully in {round(time.time()-start,2)} sec.")
        return knowledge
    except Exception as e:
        print(f"❌ Error initializing ChromaDB: {e}")
        exit(1)

knowledge = init_knowledge()

# ⚖️ Add Indian Legal Documents (run once)
async def ingest_docs():
    print("📘 Ingesting Indian legal documents into ChromaDB...")
    start = time.time()
    try:
        await knowledge.add_content_async(
            urls=[
                "https://www.indiacode.nic.in/bitstream/123456789/1999/1/A2000-21%20(1).pdf",  # IT Act 2000
                "https://www.indiacode.nic.in/bitstream/123456789/4219/1/THE-INDIAN-PENAL-CODE-1860.pdf",  # IPC 1860
            ]
        )
        print(f"✅ Documents ingested successfully in {round(time.time() - start, 2)} sec.")
    except Exception as e:
        print(f"❌ Failed to ingest: {e}")

# Uncomment below line once to ingest documents
# asyncio.run(ingest_docs())

# 🤖 Create Legal Agent
def create_legal_agent():
    print("🤖 Creating IndianLegalAdvisor agent...")
    return Agent(
        name="IndianLegalAdvisor",
        knowledge=knowledge,
        search_knowledge=True,
        model=Gemini(id="gemini-2.5-pro"),
        markdown=True,
        instructions=[
            "You are an Indian Legal Advisor AI trained on Indian laws and cyber regulations.",
            "Answer questions referencing IPC, IT Act 2000, and Cybercrime laws.",
            "Cite relevant sections and acts when possible.",
            "Clarify that you are not a lawyer and responses are for educational use only.",
            "Encourage consulting a licensed advocate for real legal advice.",
        ],
    )

# 🧠 Example test run
if __name__ == "__main__":
    # ⚠️ Run once to create vector DB
    # asyncio.run(ingest_docs())

    question = "What are the penalties for email spoofing under the IT Act in India?"
    legal_agent = create_legal_agent()
    print("🚀 Running AI query...\n")
    ans = legal_agent.print_response(question, stream=True)
    print(ans)
