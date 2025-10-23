import streamlit as st
from agent_config import create_legal_agent

st.set_page_config(page_title="⚖️ Indian Legal AI Advisor", page_icon="📚", layout="wide")

st.title("⚖️ Indian Legal Advisor (Gemini 2.5 + MongoDB)")
st.caption("Get general insights based on Indian laws like IPC & IT Act 🧠")

query = st.text_area(
    "Ask your legal question 👇",
    placeholder="Example: What are the penalties for phishing under the IT Act 2000?",
    height=100,
)

if st.button("🔍 Get Legal Insights"):
    if query.strip():
        with st.spinner("Consulting Indian Law knowledge base..."):
            agent = create_legal_agent()
            response = agent.run(query)

            # 🧾 Extract clean output
            ai_output = None
            if hasattr(response, "output") and response.output:
                ai_output = response.output
            elif hasattr(response, "messages") and len(response.messages) > 0:
                last_msg = response.messages[-1]
                ai_output = getattr(last_msg, "content", None)

            if ai_output:
                st.success("✅ Response Ready!")
                st.markdown("### 🧾 Legal Information:")
                st.write(ai_output)
            else:
                st.error("⚠️ No valid text from AI Agent.")
                st.json(response.model_dump())
    else:
        st.warning("Please enter a question first.")

st.markdown("---")
st.markdown("👨‍💻 Built by Bhargav | Powered by Gemini 2.5 + MongoDB")
