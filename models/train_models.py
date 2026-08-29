"""
AIDED-EDC QSAR Model Trainer
Trains Random Forest classifiers for ER-alpha, AR, and TR-alpha receptor activity.
Run: python models/train_models.py
"""
import sqlite3
import pickle
import numpy as np
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

BASE_DIR   = Path(__file__).resolve().parent.parent
DB_PATH    = BASE_DIR / "database" / "aided_edc.db"
MODELS_DIR = BASE_DIR / "models" / "saved"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, DataStructs
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import cross_val_score
    from sklearn.metrics import classification_report
    RDKIT_OK = True
except ImportError:
    print("[!] RDKit or scikit-learn not installed. Run: pip install rdkit scikit-learn")
    RDKIT_OK = False


def smiles_to_fp(smiles: str, radius=2, nbits=2048):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
    arr = np.zeros((nbits,), dtype=np.uint8)
    DataStructs.ConvertToNumpyArray(fp, arr)
    return arr


def train_receptor(cursor, receptor_target: str, model_name: str):
    cursor.execute(
        """SELECT c.smiles, b.activity_classification
           FROM bioactivity b
           JOIN chemicals c ON b.compound_id = c.compound_id
           WHERE b.receptor_target = ?""",
        (receptor_target,)
    )
    rows = cursor.fetchall()
    if not rows:
        print(f"  [!] No data for {receptor_target}")
        return None

    X, y = [], []
    for smiles, label in rows:
        fp = smiles_to_fp(smiles)
        if fp is not None:
            X.append(fp)
            y.append(1 if label == "Active" else 0)

    if len(X) < 4:
        print(f"  [!] Too few samples for {receptor_target} ({len(X)}). Skipping CV.")
        clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        clf.fit(np.array(X), np.array(y))
    else:
        clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
        cv_scores = cross_val_score(clf, np.array(X), np.array(y), cv=min(3, len(X)), scoring="balanced_accuracy")
        print(f"  CV Balanced Accuracy ({receptor_target}): {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
        clf.fit(np.array(X), np.array(y))

    # Save model + training FPs for applicability domain
    save_path = MODELS_DIR / f"{model_name}.pkl"
    with open(save_path, "wb") as f:
        pickle.dump({"model": clf, "train_fps": np.array(X), "classes": ["Inactive", "Active"]}, f)
    print(f"  [✓] Saved: {save_path}")
    return clf


def main():
    if not RDKIT_OK:
        return
    if not DB_PATH.exists():
        print(f"[!] Database not found at {DB_PATH}. Run seed_database.py first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    print("[+] Training ER-alpha model...")
    train_receptor(cur, "ERalpha",  "er_alpha_model")
    print("[+] Training AR model...")
    train_receptor(cur, "AR",       "ar_model")
    print("[+] Training TR-alpha model...")
    train_receptor(cur, "TRalpha",  "tr_alpha_model")
    conn.close()
    print("\n[✓] All models trained and saved.")


if __name__ == "__main__":
    main()
