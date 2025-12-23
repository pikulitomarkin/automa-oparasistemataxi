"""
Streamlit Dashboard - Taxi Automation System
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

load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Central Táxi - Liquid Theme",
    page_icon="🚕",
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    /* Sidebar - Frosted Glass Dark */
    [data-testid="stSidebar"] {
        background: rgba(20, 20, 40, 0.75) !important;
        backdrop-filter: blur(40px) saturate(180%);
        border-right: 1px solid rgba(255, 255, 255, 0.125);
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox > div > div,
    [data-testid="stSidebar"] .stMultiSelect > div > div {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 16px !important;
        padding: 14px 24px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
    }
    
    /* Main content */
    .main .block-container {
        padding: 2rem 3rem;
    }
    
    /* Hide Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Títulos e textos */
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #ffffff !important;
    }
    
    /* Tabs - Liquid Navigation */
    .stTabs {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        border-radius: 20px;
        padding: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        color: rgba(255, 255, 255, 0.7);
        font-weight: 600;
        font-size: 1rem;
        padding: 0 32px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4)) !important;
        color: #ffffff !important;
        border-color: rgba(255, 255, 255, 0.4) !important;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        font-weight: 700;
    }
    
    /* Dataframe */
    .dataframe {
        background: rgba(255, 255, 255, 0.95) !important;
        border-radius: 16px !important;
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: 16px !important;
        border: none !important;
    }
    
    .dataframe tbody tr:hover {
        background: rgba(102, 126, 234, 0.08) !important;
    }
    
    .dataframe tbody td {
        color: #2c3e50 !important;
        padding: 14px !important;
    }
    
    /* Buttons */
    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9), rgba(118, 75, 162, 0.9));
        backdrop-filter: blur(10px);
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 16px;
        padding: 14px 28px;
        font-weight: 700;
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 32px rgba(102, 126, 234, 0.5);
    }
    
    /* Radio buttons */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.25) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 16px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        padding: 1rem 1.5rem !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.6), rgba(118, 75, 162, 0.6));
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_db_manager():
    return DatabaseManager(os.getenv('DATABASE_PATH', 'data/taxi_orders.db'))


def format_datetime(dt):
    if dt is None:
        return "-"
    return dt.strftime("%d/%m/%Y %H:%M")


def create_map(orders):
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


def main():
    # Header Liquid
    st.markdown("""
        <div style='background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(20px); 
                    border-radius: 28px; padding: 3rem 2rem; margin-bottom: 3rem;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);'>
            <div style='text-align: center;'>
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
    
    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style='text-align: center; padding: 1.5rem 0;'>
                <h2 style='margin: 0; font-size: 1.5rem; font-weight: 700;'>⚙️ Painel de Controle</h2>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border: none; height: 1px; background: rgba(255,255,255,0.2); margin: 1.5rem 0;'>", unsafe_allow_html=True)
        
        st.markdown("##### 📅 Período")
        date_range = st.selectbox(
            "period",
            ["Últimas 24h", "Últimos 7 dias", "Últimos 30 dias", "Todos"],
            index=1,
            label_visibility="collapsed"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("##### 🏷️ Status dos Pedidos")
        status_filter = st.multiselect(
            "status",
            [s.value for s in OrderStatus],
            default=[OrderStatus.DISPATCHED.value, OrderStatus.FAILED.value],
            label_visibility="collapsed"
        )
        
        st.markdown("<hr style='border: none; height: 1px; background: rgba(255,255,255,0.2); margin: 2rem 0;'>", unsafe_allow_html=True)
        
        if st.button("🔄 Atualizar", type="primary", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
        
        st.markdown("<hr style='border: none; height: 1px; background: rgba(255,255,255,0.2); margin: 2rem 0;'>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='text-align: center; color: rgba(255,255,255,0.7);'>
                <p style='margin: 0; font-size: 0.9rem;'>Sistema de Automação</p>
                <p style='margin: 0; font-size: 0.8rem;'>v1.0.0</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Database
    db = get_db_manager()
    stats = db.get_statistics()
    
    # KPI Cards - Liquid Style
    col1, col2, col3, col4 = st.columns(4)
    
    cards = [
        {
            'col': col1,
            'title': 'Total de Pedidos',
            'value': stats['total'],
            'gradient': 'linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3))',
            'icon': '📊'
        },
        {
            'col': col2,
            'title': '✅ Despachados',
            'value': stats.get(OrderStatus.DISPATCHED.value, 0),
            'gradient': 'linear-gradient(135deg, rgba(17, 153, 142, 0.3), rgba(56, 239, 125, 0.3))',
            'icon': '✅'
        },
        {
            'col': col3,
            'title': '❌ Falhas',
            'value': stats.get(OrderStatus.FAILED.value, 0) + stats.get(OrderStatus.MANUAL_REVIEW.value, 0),
            'gradient': 'linear-gradient(135deg, rgba(238, 9, 121, 0.3), rgba(255, 106, 0, 0.3))',
            'icon': '❌'
        },
        {
            'col': col4,
            'title': 'Taxa de Sucesso',
            'value': f"{(stats.get(OrderStatus.DISPATCHED.value, 0) / stats['total'] * 100) if stats['total'] > 0 else 0:.1f}%",
            'gradient': 'linear-gradient(135deg, rgba(240, 147, 251, 0.3), rgba(245, 87, 108, 0.3))',
            'icon': '📈'
        }
    ]
    
    for card in cards:
        with card['col']:
            st.markdown(f"""
                <div style='background: {card['gradient']};
                            backdrop-filter: blur(30px) saturate(180%);
                            border-radius: 24px; padding: 2rem 1.5rem;
                            border: 1px solid rgba(255, 255, 255, 0.25);
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
                            transition: all 0.4s ease;
                            position: relative; overflow: hidden;'>
                    <div style='color: rgba(255, 255, 255, 0.85); font-size: 0.95rem;
                                font-weight: 600; margin-bottom: 0.75rem; letter-spacing: 0.5px;'>
                        {card['icon']} {card['title']}
                    </div>
                    <div style='color: #ffffff; font-size: 3rem; font-weight: 800;
                                margin: 0; line-height: 1; text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                                letter-spacing: -2px;'>
                        {card['value']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Tabs Navigation
    tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "🗺️ Mapa", "📋 Detalhes"])
    
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div style='background: rgba(255, 255, 255, 0.12); backdrop-filter: blur(30px);
                            border-radius: 24px; padding: 2rem; border: 1px solid rgba(255, 255, 255, 0.2);
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);'>
                    <h3 style='margin-top: 0; font-weight: 700;'>📊 Distribuição por Status</h3>
                </div>
            """, unsafe_allow_html=True)
            
            status_data = {k: v for k, v in stats.items() if k != 'total' and v > 0}
            
            if status_data:
                fig = px.pie(
                    values=list(status_data.values()),
                    names=list(status_data.keys()),
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff', size=14)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Nenhum dado disponível")
        
        with col2:
            st.markdown("""
                <div style='background: rgba(255, 255, 255, 0.12); backdrop-filter: blur(30px);
                            border-radius: 24px; padding: 2rem; border: 1px solid rgba(255, 255, 255, 0.2);
                            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);'>
                    <h3 style='margin-top: 0; font-weight: 700;'>📈 Timeline</h3>
                </div>
            """, unsafe_allow_html=True)
            
            orders = db.get_all_orders(limit=50)
            
            if orders:
                df = pd.DataFrame([{
                    'Data': o.created_at,
                    'Pedidos': 1
                } for o in orders])
                df['Data'] = pd.to_datetime(df['Data']).dt.date
                timeline = df.groupby('Data').sum().reset_index()
                
                fig = px.line(timeline, x='Data', y='Pedidos', markers=True)
                fig.update_traces(line_color='#667eea', line_width=3)
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📭 Nenhum pedido")
    
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.12); backdrop-filter: blur(30px);
                        border-radius: 24px; padding: 2rem; border: 1px solid rgba(255, 255, 255, 0.2);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);'>
                <h3 style='margin-top: 0;'>🗺️ Mapa de Coletas</h3>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        all_orders = db.get_all_orders(limit=100)
        filtered_orders = [o for o in all_orders if o.status.value in status_filter and o.pickup_lat] if status_filter else [o for o in all_orders if o.pickup_lat]
        
        if filtered_orders:
            st.info(f"📍 {len(filtered_orders)} pedidos no mapa")
            map_obj = create_map(filtered_orders)
            folium_static(map_obj, width=1200, height=600)
        else:
            st.warning("⚠️ Nenhum pedido com coordenadas")
    
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background: rgba(255, 255, 255, 0.12); backdrop-filter: blur(30px);
                        border-radius: 24px; padding: 2rem; border: 1px solid rgba(255, 255, 255, 0.2);
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);'>
                <h3 style='margin-top: 0;'>📋 Lista de Pedidos</h3>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        view_option = st.radio(
            "Visualizar:",
            ["Todos", "Despachados", "Falhas", "Revisão Manual"],
            horizontal=True
        )
        
        if view_option == "Todos":
            orders = db.get_all_orders(limit=100)
        elif view_option == "Despachados":
            orders = db.get_orders_by_status(OrderStatus.DISPATCHED)
        elif view_option == "Falhas":
            orders = db.get_orders_by_status(OrderStatus.FAILED)
        else:
            orders = db.get_orders_by_status(OrderStatus.MANUAL_REVIEW)
        
        if orders:
            df = pd.DataFrame([{
                'ID': o.id,
                'Passageiro': o.passenger_name,
                'Telefone': o.phone,
                'Endereço': o.pickup_address,
                'Horário': format_datetime(o.pickup_time),
                'Status': o.status.value
            } for o in orders])
            
            st.dataframe(df, use_container_width=True, hide_index=True, height=400)
            
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Baixar CSV",
                csv,
                "pedidos.csv",
                "text/csv",
                use_container_width=False
            )
        else:
            st.info("📭 Nenhum pedido encontrado")


if __name__ == "__main__":
    main()
