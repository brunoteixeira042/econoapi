import streamlit as st
import pandas as pd
import altair as alt
import sys
import os
from datetime import datetime

# Add the project root to sys.path to allow absolute imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.collector import DataCollector
from app.database.bcb import BCBDataSource
from app.database.ibge import IBGEDataSource
from app.core.transformer import Transformer

# Page configuration
st.set_page_config(
    page_title="EconoAPI - Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    .main-header p {
        margin: 10px 0 0 0;
        font-size: 1.1rem;
        color: #b0bec5;
    }
    
    .metric-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    
    /* Responsive layout tweaks */
    .stMetric {
        background-color: #f8f9fa !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border-left: 5px solid #1e88e5 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    
    .stMetric [data-testid="stMetricLabel"] {
        color: #64748b !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Cache data loading to prevent hitting the APIs on every render
@st.cache_data(ttl=600)  # Cache for 10 minutes
def load_data():
    coletor = DataCollector()
    coletor.adicionar_fonte(BCBDataSource())
    coletor.adicionar_fonte(IBGEDataSource())
    
    try:
        selic_serie = coletor.coletar_por_nome('Banco do Brasil', '11')
    except Exception as e:
        st.error(f"Erro ao obter dados da SELIC: {e}")
        selic_serie = None
        
    try:
        ipca_serie = coletor.coletar_por_nome('IBGE', '1737')
    except Exception as e:
        st.error(f"Erro ao obter dados do IPCA: {e}")
        ipca_serie = None
        
    return selic_serie, ipca_serie

# Load the data
with st.spinner("Conectando às APIs do Banco Central e IBGE..."):
    selic_serie, ipca_serie = load_data()
    transformer = Transformer()

# Header
st.markdown("""
<div class="main-header">
    <h1>📈 EconoAPI Dashboard</h1>
    <p>Painel de Monitoramento de Indicadores Macroeconômicos em Tempo Real</p>
</div>
""", unsafe_allow_html=True)

# Check if we successfully loaded at least some data
if not selic_serie and not ipca_serie:
    st.error("Não foi possível carregar os dados de nenhuma fonte externa. Por favor, tente novamente mais tarde.")
    st.stop()

# Sidebar controls
st.sidebar.header("⚙️ Configurações & Filtros")

# Last updated timestamp
st.sidebar.caption(f"Dados atualizados em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# Select Source
selected_source = st.sidebar.selectbox(
    "Escolher Fonte de Dados",
    ["Todas as Fontes (Comparação)", "Banco do Brasil (SELIC)", "IBGE (IPCA)"]
)

# Filter by period
period_options = {
    "Últimos 3 meses": 90,
    "Últimos 6 meses": 180,
    "Último 1 ano": 365,
    "Todo o histórico": 9999
}
selected_period_label = st.sidebar.selectbox("Filtrar Período", list(period_options.keys()), index=2)
selected_days = period_options[selected_period_label]

# Real-time refresh button
if st.sidebar.button("🔄 Atualizar Dados em Tempo Real", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Processing SELIC data
if selic_serie:
    df_selic = selic_serie.to_dataframe()
    df_selic['data'] = pd.to_datetime(df_selic['data'], format='%d/%m/%Y')
    df_selic = df_selic.sort_values('data')
    
    # Filter by period
    cutoff_date = datetime.now() - pd.Timedelta(days=selected_days)
    df_selic_filtered = (df_selic[df_selic['data'] >= cutoff_date] if selected_days != 9999 else df_selic).copy()
    
    latest_selic = df_selic_filtered.iloc[-1]['valor'] if not df_selic_filtered.empty else 0.0
    prev_selic = df_selic_filtered.iloc[-2]['valor'] if len(df_selic_filtered) > 1 else latest_selic
    selic_diff = latest_selic - prev_selic
    
    # Calculate average on filtered data using our transformer
    selic_filtered_serie = selic_serie
    if selected_days != 9999:
        filtered_dados = df_selic_filtered.copy()
        filtered_dados['data'] = filtered_dados['data'].dt.strftime('%d/%m/%Y')
        selic_filtered_serie = selic_serie.__class__(
            codigo=selic_serie.codigo,
            nome=selic_serie.nome,
            dados=filtered_dados.to_dict('records'),
            total_registros=len(filtered_dados)
        )
    selic_avg = transformer.calcular_media(selic_filtered_serie)

    # Group by month for a monthly bar chart
    if not df_selic_filtered.empty:
        df_selic_monthly = df_selic_filtered.copy()
        df_selic_monthly['periodo'] = df_selic_monthly['data'].dt.strftime('%m/%Y')
        df_selic_monthly['ano_mes'] = df_selic_monthly['data'].dt.to_period('M')
        df_selic_grouped = df_selic_monthly.groupby(['ano_mes', 'periodo'])['valor'].mean().reset_index()
        df_selic_grouped = df_selic_grouped.sort_values('ano_mes')
    else:
        df_selic_grouped = pd.DataFrame()
else:
    latest_selic, selic_diff, selic_avg = 0.0, 0.0, 0.0
    df_selic_grouped = pd.DataFrame()

# Processing IPCA data
if ipca_serie:
    df_ipca = ipca_serie.to_dataframe()
    # Format: YYYY-MM
    df_ipca['data'] = pd.to_datetime(df_ipca['data'] + '-01', format='%Y-%m-%d')
    df_ipca = df_ipca.sort_values('data')
    
    # Filter by period
    cutoff_date = datetime.now() - pd.Timedelta(days=selected_days)
    df_ipca_filtered = (df_ipca[df_ipca['data'] >= cutoff_date] if selected_days != 9999 else df_ipca).copy()
    if not df_ipca_filtered.empty:
        df_ipca_filtered['periodo'] = df_ipca_filtered['data'].dt.strftime('%m/%Y')
    
    latest_ipca = df_ipca_filtered.iloc[-1]['valor'] if not df_ipca_filtered.empty else 0.0
    prev_ipca = df_ipca_filtered.iloc[-2]['valor'] if len(df_ipca_filtered) > 1 else latest_ipca
    ipca_diff = latest_ipca - prev_ipca
    
    # Calculate average on filtered data
    ipca_filtered_serie = ipca_serie
    if selected_days != 9999:
        filtered_dados = df_ipca_filtered.copy()
        filtered_dados['data'] = filtered_dados['data'].dt.strftime('%Y-%m')
        ipca_filtered_serie = ipca_serie.__class__(
            codigo=ipca_serie.codigo,
            nome=ipca_serie.nome,
            dados=filtered_dados.to_dict('records'),
            total_registros=len(filtered_dados)
        )
    ipca_avg = transformer.calcular_media(ipca_filtered_serie)
else:
    latest_ipca, ipca_diff, ipca_avg = 0.0, 0.0, 0.0


# Main Dashboard Area

# 1. KPIs Section
st.subheader("📊 Principais Indicadores")

# Legenda dinâmica dos indicadores
legend_text = "💡 **O que medem estes indicadores:**\n\n"
if selected_source == "Banco do Brasil (SELIC)":
    legend_text += (
        "* **Última SELIC (a.d. diária):** Taxa de juros diária divulgada pelo Banco Central do Brasil, representando a taxa média ponderada das operações de financiamento por 1 dia.\n"
        "* **SELIC Média no Período:** Média aritmética simples de todas as taxas SELIC registradas no intervalo de tempo selecionado."
    )
elif selected_source == "IBGE (IPCA)":
    legend_text += (
        "* **Último IPCA (Mensal):** Índice de Preços ao Consumidor Amplo (Inflação Oficial), calculado pelo IBGE, que indica a variação percentual dos preços de bens e serviços de um mês para o outro.\n"
        "* **IPCA Médio no Período:** Média aritmética simples das taxas de inflação mensais no intervalo selecionado."
    )
else:  # Todas as Fontes
    legend_text += (
        "* **Última SELIC (a.d. diária):** Taxa de juros diária divulgada pelo Banco Central do Brasil, representando a taxa média ponderada das operações de financiamento por 1 dia.\n"
        "* **SELIC Média no Período:** Média aritmética simples das taxas SELIC diárias no intervalo selecionado.\n"
        "* **Último IPCA (Mensal):** Variação mensal do Índice de Preços ao Consumidor Amplo (IPCA), calculado pelo IBGE, representando a inflação oficial do país.\n"
        "* **IPCA Médio no Período:** Média das taxas de inflação mensais no intervalo selecionado."
    )
st.info(legend_text)

if selected_source == "Banco do Brasil (SELIC)":
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Última SELIC (a.d. diária)",
            value=f"{latest_selic:.4f}%",
            delta=f"{selic_diff:.4f}%" if selic_diff != 0 else None,
            help="Taxa diária SELIC obtida do Banco Central do Brasil."
        )
    with col2:
        st.metric(
            label="SELIC Média no Período",
            value=f"{selic_avg:.4f}%",
            help="Média simples da taxa SELIC diária no período filtrado."
        )

elif selected_source == "IBGE (IPCA)":
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="Último IPCA (Mensal)",
            value=f"{latest_ipca:+.2f}%",
            delta=f"{ipca_diff:+.2f}%" if ipca_diff != 0 else None,
            help="Índice Nacional de Preços ao Consumidor Amplo (IPCA) obtido do IBGE."
        )
    with col2:
        st.metric(
            label="IPCA Médio no Período",
            value=f"{ipca_avg:+.2f}%",
            help="Média simples da inflação mensal do IPCA no período filtrado."
        )

else:  # "Todas as Fontes (Comparação)"
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            label="Última SELIC (a.d. diária)",
            value=f"{latest_selic:.4f}%",
            delta=f"{selic_diff:.4f}%" if selic_diff != 0 else None,
            help="Taxa diária SELIC obtida do Banco Central do Brasil."
        )
    with col2:
        st.metric(
            label="SELIC Média no Período",
            value=f"{selic_avg:.4f}%",
            help="Média simples da taxa SELIC diária no período filtrado."
        )
    with col3:
        st.metric(
            label="Último IPCA (Mensal)",
            value=f"{latest_ipca:+.2f}%",
            delta=f"{ipca_diff:+.2f}%" if ipca_diff != 0 else None,
            help="Índice Nacional de Preços ao Consumidor Amplo (IPCA) obtido do IBGE."
        )
    with col4:
        st.metric(
            label="IPCA Médio no Período",
            value=f"{ipca_avg:+.2f}%",
            help="Média simples da inflação mensal do IPCA no período filtrado."
        )

st.markdown("---")

# 2. Charts Section
st.subheader("📈 Análise Gráfica")

if selected_source == "Banco do Brasil (SELIC)":
    if selic_serie and not df_selic_filtered.empty:
        st.markdown("### Evolução Diária da Taxa SELIC (Linha)")
        st.line_chart(
            df_selic_filtered,
            x='data',
            y='valor',
            color='#1e88e5',
            x_label='Data',
            y_label='Taxa (%)',
            height=300
        )
        
        st.markdown("### Média Mensal da Taxa SELIC (Barras)")
        st.bar_chart(
            df_selic_grouped,
            x='periodo',
            y='valor',
            color='#1769aa',
            x_label='Mês/Ano',
            y_label='Taxa Média (%)',
            height=300
        )
    else:
        st.info("Dados da SELIC não disponíveis para o gráfico.")

elif selected_source == "IBGE (IPCA)":
    if ipca_serie and not df_ipca_filtered.empty:
        st.markdown("### Variação Mensal do IPCA (Inflação %)")
        st.bar_chart(
            df_ipca_filtered,
            x='periodo',
            y='valor',
            color='#26a69a',
            x_label='Mês/Ano',
            y_label='Variação (%)',
            height=400
        )
    else:
        st.info("Dados do IPCA não disponíveis para o gráfico.")

else:  # "Todas as Fontes (Comparação)"
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        if selic_serie and not df_selic_grouped.empty:
            st.markdown("### Média Mensal da Taxa SELIC")
            st.bar_chart(
                df_selic_grouped,
                x='periodo',
                y='valor',
                color='#1769aa',
                x_label='Mês/Ano',
                y_label='Taxa Média (%)',
                height=350
            )
        else:
            st.info("Dados da SELIC não disponíveis para o gráfico.")

    with chart_col2:
        if ipca_serie and not df_ipca_filtered.empty:
            st.markdown("### Variação Mensal do IPCA (Inflação %)")
            st.bar_chart(
                df_ipca_filtered,
                x='periodo',
                y='valor',
                color='#26a69a',
                x_label='Mês/Ano',
                y_label='Variação (%)',
                height=350
            )
        else:
            st.info("Dados do IPCA não disponíveis para o gráfico.")

st.markdown("---")

# 3. Data Explorer Section
st.subheader("🗂️ Explorador de Dados Históricos")

if selected_source == "Banco do Brasil (SELIC)":
    if selic_serie:
        df_selic_display = df_selic_filtered.copy()
        df_selic_display['data'] = df_selic_display['data'].dt.strftime('%d/%m/%Y')
        st.write("### Série Histórica da Taxa SELIC (Banco Central)")
        st.dataframe(df_selic_display.sort_values('data', ascending=False), width="stretch")
        csv_selic = df_selic_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Baixar SELIC em CSV",
            data=csv_selic,
            file_name=f"selic_historico_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado da SELIC disponível.")

elif selected_source == "IBGE (IPCA)":
    if ipca_serie:
        df_ipca_display = df_ipca_filtered.copy()
        df_ipca_display['data'] = df_ipca_display['data'].dt.strftime('%m/%Y')
        st.write("### Série Histórica do IPCA (IBGE)")
        st.dataframe(df_ipca_display.sort_values('data', ascending=False), width="stretch")
        csv_ipca = df_ipca_display.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Baixar IPCA em CSV",
            data=csv_ipca,
            file_name=f"ipca_historico_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhum dado do IPCA disponível.")

else:  # "Todas as Fontes (Comparação)"
    expander = st.expander("Clique para expandir as tabelas de dados brutos e baixar relatórios")
    with expander:
        tab1, tab2 = st.tabs(["Série SELIC (Banco Central)", "Série IPCA (IBGE)"])
        
        with tab1:
            if selic_serie:
                df_selic_display = df_selic_filtered.copy()
                df_selic_display['data'] = df_selic_display['data'].dt.strftime('%d/%m/%Y')
                st.dataframe(df_selic_display.sort_values('data', ascending=False), width="stretch")
                
                # Download button
                csv_selic = df_selic_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Baixar SELIC em CSV",
                    data=csv_selic,
                    file_name=f"selic_historico_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.write("Nenhum dado disponível.")
                
        with tab2:
            if ipca_serie:
                df_ipca_display = df_ipca_filtered.copy()
                df_ipca_display['data'] = df_ipca_display['data'].dt.strftime('%m/%Y')
                st.dataframe(df_ipca_display.sort_values('data', ascending=False), width="stretch")
                
                # Download button
                csv_ipca = df_ipca_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="⬇️ Baixar IPCA em CSV",
                    data=csv_ipca,
                    file_name=f"ipca_historico_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.write("Nenhum dado disponível.")

# Footer
st.markdown("""
<div style="text-align: center; color: #78909c; padding: 20px; font-size: 0.9rem;">
    EconoAPI Dashboard • Desenvolvido com Streamlit e Python • Dados obtidos das APIs públicas oficiais do BCB e IBGE.
</div>
""", unsafe_allow_html=True)
