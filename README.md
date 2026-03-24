# Attribution des tarifs — Institut Imagine

Application Streamlit pour recommander le type de tarif à attribuer à un demandeur, à partir des référentiels officiels :
- CRMR
- FSMR
- Sociétés savantes
- GENERAL

## Déploiement rapide
1. Créer un dépôt GitHub public.
2. Ajouter tous les fichiers du projet.
3. Connecter le dépôt à Streamlit Community Cloud.
4. Définir les secrets suivants dans Streamlit Cloud :

```toml
GITHUB_REPO = "VOTRE_COMPTE_GITHUB/VOTRE_REPO"
GITHUB_TOKEN = "VOTRE_TOKEN_GITHUB"
GITHUB_BRANCH = "main"
ADMIN_PASSWORD = "votre_mot_de_passe_admin"
```

5. Déployer en choisissant `app.py` comme fichier principal.

## Fichiers de données
Le projet attend les fichiers suivants dans `data/` :
- `revision_tarifs_2027.xlsx`
- `liste_evenements_2014_2025.xlsx`
- `historique_attribution_tarif.xlsx`
- `prix_agents_securite_2025.xlsx`
- `prix_location_materiel.xlsx`
- `aliases.csv`
- `exceptions.csv`
- `config.yaml`

## Admin
La page Admin permet de modifier :
- les alias
- les exceptions

Les changements sont sauvegardés dans GitHub via l’API GitHub.
