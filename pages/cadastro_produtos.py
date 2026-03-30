import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("📦 Cadastro de Produtos")

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

produto = st.text_input("Nome do produto")

trilha = st.selectbox(
    "Trilha",
    ["Gato", "Essencial", "Extra petisco", "Extra brinquedo", "Natural", "Mordedor"]
)

quantidade = st.number_input("Quantidade inicial", min_value=0)

if st.button("Cadastrar produto"):

    if produto == "":
        st.warning("Informe o produto")

    elif not df.empty and produto in df["Produto"].values:
        st.warning("Produto já existe")

    else:

        sheet.append_row([
            produto,
            trilha,
            quantidade,
            quantidade  # total fixo
        ])

        st.success("Produto cadastrado!")
        st.rerun()

st.subheader("📊 Produtos cadastrados")
st.dataframe(df, use_container_width=True)
