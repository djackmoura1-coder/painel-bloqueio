import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("📦 Cadastro de Produtos por Trilha")

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

# 📊 DADOS
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

# 📝 FORMULÁRIO
produto = st.text_input("Nome do produto")

trilha = st.selectbox(
    "Trilha",
    [
        "Gato",
        "Essencial",
        "Extra petisco",
        "Extra brinquedo",
        "Natural",
        "Mordedor"
    ]
)

quantidade = st.number_input("Quantidade inicial", min_value=0)

# 🚀 CADASTRO
if st.button("Cadastrar produto"):

    if produto == "":
        st.warning("Informe o nome do produto")

    elif not df.empty and produto in df["Produto"].values:
        st.warning("Produto já cadastrado")

    else:

        sheet.append_row([
            produto,
            trilha,
            quantidade
        ])

        st.success("Produto cadastrado com sucesso!")
        st.rerun()

# 📊 LISTA
st.subheader("📊 Produtos cadastrados")

st.dataframe(df, use_container_width=True)
