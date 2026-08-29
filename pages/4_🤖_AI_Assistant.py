"""
AIDED-EDC — AI Assistant Chat Page
"""
import streamlit as st
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(page_title="AI Assistant | AIDED-EDC", page_icon="🤖", layout="wide")

st.markdown("## 🤖 AI Query Assistant")
st.markdown(
    "Ask questions about the AIDED-EDC database in plain English. "
    "No API key required — powered by intelligent keyword-to-SQL parsing."
)
st.divider()

# Example queries in sidebar
with st.sidebar:
    st.markdown("### 💡 Example Questions")
    examples = [
        "How many chemicals are in the database?",
        "Show all bisphenol compounds",
        "Which chemicals are active on ERalpha?",
        "List all inactive controls",
        "What are the most potent EDCs?",
        "Show regulatory hazard data",
        "Find parabens",
        "Which AR antagonists are in the database?",
        "Show thyroid disruptors",
        "List all isoflavones",
    ]
    for ex in examples:
        if st.button(ex, key=f"ex_{ex}", use_container_width=True):
            st.session_state.pending_query = ex

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []

# ─── Chat state ───────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"], avatar="🧬" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        if "df" in msg and msg["df"] is not None and not msg["df"].empty:
            st.dataframe(msg["df"], use_container_width=True, hide_index=True)
        if "sql" in msg and msg["sql"]:
            with st.expander("🔍 SQL Used"):
                st.code(msg["sql"], language="sql")

# ─── Handle pending query from sidebar button ─────────────────────────────────
if "pending_query" in st.session_state:
    user_input = st.session_state.pop("pending_query")
else:
    user_input = st.chat_input("Ask anything about the database...")

if user_input:
    # Show user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Get response
    with st.spinner("Querying database..."):
        try:
            from ai.chatbot import EDCQueryAssistant
            assistant = EDCQueryAssistant()
            msg, df, used_sql = assistant.parse_and_respond(user_input)
        except Exception as e:
            msg = f"❌ Error: {e}"
            df = None
            used_sql = ""

    # Show assistant response
    with st.chat_message("assistant", avatar="🧬"):
        st.markdown(msg)
        import pandas as pd
        if isinstance(df, pd.DataFrame) and not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download Results", csv, "query_results.csv", "text/csv")
        if used_sql and not used_sql.startswith("SQL Error"):
            with st.expander("🔍 SQL Used"):
                st.code(used_sql, language="sql")

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": msg,
        "df": df if isinstance(df, pd.DataFrame) else None,
        "sql": used_sql
    })
    st.rerun()
