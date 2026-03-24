from __future__ import annotations

import pandas as pd



def build_exception_list(row: dict, exceptions_df: pd.DataFrame) -> list[str]:
    results = []
    commentaire = (row.get("commentaire") or "").strip()
    if commentaire:
        results.append(f"Commentaire du référentiel : {commentaire}")

    if exceptions_df is not None and not exceptions_df.empty:
        canon = row.get("canonical_name", "")
        matches = exceptions_df[
            exceptions_df["canonical_name"].astype(str).str.casefold() == str(canon).casefold()
        ]
        for _, ex in matches.iterrows():
            active = ex.get("active", True)
            if str(active).lower() in {"false", "0", "non"}:
                continue
            txt = str(ex.get("exception_text", "")).strip()
            if txt:
                results.append(txt)
    return results



def build_explanation(match: dict, exceptions_df: pd.DataFrame) -> dict:
    if match.get("status") != "matched":
        return {
            "tarif": "Aucun résultat certain",
            "confidence": "Faible",
            "justification": "Aucune correspondance exploitable n’a été trouvée dans les référentiels officiels.",
            "rule": "Absence de match dans CRMR, FSMR, Sociétés savantes et GENERAL.",
            "exceptions": [],
            "why": "Le moteur n’a trouvé ni correspondance exacte, ni alias fiable, ni rapprochement suffisamment robuste.",
        }

    row = match["row"]
    match_type = match.get("match_type")
    referentiel = row.get("referentiel")
    canonical_name = row.get("canonical_name")
    tarif = row.get("tarif") or "Non renseigné"
    confidence = match.get("confidence", "Faible")
    score = match.get("score", 0)

    if match_type == "exact_canonical":
        justification = f"Correspondance exacte trouvée dans le référentiel {referentiel} pour « {canonical_name} »."
    elif match_type == "exact_alias":
        justification = f"Alias reconnu (« {match.get('alias_used', '')} ») renvoyant vers « {canonical_name} » dans le référentiel {referentiel}."
    elif match_type == "fuzzy_alias":
        justification = f"Correspondance approchée sur un alias (« {match.get('alias_used', '')} ») menant à « {canonical_name} » dans le référentiel {referentiel}."
    else:
        justification = f"Correspondance approchée trouvée dans le référentiel {referentiel} pour « {canonical_name} » (score {score}/100)."

    rule = f"Priorité appliquée : CRMR → FSMR → Sociétés savantes → GENERAL. Match retenu dans {referentiel}."
    why_lines = [
        f"Nom retenu : {canonical_name}",
        f"Référentiel : {referentiel}",
        f"Type de match : {match_type}",
        f"Score : {score}/100",
    ]
    details = row.get("details")
    if details:
        why_lines.append(f"Détails : {details}")

    exceptions = build_exception_list(row, exceptions_df)

    if match.get("alternatives"):
        alts = ", ".join(
            [f"{a['canonical_name']} ({a['referentiel']}, {a['score']}/100)" for a in match["alternatives"][:3]]
        )
        why_lines.append(f"Correspondances proches : {alts}")

    return {
        "tarif": tarif,
        "confidence": confidence,
        "justification": justification,
        "rule": rule,
        "exceptions": exceptions,
        "why": "\n".join(why_lines),
    }
