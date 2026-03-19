import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.title("📌 Solicitar Bloqueio de Pedido")

# CONEXÃO GOOGLE SHEETS
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
).sheet1

# FORMULÁRIO
data = st.date_input("Data da solicitação", value=date.today())
responsavel = st.text_input("Responsável solicitante")
email = st.text_input("Email do solicitante")
rastreio = st.text_input("Rastreio do pedido")
motivo = st.text_area("Motivo do bloqueio")

# BOTÃO
if st.button("Enviar solicitação"):

    if rastreio == "":
        st.warning("⚠️ Informe o rastreio")

    elif email == "":
        st.warning("⚠️ Informe o email")

    else:

        sheet.append_row([
            str(data),
            responsavel,
            email,
            rastreio,
            motivo,
            "Pendente",
            ""
        ])

        st.success("✅ Solicitação enviada com sucesso!")

        st.rerun()  # 🔥 ATUALIZA A TELA AUTOMATICAMENTE
