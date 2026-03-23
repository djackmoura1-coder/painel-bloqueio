import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# 🔒 BLOQUEIO
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("🏠 Solicitar Atualização de Endereço")

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
).worksheet("enderecos")

# FORMULÁRIO
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

# ENVIO
if st.button("Enviar solicitação"):

    dados_atualizados = sheet.get_all_records()
    df_atualizado = pd.DataFrame(dados_atualizados)

    if rastreio == "":
        st.warning("Informe o rastreio")

    elif not df_atualizado.empty and rastreio in df_atualizado["Rastreio"].astype(str).values:
        st.warning("Já existe solicitação para este rastreio")

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

        st.success("Solicitação enviada!")
        st.rerun()
