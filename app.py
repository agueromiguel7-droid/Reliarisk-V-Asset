import streamlit as st
import os
import sys

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth import authenticate_user, render_user_profile
from src.data_loader import load_data, recalculate_stariv
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
    
    df = load_data()

    # === Top Navigation Bar ===
    top_col_area, top_col_dev, top_col_user, top_col_lang, top_col_out = st.columns([2.0, 2.0, 4.0, 1.2, 1.8])
    
    with top_col_area:
        if df is not None:
            area_col = next((c for c in df.columns if 'Area' in c or 'Área' in c), None)
            if area_col:
                area_list = sorted(list(df[area_col].dropna().unique()))
                selected_area = st.selectbox(
                    f"🌍 {get_text('filter_area', 'Seleccionar Área Operativa')}",
                    [get_text("all", "Todas")] + area_list,
                    key="global_area_filter",
                    label_visibility="collapsed"
                )
                if selected_area != get_text("all", "Todas"):
                    df = df[df[area_col] == selected_area]

    with top_col_dev:
        if df is not None:
            dev_col = next((c for c in df.columns if 'Desarrollo' in c), None)
            if dev_col:
                dev_list = sorted(list(df[dev_col].dropna().unique()))
                selected_dev = st.selectbox(
                    f"🏗️ {get_text('filter_dev', 'Tipo de Desarrollo')}",
                    [get_text("all", "Todas")] + dev_list,
                    key="global_dev_filter",
                    label_visibility="collapsed"
                )
                if selected_dev != get_text("all", "Todas"):
                    df = df[df[dev_col] == selected_dev]
                    
    # Recalculate STARIV if we filtered the data
    if df is not None:
        df = df.reset_index(drop=True)
        df = recalculate_stariv(df)
                    
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

    # 6. --- Legal Disclaimer ---
    disclaimer_html = """
    <div style="margin-top: 50px;">
        <details>
            <summary style="font-size: 0.75rem; color: #7f8c8d; cursor: pointer; list-style-type: none;">
                © 2026 Grupo Reliarisk. El uso de STARIV está sujeto al <a style="color: #95a5a6; text-decoration: underline;">Descargo de Responsabilidad</a>.
            </summary>
            <div style="font-size: 0.7rem; color: #7f8c8d; padding: 10px; margin-top: 5px; background-color: #1e2022; border-radius: 5px; text-align: justify; line-height: 1.4;">
                <b>AVISO LEGAL Y LIMITACIÓN DE RESPONSABILIDAD – RELIARISK V-ASSET</b><br/><br/>
                <b>1. Naturaleza de la Información:</b><br/>
                Esta aplicación y los informes generados por ella son propiedad de Grupo Reliarisk y se proporcionan exclusivamente con fines informativos y de soporte a la toma de decisiones estratégicas. La información técnica, geográfica y de producción contenida en Reliarisk V-Asset proviene de fuentes públicas oficiales, registros históricos del Estado Venezolano (PDVSA/MinPetróleo) y bases de datos técnicas de la industria. Grupo Reliarisk no garantiza la exactitud, integridad o actualización en tiempo real de dicha data externa.<br/><br/>
                <b>2. Proyecciones y Estimaciones Estocásticas:</b><br/>
                Los indicadores como el Índice de Proximidad a Infraestructura (IPI), el Cuadro de Mando de Riesgos y el Resumen Ejecutivo Automático son el resultado de modelos algorítmicos y análisis de riesgo probabilístico. Estas proyecciones representan expectativas sobre eventos futuros y están sujetas a variables económicas, políticas, geológicas y operativas fuera del control de Grupo Reliarisk. Los resultados reales pueden variar significativamente de las estimaciones presentadas.<br/><br/>
                <b>3. No Asesoría Financiera ni de Inversión:</b><br/>
                El contenido de esta plataforma no constituye una oferta de venta, una solicitud de compra de activos petroleros, ni una recomendación formal de inversión. El usuario y/o potencial inversionista es el único responsable de realizar su propia debida diligencia (Due Diligence) técnica y legal antes de comprometer capital o recursos en los campos mencionados.<br/><br/>
                <b>4. Confidencialidad y Uso de Datos:</b><br/>
                Dado el carácter sensible de la información estratégica del sector hidrocarburos, el acceso a esta aplicación está restringido. El uso no autorizado, la reproducción total o parcial, o la divulgación de los mapas y dashboards de Reliarisk V-Asset a terceros sin el consentimiento expreso de Grupo Reliarisk está estrictamente prohibido y puede estar sujeto a sanciones legales.<br/><br/>
                <b>5. Exclusión de Daños:</b><br/>
                Bajo ninguna circunstancia Grupo Reliarisk, sus directivos o desarrolladores serán responsables por pérdidas financieras, daños directos o indirectos derivados del uso o la imposibilidad de uso de esta herramienta tecnológica.
            </div>
        </details>
    </div>
    """
    st.sidebar.markdown(disclaimer_html, unsafe_allow_html=True)
