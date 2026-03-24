from __future__ import annotations

import streamlit as st
import pandas as pd

from src.loader import load_aliases, load_exceptions
from src.utils import df_to_csv_text, save_text_file_to_github, get_github_settings

st.set_page_config(page_title="Admin — Attribution des tarifs", page_icon="🔐", layout="wide")

st.title("Admin")
st.caption("Cette page permet de modifier les alias et exceptions puis de sauvegarder les changements dans GitHub.")

repo, token, branch, admin_password = get_github_settings()

if not admin_password:
    st.error("ADMIN_PASSWORD n’est pas défini dans les secrets Streamlit.")
    st.stop()

password = st.text_input("Mot de passe admin", type="password")
if password != admin_password:
    st.info("Entrez le mot de passe admin pour accéder à la page.")
    st.stop()

aliases_df = load_aliases().drop(columns=[c for c in ["alias_norm", "alias_simple"] if c in load_aliases().columns])
exceptions_df = load_exceptions()

st.subheader("Alias")
edited_aliases = st.data_editor(
    aliases_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="aliases_editor",
)

st.subheader("Exceptions")
edited_exceptions = st.data_editor(
    exceptions_df,
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="exceptions_editor",
)

save = st.button("Sauvegarder dans GitHub", type="primary")
if save:
    if not repo or not token:
        st.error("Renseignez GITHUB_REPO et GITHUB_TOKEN dans les secrets Streamlit avant de sauvegarder.")
        st.stop()

    try:
        save_text_file_to_github(
            repo=repo,
            path="data/aliases.csv",
            content=df_to_csv_text(pd.DataFrame(edited_aliases)),
            token=token,
            branch=branch,
            commit_message="Mise à jour des alias depuis l’admin Streamlit",
        )
        save_text_file_to_github(
            repo=repo,
            path="data/exceptions.csv",
            content=df_to_csv_text(pd.DataFrame(edited_exceptions)),
            token=token,
            branch=branch,
            commit_message="Mise à jour des exceptions depuis l’admin Streamlit",
        )
        st.success("Les fichiers ont été mis à jour dans GitHub.")
    except Exception as e:
        st.error(f"Échec de sauvegarde : {e}")
