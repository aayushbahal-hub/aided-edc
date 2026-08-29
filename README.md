# 🧬 AIDED-EDC
### AI-Integrated Database for Endocrine Disrupting Chemicals

A comprehensive, interactive database for EDCs targeting **ER-alpha**, **Androgen Receptor (AR)**, and **Thyroid Receptor alpha (TR-alpha)** pathways. Features QSAR prediction, chemical similarity networks, and a natural-language AI query assistant.

---

## 🚀 Run Locally

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Seed the database (creates aided_edc.db with 55 compounds)
```bash
python database/seed_database.py
```

### 3. Train the QSAR models (ER-alpha, AR, TR-alpha)
```bash
python models/train_models.py
```

### 4. Launch the app
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌐 Deploy Online (Streamlit Community Cloud)

Anyone with the link can access the app — including your supervisor — from any internet connection.

### Step 1: Push to GitHub
```bash
cd aided_edc
git init
git add .
git commit -m "Initial AIDED-EDC release"
# Create a new public repo on github.com, then:
git remote add origin https://github.com/YOUR_USERNAME/aided-edc.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to **https://share.streamlit.io**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repo, branch `main`, main file `app.py`
5. Click **Deploy**

Your live URL will be: `https://YOUR_USERNAME-aided-edc-app-XXXX.streamlit.app`

> **Note:** The SQLite database (`aided_edc.db`) and model `.pkl` files need to be committed to the repo for Streamlit Cloud to use them. Run seed + train locally first, then commit the generated files.

### Commit the database and models before deploying:
```bash
git add database/aided_edc.db models/saved/*.pkl
git commit -m "Add seeded database and trained models"
git push
```

---

## 📁 Project Structure
```
aided_edc/
├── app.py                  # Home dashboard
├── requirements.txt
├── README.md
├── .streamlit/
│   └── config.toml         # Dark theme
├── database/
│   ├── schema.sql          # SQLite schema (4 tables)
│   ├── seed_database.py    # Seeds 55 EDCs + bioactivity
│   └── aided_edc.db        # Generated database (after seeding)
├── models/
│   ├── train_models.py     # QSAR model training
│   ├── predict.py          # Prediction + AD check
│   └── saved/              # Trained .pkl files
├── ai/
│   └── chatbot.py          # NL→SQL query assistant
└── pages/
    ├── 1_🔍_Search.py      # Chemical search & filtering
    ├── 2_🧪_Predict.py     # QSAR predictor with radar chart
    ├── 3_🕸️_Visualize.py   # Tanimoto similarity network
    └── 4_🤖_AI_Assistant.py # Chat interface
```

---

## 🗄️ Database Contents
| Table | Records | Description |
|-------|---------|-------------|
| chemicals | 55 | Compound info, SMILES, descriptors |
| bioactivity | 47 | IC50/Ki values for ER-α, AR, TR-α |
| toxicology_hazards | 12 | GHS codes, regulatory listings |
| literature_references | 8 | PubMed references |

---

## 🔬 Features
- **Chemical Search** — Filter by name, CAS, class, receptor, MW, LogP
- **QSAR Predictor** — Morgan FP + Random Forest for 3 receptors, Applicability Domain
- **Network Visualization** — Tanimoto similarity graph via PyVis
- **AI Assistant** — Keyword NL→SQL chatbot (no API key needed)

---

## 📖 Citation
If you use AIDED-EDC in your research, please cite:  
*[Your Name] (2026). AIDED-EDC: AI-Integrated Database for Endocrine Disrupting Chemicals. Dissertation.*

Data sources: ChEMBL, CompTox Dashboard, CERAPP, OECD QSAR Toolbox.
