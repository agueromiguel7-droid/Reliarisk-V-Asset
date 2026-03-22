import streamlit as st
import bcrypt
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from src.i18n import get_text

def authenticate_user():
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None

    if not st.session_state['authentication_status']:
        
        # Language selector on the login screen
        col1, col2 = st.columns([8, 2])
        with col2:
            st.selectbox("Idioma / Language", ["Español", "English"], key="language_login")
            if st.session_state.get('language_login'):
                st.session_state['language'] = st.session_state['language_login']

        st.markdown(f"## {get_text('auth_restricted')}")
        st.markdown(get_text('auth_prompt'))
        
        with st.form("login_form"):
            username = st.text_input(get_text('auth_user'))
            password = st.text_input(get_text('auth_pass'), type="password")
            submitted = st.form_submit_button(get_text('auth_login'))
            
            if submitted:
                # GOOGLE SHEETS AUTHENTICATION
                try:
                    # check if secrets are set up
                    if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        users_df = conn.read(worksheet="Usuarios", ttl=600)
                        users_df.columns = users_df.columns.astype(str).str.strip()
                        
                        if 'username' in users_df.columns:
                            user_row = users_df[users_df['username'] == username]
                            if not user_row.empty:
                                stored_hash = str(user_row.iloc[0]['password_hash'])
                                active_val = str(user_row.iloc[0].get('active', 'TRUE')).upper()
                                is_active = active_val == 'TRUE' or active_val == '1.0' or active_val == '1'
                                
                                # Compare password with bcrypt hash
                                if is_active and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                                    st.session_state['authentication_status'] = True
                                    st.session_state['username'] = username
                                    st.session_state['role'] = 'admin' if username.lower() == 'admin' else 'inversor'
                                    st.rerun()
                                else:
                                    st.error(get_text('auth_wrong'))
                            else:
                                st.error(get_text('auth_wrong'))
                        else:
                            st.error("Error: Columna 'username' no encontrada en hoja Usuarios.")
                    else:
                        raise Exception("No secrets defined")
                        
                except Exception as e:
                    # Fallback MOCK VALIDATION for local dev before secrets are added
                    if username == "admin" and password == "123":
                        st.session_state['authentication_status'] = True
                        st.session_state['username'] = username
                        st.session_state['role'] = 'admin'
                        st.rerun()
                    elif username == "inversor" and password == "123":
                        st.session_state['authentication_status'] = True
                        st.session_state['username'] = username
                        st.session_state['role'] = 'inversor'
                        st.rerun()
                    else:
                        st.error(get_text('auth_wrong'))
        
        return False
        
    return True

def render_user_profile():
    st.success(f"👤 {st.session_state['username']} ({st.session_state['role'].capitalize()})")
    if st.button(get_text('auth_logout'), use_container_width=True):
        st.session_state['authentication_status'] = None
        st.session_state['username'] = None
        st.session_state['role'] = None
        st.rerun()
