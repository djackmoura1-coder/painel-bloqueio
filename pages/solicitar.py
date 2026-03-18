import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from datetime import date

st.title("📌 Solicitar Bloqueio de Pedido")

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


data = st.date_input("Data da solicitação", value=date.today())
responsavel = st.text_input("Responsável solicitante")
email = st.text_input("Email do solicitante")
rastreio = st.text_input("Rastreio do pedido")
motivo = st.text_area("Motivo do bloqueio")


if st.button("Enviar solicitação"):

    if rastreio == "":
        st.warning("Informe o rastreio")
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

        st.success("Solicitação enviada com sucesso!")
