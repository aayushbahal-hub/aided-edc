"""
AIDED-EDC — QSAR Predictor Page
"""
import streamlit as st
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(page_title="QSAR Predictor | AIDED-EDC", page_icon="🧪", layout="wide")

st.markdown("## 🧪 QSAR Activity Predictor")
st.markdown("Enter any SMILES string to predict ER-alpha, AR, and TR-alpha receptor binding activity.")
st.divider()

EXAMPLES = {
    "Bisphenol A":      "CC(C)(c1ccc(O)cc1)c1ccc(O)cc1",
    "Genistein":        "O=c1c(-c2ccc(O)cc2)coc2cc(O)cc(O)c12",
    "Atrazine":         "CCNc1nc(Cl)nc(NC(C)C)n1",
    "17β-Estradiol":    "OC1CC2=CC(=O)CC[C@@H]2[C@@H]2CC[C@H](O)[C@@]12C",
    "Flutamide":        "CC(C)C(=O)Nc1ccc([N+](=O)[O-])c(C(F)(F)F)c1",
    "PFOA":             "OC(=O)CCCCCCC(F)(F)F",
}

col_input, col_examples = st.columns([3, 1])
with col_input:
    smiles_input = st.text_area("Enter SMILES", height=80, placeholder="e.g. CC(C)(c1ccc(O)cc1)c1ccc(O)cc1")
with col_examples:
    st.markdown("**Quick Examples**")
    for name, smi in EXAMPLES.items():
        if st.button(name, key=f"ex_{name}"):
            smiles_input = smi

predict_btn = st.button("🔮 Predict Activity", type="primary", use_container_width=True)

if predict_btn and smiles_input.strip():
    with st.spinner("Running QSAR models..."):
        try:
            from models.predict import predict_all, compute_descriptors, render_mol_svg
        except ImportError:
            st.error("Prediction module not found. Ensure models/predict.py exists.")
            st.stop()

        results = predict_all(smiles_input.strip())
        descriptors = compute_descriptors(smiles_input.strip())
        svg = render_mol_svg(smiles_input.strip())

    if "error" in results:
        st.error(results["error"])
        st.stop()

    col_str, col_pred, col_desc = st.columns([1, 2, 1])

    with col_str:
        st.markdown("### 🔬 2D Structure")
        if svg:
            st.markdown(svg, unsafe_allow_html=True)
        else:
            st.info("Could not render structure.")

    with col_pred:
        st.markdown("### 🎯 Predicted Activity")
        import plotly.graph_objects as go

        receptors = list(results.keys())
        probs = [results[r].get("prob_active") or 0 for r in receptors]
        colors = ["#00D4AA" if p >= 0.5 else "#FF6B6B" for p in probs]

        fig = go.Figure(go.Bar(
            x=receptors, y=probs,
            marker_color=colors,
            text=[f"{p:.1%}" for p in probs],
            textposition="outside"
        ))
        fig.add_hline(y=0.5, line_dash="dash", line_color="#FFD700", annotation_text="Active threshold")
        fig.update_layout(
            yaxis_title="P(Active)",
            yaxis_range=[0, 1.1],
            template="plotly_dark",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            height=350,
            margin=dict(l=0, r=0, t=20, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

        # Radar chart
        radar_fig = go.Figure(go.Scatterpolar(
            r=probs + [probs[0]],
            theta=receptors + [receptors[0]],
            fill="toself",
            line_color="#00D4AA",
            fillcolor="rgba(0,212,170,0.2)"
        ))
        radar_fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            template="plotly_dark", paper_bgcolor="#0E1117",
            height=300, margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(radar_fig, use_container_width=True)

        # Classification badges
        for rec in receptors:
            r = results[rec]
            if r["classification"] in ("Model not trained", None):
                st.warning(f"**{rec}**: Model not trained yet.")
                continue
            col_a, col_b = st.columns(2)
            badge_color = "green" if r["classification"] == "Active" else "red"
            ad_icon = "✅ In AD" if r.get("in_AD") else "⚠️ Outside AD"
            col_a.markdown(f"**{rec}** → :{badge_color}[{r['classification']}] (p={r['prob_active']:.3f})")
            col_b.markdown(ad_icon)

    with col_desc:
        st.markdown("### 📋 Descriptors")
        if descriptors:
            import pandas as pd
            df_desc = pd.DataFrame(list(descriptors.items()), columns=["Property", "Value"])
            st.dataframe(df_desc, hide_index=True, use_container_width=True)

            # Lipinski Rule of 5 check
            st.markdown("### 🟢 Lipinski Ro5")
            violations = 0
            checks = [
                ("MW ≤ 500", descriptors.get("Molecular Weight", 999) <= 500),
                ("LogP ≤ 5", descriptors.get("LogP", 99) <= 5),
                ("HBD ≤ 5", descriptors.get("HBD", 99) <= 5),
                ("HBA ≤ 10", descriptors.get("HBA", 99) <= 10),
            ]
            for label, passed in checks:
                icon = "✅" if passed else "❌"
                if not passed:
                    violations += 1
                st.markdown(f"{icon} {label}")
            if violations == 0:
                st.success("Drug-like (0 violations)")
            else:
                st.warning(f"{violations} violation(s)")
        else:
            st.info("Install RDKit for descriptors.")

elif predict_btn:
    st.warning("Please enter a SMILES string.")
