import streamlit as st
import pandas as pd
from src.i18n import get_text, translate_columns

def render_screener(df):
    st.markdown(f"## {get_text('scr_title')}")
    st.markdown(get_text('scr_desc'))
    
    if df is not None and not df.empty:
        # Define sorting options dynamically
        sort_options_base = [
            'STARIV',
            'Nivel de Riesgo',
            'Reservas Remanentes Líquido',
            'Reservas Remanentes Gas',
            'Reservas Remanentes Petróleo Equivalente',
            'Producción Actual',
            'Pozos Categoria 2 y 3',
            'Gravedad API'
        ]
        
        available_sort_cols = []
        col_mapping = {}
        for opt in sort_options_base:
            # Map column names flexibly
            best_col = None
            if opt in df.columns:
                best_col = opt
            else:
                words = opt.replace("ó", "o").replace("í", "i").lower().split()
                for c in df.columns:
                    c_clean = str(c).replace("ó", "o").replace("í", "i").lower()
                    if all(w[:4] in c_clean for w in words): 
                        best_col = c
                        break
            
            if best_col and best_col not in col_mapping.values():
                opt_display = opt
                if st.session_state.get('language') == "English":
                    en_dict = {
                        'STARIV': 'STARIV Index',
                        'Nivel de Riesgo': 'Risk Level',
                        'Reservas Remanentes Líquido': 'Liquid Reserves',
                        'Reservas Remanentes Gas': 'Gas Reserves',
                        'Reservas Remanentes Petróleo Equivalente': 'Eq. Oil Reserves',
                        'Producción Actual': 'Current Production',
                        'Pozos Categoria 2 y 3': 'Cat 2 & 3 Wells',
                        'Gravedad API': 'API Gravity'
                    }
                    opt_display = en_dict.get(opt, opt)
                
                col_mapping[opt_display] = best_col
                available_sort_cols.append(opt_display)


        col1, _ = st.columns([1, 2])
        with col1:
            available_sort_cols = sorted(available_sort_cols)
            selected_sort = st.selectbox(get_text('scr_sort_by'), available_sort_cols)
        
        if selected_sort and selected_sort in col_mapping:
            actual_col = col_mapping[selected_sort]
            df = df.sort_values(by=actual_col, ascending=False)
            
        display_df = translate_columns(df.copy())
        
        numeric_cols = display_df.select_dtypes(include=['number']).columns
        style_dict = {col: "{:,.2f}" for col in numeric_cols}
        
        styled_df = display_df.style.format(style_dict)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=get_text('scr_dl'),
            data=csv,
            file_name='screener_campos.csv',
            mime='text/csv',
            type="primary"
        )
    else:
        st.warning(get_text('port_no_data'))
