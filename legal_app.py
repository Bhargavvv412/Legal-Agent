import streamlit as st
import asyncio
import os
import time
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.models.google import Gemini
from agno.vectordb.chroma import ChromaDb
from dotenv import load_dotenv

# 🔹 Load environment
load_dotenv()
os.getenv("GOOGLE_API_KEY")
os.getenv("EXA_API_KEY")

CHROMA_DIR = "./legal_chromadb"

# 🧠 Initialize ChromaDB knowledge store
@st.cache_resource
def init_knowledge():
    st.write("🧠 Initializing ChromaDB knowledge store...")
    start = time.time()
    knowledge = Knowledge(
        vector_db=ChromaDb(
            collection="indian_laws",
            path=CHROMA_DIR,
        ),
    )
    st.success(f"✅ Knowledge base ready in {round(time.time()-start,2)} sec.")
    return knowledge

knowledge = init_knowledge()

# 🧩 Create Legal Agent
@st.cache_resource
def create_legal_agent():
    st.write("🤖 Creating IndianLegalAdvisor agent...")
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

agent = create_legal_agent()

# 🚀 Streamlit UI
st.title("⚖️ Indian Legal Advisor AI")
st.write("Ask any question related to Indian laws, cybercrime, or IT Act 2000.")

question = st.text_area("Enter your question:", height=120)

if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking... 🤔"):
            try:
                response = agent.run(question)
                output = getattr(response, "output_text", str(response))
                st.markdown("### 🧾 Answer")
                st.markdown(output)
            except Exception as e:
                st.error(f"❌ Error: {e}")
