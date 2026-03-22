import streamlit as st
import plotly.express as px
import pandas as pd
from src.i18n import get_text

def render_detail_risk(df):
    
    if df is not None and not df.empty:
        campo_col = next((c for c in df.columns if 'Campos' in c), 'Campos')
        if campo_col in df.columns:
            
            # Place the title and the selectbox natively to prevent UI squashing / cutting off
            st.markdown(f"## {get_text('rad_title')}")
            
            # Give the selectbox its own clear space at the top
            col1, col2 = st.columns([1, 2])
            with col1:
                selected_field = st.selectbox(get_text('rad_select'), df[campo_col].unique())
                
            field_data = df[df[campo_col] == selected_field].iloc[0]
            
            # --- Identify Data Columns ---
            prod_col = next((c for c in df.columns if 'Producción Actual' in c and 'Gas' not in c and 'Mpcd' not in c), None)
            api_col = next((c for c in df.columns if 'Gravedad API' in c or 'API' in c), None)
            reserva_col = next((c for c in df.columns if 'Petróleo equivalente' in c or 'Reserva' in c), None)
            
            # Additional Gas Columns
            prod_gas_col = next((c for c in df.columns if 'P. Actual Gas' in c or 'Gas' in c and 'Prod' in c or 'Mpcd' in c), None)
            grav_gas_col = next((c for c in df.columns if 'Gravedad Esp. Gas' in c), None)
            rgp_col = next((c for c in df.columns if 'RGP' in c), None)
            
            depth_col = next((c for c in df.columns if 'Profundidad' in c or 'plano' in c), None)
            perm_col = next((c for c in df.columns if 'Permeabilidad' in c or 'K (mD)' in c), None)
            poro_col = next((c for c in df.columns if 'Porosidad' in c), None)
            visc_col = next((c for c in df.columns if 'Viscosidad' in c), None)
            wells_col = next((c for c in df.columns if 'Categoría 2' in c or 'Categoria 2' in c or 'Pozos' in c), None)
            
            # --- Layout ---
            st.markdown("<br/>", unsafe_allow_html=True)
            left_col, right_col = st.columns([3, 2])
            
            with left_col:
                # Top 3 KPIs (Liquid / Equivalents)
                k1, k2, k3 = st.columns(3)
                
                v_prod = field_data.get(prod_col, 0)
                v_api = field_data.get(api_col, 0)
                v_res = field_data.get(reserva_col, 0)
                
                k1.markdown(f"""
                <div class="custom-card">
                    <div class="custom-card-label">{get_text('rad_kpi_prod')}</div>
                    <div class="custom-card-value">{float(v_prod):,.1f} <span class="custom-card-unit">BPD</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                k2.markdown(f"""
                <div class="custom-card">
                    <div class="custom-card-label">{get_text('rad_kpi_api')}</div>
                    <div class="custom-card-value">{float(v_api):,.1f} <span class="custom-card-unit">°</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                k3.markdown(f"""
                <div class="custom-card">
                    <div class="custom-card-label">{get_text('rad_kpi_res')}</div>
                    <div class="custom-card-value">{float(v_res):,.1f} <span class="custom-card-unit">MMBN</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
                
                # Bottom 3 KPIs (Gas Metrics)
                g1, g2, g3 = st.columns(3)
                
                v_gas_prod = field_data.get(prod_gas_col, 0) if prod_gas_col else 0
                v_gas_grav = field_data.get(grav_gas_col, 0) if grav_gas_col else 0
                v_rgp = field_data.get(rgp_col, 0) if rgp_col else 0
                
                g1.markdown(f"""
                <div class="custom-card">
                    <div class="custom-card-label">{get_text('rad_kpi_gas_prod')}</div>
                    <div class="custom-card-value">{float(v_gas_prod):,.1f} <span class="custom-card-unit">MPCD</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                g2.markdown(f"""
                <div class="custom-card">
                    <div class="custom-card-label">{get_text('rad_kpi_gas_grav')}</div>
                    <div class="custom-card-value">{float(v_gas_grav):,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                
                g3.markdown(f"""
                <div class="custom-card">
                    <div class="custom-card-label">{get_text('rad_kpi_rgp')}</div>
                    <div class="custom-card-value">{float(v_rgp):,.1f} <span class="custom-card-unit">pc/Bn</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("<br/>", unsafe_allow_html=True)
                
                # Tech Specs
                v_dep = field_data.get(depth_col, '-') if pd.notna(field_data.get(depth_col, '-')) else '-'
                v_per = field_data.get(perm_col, '-') if pd.notna(field_data.get(perm_col, '-')) else '-'
                v_por = field_data.get(poro_col, '-') if pd.notna(field_data.get(poro_col, '-')) else '-'
                v_vis = field_data.get(visc_col, '-') if pd.notna(field_data.get(visc_col, '-')) else '-'
                v_wel = field_data.get(wells_col, '-') if pd.notna(field_data.get(wells_col, '-')) else '-'
                
                # Format numbers if possible
                v_dep = f"{float(v_dep):,.1f}" if isinstance(v_dep, (int, float)) else v_dep
                v_per = f"{float(v_per):,.1f}" if isinstance(v_per, (int, float)) else v_per
                
                st.markdown(f"""
                <div class="custom-card">
                    <h5 style="color:white; margin-bottom: 20px;">⧉ {get_text('rad_specs_title')}</h5>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <div style="width: 25%;">
                            <div class="custom-card-label">{get_text('rad_ref_depth')}</div>
                            <div class="specs-val">{v_dep} <span class="custom-card-unit">ft</span></div>
                        </div>
                        <div style="width: 25%;">
                            <div class="custom-card-label">{get_text('rad_perm')}</div>
                            <div class="specs-val">{v_per} <span class="custom-card-unit">mD</span></div>
                        </div>
                        <div style="width: 25%;">
                            <div class="custom-card-label">{get_text('rad_poro')}</div>
                            <div class="specs-val">{v_por} <span class="custom-card-unit">%</span></div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <div style="width: 25%;">
                            <div class="custom-card-label">{get_text('rad_visc')}</div>
                            <div class="specs-val">{v_vis} <span class="custom-card-unit">cP</span></div>
                        </div>
                        <div style="width: 25%;">
                            <div class="custom-card-label">{get_text('rad_wells')}</div>
                            <div class="specs-val">{v_wel}</div>
                        </div>
                        <div style="width: 25%;">
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with right_col:
                st.markdown(f"""<div class="custom-card">
                    <div class="custom-card-label" style="font-size: 1rem; color:white; margin-bottom: 0px;">{get_text('rad_radar_title')}</div>
                    <div style="margin-top: -10px;">
                """, unsafe_allow_html=True)
                
                infra_val = field_data.get('Infra_Num', 1)
                inseg_val = field_data.get('Inseg_Num', 1)
                
                humano_col = next((c for c in df.columns if 'Humano' in c), None)
                humano_val = 1
                if humano_col:
                    v = str(field_data.get(humano_col, '')).lower()
                    if 'alta' in v: humano_val = 3
                    elif 'media' in v: humano_val = 2
                    elif 'baja' in v: humano_val = 1
                    
                vals = [infra_val, inseg_val, humano_val, infra_val]
                
                lang = st.session_state.get('language', 'Español')
                labels = ['Infraestructura', 'Seguridad', 'Talento Humano', 'Infraestructura'] if lang == 'Español' else ['Infrastructure', 'Security', 'Human Talent', 'Infrastructure']
                
                radar_df = pd.DataFrame(dict(r=vals, theta=labels))
                
                fig = px.line_polar(radar_df, r='r', theta='theta', line_close=True, range_r=[0, 3])
                fig.update_traces(fill='toself', fillcolor='rgba(0, 90, 156, 0.5)', line_color='#81cfff', line_width=4)
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0, 3], gridcolor='#333'),
                        angularaxis=dict(gridcolor='#333'),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#e2e2e5',
                    height=380,
                    margin=dict(l=30, r=30, t=30, b=30)
                )
                
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                st.markdown("</div></div>", unsafe_allow_html=True)
                
        else:
            st.error(get_text('rad_err'))
    else:
        st.warning(get_text('port_no_data'))
