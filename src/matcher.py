from __future__ import annotations

from rapidfuzz import fuzz, process
import pandas as pd

from src.normalizer import normalize_text, simplify_for_match


PRIORITY_ORDER = ["CRMR", "FSMR", "SOCIETES SAVANTES", "GENERAL"]



def _find_alias_match(query_norm: str, query_simple: str, aliases_df: pd.DataFrame):
    if aliases_df.empty:
        return None

    exact = aliases_df[(aliases_df["alias_norm"] == query_norm) | (aliases_df["alias_simple"] == query_simple)]
    if not exact.empty:
        return exact.iloc[0].to_dict()
    return None



def _fuzzy_candidates(query: str, choices: list[str], limit: int = 5):
    if not query or not choices:
        return []
    return process.extract(query, choices, scorer=fuzz.WRatio, limit=limit)



def find_best_match(org_name: str, alt_name: str, ref_df: pd.DataFrame, aliases_df: pd.DataFrame, cfg: dict) -> dict:
    queries = [q for q in [org_name, alt_name] if q and str(q).strip()]
    if not queries:
        return {"status": "empty"}

    fuzzy_threshold_low = cfg.get("fuzzy_threshold_low", 80)
    fuzzy_threshold_medium = cfg.get("fuzzy_threshold_medium", 90)

    for raw_query in queries:
        query_norm = normalize_text(raw_query)
        query_simple = simplify_for_match(raw_query)

        # 1) Exact canonical match by priority
        for referentiel in PRIORITY_ORDER:
            subset = ref_df[ref_df["referentiel"] == referentiel]
            exact = subset[(subset["canonical_norm"] == query_norm) | (subset["canonical_simple"] == query_simple)]
            if not exact.empty:
                row = exact.iloc[0].to_dict()
                return {
                    "status": "matched",
                    "match_type": "exact_canonical",
                    "score": 100,
                    "confidence": "Élevé",
                    "matched_on": raw_query,
                    "row": row,
                    "alternatives": [],
                }

        # 2) Exact alias match by priority
        alias_match = _find_alias_match(query_norm, query_simple, aliases_df)
        if alias_match:
            subset = ref_df[
                (ref_df["canonical_name"] == alias_match["canonical_name"])
                & (ref_df["referentiel"] == alias_match["referentiel"])
            ]
            if not subset.empty:
                row = subset.iloc[0].to_dict()
                return {
                    "status": "matched",
                    "match_type": "exact_alias",
                    "score": 99,
                    "confidence": "Élevé",
                    "matched_on": raw_query,
                    "alias_used": alias_match["alias"],
                    "row": row,
                    "alternatives": [],
                }

        # 3) Fuzzy canonical/alias match by priority
        all_alternatives = []
        for referentiel in PRIORITY_ORDER:
            subset = ref_df[ref_df["referentiel"] == referentiel].copy()
            choices = subset["canonical_simple"].dropna().tolist()
            fuzzy = _fuzzy_candidates(query_simple, choices, limit=5)
            if fuzzy:
                best_choice, best_score, best_index = fuzzy[0]
                if best_score >= fuzzy_threshold_low:
                    matched = subset[subset["canonical_simple"] == best_choice].iloc[0].to_dict()
                    confidence = "Moyen" if best_score >= fuzzy_threshold_medium else "Faible"
                    for choice, score, _ in fuzzy[:3]:
                        alt_row = subset[subset["canonical_simple"] == choice].iloc[0]
                        all_alternatives.append(
                            {
                                "canonical_name": alt_row["canonical_name"],
                                "referentiel": alt_row["referentiel"],
                                "score": score,
                            }
                        )
                    return {
                        "status": "matched",
                        "match_type": "fuzzy_canonical",
                        "score": int(best_score),
                        "confidence": confidence,
                        "matched_on": raw_query,
                        "row": matched,
                        "alternatives": all_alternatives,
                    }

            # fuzzy alias in same referentiel
            alias_subset = aliases_df[aliases_df["referentiel"] == referentiel].copy()
            alias_choices = alias_subset["alias_simple"].dropna().tolist() if not alias_subset.empty else []
            fuzzy_alias = _fuzzy_candidates(query_simple, alias_choices, limit=5)
            if fuzzy_alias:
                best_choice, best_score, _ = fuzzy_alias[0]
                if best_score >= fuzzy_threshold_low:
                    alias_row = alias_subset[alias_subset["alias_simple"] == best_choice].iloc[0]
                    subset2 = ref_df[
                        (ref_df["canonical_name"] == alias_row["canonical_name"])
                        & (ref_df["referentiel"] == alias_row["referentiel"])
                    ]
                    if not subset2.empty:
                        matched = subset2.iloc[0].to_dict()
                        confidence = "Moyen" if best_score >= fuzzy_threshold_medium else "Faible"
                        return {
                            "status": "matched",
                            "match_type": "fuzzy_alias",
                            "score": int(best_score),
                            "confidence": confidence,
                            "matched_on": raw_query,
                            "alias_used": alias_row["alias"],
                            "row": matched,
                            "alternatives": [],
                        }

    return {"status": "not_found"}
