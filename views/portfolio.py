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
        area_col = next((c for c in df.columns if 'Area' in c or 'Área' in c), None)
        campo_col = next((c for c in df.columns if 'Campos' in c), 'Campos')
        bloque_col = next((c for c in df.columns if 'Bloque' in c), None)
        
        # Calculate KPIs based on current DF
        tot_res_val = pd.to_numeric(df[reserva_col], errors='coerce').sum() if reserva_col else 0
        tot_prod_val = pd.to_numeric(df[prod_col], errors='coerce').sum() if prod_col else 0
        
        # Robust API min/max handling to fix the reported error
        api_series = pd.to_numeric(df[api_col], errors='coerce') if api_col else pd.Series([])
        avg_api_val = api_series.mean() if not api_series.empty else 0
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric(get_text('port_tot_res'), f"{tot_res_val:,.1f} MMBN")
        with c2:
            st.metric(get_text('port_tot_prod'), f"{tot_prod_val:,.1f} BD")
        with c3:
            st.metric(get_text('port_avg_api'), f"{avg_api_val:,.1f}° API")
        with c4:
            avg_stariv = df['STARIV'].mean() if 'STARIV' in df.columns else 0
            st.metric(get_text('idx_stariv', "Índice STARIV"), f"{avg_stariv:.3f}")
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        # === MAP AND FILTERS (NEW ORDER: MAP FIRST) ===
        map_view_col, filter_tab_col = st.columns([3, 1])
        
        with filter_tab_col:
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
                    api_clean = pd.to_numeric(df[api_col], errors='coerce').dropna()
                    if not api_clean.empty:
                        min_api = float(api_clean.min())
                        max_api = float(api_clean.max())
                        if min_api < max_api:
                            sel_api = st.slider(get_text("filter_api"), min_api, max_api, (min_api, max_api))
                            df = df[(pd.to_numeric(df[api_col], errors='coerce') >= sel_api[0]) & (pd.to_numeric(df[api_col], errors='coerce') <= sel_api[1]) | df[api_col].isna()]
                
                if depth_col:
                    depth_clean = pd.to_numeric(df[depth_col], errors='coerce').dropna()
                    if not depth_clean.empty:
                        min_depth = float(depth_clean.min())
                        max_depth = float(depth_clean.max())
                        if min_depth < max_depth:
                            sel_depth = st.slider(get_text("filter_depth"), min_depth, max_depth, (min_depth, max_depth))
                            df = df[(pd.to_numeric(df[depth_col], errors='coerce') >= sel_depth[0]) & (pd.to_numeric(df[depth_col], errors='coerce') <= sel_depth[1]) | df[depth_col].isna()]
                        
                if dev_col:
                    dev_opts = df[dev_col].dropna().unique()
                    if len(dev_opts) > 0:
                        sel_dev = st.multiselect(get_text("filter_dev"), dev_opts, default=[])
                        if sel_dev:
                            df = df[df[dev_col].isin(sel_dev)]
                            
            with tab_risk:
                risk_col_name = 'Nivel de Riesgo'
                if risk_col_name in df.columns:
                    min_r = float(df[risk_col_name].min())
                    max_r = float(df[risk_col_name].max())
                    if min_r < max_r:
                        sel_risk = st.slider(get_text("idx_risk"), min_r, max_r, (min_r, max_r))
                        df = df[(df[risk_col_name] >= sel_risk[0]) & (df[risk_col_name] <= sel_risk[1])]

            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button(get_text('port_export'), use_container_width=True):
                st.info(get_text('port_export_msg'))
                
        with map_view_col:
            if 'Latitud' in df.columns and 'Longitud' in df.columns:
                df['Latitud'] = pd.to_numeric(df['Latitud'], errors='coerce')
                df['Longitud'] = pd.to_numeric(df['Longitud'], errors='coerce')
                map_df = df.dropna(subset=['Latitud', 'Longitud']).copy()
                
                if not map_df.empty:
                    if reserva_col:
                        map_df['radius'] = np.sqrt(pd.to_numeric(map_df[reserva_col], errors='coerce').fillna(1)) * 300
                    else:
                        map_df['radius'] = 1000
    
                    view_state = pdk.ViewState(
                        latitude=map_df['Latitud'].mean(),
                        longitude=map_df['Longitud'].mean(),
                        zoom=6.5,
                        pitch=0
                    )
                    
                    layer = pdk.Layer(
                        'ScatterplotLayer',
                        data=map_df,
                        get_position='[Longitud, Latitud]',
                        get_radius='radius',
                        get_fill_color='[0, 145, 255, 160]',
                        pickable=True,
                        auto_highlight=True
                    )
                    
                    st.pydeck_chart(pdk.Deck(
                        map_style='dark',
                        initial_view_state=view_state,
                        layers=[layer],
                        tooltip={"text": "{Campos}\nSTARIV: {STARIV}"}
                    ))
                else:
                    st.warning(get_text('port_no_coord'))
            else:
                st.warning(get_text('port_no_col_coord'))

        st.markdown("<hr/>", unsafe_allow_html=True)
        
        # === RANKING SECTION (STARIV) ===
        st.markdown(f"### 🏆 {get_text('scr_rank_title', 'Jerarquización de Campos (STARIV)')}")
        
        # Pre-calculate top fields
        ranking_df = df.sort_values('STARIV', ascending=False).head(15).copy()
        
        rank_col, graph_col = st.columns([1.5, 2.5])
        
        with rank_col:
            # Custom CSS for leaderboard
            st.markdown("""
            <style>
            .rank-item { padding: 10px; border-radius: 5px; margin-bottom: 5px; background: #1e2022; border-left: 5px solid #81cfff; }
            .rank-gold { border-left: 5px solid #ffd700; background: #2a2d30; }
            .rank-silver { border-left: 5px solid #c0c0c0; }
            .rank-bronze { border-left: 5px solid #cd7f32; }
            </style>
            """, unsafe_allow_html=True)
            
            for i, row in enumerate(ranking_df.itertuples()):
                cls = "rank-gold" if i==0 else "rank-silver" if i==1 else "rank-bronze" if i==2 else ""
                st.markdown(f"""
                <div class="rank-item {cls}">
                    <span style="font-weight:bold; color:#81cfff">#{i+1}</span> {row.Campos} <br/>
                    <small style="color:#b2b9c1">STARIV: <b>{row.STARIV:.4f}</b> | Riesgo: {row._29 if hasattr(row, 'Nivel_de_Riesgo') else row._11 if hasattr(row, 'Nivel de Riesgo') else 'N/A'}</small>
                </div>
                """, unsafe_allow_html=True)

        with graph_col:
            # Chart for STARIV Ranking
            import plotly.express as px
            fig = px.bar(
                ranking_df, 
                x='STARIV', 
                y=campo_col, 
                orientation='h',
                title=get_text('scr_rank_chart', "Ranking de Atractividad STARIV"),
                color='STARIV',
                color_continuous_scale='Blues',
                template='plotly_dark'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)


        st.markdown("<hr/>", unsafe_allow_html=True)
        # === MATRIX SECTION ===
        st.markdown(f"### {get_text('port_matrix')}")
        st.caption(get_text('port_matrix_cap'))
        
        display_cols = [c for c in [campo_col, area_col, 'STARIV', 'Nivel de Riesgo', reserva_col, prod_col, api_col, dev_col] if c in df.columns]
        if display_cols:
            display_df = translate_columns(df[display_cols].copy())
            
            numeric_cols = display_df.select_dtypes(include=['number']).columns
            style_dict = {col: "{:,.3f}" if 'STARIV' in str(col) else "{:,.2f}" for col in numeric_cols}
            
            styled_df = display_df.style.format(style_dict)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)


    else:
        st.warning(get_text('port_no_data'))
