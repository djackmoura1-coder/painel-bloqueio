import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Sistema de Bloqueio",
    layout="wide"
)

# 🔗 CONEXÃO GOOGLE
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)

# 🔑 CONECTA NA ABA USUÁRIOS
sheet_usuarios = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("usuarios")

dados = sheet_usuarios.get_all_records()
df_users = pd.DataFrame(dados)

# SESSION
if "logado" not in st.session_state:
    st.session_state.logado = False

# 🔐 LOGIN
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        if usuario in df_users["usuario"].values:

            user_data = df_users[df_users["usuario"] == usuario].iloc[0]

            if user_data["senha"] == senha:

                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.session_state.perfil = user_data["perfil"]

                st.rerun()

            else:
                st.error("Senha incorreta")

        else:
            st.error("Usuário não encontrado")

# SISTEMA LIBERADO
else:

    st.sidebar.success(f"👤 {st.session_state.usuario}")

    if st.sidebar.button("Sair"):
        st.session_state.logado = False
        st.rerun()

    st.title("📦 Sistema Operacional de Bloqueio")

    st.markdown("""
    Use o menu lateral:

    📌 Solicitar  
    🔧 Resolver  
    📊 Dashboard  
    👤 Usuários (admin)
    """)
