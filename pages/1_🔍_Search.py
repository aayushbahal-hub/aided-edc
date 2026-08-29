"""
AIDED-EDC — Chemical Search Page
"""
import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "database" / "aided_edc.db"

st.set_page_config(page_title="Search | AIDED-EDC", page_icon="🔍", layout="wide")

st.markdown("## 🔍 Chemical Search")
st.markdown("Search the database by name, CAS number, chemical class, or receptor activity.")
st.divider()

if not DB_PATH.exists():
    st.error("Database not found. Please run `python database/seed_database.py` first.")
    st.stop()


@st.cache_data
def load_all():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT c.compound_id, c.chemical_name, c.cas_number, c.smiles,
               c.molecular_weight, c.logp, c.tpsa, c.hbd, c.hba,
               c.chemical_class, c.common_uses,
               GROUP_CONCAT(DISTINCT b.receptor_target || ':' || b.activity_classification) AS receptor_activity
        FROM chemicals c
        LEFT JOIN bioactivity b ON c.compound_id = b.compound_id
        GROUP BY c.compound_id
        ORDER BY c.chemical_name
    """, conn)
    conn.close()
    return df


df = load_all()

# ─── Sidebar filters ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔧 Filters")
    search_term  = st.text_input("Search name / CAS", placeholder="e.g. bisphenol, 80-05-7")
    class_filter = st.multiselect("Chemical Class",
                                  sorted(df["chemical_class"].dropna().unique()))
    mw_min, mw_max = float(df["molecular_weight"].min()), float(df["molecular_weight"].max())
    mw_range = st.slider("Molecular Weight (Da)", mw_min, mw_max, (mw_min, mw_max), step=5.0)
    logp_min, logp_max = float(df["logp"].min()), float(df["logp"].max())
    logp_range = st.slider("LogP", logp_min, logp_max, (logp_min, logp_max), step=0.1)
    receptor_filter = st.selectbox("Receptor Activity Contains", ["All", "ERalpha:Active", "AR:Active", "TRalpha:Active", "ERalpha:Inactive"])
    st.divider()
    st.markdown("**Total:** " + str(len(df)) + " chemicals")

# ─── Apply filters ────────────────────────────────────────────────────────────
filtered = df.copy()
if search_term:
    mask = (filtered["chemical_name"].str.contains(search_term, case=False, na=False) |
            filtered["cas_number"].str.contains(search_term, case=False, na=False))
    filtered = filtered[mask]
if class_filter:
    filtered = filtered[filtered["chemical_class"].isin(class_filter)]
filtered = filtered[
    (filtered["molecular_weight"] >= mw_range[0]) &
    (filtered["molecular_weight"] <= mw_range[1]) &
    (filtered["logp"]             >= logp_range[0]) &
    (filtered["logp"]             <= logp_range[1])
]
if receptor_filter != "All":
    filtered = filtered[filtered["receptor_activity"].str.contains(receptor_filter, na=False)]

st.markdown(f"**Showing {len(filtered)} of {len(df)} chemicals**")

# ─── Results table ────────────────────────────────────────────────────────────
display_cols = ["chemical_name", "cas_number", "chemical_class", "molecular_weight", "logp", "tpsa", "receptor_activity"]
st.dataframe(
    filtered[display_cols].rename(columns={
        "chemical_name": "Name", "cas_number": "CAS",
        "chemical_class": "Class", "molecular_weight": "MW (Da)",
        "logp": "LogP", "tpsa": "TPSA (Å²)", "receptor_activity": "Receptor Activity"
    }),
    use_container_width=True, hide_index=True, height=400
)

# ─── Download ─────────────────────────────────────────────────────────────────
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Download Results as CSV", csv, "aided_edc_search_results.csv", "text/csv")

# ─── Detail view ──────────────────────────────────────────────────────────────
st.divider()
st.markdown("### 🔬 Compound Detail View")
if not filtered.empty:
    selected = st.selectbox("Select a compound for details", filtered["chemical_name"].tolist())
    row = filtered[filtered["chemical_name"] == selected].iloc[0]
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"**Name:** {row.chemical_name}")
        st.markdown(f"**CAS:** {row.cas_number}")
        st.markdown(f"**Class:** {row.chemical_class}")
        st.markdown(f"**Uses:** {row.common_uses}")
        st.markdown(f"**MW:** {row.molecular_weight} Da")
        st.markdown(f"**LogP:** {row.logp}")
        st.markdown(f"**TPSA:** {row.tpsa} Å²")
        st.markdown(f"**HBD/HBA:** {row.hbd} / {row.hba}")
    with col2:
        st.markdown("**SMILES:**")
        st.code(row.smiles, language="text")
        # 2D structure
        try:
            import sys
            sys.path.insert(0, str(BASE_DIR))
            from models.predict import render_mol_svg
            svg = render_mol_svg(row.smiles)
            if svg:
                st.markdown(svg, unsafe_allow_html=True)
        except Exception:
            st.info("Install RDKit to view 2D structures.")

        # Bioactivity detail
        conn = sqlite3.connect(DB_PATH)
        df_bio = pd.read_sql_query(
            "SELECT receptor_target, activity_classification, measurement_type, value_normalized_nm, assay_type, source_database FROM bioactivity WHERE compound_id=?",
            conn, params=(row.compound_id,)
        )
        conn.close()
        if not df_bio.empty:
            st.markdown("**Bioactivity Data:**")
            st.dataframe(df_bio, hide_index=True, use_container_width=True)
