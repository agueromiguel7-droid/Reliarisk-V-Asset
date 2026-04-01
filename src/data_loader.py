import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

@st.cache_data(ttl=600)
def load_data(filepath="BD_Campos_San-Tome.xlsx"):
    try:
        # Prioritize Google Sheets if credentials exist
        if "connections" in st.secrets and "gsheets" in st.secrets["connections"]:
            try:
                conn = st.connection("gsheets", type=GSheetsConnection)
                df = conn.read(worksheet="Campos", ttl=600)
                # Ensure we skip empty trailing rows if any exist in GSheets
                df = df.dropna(how='all')
            except Exception as e:
                error_msg = str(e)
                if "404" in error_msg:
                    st.warning("⚠️ Sin acceso a Google Sheets (Error 404). Verifica que en tu archivo de Google Sheets le hayas dado click a 'Compartir' y pegado el 'client_email' de tu Service Account como Lector. (Mostrando datos locales de respaldo temporales).")
                else:
                    st.warning(f"Advertencia de Conexión: {e}")
                df = pd.read_excel(filepath, header=0)
        else:
            df = pd.read_excel(filepath, header=0)
            
        if 'Campos' not in df.columns and 'N°' not in df.columns:
            df = pd.read_excel(filepath, header=1)
            if 'Campos' not in df.columns:
                 df = pd.read_excel(filepath, header=2)
                 
        df.columns = [str(c).strip().replace('.p', '').replace('.1', '') for c in df.columns]
        
        # --- Column Identification ---
        # Identify key columns using flexible naming
        campo_col = next((c for c in df.columns if 'Campos' in c), 'Campos')
        area_col = next((c for c in df.columns if 'Area' in c or 'Área' in c), 'Area')
        reg_col = next((c for c in df.columns if 'Región' in c or 'Sub-cuenca' in c), 'Región/Sub-cuenca')
        
        reserva_col = next((c for c in df.columns if 'Reserva de Petróleo equivalente' in c or 'Petróleo equivalente' in c), None)
        rgp_col = next((c for c in df.columns if 'RGP' in c), None)
        prod_col = next((c for c in df.columns if 'Producción Actual' in c and 'BD' in c), None)
        pcat_col = next((c for c in df.columns if 'Pozos Categoria' in c or 'Pozos Cat' in c), None)
        api_col = next((c for c in df.columns if 'Gravedad API' in c or 'API' in c), None)
        
        drhe_col = next((c for c in df.columns if 'Recurso Humano' in c), None)
        infra_col = next((c for c in df.columns if 'Infraestructura' in c), None)
        inseg_col = next((c for c in df.columns if 'Inseguridad' in c), None)
        
        def map_drhe(val):
            v = str(val).lower()
            if 'no apli' in v: return 0
            if 'alt' in v: return 1
            if 'med' in v: return 3
            if 'baj' in v: return 7
            return 3
            
        def map_infra(val):
            v = str(val).lower()
            if 'comercialización' in v or 'comercializacion' in v or 'separación' in v: return 9
            if 'compresión' in v or 'compresion' in v: return 7
            if 'ductos' in v: return 3
            if 'líneas' in v or 'lineas' in v: return 1
            return 5
            
        def map_inseg(val):
            v = str(val).lower()
            if 'no apli' in v: return 0
            if 'baj' in v: return 1
            if 'med' in v: return 3
            if 'alt' in v: return 9
            return 1

        if all(c in df.columns for c in [drhe_col, infra_col, inseg_col]):
            df['PTO_drhe'] = df[drhe_col].apply(map_drhe)
            df['PTO_infra'] = df[infra_col].apply(map_infra)
            df['PTO_inseg'] = df[inseg_col].apply(map_inseg)
            df['Nivel de Riesgo'] = (0.25 * df['PTO_drhe'] + 0.5 * df['PTO_infra'] + 0.25 * df['PTO_inseg']).round(2)
        else:
            df['Nivel de Riesgo'] = 0

        def safe_norm(col):
            if not col or col not in df.columns: return 0
            vals = pd.to_numeric(df[col], errors='coerce').fillna(0)
            m = vals.max()
            return vals / m if m > 0 else vals
            
        df['PTO_res'] = safe_norm(reserva_col)
        df['PTO_pa'] = safe_norm(prod_col)
        df['PTO_pcat'] = safe_norm(pcat_col)
        df['PTO_api'] = safe_norm(api_col)
        df['PTO_rgp'] = safe_norm(rgp_col)
        
        m_risk = df['Nivel de Riesgo'].max()
        df['PTO_riesgo'] = df['Nivel de Riesgo'] / m_risk if m_risk > 0 else 0
        
        # STARIV Formula: (0.35*Res + 0.25*PA + 0.2*PCat + 0.05*API + 1) / (0.05*RGP + 0.1*Riesgo + 1)
        num = (0.35 * df['PTO_res'] + 0.25 * df['PTO_pa'] + 0.2 * df['PTO_pcat'] + 0.05 * df['PTO_api'] + 1)
        den = (0.05 * df['PTO_rgp'] + 0.1 * df['PTO_riesgo'] + 1)
        df['STARIV'] = (num / den).round(4)
        df['Score de Atractividad'] = df['STARIV']
        df = df.sort_values('STARIV', ascending=False).reset_index(drop=True)

        dev_col = next((c for c in df.columns if 'Desarrollo' in c), None)
        if dev_col:
            df['Detalle Tipo de Desarrollo'] = df[dev_col]
            def split_dev(val):
                v = str(val).strip().upper()
                if v.startswith('CPP'): return 'CPP'
                if v.startswith('EP'): return 'EP'
                return val
            df[dev_col] = df[dev_col].apply(split_dev)
            
        lat_c = next((c for c in df.columns if 'Latitud' in c), None)
        lon_c = next((c for c in df.columns if 'Longitud' in c), None)
        if lat_c: df.rename(columns={lat_c: 'Latitud'}, inplace=True)
        if lon_c: df.rename(columns={lon_c: 'Longitud'}, inplace=True)
            
        return df
    except Exception as e:
        import traceback
        st.error(f"Error cargando datos: {e}\n{traceback.format_exc()}")
        return None
