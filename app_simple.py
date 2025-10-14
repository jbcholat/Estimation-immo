import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_processing import load_and_prepare_data

# Configuration
st.set_page_config(
    page_title="Estimation Immobilière 74",
    page_icon="🏠",
    layout="wide"
)

# Titre
st.title("🏠 Estimation Immobilière Haute-Savoie (74)")

# Chargement des données
@st.cache_data
def load_data():
    return load_and_prepare_data()

with st.spinner("Chargement des données..."):
    df = load_data()

# Statistiques générales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Transactions", f"{len(df):,}")
with col2:
    st.metric("Prix/m² médian", f"{df['prix_m2'].median():.0f} €")
with col3:
    st.metric("Communes", df['commune'].nunique())
with col4:
    st.metric("Types de biens", df['type_bien_simple'].nunique())

# Filtres
st.sidebar.header("Filtres")
type_bien = st.sidebar.selectbox("Type de bien", ['Tous'] + list(df['type_bien_simple'].unique()))
annee_min = st.sidebar.slider("Année minimum", 2020, 2024, 2022)

# Application des filtres
df_filtered = df.copy()
if type_bien != 'Tous':
    df_filtered = df_filtered[df_filtered['type_bien_simple'] == type_bien]
df_filtered = df_filtered[df_filtered['anneemut'] >= annee_min]

# Graphiques
col1, col2 = st.columns(2)

with col1:
    fig_prix = px.histogram(
        df_filtered, 
        x='prix_m2', 
        title="Distribution des prix au m²",
        nbins=50
    )
    st.plotly_chart(fig_prix, use_container_width=True)

with col2:
    fig_type = px.pie(
        df_filtered, 
        names='type_bien_simple', 
        title="Répartition par type de bien"
    )
    st.plotly_chart(fig_type, use_container_width=True)

# Top communes
st.subheader("Top 10 des communes")
top_communes = df_filtered.groupby('commune').agg({
    'prix_m2': 'median',
    'valeurfonc': 'count'
}).rename(columns={'valeurfonc': 'nb_transactions'}).sort_values('nb_transactions', ascending=False).head(10)

st.dataframe(top_communes)
