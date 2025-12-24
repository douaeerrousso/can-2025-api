import streamlit as st
import pandas as pd
from supabase import create_client
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration Page
st.set_page_config(page_title="CAN 2025 - Dashboard Premium", layout="wide")

# Connexion Supabase
SUPABASE_URL = "https://qpwwceigajtigvhpmbpg.supabase.co"
SUPABASE_KEY = "sb_publishable_hYAcKlZbCfCdW-SzdiEIDA_Ng7jGwO7"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

CAPACITY = {
    'Rabat': 50000, 'Tanger': 65000, 'Agadir': 45000, 
    'Casablanca': 70000, 'Marrakech': 40000
}

# --- STYLE CSS (Le look React/Vercel) ---
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #166534 0%, #991b1b 50%, #ca8a04 100%);
        color: white;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        border-radius: 10px;
        padding: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(12px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 20px;
    }
    h1, h2, h3 { color: white !important; font-weight: bold; }
    .status-red { color: #fca5a5; font-weight: bold; }
    .status-green { color: #86efac; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIQUE DE DONNÉES ---
def get_data():
    res = supabase.table("affluence").select("*").order("timestamp", desc=True).limit(100).execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = get_data()

if not df.empty:
    # Calculs comme dans ton React
    latest_by_stade = df.sort_values('timestamp').groupby('stade').tail(1)
    latest_by_stade['capacity'] = latest_by_stade['stade'].map(lambda x: CAPACITY.get(x, 50000))
    latest_by_stade['taux'] = (latest_by_stade['nombre_supporters'] / latest_by_stade['capacity'] * 100).round()
    
    total_supporters = latest_by_stade['nombre_supporters'].sum()
    avg_occ = int(latest_by_stade['taux'].mean())
    critical = len(latest_by_stade[latest_by_stade['taux'] > 80])

    # --- HEADER ---
    st.markdown(f"""
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1>🏆 CAN 2025 - Surveillance Affluence</h1>
                    <p style="color: #bbf7d0;">Système de Gestion Temps Réel des Stades (AI Powered)</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin:0;">Dernière mise à jour</p>
                    <h2 style="color: #fde047; margin:0;">{datetime.now().strftime('%H:%M:%S')}</h2>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- KPIs ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Supporters", f"{total_supporters:,}")
    c2.metric("Taux Moyen", f"{avg_occ}%")
    c3.metric("Stades Critiques", critical)
    c4.metric("Stades Actifs", len(latest_by_stade))

    # --- ALERTES SMS (Le bandeau rouge) ---
    alerts = latest_by_stade[latest_by_stade['taux'] > 80]
    if not alerts.empty:
        with st.container():
            st.markdown('<div class="card" style="background: rgba(239,68,68,0.2);"><h3>🚨 Alertes SMS Twilio Actives</h3>', unsafe_allow_html=True)
            for _, row in alerts.iterrows():
                st.write(f"⚠️ **{row['stade']}** : {int(row['nombre_supporters'])} pers. ({int(row['taux'])}%) - SMS Envoyé")
            st.markdown('</div>', unsafe_allow_html=True)

    # --- GRAPHIQUES ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="card"><h3>📊 Occupation Actuelle</h3>', unsafe_allow_html=True)
        fig_bar = px.bar(latest_by_stade, x='stade', y=['nombre_supporters', 'capacity'], 
                         barmode='group', template='plotly_dark',
                         color_discrete_sequence=['#4ade80', '#94a3b8'])
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card"><h3>🥧 Répartition</h3>', unsafe_allow_html=True)
        fig_pie = px.pie(latest_by_stade, values='nombre_supporters', names='stade', 
                         hole=0.4, template='plotly_dark')
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TIMELINE ---
    st.markdown('<div class="card"><h3>📈 Évolution Temporelle</h3>', unsafe_allow_html=True)
    fig_line = px.line(df, x='timestamp', y='nombre_supporters', color='stade',
                       template='plotly_dark', line_shape='spline')
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.warning("En attente de connexion avec Supabase...")

st.empty()
import time
time.sleep(5)
st.rerun()
