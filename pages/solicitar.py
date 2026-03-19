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

# 🔥 CARREGA DADOS PARA VALIDAÇÃO
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

# FORMULÁRIO
with st.form("form_solicitacao", clear_on_submit=True):

    data = st.date_input("Data da solicitação", value=date.today())
    responsavel = st.text_input("Responsável solicitante")
    email = st.text_input("Email do solicitante")
    rastreio = st.text_input("Rastreio do pedido")
    motivo = st.text_area("Motivo do bloqueio")

    enviar = st.form_submit_button("Enviar solicitação")

    if enviar:

        if rastreio == "":
            st.warning("⚠️ Informe o rastreio")

        elif email == "":
            st.warning("⚠️ Informe o email")

        # 🔥 VALIDAÇÃO DE DUPLICIDADE
        elif not df.empty and rastreio in df["Rastreio"].astype(str).values:
            st.warning("⚠️ Já existe uma solicitação com este código")

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
