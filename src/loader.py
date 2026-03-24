from __future__ import annotations

from pathlib import Path
import pandas as pd
import yaml

from src.normalizer import normalize_text, simplify_for_match, normalize_tarif_label

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REVISION_FILE = DATA_DIR / "revision_tarifs_2027.xlsx"
ALIASES_FILE = DATA_DIR / "aliases.csv"
EXCEPTIONS_FILE = DATA_DIR / "exceptions.csv"
CONFIG_FILE = DATA_DIR / "config.yaml"

SHEET_CONFIG = {
    "GENERAL": {
        "sheet_name": "GENERAL",
        "name_col": "TYPE D'ORGANISATEUR",
        "tarif_col": "TARIF ACTUEL",
        "comment_col": "COMMENTAIRES",
        "extra_cols": [],
        "priority": 4,
    },
    "FSMR": {
        "sheet_name": "FSMR",
        "name_col": "FILIERES DE SANTE MALADIES RARES",
        "tarif_col": "TARIF ACTUEL",
        "comment_col": "COMMENTAIRES",
        "extra_cols": ["COORDINATEUR"],
        "priority": 2,
    },
    "CRMR": {
        "sheet_name": "CRMR",
        "name_col": "CENTRES DE REFERENCE MALADIES RARES",
        "tarif_col": "TARIF ACTUEL",
        "comment_col": "COMMENTAIRES",
        "extra_cols": ["COORDINATEUR"],
        "priority": 1,
    },
    "SOCIETES SAVANTES": {
        "sheet_name": "SOCIETES SAVANTES",
        "name_col": "SOCIETES SAVANTES",
        "tarif_col": "TARIF ACTUEL",
        "comment_col": "COMMENTAIRES",
        "extra_cols": ["DOMAINE"],
        "priority": 3,
    },
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _read_sheet(sheet_name: str) -> pd.DataFrame:
    return pd.read_excel(REVISION_FILE, sheet_name=sheet_name, header=4)



def load_references() -> pd.DataFrame:
    rows = []
    for referentiel, cfg in SHEET_CONFIG.items():
        df = _read_sheet(cfg["sheet_name"])
        if cfg["name_col"] not in df.columns:
            continue

        df = df.rename(columns=lambda c: str(c).strip() if c is not None else c)
        df = df[df[cfg["name_col"]].notna()].copy()

        for _, row in df.iterrows():
            canonical_name = str(row.get(cfg["name_col"], "")).strip()
            tarif = normalize_tarif_label(row.get(cfg["tarif_col"], ""))
            commentaire = str(row.get(cfg["comment_col"], "") or "").strip()

            if not canonical_name:
                continue

            extras = []
            for col in cfg["extra_cols"]:
                value = row.get(col)
                if pd.notna(value) and str(value).strip():
                    extras.append(f"{col}: {str(value).strip()}")

            rows.append(
                {
                    "canonical_name": canonical_name,
                    "canonical_norm": normalize_text(canonical_name),
                    "canonical_simple": simplify_for_match(canonical_name),
                    "referentiel": referentiel,
                    "tarif": tarif,
                    "commentaire": commentaire,
                    "details": " | ".join(extras),
                    "priority": cfg["priority"],
                }
            )

    ref_df = pd.DataFrame(rows)
    if not ref_df.empty:
        ref_df = ref_df.sort_values(["priority", "canonical_name"]).reset_index(drop=True)
    return ref_df



def load_aliases() -> pd.DataFrame:
    if ALIASES_FILE.exists():
        df = pd.read_csv(ALIASES_FILE)
    else:
        df = pd.DataFrame(columns=["alias", "canonical_name", "referentiel", "notes"])

    if df.empty:
        return pd.DataFrame(columns=["alias", "canonical_name", "referentiel", "notes", "alias_norm", "alias_simple"])

    for col in ["alias", "canonical_name", "referentiel", "notes"]:
        if col not in df.columns:
            df[col] = ""

    df["alias"] = df["alias"].fillna("").astype(str)
    df["canonical_name"] = df["canonical_name"].fillna("").astype(str)
    df["referentiel"] = df["referentiel"].fillna("").astype(str)
    df["notes"] = df["notes"].fillna("").astype(str)
    df["alias_norm"] = df["alias"].map(normalize_text)
    df["alias_simple"] = df["alias"].map(simplify_for_match)
    return df



def load_exceptions() -> pd.DataFrame:
    if EXCEPTIONS_FILE.exists():
        df = pd.read_csv(EXCEPTIONS_FILE)
    else:
        df = pd.DataFrame(columns=["canonical_name", "exception_text", "type_exception", "active"])

    for col in ["canonical_name", "exception_text", "type_exception", "active"]:
        if col not in df.columns:
            df[col] = ""

    if not df.empty:
        df["canonical_name"] = df["canonical_name"].fillna("").astype(str)
        df["exception_text"] = df["exception_text"].fillna("").astype(str)
        df["type_exception"] = df["type_exception"].fillna("").astype(str)
        df["active"] = df["active"].fillna(True)
    return df
