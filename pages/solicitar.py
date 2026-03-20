import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.title("📌 Solicitar Bloqueio de Pedido")

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
).sheet1

# FORMULÁRIO
data = st.date_input("Data da solicitação", value=date.today())
responsavel = st.text_input("Responsável solicitante")
email = st.text_input("Email do solicitante")

id_assinatura = st.text_input("ID Assinatura")  # 👈 NOVO CAMPO

rastreio = st.text_input("Rastreio do pedido")
motivo = st.text_area("Motivo do bloqueio")

# CARREGA DADOS PARA VALIDAR DUPLICIDADE
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

if st.button("Enviar solicitação"):

    if rastreio == "":
        st.warning("Informe o rastreio")

    elif not df.empty and rastreio in df["Rastreio"].astype(str).values:
        st.warning("Já existe uma solicitação com este rastreio")

    else:

        sheet.append_row([
            str(data),
            responsavel,
            email,
            id_assinatura,  # 👈 SALVANDO NOVO CAMPO
            rastreio,
            motivo,
            "Pendente",
            ""
        ])

        st.success("✅ Solicitação enviada com sucesso!")
        st.rerun()
