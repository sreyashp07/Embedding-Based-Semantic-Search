import streamlit as st
import requests
import sys
import os

# Add project root to path so we can import utils/helpers.py
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


def check_api_health():
    try:
        r = requests.get(API_URL + "/", timeout=3)
        return r.status_code == 200
    except:
        return False


def get_status():
    try:
        r = requests.get(API_URL + "/status", timeout=5)
        return r.json()
    except:
        return {"indexed": False, "document_count": 0}


def trigger_index():
    try:
        r = requests.post(API_URL + "/index", json={}, timeout=60)
        return r.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def do_search(query, top_k):
    try:
        r = requests.post(
            API_URL + "/search",
            json={"query": query, "top_k": top_k},
            timeout=30
        )
        if r.status_code == 200:
            return {"success": True, "data": r.json()}
        return {"success": False, "error": r.json().get("detail", "Error")}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API. Is FastAPI running?"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def make_card(rank, title, pct, badge_class, content, score, doc_id):
    return (
        "<div class='result-card'>"
        "<div style='display:flex;justify-content:space-between;align-items:center;'>"
        "<span style='font-size:18px;font-weight:bold;'>"
        + "#" + str(rank) + " &mdash; " + str(title) +
        "</span>"
        "<span class='score-badge " + badge_class + "'>"
        + "Match: " + str(pct) +
        "</span>"
        "</div>"
        "<p style='color:#94a3b8;margin-top:8px;font-size:14px;'>"
        + truncate_text(str(content), 250) +
        "</p>"
        "<small style='color:#6b7280;'>"
        + "Score: " + str(score) + " | Doc ID: " + str(doc_id) +
        "</small>"
        "</div>"
    )


# ── SIDEBAR ──────────────────────────────────────────
with st.sidebar:
    st.title("Settings")
    st.markdown("---")

    api_healthy = check_api_health()

    if api_healthy:
        st.success("API Connected")
    else:
        st.error("API Offline")
        st.markdown("Start the backend:")
        st.code("cd backend\nuvicorn main:app --reload", language="bash")

    st.markdown("---")

    status = get_status()
    if status["indexed"]:
        st.info("Documents indexed: " + str(status["document_count"]))
    else:
        st.warning("No documents indexed yet")

    if st.button("Re-index Documents", use_container_width=True):
        with st.spinner("Indexing..."):
            res = trigger_index()
        if res.get("success"):
            st.success(res.get("message", "Done"))
            st.rerun()
        else:
            st.error(res.get("message", "Failed"))

    st.markdown("---")
    top_k = st.slider("Number of results", 1, 10, 5)
    st.markdown("---")
    st.markdown("Model: all-MiniLM-L6-v2")
    st.markdown("Method: Cosine Similarity")
    st.markdown("[GitHub Repo](https://github.com/sreyashp07/Embedding-Based-Semantic-Search)")


# ── MAIN PAGE ─────────────────────────────────────────
st.title("Embedding-Based Semantic Search")
st.markdown("Search documents by meaning, not just keywords.")
st.markdown("---")

col1, col2 = st.columns([5, 1])
with col1:
    query = st.text_input(
        "query",
        placeholder="e.g. how do machines learn from data",
        label_visibility="collapsed"
    )
with col2:
    search_clicked = st.button("Search", use_container_width=True, type="primary")

st.markdown("Try an example:")
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

# ── SEARCH LOGIC ──────────────────────────────────────
if search_clicked and query.strip():
    if not api_healthy:
        st.error("FastAPI is not running. Start it first:")
        st.code("cd backend\nuvicorn main:app --reload", language="bash")
    else:
        with st.spinner("Searching..."):
            result = do_search(query, top_k)

        if result["success"]:
            data    = result["data"]
            results = data["results"]

            st.subheader("Results for: " + str(data["query"]))

            if not results:
                st.warning("No results found. Try a different query.")
            else:
                for rank, doc in enumerate(results, start=1):
                    score = doc["score"]
                    pct   = score_to_percentage(score)
                    color = get_score_color(score)

                    if color == "green":
                        badge = "high-score"
                    elif color == "orange":
                        badge = "mid-score"
                    else:
                        badge = "low-score"

                    st.markdown(
                        make_card(rank, doc["title"], pct, badge,
                                  doc["content"], score, doc["id"]),
                        unsafe_allow_html=True
                    )

            with st.expander("Score Guide"):
                st.markdown("""
| Color | Score Range | Meaning |
|---|---|---|
| Green | 0.6 to 1.0 | Strong semantic match |
| Orange | 0.35 to 0.59 | Moderate match |
| Red | 0.0 to 0.34 | Weak match |
                """)

        else:
            st.error("Search failed: " + str(result["error"]))

elif search_clicked and not query.strip():
    st.warning("Please type something to search.")


# ── HOW IT WORKS ──────────────────────────────────────
with st.expander("How does this work?"):
    st.markdown("""
**Step 1:** You type a query into the search box.

**Step 2:** Streamlit sends your query to FastAPI via HTTP POST.

**Step 3:** FastAPI converts your query into a 384-number vector using the AI model.

**Step 4:** That vector is compared to all document vectors using cosine similarity.

**Step 5:** Documents are ranked by similarity score from highest to lowest.

**Step 6:** Top results are sent back and displayed as cards with color-coded scores.

**Why this beats keyword search:**
Keyword search only finds exact word matches.
Semantic search understands meaning.
Searching for "joyful" will find documents about "happiness".
Searching for "AI" will find documents about "machine learning".
    """)