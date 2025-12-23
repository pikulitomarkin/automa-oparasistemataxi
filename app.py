"""
Streamlit Dashboard for Taxi Automation System.
Central de Rádio - Monitoramento Operacional.
Tema: Liquid iPhone - Premium UI/UX
"""
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from src.services.database import DatabaseManager
from src.models import OrderStatus

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Central Táxi - Monitoramento",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Tema Liquid iPhone com Glassmorphism
st.markdown("""
<style>
    /* Tema geral mais claro */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* Sidebar mais clara */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Métricas com visual moderno */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    [data-testid="stMetric"] label {
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 32px !important;
        font-weight: 700 !important;
    }
    
    /* Cards de conteúdo */
    .element-container {
        color: #2c3e50;
    }
    
    /* Títulos mais visíveis */
    h1 {
        color: #1a1a1a !important;
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        margin-bottom: 2rem !important;
    }
    
    h2 {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 1.8rem !important;
    }
    
    h3 {
        color: #34495e !important;
        font-weight: 600 !important;
        font-size: 1.4rem !important;
    }
    
    /* Tabs mais modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f8f9fa;
        border-radius: 8px;
        color: #2c3e50;
        font-weight: 600;
        padding: 0 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Tabelas mais legíveis */
    .dataframe {
        font-size: 14px !important;
        color: #2c3e50 !important;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 12px !important;
    }
    
    .dataframe tbody tr {
        background-color: #ffffff;
    }
    
    .dataframe tbody tr:hover {
        background-color: #f0f2f6 !important;
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0,0,0,0.15);
    }
    
    /* Select boxes mais claros */
    .stSelectbox, .stMultiSelect {
        color: #2c3e50 !important;
    }
    
    /* Info/Warning boxes */
    .stInfo, .stWarning {
        background-color: #ffffff !important;
        border-left: 4px solid #667eea !important;
        color: #2c3e50 !important;
        padding: 1rem !important;
        border-radius: 8px !important;
    }
    
    /* Expander mais visível */
    .streamlit-expanderHeader {
        background-color: #ffffff !important;
        color: #2c3e50 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_manager():
    """Retorna instância do DatabaseManager (cached)."""
    return DatabaseManager(os.getenv('DATABASE_PATH', 'data/taxi_orders.db'))


def format_datetime(dt):
    """Formata datetime para exibição."""
    if dt is None:
        return "-"
    return dt.strftime("%d/%m/%Y %H:%M")


def create_map(orders):
    """
    Cria mapa com marcadores dos pontos de coleta.
    
    Args:
        orders: Lista de orders com coordenadas.
        
    Returns:
        Objeto folium.Map.
    """
    # Centro padrão: Belo Horizonte
    center_lat = -19.9191
    center_lng = -43.9386
    
    # Se há pedidos, centraliza no primeiro
    if orders and orders[0].pickup_lat:
        center_lat = orders[0].pickup_lat
        center_lng = orders[0].pickup_lng
    
    # Cria mapa
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=12,
        tiles="OpenStreetMap"
    )
    
    # Adiciona marcadores
    for order in orders:
        if order.pickup_lat and order.pickup_lng:
            # Cor baseada no status
            color = {
                OrderStatus.DISPATCHED: 'green',
                OrderStatus.GEOCODED: 'blue',
                OrderStatus.FAILED: 'red',
                OrderStatus.MANUAL_REVIEW: 'orange'
            }.get(order.status, 'gray')
            
            # Popup com informações
            popup_html = f"""
            <b>Pedido #{order.id}</b><br>
            <b>Passageiro:</b> {order.passenger_name}<br>
            <b>Telefone:</b> {order.phone}<br>
            <b>Endereço:</b> {order.pickup_address}<br>
            <b>Horário:</b> {format_datetime(order.pickup_time)}<br>
            <b>Status:</b> {order.status.value}
            """
            
            folium.Marker(
                location=[order.pickup_lat, order.pickup_lng],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color, icon='taxi', prefix='fa')
            ).add_to(m)
    
    return m


def main():
    """Função principal do dashboard."""
    
    # Header moderno
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='margin: 0;'>🚕 Central de Táxi - Monitoramento Operacional</h1>
            <p style='color: #7f8c8d; font-size: 1.1rem; margin-top: 0.5rem;'>
                Sistema de automação inteligente de pedidos
            </p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<hr style='margin: 2rem 0; border: none; height: 2px; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);'>", unsafe_allow_html=True)
    
    # Sidebar com estilo moderno
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h2 style='color: #2c3e50; margin: 0;'>⚙️ Painel de Controle</h2>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr style='margin: 1rem 0;'>", unsafe_allow_html=True)
        
        # Filtro de data
        st.markdown("##### 📅 Período")
        date_range = st.selectbox(
            "Selecione o período",
            ["Últimas 24h", "Últimos 7 dias", "Últimos 30 dias", "Todos"],
            index=1,
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Filtro de status
        st.markdown("##### 🏷️ Status dos Pedidos")
        status_filter = st.multiselect(
            "Filtrar por status",
            [s.value for s in OrderStatus],
            default=[OrderStatus.DISPATCHED.value, OrderStatus.FAILED.value],
            label_visibility="collapsed"
        )
        
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        
        # Botão de atualização
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔄 Atualizar", type="primary", use_container_width=True):
                st.cache_resource.clear()
                st.rerun()
        
        st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0; color: #7f8c8d;'>
                <p style='margin: 0; font-size: 0.9rem;'>Sistema de Automação de Táxi</p>
                <p style='margin: 0; font-size: 0.8rem;'>v1.0.0</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Carrega dados
    db = get_db_manager()
    
    # Estatísticas gerais
    stats = db.get_statistics()
    
    # Métricas principais com gradientes diferentes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;'>Total de Pedidos</p>
                <h2 style='color: white; font-size: 2.5rem; margin: 0.5rem 0 0 0;'>{}</h2>
            </div>
        """.format(stats['total']), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div style='background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;'>✅ Despachados</p>
                <h2 style='color: white; font-size: 2.5rem; margin: 0.5rem 0 0 0;'>{}</h2>
            </div>
        """.format(stats.get(OrderStatus.DISPATCHED.value, 0)), unsafe_allow_html=True)
    
    with col3:
        falhas = stats.get(OrderStatus.FAILED.value, 0) + stats.get(OrderStatus.MANUAL_REVIEW.value, 0)
        st.markdown("""
            <div style='background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;'>❌ Falhas</p>
                <h2 style='color: white; font-size: 2.5rem; margin: 0.5rem 0 0 0;'>{}</h2>
            </div>
        """.format(falhas), unsafe_allow_html=True)
    
    with col4:
        success_rate = 0
        if stats['total'] > 0:
            success_rate = (stats.get(OrderStatus.DISPATCHED.value, 0) / stats['total']) * 100
        st.markdown("""
            <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                        padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                <p style='color: rgba(255,255,255,0.8); font-size: 0.9rem; margin: 0;'>Taxa de Sucesso</p>
                <h2 style='color: white; font-size: 2.5rem; margin: 0.5rem 0 0 0;'>{:.1f}%</h2>
            </div>
        """.format(success_rate), unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Tabs principais
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🗺️ Mapa", "📋 Detalhes"])
    
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        # Gráfico de pizza - Status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                            box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
                    <h3 style='color: #2c3e50; margin-top: 0;'>📊 Distribuição por Status</h3>
                </div>
            """, unsafe_allow_html=True)
            
            status_data = {k: v for k, v in stats.items() if k != 'total' and v > 0}
            
            if status_data:
                fig = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#2c3e50', size=14)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Nenhum dado disponível ainda.")
        
        with col2:
            st.markdown("""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                            box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
                    <h3 style='color: #2c3e50; margin-top: 0;'>📈 Timeline de Pedidos</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Busca pedidos recentes
            orders = db.get_all_orders(limit=50)
            
            if orders:
                # Cria DataFrame para timeline
                df = pd.DataFrame([{
                    'Data': o.created_at,
                    'Status': o.status.value,
                    'Passageiro': o.passenger_name
                } for o in orders])
                
                # Conta por dia
                df['Data'] = pd.to_datetime(df['Data']).dt.date
                timeline = df.groupby('Data').size().reset_index(name='Pedidos')
                
                fig = px.line(
                    timeline,
                    x='Data',
                    y='Pedidos',
                    markers=True
                )
                fig.update_traces(
                    line_color='#667eea',
                    line_width=3,
                    marker=dict(size=8, color='#764ba2')
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#2c3e50', size=14),
                    xaxis=dict(showgrid=True, gridcolor='#e0e0e0'),
                    yaxis=dict(showgrid=True, gridcolor='#e0e0e0')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Nenhum pedido ainda.")
    
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
                <h3 style='color: #2c3e50; margin-top: 0;'>🗺️ Mapa de Coletas</h3>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Busca pedidos com coordenadas
        all_orders = db.get_all_orders(limit=100)
        
        # Filtra por status selecionado
        if status_filter:
            filtered_orders = [
                o for o in all_orders 
                if o.status.value in status_filter and o.pickup_lat
            ]
        else:
            filtered_orders = [o for o in all_orders if o.pickup_lat]
        
        if filtered_orders:
            st.info(f"Exibindo {len(filtered_orders)} pedidos no mapa")
            map_obj = create_map(filtered_orders)
            folium_static(map_obj, width=1200, height=600)
        else:
            st.warning("Nenhum pedido com coordenadas para exibir no mapa.")
    
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
                <h3 style='color: #2c3e50; margin-top: 0;'>📋 Lista Detalhada de Pedidos</h3>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Seletor de visualização
        view_option = st.radio(
            "Visualizar:",
            ["Todos", "Despachados", "Falhas", "Revisão Manual"],
            horizontal=True
        )
        
        # Busca pedidos baseado na seleção
        if view_option == "Todos":
            orders = db.get_all_orders(limit=100)
        elif view_option == "Despachados":
            orders = db.get_orders_by_status(OrderStatus.DISPATCHED)
        elif view_option == "Falhas":
            orders = db.get_orders_by_status(OrderStatus.FAILED)
        else:
            orders = db.get_orders_by_status(OrderStatus.MANUAL_REVIEW)
        
        if orders:
            # Cria DataFrame
            df = pd.DataFrame([{
                'ID': o.id,
                'Passageiro': o.passenger_name,
                'Telefone': o.phone,
                'Endereço Coleta': o.pickup_address,
                'Horário': format_datetime(o.pickup_time),
                'Status': o.status.value,
                'Criado em': format_datetime(o.created_at),
                'Erro': o.error_message if o.error_message else '-'
            } for o in orders])
            
            # Estilo da tabela
            st.markdown("<br>", unsafe_allow_html=True)
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Botões de ação
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Baixar CSV",
                    csv,
                    "pedidos_taxi.csv",
                    "text/csv",
                    key='download-csv',
                    use_container_width=True
                )
        else:
            st.info("📭 Nenhum pedido encontrado para esta categoria.")
    
    # Espaçamento
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Informações adicionais em cards modernos
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("ℹ️ Legenda de Status", expanded=False):
            st.markdown("""
            <div style='background: white; padding: 1rem; border-radius: 8px;'>
                <p style='color: #2c3e50; margin: 0.5rem 0;'><strong>received:</strong> E-mail recebido, aguardando processamento</p>
                <p style='color: #2c3e50; margin: 0.5rem 0;'><strong>extracted:</strong> Dados extraídos com sucesso pela IA</p>
                <p style='color: #2c3e50; margin: 0.5rem 0;'><strong>geocoded:</strong> Endereços convertidos em coordenadas</p>
                <p style='color: #11998e; margin: 0.5rem 0;'><strong>✅ dispatched:</strong> Pedido enviado com sucesso para MinasTaxi</p>
                <p style='color: #ee0979; margin: 0.5rem 0;'><strong>❌ failed:</strong> Falha no envio para API</p>
                <p style='color: #ff6a00; margin: 0.5rem 0;'><strong>⚠️ manual_review:</strong> Requer atenção manual (erro na extração/geocoding)</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.expander("🔧 Ações Administrativas", expanded=False):
            st.markdown("""
            <div style='background: white; padding: 1rem; border-radius: 8px;'>
                <p style='color: #e74c3c; margin-bottom: 1rem;'><strong>⚠️ Esta seção é para administradores do sistema.</strong></p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("♻️ Reprocessar Pedidos Falhados", use_container_width=True):
                st.info("🔄 Funcionalidade em desenvolvimento - integrar com processor.reprocess_failed_orders()")
    
    # Footer moderno
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; border-top: 2px solid #e0e0e0;'>
            <p style='color: #7f8c8d; margin: 0;'>
                Desenvolvido com ❤️ para automação inteligente de táxi
            </p>
            <p style='color: #95a5a6; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>
                © 2025 Sistema de Automação de Táxi v1.0
            </p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
