from __future__ import annotations

import base64
from io import StringIO
import pandas as pd
import requests
import streamlit as st



def df_to_csv_text(df: pd.DataFrame) -> str:
    buffer = StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue()



def save_text_file_to_github(repo: str, path: str, content: str, token: str, branch: str = "main", commit_message: str | None = None):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    sha = None
    current = requests.get(url, headers=headers, params={"ref": branch}, timeout=30)
    if current.status_code == 200:
        sha = current.json().get("sha")

    payload = {
        "message": commit_message or f"Mise à jour de {path}",
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()



def get_github_settings():
    repo = st.secrets.get("GITHUB_REPO", "")
    token = st.secrets.get("GITHUB_TOKEN", "")
    branch = st.secrets.get("GITHUB_BRANCH", "main")
    admin_password = st.secrets.get("ADMIN_PASSWORD", "")
    return repo, token, branch, admin_password
