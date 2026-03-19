import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 BLOQUEIO DE ACESSO
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

# 🔒 SOMENTE ADMIN
if st.session_state.perfil != "admin":
    st.error("Acesso restrito ao administrador")
    st.stop()

st.title("👤 Cadastro de Usuários")

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

sheet = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("usuarios")

dados = sheet.get_all_records()
df = pd.DataFrame(dados)

# FORMULÁRIO
with st.form("cadastro_usuario", clear_on_submit=True):

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    perfil = st.selectbox("Perfil", ["admin", "operador"])

    salvar = st.form_submit_button("Cadastrar")

    if salvar:

        if usuario == "" or senha == "":
            st.warning("Preencha todos os campos")

        elif not df.empty and usuario in df["usuario"].values:
            st.warning("Usuário já existe")

        else:

            sheet.append_row([
                usuario,
                senha,
                perfil
            ])

            st.success("Usuário cadastrado com sucesso!")

# LISTA
st.subheader("Usuários cadastrados")
st.dataframe(df, use_container_width=True)
