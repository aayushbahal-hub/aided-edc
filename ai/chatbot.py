"""
AIDED-EDC AI Query Assistant
A keyword-based NL→SQL chatbot. No API key required.
"""
import sqlite3
import re
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "database" / "aided_edc.db"


class EDCQueryAssistant:
    def __init__(self):
        self.db_path = DB_PATH

    def _run_query(self, sql: str, params=()):
        try:
            conn = sqlite3.connect(self.db_path)
            df   = pd.read_sql_query(sql, conn, params=params)
            conn.close()
            return df, sql
        except Exception as e:
            return pd.DataFrame(), f"SQL Error: {e}"

    def parse_and_respond(self, user_input: str):
        text = user_input.lower().strip()

        # ── Stats / overview ────────────────────────────────────────────────
        if any(w in text for w in ["how many", "total", "count", "statistics", "overview", "summary"]):
            sql = """
                SELECT
                  (SELECT COUNT(*) FROM chemicals)                          AS total_chemicals,
                  (SELECT COUNT(*) FROM bioactivity)                        AS total_activity_records,
                  (SELECT COUNT(*) FROM bioactivity WHERE receptor_target='ERalpha' AND activity_classification='Active') AS er_actives,
                  (SELECT COUNT(*) FROM bioactivity WHERE receptor_target='AR'     AND activity_classification='Active') AS ar_actives,
                  (SELECT COUNT(*) FROM bioactivity WHERE receptor_target='TRalpha'AND activity_classification='Active') AS tr_actives
            """
            df, used_sql = self._run_query(sql)
            msg = "📊 **Database Overview**\n" + df.to_string(index=False)
            return msg, df, used_sql

        # ── List all chemicals ──────────────────────────────────────────────
        if any(w in text for w in ["list all", "show all", "all chemicals", "all compounds"]):
            sql = "SELECT compound_id, chemical_name, cas_number, chemical_class, molecular_weight FROM chemicals ORDER BY chemical_name"
            df, used_sql = self._run_query(sql)
            msg = f"🧪 Found **{len(df)}** chemicals in the database."
            return msg, df, used_sql

        # ── Chemical class filter ───────────────────────────────────────────
        for cls in ["bisphenol","paraben","phthalate","isoflavone","steroid","pcb","pfas",
                    "organochlorine","organophosphate","phenol","alkylphenol","fungicide",
                    "herbicide","organotin","mycotoxin","lignan"]:
            if cls in text:
                sql = "SELECT compound_id, chemical_name, cas_number, molecular_weight, logp FROM chemicals WHERE LOWER(chemical_class) LIKE ?"
                df, used_sql = self._run_query(sql, (f"%{cls}%",))
                msg = f"🔎 Found **{len(df)}** {cls.title()} compounds."
                return msg, df, used_sql

        # ── Receptor + activity ─────────────────────────────────────────────
        receptor = None
        if any(w in text for w in ["er", "estrogen", "eralpha", "er-alpha"]):
            receptor = "ERalpha"
        elif any(w in text for w in [" ar ", "androgen"]):
            receptor = "AR"
        elif any(w in text for w in ["tr", "thyroid", "tralpha", "tr-alpha"]):
            receptor = "TRalpha"

        if receptor:
            activity = None
            if "active" in text and "inactive" not in text:
                activity = "Active"
            elif "inactive" in text:
                activity = "Inactive"

            if activity:
                sql = """SELECT c.chemical_name, b.receptor_target, b.activity_classification,
                                b.value_normalized_nm, b.measurement_type, b.source_database
                         FROM bioactivity b JOIN chemicals c ON b.compound_id=c.compound_id
                         WHERE b.receptor_target=? AND b.activity_classification=?
                         ORDER BY b.value_normalized_nm"""
                df, used_sql = self._run_query(sql, (receptor, activity))
                msg = f"🎯 **{receptor} {activity}** compounds: {len(df)} found."
            else:
                sql = """SELECT c.chemical_name, b.receptor_target, b.activity_classification,
                                b.value_normalized_nm, b.measurement_type
                         FROM bioactivity b JOIN chemicals c ON b.compound_id=c.compound_id
                         WHERE b.receptor_target=? ORDER BY b.value_normalized_nm"""
                df, used_sql = self._run_query(sql, (receptor,))
                msg = f"🎯 **{receptor}** data: {len(df)} records."
            return msg, df, used_sql

        # ── Potency / most potent ───────────────────────────────────────────
        if any(w in text for w in ["most potent","potent","strongest","highest activity","lowest ic50","lowest ki"]):
            sql = """SELECT c.chemical_name, b.receptor_target, b.measurement_type,
                            b.value_normalized_nm AS value_nM, b.activity_classification
                     FROM bioactivity b JOIN chemicals c ON b.compound_id=c.compound_id
                     WHERE b.activity_classification='Active'
                     ORDER BY b.value_normalized_nm ASC LIMIT 15"""
            df, used_sql = self._run_query(sql)
            msg = "⚡ **Top 15 Most Potent EDCs** (lowest IC50/Ki values)"
            return msg, df, used_sql

        # ── Regulatory / banned ─────────────────────────────────────────────
        if any(w in text for w in ["regulatory","svhc","annex","banned","restricted","carcinogen","reproductive"]):
            sql = """SELECT c.chemical_name, t.ghs_codes, t.regulatory_listings,
                            t.carcinogenicity, t.reproductive_tox, t.target_organs
                     FROM toxicology_hazards t JOIN chemicals c ON t.compound_id=c.compound_id"""
            df, used_sql = self._run_query(sql)
            msg = f"⚠️ **Regulatory & Hazard Data** for {len(df)} compounds."
            return msg, df, used_sql

        # ── Individual chemical lookup ──────────────────────────────────────
        # Try to match a compound name from the query
        words = re.findall(r"[a-z0-9]+", text)
        if len(words) >= 1:
            for word in words:
                if len(word) > 4:
                    sql = """SELECT c.*, b.receptor_target, b.activity_classification, b.value_normalized_nm
                             FROM chemicals c
                             LEFT JOIN bioactivity b ON c.compound_id=b.compound_id
                             WHERE LOWER(c.chemical_name) LIKE ?
                             LIMIT 20"""
                    df, used_sql = self._run_query(sql, (f"%{word}%",))
                    if not df.empty:
                        msg = f"🔬 Found **{len(df)}** records matching '{word}'."
                        return msg, df, used_sql

        # ── Default fallback ────────────────────────────────────────────────
        sql = "SELECT compound_id, chemical_name, chemical_class, molecular_weight FROM chemicals ORDER BY RANDOM() LIMIT 10"
        df, used_sql = self._run_query(sql)
        msg = ("🤖 I didn't fully understand your query. Here are 10 random chemicals.\n\n"
               "**Try asking:**\n"
               "- *How many chemicals are in the database?*\n"
               "- *Show all bisphenol compounds*\n"
               "- *Which chemicals are active on ERalpha?*\n"
               "- *What are the most potent AR antagonists?*\n"
               "- *Show regulatory data*")
        return msg, df, used_sql
