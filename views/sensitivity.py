import streamlit as st
import plotly.express as px
import pandas as pd
from src.i18n import get_text

def render_sensitivity(df):
    st.markdown(f"## {get_text('sen_title')}")
    st.markdown(get_text('sen_desc'))
    
    if df is not None and not df.empty:
        x_col_default = next((c for c in df.columns if 'Liviano' in c), None)
        y_col_default = next((c for c in df.columns if 'Producción Actual' in c), None)
        campo_col = next((c for c in df.columns if 'Campos' in c), None)
        
        numeric_cols = sorted(df.select_dtypes(include=['number']).columns.tolist())
        
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            
            idx_x = numeric_cols.index(x_col_default) if x_col_default in numeric_cols else 0
            idx_y = numeric_cols.index(y_col_default) if y_col_default in numeric_cols else 1
            
            x_col = col1.selectbox(get_text('sen_x'), numeric_cols, index=idx_x)
            y_col = col2.selectbox(get_text('sen_y'), numeric_cols, index=idx_y)
            
            plot_df = df.dropna(subset=[x_col, y_col]).copy()
            
            # Bubble Size handling based on STARIV
            score_col = 'STARIV' if 'STARIV' in plot_df.columns else 'Score de Atractividad'
            if score_col in plot_df.columns:
                # size must be strictly positive for Plotly size parameter
                plot_df['bubble_size'] = pd.to_numeric(plot_df[score_col], errors='coerce').fillna(1).apply(lambda x: max(0.5, float(x)))
            else:
                plot_df['bubble_size'] = 1
                
            fig = px.scatter(
                plot_df, x=x_col, y=y_col, hover_name=campo_col, 
                color=score_col, color_continuous_scale='Blues',
                size='bubble_size', size_max=40,
                opacity=0.8,
                template='plotly_dark'
            )

            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e2e5',
                xaxis=dict(gridcolor='#333'),
                yaxis=dict(gridcolor='#333')
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning(get_text('sen_err'))
