import streamlit as st
import pandas as pd
from supabase import create_client
import time
import plotly.express as px

# Connexion
SUPABASE_URL = "https://qpwwceigajtigvhpmbpg.supabase.co"
SUPABASE_KEY = "sb_publishable_hYAcKlZbCfCdW-SzdiEIDA_Ng7jGwO7" 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="CAN 2025 - AI Command Center", layout="wide")

# Style Maroc / CAN
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #d4af37; text-align: center; border-bottom: 2px solid #c1272d; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇲🇦 CAN 2025 - DASHBOARD LIVE")

def load_data():
    # Correction ici : On trie par 'timestamp' (le nom dans ton image)
    response = supabase.table("affluence").select("*").order("timestamp", desc=True).execute()
    return pd.DataFrame(response.data)

df = load_data()

if not df.empty:
    # On utilise 'timestamp' au lieu de 'created_at'
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dernier Stade", df.iloc[0]['stade'])
    with col2:
        val = df.iloc[0]['nombre_supporters']
        st.metric("Supporters", val, delta="ALERTE" if val > 5000 else "OK", delta_color="inverse" if val > 5000 else "normal")
    with col3:
        st.metric("Total Analyses", len(df))

    st.subheader("📈 Évolution de l'affluence")
    fig = px.line(df, x="timestamp", y="nombre_supporters", color="stade", 
                  template="plotly_dark", color_discrete_sequence=['#d4af37', '#c1272d'])
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Historique des détections")
    st.dataframe(df[['timestamp', 'stade', 'nombre_supporters']], use_container_width=True)

else:
    st.info("Aucune donnée trouvée dans la table 'affluence'.")

time.sleep(10)
st.rerun()
