import streamlit as st

st.set_page_config(
    page_title="Sistema de Bloqueio de Pedidos",
    page_icon="📦",
    layout="wide"
)

st.image("assets/logo_petiko.png", width=250)

st.title("📦 Sistema Operacional de Bloqueio")

st.markdown("""
### Bem-vindo ao painel

Utilize o menu lateral para acessar as funcionalidades:

📌 Solicitar Bloqueio  
🔧 Resolver Ocorrências  
📊 Dashboard Operacional
""")

st.info("Sistema interno de controle de bloqueios logísticos")
