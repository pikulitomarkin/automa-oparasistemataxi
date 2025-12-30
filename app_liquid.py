"""
Streamlit Dashboard - Taxi Automation System
Tema: Liquid iPhone - Premium UI/UX
"""
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from src.services.database import DatabaseManager
from src.models import OrderStatus

load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Central Táxi - Liquid Theme",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS - Tema Liquid iPhone Premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* Background líquido animado */
    .stApp {
        background: linear-gradient(135deg, 
            #667eea 0%, #764ba2 25%, #f093fb 50%, 
            #4facfe 75%, #00f2fe 100%);
        background-size: 400% 400%;
        animation: liquidFlow 15s ease infinite;
    }
    
    @keyframes liquidFlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Esconder sidebar completamente */
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"],
    button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
    }
    
    /* Main content */
    .main .block-container {
        padding: 2rem 3rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Títulos e textos */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }
    
    /* Tabs - Liquid Navigation */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 20px;
        backdrop-filter: blur(20px);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 12px 28px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4)) !important;
        border: 1px solid rgba(255, 255, 255, 0.4) !important;
        color: #ffffff !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    
    /* Cards de Métricas - Liquid Glass */
    [data-testid="stMetricValue"] {
        font-size: 3rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1rem !important;
        font-weight: 600 !important;
        color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 1rem !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.6), rgba(118, 75, 162, 0.6));
        border-radius: 10px;
    }
    
    /* Inputs com tema Liquid */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 16px !important;
        color: white !important;
    }
    
    /* Botões com tema premium */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
        color: white !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_manager():
    """Inicializa o gerenciador de banco de dados."""
    return DatabaseManager(os.getenv('DATABASE_PATH', 'data/taxi_orders.db'))


def format_datetime(dt):
    """Formata datetime para exibição."""
    if dt is None:
        return "-"
    return dt.strftime("%d/%m/%Y %H:%M")


def create_map(orders):
    """Cria mapa interativo com marcadores de pedidos."""
    center_lat, center_lng = -19.9191, -43.9386
    if orders and orders[0].pickup_lat:
        center_lat, center_lng = orders[0].pickup_lat, orders[0].pickup_lng
    
    m = folium.Map(location=[center_lat, center_lng], zoom_start=12)
    
    for order in orders:
        if order.pickup_lat and order.pickup_lng:
            color = {
                OrderStatus.DISPATCHED: 'green',
                OrderStatus.GEOCODED: 'blue',
                OrderStatus.FAILED: 'red',
                OrderStatus.MANUAL_REVIEW: 'orange'
            }.get(order.status, 'gray')
            
            popup_html = f"""
            <b>Pedido #{order.id}</b><br>
            <b>Passageiro:</b> {order.passenger_name}<br>
            <b>Telefone:</b> {order.phone}<br>
            <b>Endereço:</b> {order.pickup_address}<br>
            <b>Horário:</b> {format_datetime(order.pickup_time)}<br>
            <b>Status:</b> {order.status.value}
            """
            
            folium.Marker(
                [order.pickup_lat, order.pickup_lng],
                popup=folium.Popup(popup_html, max_width=300),
                icon=folium.Icon(color=color, icon='taxi', prefix='fa')
            ).add_to(m)
    
    return m


def render_header():
    """Renderiza o cabeçalho premium da aplicação com filtros integrados."""
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); 
                    border-radius: 28px; padding: 2.5rem 2.5rem 1.5rem 2.5rem; margin-bottom: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);'>
            <div style='text-align: center; margin-bottom: 2rem;'>
                <h1 style='font-size: 3rem; font-weight: 800; margin: 0;
                           background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
                           -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                           letter-spacing: -1px;'>
                    🚕 Central de Táxi - Monitoramento Operacional
                </h1>
                <p style='color: rgba(255, 255, 255, 0.9); font-size: 1.2rem; 
                          margin-top: 0.75rem; font-weight: 400;'>
                    Sistema de automação inteligente de pedidos
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Painel de Controle Premium
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(15px); 
                    border-radius: 24px; padding: 1.5rem 2rem 0.5rem 2rem; margin-bottom: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.15);'>
            <h3 style='color: white; font-size: 1.3rem; font-weight: 700; margin: 0 0 1.2rem 0;'>
                ⚙️ Painel de Controle
            </h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Filtros em colunas
    col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
    
    with col1:
        date_range = st.selectbox(
            "📅 Período",
            ["Últimas 24h", "Últimos 7 dias", "Últimos 30 dias", "Todos"],
            index=1,
            key="date_filter"
        )
    
    with col2:
        status_filter = st.multiselect(
            "🏷️ Status dos Pedidos",
            [s.value for s in OrderStatus],
            default=[OrderStatus.DISPATCHED.value, OrderStatus.FAILED.value],
            key="status_filter"
        )
    
    with col3:
        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
        refresh_btn = st.button("🔄 Atualizar Dados", type="primary", width='stretch')
    
    with col4:
        st.markdown("""
            <div style='text-align: center; padding-top: 8px;'>
                <p style='color: rgba(255,255,255,0.7); font-size: 0.85rem; margin: 0;'>Sistema</p>
                <p style='color: white; font-weight: 600; margin: 0;'>v1.0.0</p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
    
    return date_range, status_filter, refresh_btn



def render_kpi_cards(stats):
    """Renderiza os cards de KPI."""
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcula taxa de sucesso
    total = stats.get('total', 0)
    dispatched = stats.get(OrderStatus.DISPATCHED.value, 0)
    success_rate = (dispatched / total * 100) if total > 0 else 0.0
    
    cards = [
        {
            'col': col1,
            'title': '📊 Total de Pedidos',
            'value': total,
            'gradient': 'linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3))'
        },
        {
            'col': col2,
            'title': '✅ Despachados',
            'value': dispatched,
            'gradient': 'linear-gradient(135deg, rgba(17, 153, 142, 0.3), rgba(56, 239, 125, 0.3))'
        },
        {
            'col': col3,
            'title': '❌ Falhas',
            'value': stats.get(OrderStatus.FAILED.value, 0),
            'gradient': 'linear-gradient(135deg, rgba(234, 82, 111, 0.3), rgba(255, 89, 94, 0.3))'
        },
        {
            'col': col4,
            'title': '📈 Taxa de Sucesso',
            'value': f"{success_rate:.1f}%",
            'gradient': 'linear-gradient(135deg, rgba(240, 147, 251, 0.3), rgba(245, 87, 108, 0.3))'
        }
    ]
    
    for card in cards:
        with card['col']:
            st.markdown(f"""
                <div style='background: {card['gradient']}; 
                            backdrop-filter: blur(20px);
                            border-radius: 24px; 
                            padding: 2rem 1.5rem;
                            border: 1px solid rgba(255, 255, 255, 0.2);
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                            min-height: 180px;
                            display: flex;
                            flex-direction: column;
                            justify-content: center;'>
                    <p style='margin: 0; font-size: 1rem; font-weight: 600; 
                              color: rgba(255, 255, 255, 0.9); margin-bottom: 1rem;'>
                        {card['title']}
                    </p>
                    <p style='margin: 0; font-size: 3rem; font-weight: 800; 
                              color: #ffffff;'>
                        {card['value']}
                    </p>
                </div>
            """, unsafe_allow_html=True)


def main():
    """Função principal da aplicação."""
    
    # Renderiza header premium com filtros integrados
    date_range, status_filter, refresh_btn = render_header()
    
    # Atualiza cache se botão pressionado
    if refresh_btn:
        st.cache_resource.clear()
        st.rerun()
    
    # Database
    db = get_db_manager()
    stats = db.get_statistics()
    
    # KPI Cards
    render_kpi_cards(stats)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs de navegação
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🗺️ Mapa", "📋 Detalhes"])
    
    with tab1:
        st.markdown("### 📈 Distribuição de Status")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Gráfico de pizza
            if stats['total'] > 0:
                status_data = {k: v for k, v in stats.items() if k not in ['total', 'success_rate']}
                fig = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    title="Status dos Pedidos",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=14)
                )
                st.plotly_chart(fig, width='stretch')
            else:
                st.info("📭 Nenhum pedido encontrado")
        
        with col2:
            # Timeline (placeholder)
            st.markdown("#### ⏱️ Timeline Recente")
            orders = db.get_all_orders(limit=10)
            
            if orders:
                for order in orders[:5]:
                    status_color = {
                        OrderStatus.DISPATCHED: '#10B981',
                        OrderStatus.FAILED: '#EF4444',
                        OrderStatus.GEOCODED: '#3B82F6',
                        OrderStatus.MANUAL_REVIEW: '#F59E0B'
                    }.get(order.status, '#6B7280')
                    
                    st.markdown(f"""
                        <div style='background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);
                                    border-left: 4px solid {status_color};
                                    padding: 1rem; margin-bottom: 0.5rem; border-radius: 12px;'>
                            <p style='margin: 0; color: white; font-weight: 600;'>{order.passenger_name}</p>
                            <p style='margin: 0; color: rgba(255,255,255,0.7); font-size: 0.9rem;'>
                                {format_datetime(order.created_at)} - {order.status.value}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📭 Nenhum pedido recente")
    
    with tab2:
        st.markdown("### 🗺️ Mapa de Coletas")
        
        orders = db.get_all_orders()
        orders_with_coords = [o for o in orders if o.pickup_lat and o.pickup_lng]
        
        if orders_with_coords:
            m = create_map(orders_with_coords)
            st_folium(m, width=1200, height=600)
        else:
            st.info("🗺️ Nenhum pedido com coordenadas disponível")
    
    with tab3:
        st.markdown("### 📋 Todos os Pedidos")
        
        orders = db.get_all_orders()
        
        if orders:
            data = []
            for order in orders:
                data.append({
                    'ID': order.id,
                    'Passageiro': order.passenger_name,
                    'Telefone': order.phone,
                    'Endereço': order.pickup_address,
                    'Horário': format_datetime(order.pickup_time),
                    'Status': order.status.value,
                    'Criado': format_datetime(order.created_at)
                })
            
            df = pd.DataFrame(data)
            
            # Filtro por status
            if status_filter:
                df = df[df['Status'].isin(status_filter)]
            
                st.dataframe(df, width='stretch', hide_index=True)
            
            # Botão de export
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Baixar CSV",
                data=csv,
                file_name=f"pedidos_taxi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("📭 Nenhum pedido encontrado")


if __name__ == "__main__":
    main()
