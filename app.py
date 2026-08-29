"""
AIDED-EDC: AI-Integrated Database for Endocrine Disrupting Chemicals
Main Home Dashboard
"""
import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH  = BASE_DIR / "database" / "aided_edc.db"

st.set_page_config(
    page_title="AIDED-EDC",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS overrides ────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stat-card {
    background: linear-gradient(135deg, #1A1F2E 0%, #252B3B 100%);
    border: 1px solid #00D4AA33;
    border-radius: 12px;
    padding: 1.2rem 1rem;
    text-align: center;
    margin: 0.3rem;
}
.stat-number { font-size: 2.2rem; font-weight: 800; color: #00D4AA; }
.stat-label  { font-size: 0.85rem; color: #9BA3B7; margin-top: 4px; }
.hero-title  { font-size: 2.8rem; font-weight: 900; color: #00D4AA; }
.hero-sub    { font-size: 1.1rem;  color: #C4C8D4; }
.nav-card {
    background: #1A1F2E;
    border: 1px solid #00D4AA44;
    border-radius: 10px;
    padding: 1.2rem;
    margin: 0.3rem;
    min-height: 120px;
}
.nav-card h4 { color: #00D4AA; margin-bottom: 6px; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def get_stats():
    if not DB_PATH.exists():
        return {"total": 0, "er": 0, "ar": 0, "tr": 0, "inactive": 0}
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    def q(sql): return cur.execute(sql).fetchone()[0]
    stats = {
        "total":    q("SELECT COUNT(*) FROM chemicals"),
        "er":       q("SELECT COUNT(DISTINCT compound_id) FROM bioactivity WHERE receptor_target='ERalpha' AND activity_classification='Active'"),
        "ar":       q("SELECT COUNT(DISTINCT compound_id) FROM bioactivity WHERE receptor_target='AR'      AND activity_classification='Active'"),
        "tr":       q("SELECT COUNT(DISTINCT compound_id) FROM bioactivity WHERE receptor_target='TRalpha' AND activity_classification='Active'"),
        "inactive": q("SELECT COUNT(DISTINCT compound_id) FROM bioactivity WHERE activity_classification='Inactive'"),
    }
    conn.close()
    return stats


@st.cache_data(ttl=300)
def get_recent_chemicals(n=8):
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT chemical_name, cas_number, chemical_class, molecular_weight, logp FROM chemicals ORDER BY date_added DESC LIMIT ?",
        conn, params=(n,)
    )
    conn.close()
    return df


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧬 AIDED-EDC")
    st.markdown("**AI-Integrated Database for**\n**Endocrine Disrupting Chemicals**")
    st.divider()
    st.markdown("### Navigate")
    st.page_link("pages/1_🔍_Search.py",     label="🔍 Chemical Search")
    st.page_link("pages/2_🧪_Predict.py",    label="🧪 QSAR Predictor")
    st.page_link("pages/3_🕸️_Visualize.py", label="🕸️ Network View")
    st.page_link("pages/4_🤖_AI_Assistant.py", label="🤖 AI Assistant")
    st.divider()
    st.markdown("**v1.0** | Dissertation Project\nReceptors: ER-α · AR · TR-α")


# ─── Hero ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🧬 AIDED-EDC</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">AI-Integrated Database of Endocrine Disrupting Chemicals — ER-α · AR · TR-α</div>', unsafe_allow_html=True)
st.markdown("---")

# ─── Stats cards ──────────────────────────────────────────────────────────────
stats = get_stats()
cols  = st.columns(5)
cards = [
    (stats["total"],    "Total Chemicals"),
    (stats["er"],       "ER-α Actives"),
    (stats["ar"],       "AR Actives"),
    (stats["tr"],       "TR-α Actives"),
    (stats["inactive"], "Inactive Controls"),
]
for col, (num, lbl) in zip(cols, cards):
    col.markdown(
        f'<div class="stat-card"><div class="stat-number">{num}</div>'
        f'<div class="stat-label">{lbl}</div></div>',
        unsafe_allow_html=True
    )

st.markdown("")

# ─── Navigation cards ─────────────────────────────────────────────────────────
st.markdown("### 🗺️ Explore the Database")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(
        '<div class="nav-card"><h4>🔍 Chemical Search</h4>'
        '<p style="color:#9BA3B7;font-size:0.9rem;">Search by name, CAS number, class, or receptor. Filter by MW and LogP.</p></div>',
        unsafe_allow_html=True)
with c2:
    st.markdown(
        '<div class="nav-card"><h4>🧪 QSAR Predictor</h4>'
        '<p style="color:#9BA3B7;font-size:0.9rem;">Predict ER/AR/TR binding from any SMILES. Includes applicability domain check.</p></div>',
        unsafe_allow_html=True)
with c3:
    st.markdown(
        '<div class="nav-card"><h4>🕸️ Network View</h4>'
        '<p style="color:#9BA3B7;font-size:0.9rem;">Explore chemical similarity networks colored by receptor activity.</p></div>',
        unsafe_allow_html=True)
with c4:
    st.markdown(
        '<div class="nav-card"><h4>🤖 AI Assistant</h4>'
        '<p style="color:#9BA3B7;font-size:0.9rem;">Ask natural language questions about any EDC in the database.</p></div>',
        unsafe_allow_html=True)

st.markdown("---")

# ─── Class distribution chart ─────────────────────────────────────────────────
col_l, col_r = st.columns([1, 1])
with col_l:
    st.markdown("### 🧫 Chemical Class Distribution")
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        df_cls = pd.read_sql_query(
            "SELECT chemical_class, COUNT(*) as count FROM chemicals GROUP BY chemical_class ORDER BY count DESC",
            conn
        )
        conn.close()
        import plotly.express as px
        fig = px.bar(df_cls, x="count", y="chemical_class", orientation="h",
                     color="count", color_continuous_scale="Teal",
                     template="plotly_dark", height=400)
        fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=20, b=0),
                          paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
                          coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Database not seeded yet. Run `python database/seed_database.py`.")

with col_r:
    st.markdown("### 🎯 Receptor Activity Breakdown")
    if DB_PATH.exists():
        conn = sqlite3.connect(DB_PATH)
        df_act = pd.read_sql_query(
            "SELECT receptor_target, activity_classification, COUNT(*) as n FROM bioactivity GROUP BY receptor_target, activity_classification",
            conn
        )
        conn.close()
        import plotly.express as px
        fig2 = px.bar(df_act, x="receptor_target", y="n", color="activity_classification",
                      barmode="group", template="plotly_dark", height=400,
                      color_discrete_map={"Active": "#00D4AA", "Inactive": "#FF6B6B"})
        fig2.update_layout(margin=dict(l=0, r=0, t=20, b=0),
                           paper_bgcolor="#0E1117", plot_bgcolor="#0E1117",
                           legend_title="Classification")
        st.plotly_chart(fig2, use_container_width=True)

# ─── Recent chemicals ─────────────────────────────────────────────────────────
st.markdown("### 🕐 Recently Added Chemicals")
df_recent = get_recent_chemicals()
if not df_recent.empty:
    st.dataframe(df_recent, use_container_width=True, hide_index=True)
else:
    st.info("No data loaded yet.")

st.markdown("---")
st.markdown(
    "<center style='color:#555;font-size:0.8rem;'>"
    "AIDED-EDC v1.0 · Dissertation Project · Built with Streamlit · Data: ChEMBL, CompTox, CERAPP"
    "</center>",
    unsafe_allow_html=True
)
