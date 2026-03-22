import streamlit as st
import os
import sys

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import authenticate_user, render_user_profile
from src.data_loader import load_data
from src.i18n import get_text
from views.portfolio import render_portfolio
from views.screener import render_screener
from views.detail_risk import render_detail_risk
from views.sensitivity import render_sensitivity
from views.admin import render_admin

st.set_page_config(
    page_title="BI Web App - Venezuela Oil Fields",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Injection ---
st.markdown("""
<style>
/* Obsidian Observatory styling overrides */
[data-testid="stSidebar"] { background-color: #1a1c1e !important; border-right: none !important; }
.stApp { background-color: #121416 !important; }
/* Universal font color fix to prevent dark-on-dark invisible text in default Light theme */
html, body, [class*="css"], [class*="st-"], p, h1, h2, h3, h4, h5, h6, span, label, div {
    color: #e2e2e5 !important;
}
/* Re-fix interactive backgrounds clashing with white font */
div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
    background-color: #1a1c1e !important;
    border: 1px solid #4a5568 !important;
}
input, .stSelectbox div[role="combobox"] { color: #e2e2e5 !important; }
div.block-container { padding-top: 3.5rem; }

/* Dashboard Cards inside Risk Radar */
.custom-card {
    background-color: #1a1c1e;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    height: 100%;
}
.custom-card-label {
    font-size: 0.75rem; font-weight: 700; color: #b2b9c1; text-transform: uppercase; margin-bottom: 8px;
}
.custom-card-value {
    font-size: 1.8rem; font-weight: bold; color: #ffffff;
}
.custom-card-unit {
    font-size: 0.9rem; font-weight: normal; color: #888;
}
.specs-val {
    font-size: 1.2rem; font-weight: bold; color: #ffffff; margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

if 'language' not in st.session_state:
    st.session_state['language'] = 'Español'

if authenticate_user():
    
    # === Top Navigation Bar ===
    top_empty, top_col_user, top_col_lang, top_col_out = st.columns([10, 3, 1.2, 1.8])
    
    with top_col_user:
        role_label = "Admin" if st.session_state.get('role', 'inversor') == 'admin' else "Inv"
        st.markdown(f"<div style='text-align: right; padding-top: 5px; color: #b2b9c1; font-size: 1.1rem; white-space: nowrap;'>👤 <b>{st.session_state.get('username')}</b> ({role_label})</div>", unsafe_allow_html=True)
        
    with top_col_lang:
        current_lang = st.session_state.get('language', 'Español')
        lang_idx = 0 if current_lang == "Español" else 1
        new_lang = st.selectbox("Lang", ["ES", "EN"], index=lang_idx, key="top_lang_selector", label_visibility="collapsed")
        target_lang = "Español" if new_lang == "ES" else "English"
        if target_lang != current_lang:
            st.session_state['language'] = target_lang
            st.rerun()
            
    with top_col_out:
        if st.button("🚪 " + ("Salir" if current_lang=="Español" else "Exit"), use_container_width=True):
            st.session_state['authentication_status'] = None
            st.session_state['username'] = None
            st.session_state['role'] = None
            st.rerun()
            
    st.markdown("<hr style='margin-top: 5px; margin-bottom: 25px; border-color: #333;'/>", unsafe_allow_html=True)

    # 1. --- Center Logo Implementation ---
    col1, col2, col3 = st.sidebar.columns([1, 4, 1])
    with col2:
        if os.path.exists("mi_logo.png"):
            st.image("mi_logo.png", use_container_width=True)
        st.markdown("<h4 style='text-align: center; color: #81cfff; margin-top: -10px; margin-bottom: 20px; font-weight: 700; font-family: sans-serif;'>Reliarisk V-Asset</h4>", unsafe_allow_html=True)
            
    st.sidebar.markdown("<br/>", unsafe_allow_html=True)
    
    # 4. --- Navigation ---
    st.sidebar.title(get_text("nav_title"))
    
    role = st.session_state.get('role', 'inversor')
    pages = [
        get_text("nav_portfolio"), 
        get_text("nav_screener"), 
        get_text("nav_radar"), 
        get_text("nav_sensitivity")
    ]
    
    if role == 'admin':
        pages.append(get_text("nav_admin"))
        
    page = st.sidebar.radio("Ir a / Go to", pages)
    
    df = load_data()
    
    if df is not None:
        if page == get_text("nav_portfolio"):
            render_portfolio(df)
        elif page == get_text("nav_screener"):
            render_screener(df)
        elif page == get_text("nav_radar"):
            render_detail_risk(df)
        elif page == get_text("nav_sensitivity"):
            render_sensitivity(df)
        elif page == get_text("nav_admin"):
            render_admin(df)
    else:
        st.error("Error Crítico: No se pudo conectar a Google Sheets y no existe archivo de respaldo local.")
        
    # 5. --- Help Section ---
    st.sidebar.markdown("<br/>"*2, unsafe_allow_html=True)
    with st.sidebar.expander(get_text("help_score_title")):
        st.markdown(get_text("help_score_text"))
