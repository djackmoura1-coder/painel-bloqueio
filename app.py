import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="Sistema de Bloqueio", layout="wide")

# CONEXÃO
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)

spreadsheet = client.open_by_key("1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao")

sheet_users = spreadsheet.worksheet("usuarios")
sheet_solic = spreadsheet.worksheet("solicitacoes_usuarios")

df_users = pd.DataFrame(sheet_users.get_all_records())
df_solic = pd.DataFrame(sheet_solic.get_all_records())

# NORMALIZAÇÃO
if not df_users.empty:
    df_users.columns = df_users.columns.str.strip().str.lower()

    for col in ["usuario", "senha", "email", "perfil", "departamento"]:
        if col not in df_users.columns:
            df_users[col] = ""

    df_users = df_users.fillna("").astype(str).apply(lambda x: x.str.strip())

# SESSION
if "logado" not in st.session_state:
    st.session_state.logado = False

# LOGIN
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        usuario = usuario.strip()
        senha = senha.strip()

        if usuario == "admin" and senha == "123456":
            st.session_state.logado = True
            st.session_state.usuario = "admin"
            st.session_state.perfil = "admin"
            st.session_state.departamento = "Admin"
            st.session_state.email = "admin@empresa.com"
            st.rerun()

        user = df_users[df_users["usuario"] == usuario]

        if not user.empty:

            user = user.iloc[0]

            if user["senha"] == senha:

                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.session_state.perfil = user["perfil"]
                st.session_state.departamento = user["departamento"]
                st.session_state.email = user["email"]

                st.rerun()

            else:
                st.error("Senha incorreta")

        else:
            st.error("Usuário não encontrado")

else:

    st.sidebar.success(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"🏢 {st.session_state.departamento}")
    st.sidebar.write(f"📧 {st.session_state.email}")

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    st.title("📦 Sistema Operacional de Bloqueio")
