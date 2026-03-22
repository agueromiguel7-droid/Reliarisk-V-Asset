import streamlit as st
import pandas as pd
from src.i18n import get_text, translate_columns

def render_screener(df):
    st.markdown(f"## {get_text('scr_title')}")
    st.markdown(get_text('scr_desc'))
    
    if df is not None and not df.empty:
        # Define sorting options dynamically
        sort_options_base = [
            'Score de Atractividad',
            'Reservas Remanentes Líquido',
            'Reservas Remanentes Gas',
            'Reservas Remanentes Petróleo Equivalente',
            'Producción Actual',
            'Pozos Categoria 2 y 3',
            'Gravedad API',
            'Profundidad plano de ref.'
        ]
        
        available_sort_cols = []
        col_mapping = {}
        for opt in sort_options_base:
            words = opt.replace("ó", "o").replace("í", "i").lower().split()
            best_col = None
            for c in df.columns:
                c_clean = c.replace("ó", "o").replace("í", "i").lower()
                if all(w[:4] in c_clean for w in words): 
                    best_col = c
                    break
            if not best_col:
                keyword = words[0] if words else ''
                for c in df.columns:
                    if keyword in c.lower() and ('api' in opt.lower() and 'api' in c.lower() or 'api' not in opt.lower()):
                        best_col = c
                        break
                        
            if not best_col and opt in df.columns:
                best_col = opt
                
            if best_col and best_col not in col_mapping.values():
                col_mapping[opt] = best_col
                # For UI display in dropdown, optionally translate the option:
                opt_display = opt
                if st.session_state.get('language') == "English":
                    # Ad-hoc translations for drop-down
                    en_dict = {
                        'Score de Atractividad': 'Attractiveness Score',
                        'Reservas Remanentes Líquido': 'Liquid Reserves',
                        'Reservas Remanentes Gas': 'Gas Reserves',
                        'Reservas Remanentes Petróleo Equivalente': 'Eq. Oil Reserves',
                        'Producción Actual': 'Current Production',
                        'Pozos Categoria 2 y 3': 'Cat 2 & 3 Wells',
                        'Gravedad API': 'API Gravity',
                        'Profundidad plano de ref.': 'Ref. Depth'
                    }
                    opt_display = en_dict.get(opt, opt)
                
                # Bi-directional tracking
                col_mapping[opt_display] = best_col
                available_sort_cols.append(opt_display)
                
        # Also always safely include 'Score'
        if 'Score de Atractividad' in df.columns:
            sc_key = 'Attractiveness Score' if st.session_state.get('language') == "English" else 'Score de Atractividad'
            if sc_key not in available_sort_cols:
                col_mapping[sc_key] = 'Score de Atractividad'
                available_sort_cols.insert(0, sc_key)

        col1, _ = st.columns([1, 2])
        with col1:
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
