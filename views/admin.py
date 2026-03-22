import streamlit as st
import pandas as pd
from src.data_loader import load_data

def render_admin(df):
    lang = st.session_state.get('language', 'Español')
    
    st.markdown("## ☁️ Sincronización en la Nube" if lang == 'Español' else "## ☁️ Cloud Synchronization")
    st.info("La base de datos (Campos y Usuarios) está ahora vinculada permanentemente a Google Sheets. Haz clic en el botón de abajo para forzar la actualización de los datos en tiempo real para todos los inversores." if lang == 'Español' else "The database (Fields and Users) is now permanently linked to Google Sheets. Click the button below to force a real-time data update across the entire app for all investors.")
    
    # Optional: Display connection info from st.secrets if available (hide actual URL for security)
    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
        st.success("🟢 Conexión con Google Cloud Platform: **Activa**" if lang == 'Español' else "🟢 Google Cloud Platform Connection: **Active**")
    else:
        st.warning("⚠️ Sin conexión a la nube configurada en secrets.toml" if lang == 'Español' else "⚠️ Cloud connection missing in secrets.toml")
        
    st.markdown("<br/>", unsafe_allow_html=True)
    
    if st.button("🔄 Sincronizar Base de Datos Ahora" if lang == 'Español' else "🔄 Sync Database Now", use_container_width=True):
        st.cache_data.clear()
        st.success("¡Datos actualizados desde Google Sheets! Todos los módulos muestran ahora la información más reciente." if lang == 'Español' else "Data updated from Google Sheets! All modules now display the latest information.")
