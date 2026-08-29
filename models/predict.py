"""
AIDED-EDC QSAR Prediction Module
Loads trained RF models and provides prediction + applicability domain checking.
"""
import pickle
import numpy as np
from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models" / "saved"

RECEPTORS = {
    "ER-alpha": "er_alpha_model",
    "AR":       "ar_model",
    "TR-alpha": "tr_alpha_model",
}

_cache = {}

def _load_model(name):
    if name not in _cache:
        path = MODELS_DIR / f"{name}.pkl"
        if not path.exists():
            return None
        with open(path, "rb") as f:
            _cache[name] = pickle.load(f)
    return _cache[name]


def smiles_to_fp(smiles: str, radius=2, nbits=2048):
    try:
        from rdkit import Chem
        from rdkit.Chem import AllChem, DataStructs
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
        arr = np.zeros((nbits,), dtype=np.uint8)
        DataStructs.ConvertToNumpyArray(fp, arr)
        return arr
    except Exception:
        return None


def check_applicability_domain(fp: np.ndarray, train_fps: np.ndarray, threshold=0.3) -> bool:
    """Returns True if the compound is within the applicability domain."""
    try:
        from rdkit.DataStructs import TanimotoSimilarity, CreateFromBitString
    except ImportError:
        return True  # assume in AD if RDKit unavailable

    sims = []
    for tf in train_fps:
        dot = np.dot(fp, tf)
        union = np.sum((fp + tf) > 0)
        sim = dot / union if union > 0 else 0
        sims.append(sim)
    return max(sims) >= threshold if sims else False


def predict_all(smiles: str) -> dict:
    """
    Returns prediction results for all 3 receptors.
    Result format: {receptor: {prob_active, classification, in_AD}}
    """
    fp = smiles_to_fp(smiles)
    if fp is None:
        return {"error": "Invalid SMILES string. Cannot parse molecule."}

    results = {}
    for receptor, model_name in RECEPTORS.items():
        data = _load_model(model_name)
        if data is None:
            results[receptor] = {"prob_active": None, "classification": "Model not trained", "in_AD": False}
            continue
        clf       = data["model"]
        train_fps = data["train_fps"]
        prob  = clf.predict_proba(fp.reshape(1, -1))[0][1]
        label = "Active" if prob >= 0.5 else "Inactive"
        in_ad = check_applicability_domain(fp, train_fps)
        results[receptor] = {"prob_active": round(float(prob), 4), "classification": label, "in_AD": in_ad}
    return results


def compute_descriptors(smiles: str) -> dict:
    """Compute Lipinski-style descriptors."""
    try:
        from rdkit import Chem
        from rdkit.Chem import Descriptors, rdMolDescriptors
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {}
        return {
            "Molecular Weight":   round(Descriptors.MolWt(mol), 2),
            "LogP":               round(Descriptors.MolLogP(mol), 2),
            "HBD":                rdMolDescriptors.CalcNumHBD(mol),
            "HBA":                rdMolDescriptors.CalcNumHBA(mol),
            "TPSA (Å²)":         round(Descriptors.TPSA(mol), 2),
            "Rotatable Bonds":    rdMolDescriptors.CalcNumRotatableBonds(mol),
            "Aromatic Rings":     rdMolDescriptors.CalcNumAromaticRings(mol),
            "Heavy Atoms":        mol.GetNumHeavyAtoms(),
        }
    except Exception:
        return {}


def mol_to_image(smiles: str, width: int = 380, height: int = 300):
    """Render 2D molecular structure as a PIL Image."""
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw, rdDepictor
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        rdDepictor.Compute2DCoords(mol)
        return Draw.MolToImage(mol, size=(width, height))
    except Exception:
        return None


def render_mol_svg(smiles: str, width=300, height=250) -> str:
    """Render a 2D molecular structure as SVG string."""
    try:
        from rdkit import Chem
        from rdkit.Chem import Draw, rdDepictor
        from rdkit.Chem.Draw import rdMolDraw2D
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return ""
        rdDepictor.Compute2DCoords(mol)
        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)
        drawer.drawOptions().addStereoAnnotation = True
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        return drawer.GetDrawingText()
    except Exception:
        return ""
