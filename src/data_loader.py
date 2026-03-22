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
                st.warning(f"Advertencia (Service Account): {e}")
                df = pd.read_excel(filepath, header=0)
        else:
            df = pd.read_excel(filepath, header=0)
            
        if 'Campos' not in df.columns and 'N°' not in df.columns:
            df = pd.read_excel(filepath, header=1)
            if 'Campos' not in df.columns:
                 df = pd.read_excel(filepath, header=2)
                 
        df.columns = df.columns.astype(str).str.strip()
        
        # Parse and separate "Tipo de Desarrollo"
        dev_col = next((c for c in df.columns if 'Desarrollo' in c), None)
        if dev_col:
            df['Detalle Tipo de Desarrollo'] = df[dev_col]
            def split_dev(val):
                v = str(val).strip().upper()
                if v.startswith('CPP'): return 'CPP'
                if v.startswith('EP'): return 'EP'
                return val
            df[dev_col] = df[dev_col].apply(split_dev)
        
        def map_risk(val):
            if pd.isna(val): return 1
            v = str(val).lower().strip()
            if 'alt' in v: return 3
            if 'med' in v or 'mei' in v: return 2
            if 'baj' in v: return 1
            return 1 # Default

        reserva_col = next((c for c in df.columns if 'Reserva de Petróleo equivalente' in c or 'Petróleo equivalente' in c), None)
        infra_col = next((c for c in df.columns if 'Infraestructura' in c), None)
        inseg_col = next((c for c in df.columns if 'Inseguridad' in c), None)
        
        if reserva_col and infra_col and inseg_col:
            df['Infra_Num'] = df[infra_col].apply(map_risk)
            df['Inseg_Num'] = df[inseg_col].apply(map_risk)
            
            # Limpiar rastro de typos en la vista visual
            df[inseg_col] = df['Inseg_Num'].map({3: 'Alta', 2: 'Media', 1: 'Baja'})
            
            # Redondear a 2 decimales
            df['Score de Atractividad'] = ((pd.to_numeric(df[reserva_col], errors='coerce').fillna(0) * 0.4) + (df['Infra_Num'] * 0.3) - (df['Inseg_Num'] * 0.3)).round(2)
            df = df.sort_values('Score de Atractividad', ascending=False).reset_index(drop=True)
            
        lat_c = next((c for c in df.columns if 'Latitud' in c), None)
        lon_c = next((c for c in df.columns if 'Longitud' in c), None)
        if lat_c: df.rename(columns={lat_c: 'Latitud'}, inplace=True)
        if lon_c: df.rename(columns={lon_c: 'Longitud'}, inplace=True)
            
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return None
