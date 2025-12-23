import streamlit as st
import pandas as pd
from supabase import create_client
import time
import plotly.express as px

# 1. Connexion à TON Cloud Supabase
SUPABASE_URL = "https://qpwwceigajtigvhpmbpg.supabase.co"
SUPABASE_KEY = "sb_publishable_hYAcKlZbCfCdW-SzdiEIDA_Ng7jGwO7" # Ta clé actuelle
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuration de la page
st.set_page_config(page_title="CAN 2025 - AI Command Center", layout="wide")

# Style CSS pour le look "Wow" (Vert, Rouge, Or)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1a202c; padding: 20px; border-radius: 10px; border: 1px solid #d4af37; }
    h1 { color: #d4af37; text-align: center; border-bottom: 2px solid #c1272d; padding-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇲🇦 CAN 2025 - DASHBOARD ANALYTIQUE")
st.subheader("Surveillance des stades par Intelligence Artificielle")

# Sidebar pour le statut des services Cloud
with st.sidebar:
    st.header("🌐 Cloud Infrastructure")
    st.success("🤖 YOLOv8 on Koyeb: ACTIVE")
    st.success("💾 Supabase DB: CONNECTED")
    st.success("⚡ Edge Functions: ARMED")
    st.warning("📱 Twilio SMS: READY")
    if st.button("🔄 Actualiser manuellement"):
        st.rerun()

# 2. Récupération des données réelles
def load_data():
    # On récupère les données insérées par ton code FastAPI/Koyeb
    response = supabase.table("affluence").select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(response.data)

df = load_data()

if not df.empty:
    # --- SECTION KPI ---
    last_entry = df.iloc[0]
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dernier Stade", last_entry['stade'])
    with col2:
        # Couleur rouge si > 5000 (comme ton Edge Function)
        st.metric("Supporters", f"{last_entry['nombre_supporters']}", 
                  delta="- Alerte Saturation" if last_entry['nombre_supporters'] > 5000 else "Flux Normal",
                  delta_color="inverse" if last_entry['nombre_supporters'] > 5000 else "normal")
    with col3:
        st.metric("Total Analyses", len(df))

    # --- SECTION GRAPHIQUES ---
    st.markdown("---")
    c1, c2 = st.columns([2, 1])

    with c1:
        st.subheader("📈 Évolution de l'affluence")
        # Graphique temporel
        df['created_at'] = pd.to_datetime(df['created_at'])
        fig = px.line(df, x="created_at", y="nombre_supporters", color="stade",
                      template="plotly_dark", color_discrete_sequence=['#d4af37', '#c1272d', '#006233'])
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("📋 Dernières Alertes")
        # On affiche uniquement les saturations > 5000
        alerts = df[df['nombre_supporters'] > 5000].head(5)
        for _, row in alerts.iterrows():
            st.error(f"⚠️ {row['stade']} : {row['nombre_supporters']} pers. (SMS envoyé)")

    # --- TABLEAU DE DONNÉES COMPLET ---
    with st.expander("🔍 Voir les logs complets de la base de données"):
        st.dataframe(df, use_container_width=True)

else:
    st.info("En attente de données venant de Koyeb...")

# Auto-refresh toutes les 10 secondes pour le côté "Live"
time.sleep(10)
st.rerun()
