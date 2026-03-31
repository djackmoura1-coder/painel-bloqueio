import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("📦 Cadastro de Produtos")

# 🔐 CONTROLE DE PERMISSÃO
departamento = str(st.session_state.get("departamento", "")).lower()

if departamento in ["atendimento", "faturamento"]:
    pode_editar = False
else:
    pode_editar = True

if not pode_editar:
    st.warning("🔒 Apenas visualização")

# 🔗 CONEXÃO
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
).worksheet("produtos")

dados = sheet.get_all_records()
df = pd.DataFrame(dados)

produto = st.text_input("Produto", disabled=not pode_editar)

trilha = st.selectbox(
    "Trilha",
    ["Gato","Essencial","Extra petisco","Extra brinquedo","Natural","Mordedor"],
    disabled=not pode_editar
)

quantidade = st.number_input("Quantidade inicial", min_value=0, disabled=not pode_editar)

if st.button("Cadastrar", disabled=not pode_editar):

    sheet.append_row([
        produto,
        trilha,
        quantidade,
        quantidade,
        quantidade
    ])

    st.rerun()

st.subheader("📊 Produtos")
st.dataframe(df)
