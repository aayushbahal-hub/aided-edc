PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS chemicals (
    compound_id      TEXT PRIMARY KEY,
    chemical_name    TEXT NOT NULL,
    cas_number       TEXT UNIQUE,
    smiles           TEXT NOT NULL,
    inchi_key        TEXT,
    pubchem_cid      INTEGER,
    chembl_id        TEXT,
    molecular_weight REAL,
    logp             REAL,
    tpsa             REAL,
    hbd              INTEGER,
    hba              INTEGER,
    rotatable_bonds  INTEGER,
    chemical_class   TEXT,
    common_uses      TEXT,
    date_added       TEXT DEFAULT (date('now'))
);

CREATE TABLE IF NOT EXISTS bioactivity (
    activity_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    compound_id             TEXT NOT NULL REFERENCES chemicals(compound_id),
    receptor_target         TEXT NOT NULL,
    receptor_pathway        TEXT NOT NULL,
    assay_type              TEXT,
    measurement_type        TEXT,
    value_original          REAL,
    unit_original           TEXT,
    value_normalized_nm     REAL,
    activity_classification TEXT NOT NULL,
    source_database         TEXT,
    pubmed_reference        TEXT
);

CREATE TABLE IF NOT EXISTS toxicology_hazards (
    hazard_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    compound_id         TEXT NOT NULL REFERENCES chemicals(compound_id),
    ghs_codes           TEXT,
    target_organs       TEXT,
    regulatory_listings TEXT,
    carcinogenicity     TEXT,
    reproductive_tox    TEXT
);

CREATE TABLE IF NOT EXISTS literature_references (
    reference_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    compound_id   TEXT NOT NULL REFERENCES chemicals(compound_id),
    pubmed_id     TEXT,
    doi           TEXT,
    citation_text TEXT,
    abstract_text TEXT,
    year          INTEGER
);

CREATE INDEX IF NOT EXISTS idx_chemicals_name ON chemicals(chemical_name);
CREATE INDEX IF NOT EXISTS idx_bioactivity_compound ON bioactivity(compound_id);
CREATE INDEX IF NOT EXISTS idx_bioactivity_receptor ON bioactivity(receptor_target);
CREATE INDEX IF NOT EXISTS idx_bioactivity_class ON bioactivity(activity_classification);
