"""
Placement Prep Assistant — Streamlit UI (Polished)
"""

import streamlit as st
import os
from dotenv import load_dotenv
from rag_pipeline import RAGPipeline

load_dotenv()

st.set_page_config(
    page_title="Placement Prep Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

#MainMenu, footer { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }

.stApp {
    background: radial-gradient(ellipse 90% 45% at 50% -5%,
        rgba(99,102,241,0.12) 0%, transparent 65%), #080b14 !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0d1120 !important;
    border-right: 1px solid #1e2a45 !important;
}

/* ── Chat bubbles ── */
[data-testid="stChatMessage"] {
    border-radius: 14px !important;
    margin: 6px 0 !important;
    animation: popIn .22s ease;
}
@keyframes popIn {
    from { opacity:0; transform:translateY(5px); }
    to   { opacity:1; transform:translateY(0); }
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(99,102,241,0.13) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #111827 !important;
    border: 1px solid #1e2a45 !important;
}

/* ── Bottom bar & input ── */
div[data-testid="stBottom"],
div[data-testid="stBottom"] > div {
    background: #080b14 !important;
}
div[data-testid="stBottom"] {
    border-top: 1px solid #1e2a45 !important;
}
div[data-testid="stChatInput"] {
    background: #111827 !important;
    border: 1.5px solid #2a3450 !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.45) !important;
    transition: border-color .2s !important;
}
div[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.16), 0 4px 20px rgba(0,0,0,0.45) !important;
}
div[data-testid="stChatInput"] > div { background: transparent !important; }
div[data-testid="stChatInput"] textarea {
    background: transparent !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: .95rem !important;
    border: none !important;
    box-shadow: none !important;
    caret-color: #6366f1 !important;
}
div[data-testid="stChatInput"] textarea::placeholder { color: #4b5563 !important; }
div[data-testid="stChatInput"] button {
    background: linear-gradient(135deg,#6366f1,#8b5cf6) !important;
    border: none !important; border-radius: 10px !important;
    width:36px !important; height:36px !important; min-width:36px !important;
    padding:0 !important; margin:0 4px !important;
    box-shadow: 0 2px 10px rgba(99,102,241,0.4) !important;
    transition: transform .15s, box-shadow .15s !important;
}
div[data-testid="stChatInput"] button:hover {
    transform: scale(1.08) !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.65) !important;
}
div[data-testid="stChatInput"] button svg { fill:#fff !important; stroke:#fff !important; }

/* ── Starter / Quick-pick buttons ── */
.stButton > button {
    background: rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(99,102,241,0.22) !important;
    color: #a5b4fc !important;
    border-radius: 20px !important;
    font-size: .82rem !important;
    font-weight: 500 !important;
    padding: 5px 14px !important;
    transition: all .18s !important;
    white-space: nowrap;
}
.stButton > button:hover {
    background: rgba(99,102,241,0.22) !important;
    border-color: rgba(99,102,241,0.5) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 3px 12px rgba(99,102,241,0.3) !important;
}

/* Sidebar clear button — override pill style */
[data-testid="stSidebar"] .stButton > button {
    border-radius: 10px !important;
    background: rgba(239,68,68,0.08) !important;
    border: 1px solid rgba(239,68,68,0.22) !important;
    color: #f87171 !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(239,68,68,0.18) !important;
    border-color: rgba(239,68,68,0.45) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* ── Source chip ── */
.source-chip {
    display: inline-flex; align-items:center;
    background: rgba(99,102,241,0.1); color: #a5b4fc;
    border: 1px solid rgba(99,102,241,0.22); border-radius: 6px;
    padding: 2px 8px; font-size: .74rem; font-weight:500; margin: 2px 3px;
}

/* ── Link card ── */
.link-card {
    display:flex; align-items:center; gap:10px;
    background:#111827; border:1px solid #1e2a45; border-radius:10px;
    padding:9px 14px; margin:5px 0; text-decoration:none !important;
    transition: all .18s;
}
.link-card:hover {
    border-color:#6366f1; background:rgba(99,102,241,0.08);
    transform:translateX(3px);
}
.link-card .lc-title { color:#a5b4fc; font-size:.85rem; font-weight:500; }

/* ── Status pill ── */
.status-pill {
    display:inline-flex; align-items:center; gap:7px;
    background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.25);
    border-radius:20px; padding:4px 14px;
    font-size:.74rem; font-weight:500; color:#34d399; margin-bottom:.9rem;
}
.sdot {
    width:7px; height:7px; border-radius:50%;
    background:#10b981; box-shadow:0 0 6px #10b981;
    animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:.3} }

/* ── Expander ── */
details {
    background:rgba(17,24,39,0.7) !important;
    border:1px solid #1e2a45 !important; border-radius:10px !important;
    padding:4px 12px !important;
}
details summary { color:#64748b; font-size:.8rem; cursor:pointer; }
details summary:hover { color:#a5b4fc; }

/* ── Topic badge (sidebar) ── */
.tbadge {
    display:flex; align-items:center; gap:9px;
    padding:8px 10px; margin:4px 0; border-radius:10px;
    background:rgba(99,102,241,0.07); border:1px solid rgba(99,102,241,0.13);
}
.tbname { font-size:.82rem; font-weight:600; color:#a5b4fc; }
.tbsub  { font-size:.69rem; color:#475569; }

/* misc */
section.main > div { padding-bottom:7rem !important; }
hr { border-color:#1e2a45 !important; }
::-webkit-scrollbar { width:4px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#1e2a45; border-radius:4px; }
p, li { color:#e2e8f0 !important; line-height:1.7 !important; }
code {
    background:rgba(99,102,241,0.14) !important; color:#a5b4fc !important;
    border-radius:4px !important; padding:1px 5px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Quick-pick prompts ─────────────────────────────────────────────────────────
QUICK_PROMPTS = [
    ("📘", "Dynamic Programming"),
    ("🗄️", "ACID Properties"),
    ("⚙️", "Deadlock Prevention"),
    ("🧠", "OOP Concepts"),
    ("📊", "Bias-Variance Tradeoff"),
    ("🌳", "Binary Search Tree"),
    ("🔍", "SQL Joins"),
    ("🖥️", "Process vs Thread"),
]


# ── Pipeline ───────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_pipeline():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        st.error("❌ GROQ_API_KEY missing from .env"); st.stop()
    try:
        rag = RAGPipeline(groq_api_key=key)
        rag.initialize(rebuild_vector_store=False)
        return rag
    except Exception as e:
        st.error(f"❌ Failed to start: {e}"); st.stop()


# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;
         padding-bottom:.9rem;border-bottom:1px solid #1e2a45;margin-bottom:1rem;">
        <div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;
             background:linear-gradient(135deg,#6366f1,#8b5cf6);
             display:flex;align-items:center;justify-content:center;font-size:1.1rem;">🎯</div>
        <div>
            <div style="font-size:.96rem;font-weight:700;
                 background:linear-gradient(90deg,#a5b4fc,#c4b5fd);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
                Prep Assistant</div>
            <div style="font-size:.67rem;color:#475569;">AI · Interview Ready</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # About
    st.markdown("""
    <p style="font-size:.7rem;font-weight:600;letter-spacing:.08em;
       color:#475569;text-transform:uppercase;margin:0 0 .4rem 2px;">About</p>
    <p style="font-size:.8rem;color:#64748b;line-height:1.7;margin:0 0 .9rem;">
    Your personal study companion for technical placement interviews.
    Ask questions on <b style="color:#a5b4fc;">DSA, DBMS, OS, OOP</b> and
    <b style="color:#a5b4fc;">ML</b> — and get clear, concise answers.
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:.7rem;font-weight:600;letter-spacing:.08em;color:#475569;text-transform:uppercase;margin:0 0 .4rem 2px;">📚 Topics</p>', unsafe_allow_html=True)

    for icon, name, sub in [
        ("🧮", "DSA",  "Arrays · Trees · Graphs · DP · Sorting"),
        ("🗄️", "DBMS", "SQL · ACID · Normalization · Indexing"),
        ("🖥️", "OS",   "Processes · Threads · Deadlocks · Scheduling"),
        ("🔷", "OOP",  "Encapsulation · Inheritance · Polymorphism"),
        ("🤖", "ML",   "Regression · Bias-Variance · Algorithms"),
    ]:
        st.markdown(f"""
        <div class="tbadge">
            <span style="font-size:1rem;">{icon}</span>
            <div><div class="tbname">{name}</div><div class="tbsub">{sub}</div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_prompt = None
        st.rerun()

    st.markdown("""
    <div style="margin-top:1.4rem;padding:8px 10px;text-align:center;
         background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.14);
         border-radius:8px;">
        <div style="font-size:.67rem;color:#334155;">Powered by</div>
        <div style="font-size:.72rem;font-weight:600;
             background:linear-gradient(90deg,#a5b4fc,#c4b5fd);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            Groq · LangChain · FAISS</div>
    </div>""", unsafe_allow_html=True)


# ── Load pipeline ──────────────────────────────────────────────────────────────
with st.spinner("Starting up…"):
    rag_pipeline = load_pipeline()


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:14px;padding:.4rem 0 .7rem;">
    <div style="width:46px;height:46px;border-radius:13px;flex-shrink:0;
         background:linear-gradient(135deg,#6366f1,#8b5cf6);
         display:flex;align-items:center;justify-content:center;
         font-size:1.4rem;box-shadow:0 4px 18px rgba(99,102,241,0.38);">🎯</div>
    <div>
        <div style="font-size:1.5rem;font-weight:700;line-height:1.2;
             background:linear-gradient(90deg,#e0e7ff 0%,#c4b5fd 60%);
             -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            Placement Prep Assistant</div>
        <div style="font-size:.81rem;color:#64748b;margin-top:2px;">
            Your AI study companion for technical interviews</div>
    </div>
</div>
<hr style="margin:.1rem 0 .7rem;">
""", unsafe_allow_html=True)

# Status pill
st.markdown("""
<div class="status-pill">
    <div class="sdot"></div>
    ✅ Knowledge base ready &nbsp;·&nbsp; 24 topics loaded
</div>""", unsafe_allow_html=True)


# ── Welcome + quick picks (only when chat is empty) ────────────────────────────
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("""
**Hey! 👋 What topic are you preparing today?**

I can help you understand key placement topics and prepare effectively.
Pick a topic below or type your own question — I'll give you a clear, interview-ready answer.
""")

    # Quick-pick buttons
    st.markdown("""
    <p style="font-size:.78rem;font-weight:600;color:#64748b;
       letter-spacing:.05em;margin:.8rem 0 .4rem 4px;">
    🚀 &nbsp;Quick topics — click to explore:</p>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for idx, (icon, label) in enumerate(QUICK_PROMPTS):
        with cols[idx % 4]:
            if st.button(f"{icon} {label}", key=f"qp_{idx}"):
                st.session_state.pending_prompt = f"Explain {label}"
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)


# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📎 View sources", expanded=False):
                for src in msg["sources"]:
                    st.markdown(f'<span class="source-chip">📄 {src["source"]}</span>',
                                unsafe_allow_html=True)
                st.markdown("")
                for i, src in enumerate(msg["sources"], 1):
                    st.markdown(f"**{i}. `{src['source']}`**")
                    st.markdown(
                        f"<div style='background:#0a0e1a;border-radius:8px;"
                        f"padding:10px 14px;font-size:.81rem;color:#94a3b8;"
                        f"border:1px solid #1e2a45;margin-bottom:8px;'>"
                        f"{src['content']}</div>", unsafe_allow_html=True)

        if msg["role"] == "assistant" and msg.get("links"):
            st.markdown("**🔗 Learn More**")
            for link in msg["links"]:
                icon = "🟢" if "geeksforgeeks" in link["url"] \
                    else "🔵" if "w3schools" in link["url"] else "📘"
                st.markdown(
                    f"<a class='link-card' href='{link['url']}' target='_blank'>"
                    f"<span>{icon}</span><span class='lc-title'>{link['title']}</span></a>",
                    unsafe_allow_html=True)


# ── Handle quick-pick or typed prompt ─────────────────────────────────────────
def run_query(prompt: str):
    """Append user message, call pipeline, stream response."""
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                answer, sources, links = rag_pipeline.query(prompt)
            except Exception as e:
                answer, sources, links = f"❌ Something went wrong: {e}", [], []

        st.markdown(answer)

        if sources:
            with st.expander("📎 View sources", expanded=False):
                for src in sources:
                    st.markdown(f'<span class="source-chip">📄 {src["source"]}</span>',
                                unsafe_allow_html=True)
                st.markdown("")
                for i, src in enumerate(sources, 1):
                    st.markdown(f"**{i}. `{src['source']}`**")
                    st.markdown(
                        f"<div style='background:#0a0e1a;border-radius:8px;"
                        f"padding:10px 14px;font-size:.81rem;color:#94a3b8;"
                        f"border:1px solid #1e2a45;margin-bottom:8px;'>"
                        f"{src['content']}</div>", unsafe_allow_html=True)

        if links:
            st.markdown("**🔗 Learn More**")
            for link in links:
                icon = "🟢" if "geeksforgeeks" in link["url"] \
                    else "🔵" if "w3schools" in link["url"] else "📘"
                st.markdown(
                    f"<a class='link-card' href='{link['url']}' target='_blank'>"
                    f"<span>{icon}</span><span class='lc-title'>{link['title']}</span></a>",
                    unsafe_allow_html=True)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "links": links,
    })


# Fire pending quick-pick prompt
if st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None
    run_query(prompt)

# Chat input
if prompt := st.chat_input("Ask anything about DSA, DBMS, OS, OOP, or ML…"):
    run_query(prompt)
