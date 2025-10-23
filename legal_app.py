import os
import time
import asyncio
import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.knowledge import Knowledge
from dotenv import load_dotenv

# 🌍 Load environment variables
load_dotenv()
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# ⚙️ ChromaDB setup
CHROMA_PATH = "./legal_chromadb"

# 🧠 Initialize local knowledge base
@st.cache_resource
def init_knowledge():
    st.info("🧠 Initializing ChromaDB knowledge store...")
    start = time.time()
    knowledge = Knowledge(
        vector_db=ChromaDb(collection="indian_laws", path=CHROMA_PATH)
    )
    st.success(f"✅ Knowledge base ready in {round(time.time() - start, 2)} sec.")
    return knowledge

knowledge = init_knowledge()

# ⚖️ Add legal docs (run once)
async def ingest_docs():
    st.info("📘 Ingesting Indian legal documents into ChromaDB...")
    try:
        await knowledge.add_content_async(
            urls=[
                "https://www.indiacode.nic.in/bitstream/123456789/1999/1/A2000-21%20(1).pdf",
                "https://www.indiacode.nic.in/bitstream/123456789/4219/1/THE-INDIAN-PENAL-CODE-1860.pdf",
            ]
        )
        st.success("✅ Documents ingested successfully!")
    except Exception as e:
        st.error(f"❌ Failed to ingest: {e}")

# 🤖 Create Legal AI Agent
def create_agent():
    try:
        model = Gemini(id="gemini-2.5-pro")
        st.success("✅ Using Gemini model")
    except Exception:
        st.warning("⚠️ Gemini unavailable, using OpenAI fallback")
        model = OpenAIChat(id="gpt-4o-mini", api_key=OPENAI_KEY)

    return Agent(
        name="IndianLegalAdvisor",
        knowledge=knowledge,
        search_knowledge=True,
        model=model,
        markdown=True,
        instructions=[
            "You are an Indian Legal Advisor AI trained on Indian laws and cyber regulations.",
            "Answer questions referencing IPC, IT Act 2000, and Cybercrime laws.",
            "Cite relevant sections and acts when possible.",
            "Clarify that you are not a lawyer and responses are for educational purposes only.",
            "Encourage consulting a licensed advocate for real legal advice.",
        ],
    )

# ⚙️ Streamlit UI
st.set_page_config(page_title="⚖️ Indian Legal Advisor AI", layout="centered")
st.title("⚖️ Indian Legal Advisor AI")
st.caption("Ask questions about Indian laws (IPC, IT Act, Cybercrime, etc.)")

# Sidebar actions
with st.sidebar:
    st.header("⚙️ Controls")
    if st.button("📥 Ingest Legal Docs"):
        asyncio.run(ingest_docs())
    st.divider()
    st.write("💾 Uses local ChromaDB at:", CHROMA_PATH)

# Create agent
agent = create_agent()

# Input box
query = st.text_area("📝 Ask your legal question:", placeholder="e.g., What is the punishment for cyber fraud under the IT Act?")
if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("⚖️ Analyzing legal references..."):
            try:
                response = agent.run(query)
                output = getattr(response, "output_text", str(response.content))
                st.markdown("### 🧾 Answer")
                st.markdown(output)
            except Exception as e:
                st.error(f"❌ Error: {e}")

st.info("💡 Tip: Try asking about Sections 66C, 66D of the IT Act or Section 420 of IPC.")
