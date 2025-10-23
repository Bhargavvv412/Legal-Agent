import os
import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.models.google import Gemini
from agno.vectordb.chroma import ChromaDb

# 🔹 Load environment variables
load_dotenv()

# ⚙️ ChromaDB setup
CHROMA_DIR = "./legal_chromadb"

# 🧠 Initialize knowledge base
def init_knowledge():
    try:
        if not os.getenv("GOOGLE_API_KEY"):
            st.error("🚨 GOOGLE_API_KEY missing in .env")
            return None

        st.info("🧠 Initializing ChromaDB knowledge store...")
        knowledge = Knowledge(
            vector_db=ChromaDb(collection="indian_laws", path=CHROMA_DIR)
        )
        st.success("✅ Knowledge base ready.")
        return knowledge
    except Exception as e:
        st.error(f"❌ Error initializing ChromaDB: {e}")
        return None

# 🤖 Create Legal Agent
def create_legal_agent(knowledge):
    if knowledge is None:
        return None
    st.info("🤖 Creating IndianLegalAdvisor agent...")
    return Agent(
        name="IndianLegalAdvisor",
        knowledge=knowledge,
        search_knowledge=True,
        model=Gemini(id="gemini-2.5-flash"),
        markdown=True,
        instructions=[
            "You are an Indian Legal Advisor AI trained on Indian laws and cyber regulations.",
            "Answer questions referencing IPC, IT Act 2000, and Cybercrime laws.",
            "Cite relevant sections and acts when possible.",
            "Clarify that you are not a lawyer and responses are for educational use only.",
            "Encourage consulting a licensed advocate for real legal advice.",
        ],
    )

# 🚀 Streamlit UI
def main():
    st.set_page_config(page_title="⚖️ Indian Legal Advisor AI", layout="wide")
    st.title("⚖️ Indian Legal Advisor AI")
    st.markdown("Ask any question related to **Indian Laws**, including the **IT Act 2000** and **IPC 1860**.")
    st.divider()

    # Session memory for agent and chat
    if 'knowledge' not in st.session_state:
        st.session_state.knowledge = init_knowledge()

    if 'agent' not in st.session_state and st.session_state.knowledge:
        st.session_state.agent = create_legal_agent(st.session_state.knowledge)

    agent = st.session_state.get('agent')
    if not agent:
        st.warning("Agent initialization failed.")
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    if prompt := st.chat_input("Ask your legal question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Run the query
                    result = agent.run(prompt)

                    # ✅ Clean output formatting
                    if hasattr(result, "output_text") and result.output_text:
                        answer = result.output_text.strip()
                    elif hasattr(result, "content"):
                        answer = str(result.content).strip()
                    else:
                        answer = str(result).strip()

                    # Clean up and format text nicely
                    answer = (
                        answer.replace("\\n", "\n")
                        .replace("**", "")
                        .replace("Important Disclaimer", "\n\n⚠️ **Disclaimer**")
                    )

                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    err = f"❌ Error: {e}"
                    st.error(err)
                    st.session_state.messages.append({"role": "assistant", "content": err})


if __name__ == "__main__":
    main()
