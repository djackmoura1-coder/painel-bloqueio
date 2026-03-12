import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.title("Solicitar Bloqueio de Pedido")

# CONEXÃO COM GOOGLE SHEETS

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(credentials)

sheet = client.open("painel-bloqueio").sheet1

# FORMULÁRIO

data = st.date_input("Data", value=date.today())

responsavel = st.text_input("Responsável solicitante")

rastreio = st.text_input("Rastreio do pedido")

motivo = st.text_area("Motivo do bloqueio")

if st.button("Enviar solicitação"):

    sheet.append_row([
        str(data),
        responsavel,
        rastreio,
        motivo,
        "Pendente",
        ""
    ])

    st.success("Solicitação enviada com sucesso!")
