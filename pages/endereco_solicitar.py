import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("🏠 Solicitar Atualização de Endereço")

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
).worksheet("enderecos")

# 🔥 LEITURA SEGURA
dados = sheet.get_all_values()

if len(dados) < 2:
    df = pd.DataFrame()
else:
    df = pd.DataFrame(dados[1:], columns=dados[0])

# 🔥 NORMALIZAÇÃO
if not df.empty:
    df.columns = (
        pd.Series(df.columns)
        .str.strip()
        .str.lower()
        .str.replace("á", "a")
        .str.replace("ã", "a")
        .str.replace("ç", "c")
        .str.replace("é", "e")
        .str.replace("í", "i")
        .str.replace("ó", "o")
        .str.replace("ú", "u")
    )

# 📝 FORMULÁRIO
data = st.date_input("Data", value=date.today())

responsavel = st.text_input("Responsável")
email = st.text_input("Email", value=st.session_state.get("email", ""))

id_assinatura = st.text_input("ID Assinatura")
rastreio = st.text_input("Rastreio")

rua = st.text_input("Rua")
numero = st.text_input("Número")
complemento = st.text_input("Complemento")
bairro = st.text_input("Bairro")
cidade = st.text_input("Cidade")
uf = st.text_input("UF")
cep = st.text_input("CEP")

# 🚀 ENVIO
if st.button("Enviar solicitação"):

    # 🔥 BUSCA ATUAL SEM CACHE
    dados_atualizados = sheet.get_all_values()

    if len(dados_atualizados) < 2:
        df_atualizado = pd.DataFrame()
    else:
        df_atualizado = pd.DataFrame(dados_atualizados[1:], columns=dados_atualizados[0])

    # 🔥 NORMALIZA
    if not df_atualizado.empty:
        df_atualizado.columns = (
            pd.Series(df_atualizado.columns)
            .str.strip()
            .str.lower()
            .str.replace("á", "a")
            .str.replace("ã", "a")
            .str.replace("ç", "c")
            .str.replace("é", "e")
            .str.replace("í", "i")
            .str.replace("ó", "o")
            .str.replace("ú", "u")
        )

    if rastreio == "":
        st.warning("Informe o rastreio")

    elif "rastreio" in df_atualizado.columns and rastreio in df_atualizado["rastreio"].astype(str).values:
        st.warning("🚫 Já existe solicitação para este rastreio")

    else:

        sheet.append_row([
            str(data),
            responsavel,
            email,
            id_assinatura,
            rastreio,
            rua,
            numero,
            complemento,
            bairro,
            cidade,
            uf,
            cep,
            "Pendente",
            ""
        ])

        st.success("✅ Solicitação enviada!")
        st.rerun()
