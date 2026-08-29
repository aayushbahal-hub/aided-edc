"""
AIDED-EDC — Chemical Similarity Network Visualization
"""
import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import os
import sys
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_PATH = str(BASE_DIR)
if ROOT_PATH not in sys.path:
    sys.path.insert(0, ROOT_PATH)
DB_PATH = BASE_DIR / "database" / "aided_edc.db"

st.set_page_config(page_title="Network | AIDED-EDC", page_icon="🕸️", layout="wide")
st.markdown("## 🕸️ Chemical Similarity Network")
st.markdown("Explore structural similarity relationships between EDCs. Node color = primary receptor class.")
st.divider()

if not DB_PATH.exists():
    st.error("Database not found. Run `python database/seed_database.py` first.")
    st.stop()

with st.sidebar:
    st.markdown("### ⚙️ Network Settings")
    sim_threshold = st.slider("Min Tanimoto Similarity", 0.1, 0.9, 0.3, 0.05)
    max_nodes = st.slider("Max Compounds", 10, 55, 30)
    filter_class = st.selectbox("Filter by Class", ["All"] + [
        "Bisphenol", "Paraben", "Phthalate", "Isoflavone", "Steroid",
        "Organochlorine", "Organophosphate", "PFAS", "PCB"
    ])
    st.divider()
    st.markdown("""
    **Node Colors:**
    - 🟢 ER-alpha Active
    - 🔵 AR Active
    - 🟠 TR-alpha Active
    - ⚪ Unknown/Inactive
    """)

@st.cache_data
def load_smiles(max_n, cls_filter):
    conn = sqlite3.connect(DB_PATH)
    where = "" if cls_filter == "All" else f"WHERE chemical_class='{cls_filter}'"
    df = pd.read_sql_query(
        f"SELECT compound_id, chemical_name, smiles, chemical_class FROM chemicals {where} LIMIT {max_n}",
        conn
    )
    # Get dominant receptor activity
    df_act = pd.read_sql_query("""
        SELECT compound_id, receptor_target, activity_classification
        FROM bioactivity WHERE activity_classification='Active'
    """, conn)
    conn.close()
    act_map = {}
    for _, r in df_act.iterrows():
        if r.compound_id not in act_map:
            act_map[r.compound_id] = r.receptor_target
    df["receptor"] = df["compound_id"].map(act_map).fillna("Unknown")
    return df

color_map = {
    "ERalpha": "#00D4AA",
    "AR":      "#4A9EE0",
    "TRalpha": "#FF9A3C",
    "Unknown": "#6B7280",
}

with st.spinner("Computing fingerprints and building network..."):
    df = load_smiles(max_nodes, filter_class)

    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem, DataStructs
        fps = []
        valid_rows = []
        for _, row in df.iterrows():
            mol = Chem.MolFromSmiles(row.smiles)
            if mol:
                fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, 2048)
                fps.append(fp)
                valid_rows.append(row)

        df_valid = pd.DataFrame(valid_rows)
        n = len(fps)

        try:
            from pyvis.network import Network
            import networkx as nx

            G = nx.Graph()
            for i, row in df_valid.iterrows():
                G.add_node(row.chemical_name,
                           color=color_map.get(row.receptor, "#6B7280"),
                           title=f"{row.chemical_name}\nClass: {row.chemical_class}\nReceptor: {row.receptor}",
                           size=20)

            names = df_valid["chemical_name"].tolist()
            for i in range(n):
                for j in range(i+1, n):
                    sim = DataStructs.TanimotoSimilarity(fps[i], fps[j])
                    if sim >= sim_threshold:
                        G.add_edge(names[i], names[j], weight=round(float(sim), 3),
                                   title=f"Tanimoto: {sim:.3f}")

            net = Network(height="600px", width="100%", bgcolor="#0E1117",
                          font_color="white", notebook=False)
            net.from_nx(G)
            net.set_options("""
            {
              "physics": {
                "enabled": true,
                "stabilization": {"iterations": 100}
              },
              "edges": {
                "color": {"inherit": false, "color": "#444"},
                "smooth": {"type": "continuous"}
              }
            }
            """)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html", dir=BASE_DIR) as f:
                net.save_graph(f.name)
                html_path = f.name

            with open(html_path, "r") as f:
                html_content = f.read()

            st.components.v1.html(html_content, height=620, scrolling=False)

            st.markdown(f"**{G.number_of_nodes()} nodes · {G.number_of_edges()} edges** "
                        f"(similarity ≥ {sim_threshold})")

            Path(html_path).unlink(missing_ok=True)

        except ImportError:
            st.warning("PyVis not installed. Showing similarity matrix instead.")
            # Fallback: heatmap
            import plotly.express as px
            sim_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    sim_matrix[i][j] = DataStructs.TanimotoSimilarity(fps[i], fps[j])
            names = df_valid["chemical_name"].tolist()
            fig = px.imshow(sim_matrix, x=names, y=names,
                            color_continuous_scale="Teal", template="plotly_dark",
                            title="Tanimoto Similarity Heatmap", height=700)
            st.plotly_chart(fig, use_container_width=True)

    except ImportError:
        st.error("RDKit is required for network visualization. Install with: pip install rdkit")
