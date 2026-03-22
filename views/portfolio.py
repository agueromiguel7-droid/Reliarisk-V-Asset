import streamlit as st
import pydeck as pdk
import pandas as pd
import numpy as np
from src.i18n import get_text, translate_columns

def render_portfolio(df):
    st.markdown(f"## {get_text('port_title')}")
    
    if df is not None and not df.empty:
        # Key column identification
        reserva_col = next((c for c in df.columns if 'Petróleo equivalente' in c or 'Reserva' in c), None)
        prod_col = next((c for c in df.columns if 'Producción Actual' in c and 'Gas' not in c and 'Mpcd' not in c), None)
        api_col = next((c for c in df.columns if 'Gravedad API' in c or 'API' in c), None)
        depth_col = next((c for c in df.columns if 'Profundidad' in c or 'plano' in c), None)
        dev_col = next((c for c in df.columns if 'Desarrollo' in c), None)
        inseg_col = next((c for c in df.columns if 'Inseguridad' in c), None)
        mat_col = next((c for c in df.columns if 'Madurez' in c or 'Tecnológica' in c), None)
        
        campo_col = next((c for c in df.columns if 'Campos' in c), 'Campos')
        bloque_col = next((c for c in df.columns if 'Bloque' in c), None)
        
        # Calculate KPIs based on current DF
        tot_res_val = pd.to_numeric(df[reserva_col], errors='coerce').sum() if reserva_col else 0
        tot_prod_val = pd.to_numeric(df[prod_col], errors='coerce').sum() if prod_col else 0
        avg_api_val = pd.to_numeric(df[api_col], errors='coerce').mean() if api_col else 0
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(get_text('port_tot_res'), f"{tot_res_val:,.1f} MMBN")
        with c2:
            st.metric(get_text('port_tot_prod'), f"{tot_prod_val:,.1f} BD")
        with c3:
            st.metric(get_text('port_avg_api'), f"{avg_api_val:,.1f}° API")
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        map_col, filter_col = st.columns([3, 1])
        
        with filter_col:
            st.markdown(f"""
            <div style="background-color: #1e2022; padding: 15px; border-radius: 8px; margin-bottom: 25px;">
                <div style="font-size: 0.75rem; font-weight: 700; color: #b2b9c1; margin-bottom: 12px; font-family: 'Inter', sans-serif;">{get_text('port_res_scale')}</div>
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 18px; height: 18px; border-radius: 50%; background-color: rgba(0, 90, 156, 0.6); border: 2px solid #81cfff; margin-right: 15px;"></div>
                    <span style="font-size: 0.9rem; color: #e2e2e5; font-family: 'Inter', sans-serif;">> 1,000 MMBN</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 12px; height: 12px; border-radius: 50%; background-color: rgba(0, 90, 156, 0.6); border: 2px solid #81cfff; margin-right: 18px; margin-left: 3px;"></div>
                    <span style="font-size: 0.9rem; color: #e2e2e5; font-family: 'Inter', sans-serif;">500 - 1,000</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <div style="width: 8px; height: 8px; border-radius: 50%; background-color: rgba(0, 90, 156, 0.6); border: 2px solid #81cfff; margin-right: 20px; margin-left: 5px;"></div>
                    <span style="font-size: 0.9rem; color: #e2e2e5; font-family: 'Inter', sans-serif;">< 500 MMBN</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"#### {get_text('port_filters')}")
            
            # Master field filter
            if campo_col:
                field_list = sorted(list(df[campo_col].dropna().unique()))
                selected_field = st.selectbox(get_text('port_field'), [get_text('port_all')] + field_list)
                if selected_field != get_text('port_all'):
                    df = df[df[campo_col] == selected_field]
            
            # TABS for detailed filters
            tab_tech, tab_risk = st.tabs([get_text("tab_tech"), get_text("tab_risk")])
            
            with tab_tech:
                if api_col:
                    min_api = float(df[api_col].min(skipna=True))
                    max_api = float(df[api_col].max(skipna=True))
                    if not pd.isna(min_api) and not pd.isna(max_api) and min_api < max_api:
                        sel_api = st.slider(get_text("filter_api"), min_api, max_api, (min_api, max_api))
                        df = df[(df[api_col] >= sel_api[0]) & (df[api_col] <= sel_api[1]) | df[api_col].isna()]
                
                if depth_col:
                    min_depth = float(df[depth_col].min(skipna=True))
                    max_depth = float(df[depth_col].max(skipna=True))
                    if not pd.isna(min_depth) and not pd.isna(max_depth) and min_depth < max_depth:
                        sel_depth = st.slider(get_text("filter_depth"), min_depth, max_depth, (min_depth, max_depth))
                        df = df[(df[depth_col] >= sel_depth[0]) & (df[depth_col] <= sel_depth[1]) | df[depth_col].isna()]
                        
                if dev_col:
                    dev_opts = df[dev_col].dropna().unique()
                    if len(dev_opts) > 0:
                        sel_dev = st.multiselect(get_text("filter_dev"), dev_opts, default=[])
                        if sel_dev:
                            df = df[df[dev_col].isin(sel_dev)]
                            
            with tab_risk:
                if inseg_col:
                    inseg_opts = sorted(list(df[inseg_col].dropna().unique()))
                    if len(inseg_opts) > 0:
                        sel_inseg = st.multiselect(get_text("filter_insecurity"), inseg_opts, default=[])
                        if sel_inseg:
                            df = df[df[inseg_col].isin(sel_inseg)]
                            
                if mat_col:
                    mat_opts = df[mat_col].dropna().unique()
                    if len(mat_opts) > 0:
                        sel_mat = st.multiselect(get_text("filter_tech_mat"), mat_opts, default=[])
                        if sel_mat:
                            df = df[df[mat_col].isin(sel_mat)]
            
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button(get_text('port_export'), use_container_width=True):
                st.info(get_text('port_export_msg'))
                
        with map_col:
            if 'Latitud' in df.columns and 'Longitud' in df.columns:
                df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
                df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
                map_df = df.dropna(subset=['Latitud', 'Longitud']).copy()
                
                if not map_df.empty:
                    if reserva_col:
                        map_df['radius'] = np.sqrt(pd.to_numeric(map_df[reserva_col], errors='coerce').fillna(1)) * 250
                    else:
                        map_df['radius'] = 1000
    
                    view_state = pdk.ViewState(
                        latitude=map_df['Latitud'].mean(),
                        longitude=map_df['Longitud'].mean(),
                        zoom=7,
                        pitch=0
                    )
                    
                    layer = pdk.Layer(
                        'ScatterplotLayer',
                        data=map_df,
                        get_position='[Longitud, Latitud]',
                        get_radius='radius',
                        get_fill_color='[0, 90, 156, 160]',
                        pickable=True,
                        auto_highlight=True
                    )
                    
                    st.pydeck_chart(pdk.Deck(
                        map_style='dark',
                        initial_view_state=view_state,
                        layers=[layer],
                        tooltip={"text": "{Campos}\nScore: {Score de Atractividad}"}
                    ))
                else:
                    st.warning(get_text('port_no_coord'))
            else:
                st.warning(get_text('port_no_col_coord'))

        st.markdown("<hr/>", unsafe_allow_html=True)
        st.markdown(f"### {get_text('port_matrix')}")
        st.caption(get_text('port_matrix_cap'))
        
        display_cols = [c for c in [campo_col, bloque_col, reserva_col, prod_col, api_col, dev_col, 'Detalle Tipo de Desarrollo', 'Score de Atractividad'] if c in df.columns]
        if display_cols:
            display_df = translate_columns(df[display_cols].copy())
            
            numeric_cols = display_df.select_dtypes(include=['number']).columns
            style_dict = {col: "{:,.2f}" for col in numeric_cols}
            
            styled_df = display_df.style.format(style_dict)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

    else:
        st.warning(get_text('port_no_data'))
