from __future__ import annotations

import streamlit as st

from src.loader import load_references, load_aliases, load_exceptions, load_config
from src.matcher import find_best_match
from src.explain import build_explanation

st.set_page_config(
    page_title="Attribution des tarifs",
    page_icon="🏷️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {font-size: 2rem; font-weight: 700; margin-bottom: 0.2rem;}
    .sub-title {color: #5f6368; margin-bottom: 1.2rem;}
    .result-card {
        border: 1px solid #ececec;
        border-radius: 18px;
        padding: 1.2rem 1.2rem 0.8rem 1.2rem;
        background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
        box-shadow: 0 6px 20px rgba(0,0,0,0.04);
    }
    .pill {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        font-size: 0.9rem;
        font-weight: 600;
        margin-right: 0.5rem;
        border: 1px solid #e7e7e7;
        background: #f7f7f7;
    }
    .tarif-value {
        font-size: 2rem;
        font-weight: 800;
        margin: 0.4rem 0 0.8rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

cfg = load_config()
ref_df = load_references()
aliases_df = load_aliases()
exceptions_df = load_exceptions()

st.markdown(f"<div class='main-title'>{cfg.get('app_title', 'Attribution des tarifs — Institut Imagine')}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='sub-title'>{cfg.get('app_subtitle', 'Outil officiel de recommandation du type de tarif')}</div>", unsafe_allow_html=True)

with st.expander("Sources utilisées", expanded=False):
    st.write("- Révision des attributions des tarifs 2027")
    st.write("- Alias manuels")
    st.write("- Exceptions signalées")

left, right = st.columns([1.1, 1.2], gap="large")

with left:
    st.subheader("Recherche")
    org_name = st.text_input("Nom de l’organisme ou du demandeur", placeholder="Ex. Société française de génétique")
    alt_name = st.text_input("Abréviation ou autre nom connu", placeholder="Ex. SFG")
    search = st.button("Déterminer le tarif", type="primary", use_container_width=True)

    st.caption("L’outil cherche d’abord dans CRMR, puis FSMR, puis Sociétés savantes, puis GENERAL.")

with right:
    st.subheader("Résultat")

    if search:
        match = find_best_match(org_name, alt_name, ref_df, aliases_df, cfg)
        explanation = build_explanation(match, exceptions_df)

        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
        st.markdown(f"<span class='pill'>Confiance : {explanation['confidence']}</span>", unsafe_allow_html=True)
        st.markdown(f"<div class='tarif-value'>{explanation['tarif']}</div>", unsafe_allow_html=True)
        st.write(f"**Justification** : {explanation['justification']}")
        st.write(f"**Règle appliquée** : {explanation['rule']}")

        if explanation["exceptions"]:
            st.write("**Exceptions détectées**")
            for item in explanation["exceptions"]:
                st.warning(item)
        else:
            st.write("**Exceptions détectées** : aucune")

        with st.expander("Pourquoi ?", expanded=False):
            st.text(explanation["why"])

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Saisissez un organisme puis cliquez sur « Déterminer le tarif ».")

st.divider()
with st.expander("Référentiels chargés", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("CRMR", int((ref_df["referentiel"] == "CRMR").sum()))
    c2.metric("FSMR", int((ref_df["referentiel"] == "FSMR").sum()))
    c3.metric("Sociétés savantes", int((ref_df["referentiel"] == "SOCIETES SAVANTES").sum()))
    c4.metric("GENERAL", int((ref_df["referentiel"] == "GENERAL").sum()))
    st.dataframe(ref_df[["canonical_name", "referentiel", "tarif", "commentaire"]], use_container_width=True, hide_index=True)
