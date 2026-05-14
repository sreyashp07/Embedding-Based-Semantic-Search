import streamlit as st
import requests
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.helpers import truncate_text, score_to_percentage, get_score_color

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Semantic Search",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .result-card {
        background: #1e1e2e;
        border-left: 4px solid #7c3aed;
        padding: 16px 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    .score-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 13px;
        font-weight: bold;
    }
    .high-score { background: #14532d; color: #4ade80; }
    .mid-score  { background: #431407; color: #fb923c; }
    .low-score  { background: #450a0a; color: #f87171; }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    try:
        response = requests.get(f"{API_URL}/", timeout=3)
        return response.status_code == 200
    except:
        return False


def get_status() -> dict:
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        return response.json()
    except:
        return {"indexed": False, "document_count": 0}


def trigger_index() -> dict:
    try:
        response = requests.post(f"{API_URL}/index", json={}, timeout=60)
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def search_documents(query: str, top_k: int) -> dict:
    try:
        payload  = {"query": query, "top_k": top_k}
        response = requests.post(
            f"{API_URL}/search",
            json=payload,
            timeout=30
        )
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            error = response.json().get("detail", "Unknown error")
            return {"success": False, "error": error}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API. Is FastAPI running?"}
    except Exception as e:
        return {"success": False, "error": str(e)}


with st.sidebar:
    st.title("⚙️ Settings")
    st.markdown("---")

    api_healthy = check_api_health()
    if api_healthy:
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline")
        st.code("cd backend\nuvicorn main:app --reload", language="bash")

    st.markdown("---")

    status = get_status()
    if status["indexed"]:
        st.info(f"📚 {status['document_count']} documents indexed")
    else:
        st.warning("⚠️ No documents indexed yet")

    if st.button("🔄 Re-index Documents", use_container_width=True):
        with st.spinner("Indexing..."):
            result = trigger_index()
            if result.get("success"):
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result.get("message", "Failed"))

    st.markdown("---")
    top_k = st.slider("Number of results", 1, 10, 5)
    st.markdown("---")
    st.markdown("**Model:** `all-MiniLM-L6-v2`")
    st.markdown("**Method:** Cosine Similarity")
    st.markdown("[GitHub](https://github.com/sreyashp07/Embedding-Based-Semantic-Search)")


st.title("🔍 Embedding-Based Semantic Search")
st.markdown("Search documents **by meaning**, not just keywords.")
st.markdown("---")

col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input(
        "Search",
        placeholder='e.g. "how do machines learn from data"',
        label_visibility="collapsed"
    )
with col2:
    search_clicked = st.button("🔍 Search", use_container_width=True, type="primary")

st.markdown("**💡 Try an example:**")
c1, c2, c3, c4 = st.columns(4)
with c1:
    if st.button("machines learning", use_container_width=True):
        query = "how do machines learn from data"
        search_clicked = True
with c2:
    if st.button("human happiness", use_container_width=True):
        query = "human emotions and happiness"
        search_clicked = True
with c3:
    if st.button("climate pollution", use_container_width=True):
        query = "environmental pollution and climate"
        search_clicked = True
with c4:
    if st.button("similar documents", use_container_width=True):
        query = "finding similar documents by meaning"
        search_clicked = True

st.markdown("---")

if search_clicked and query.strip():
    if not api_healthy:
        st.error("❌ FastAPI is not running.")
        st.code("cd backend\nuvicorn main:app --reload", language="bash")
    else:
        with st.spinner(f"Searching for: *{query}*..."):
            result = search_documents(query, top_k)

        if result["success"]:
            data    = result["data"]
            results = data["results"]
            st.subheader(f"📋 Top {len(results)} results for: *\"{data['query']}\"*")

            if not results:
                st.warning("No results found. Try different search terms.")
            else:
                for rank, doc in enumerate(results, start=1):
                    score = doc["score"]
                    pct   = score_to_percentage(score)
                    color = get_score_color(score)
                    badge_class = (
                        "high-score" if color == "green" else
                        "mid-score"  if color == "orange" else
                        "low-score"
                    )
                    st.markdown(f"""
                    <div class="result-card">
                        <div style="display:flex;justify-content:space-between;align-items:center;">
                            <span style="font-size:18px;font-weight:bold;">
                                #{rank} &mdash; {doc['title']}
                            </span>
                            <span class="score-badge {badge_class}">
                                🎯 {pct} match
                            </span>
                        </div>
                        <p style="color:#94a3b8;margin-top:8px;font-size:14px;">
                            {truncate_text(doc['content'], 250)}
                        </p>
                        <small style="color:#6b7280;">
                            Score: {score} | ID: {doc['id']}
                        </small>
                    </div>
                    """, unsafe_allow_html=True)

            with st.expander("📊 Score Guide"):
                st.markdown("""
                | Badge | Score | Meaning |
                |---|---|---|
                | 🟢 Green | 0.6–1.0 | Strong match |
                | 🟡 Orange | 0.35–0.59 | Moderate match |
                | 🔴 Red | 0.0–0.34 | Weak match |
                """)
        else:
            st.error(f"❌ {result['error']}")

elif search_clicked and not query.strip():
    st.warning("⚠️ Please type something to search.")

with st.expander("🧠 How does this work?"):
    st.markdown("""