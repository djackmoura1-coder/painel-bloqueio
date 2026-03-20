import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

# 🔒 BLOQUEIO
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login para acessar")
    st.stop()

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

df = pd.DataFrame(sheet.get_all_records())

# FORMULÁRIO
data = st.date_input("Data", value=date.today())
responsavel = st.text_input("Responsável")

# 🔥 EMAIL AUTOMÁTICO
email = st.text_input(
    "Email",
    value=st.session_state.get("email", "")
)

id_assinatura = st.text_input("ID Assinatura")
rastreio = st.text_input("Rastreio")

motivo = st.selectbox(
    "Motivo",
    [
        "Cancelamento",
        "Suspeita de fraude",
        "Alteração de porte de trilha",
        "Contestação",
        "RA",
        "Box entregue",
        "PROCON",
        "Duplicidade",
        "Correção de faturamento"
    ]
)

detalhe = st.text_area("Detalhes")

if st.button("Enviar"):

    if rastreio == "":
        st.warning("Informe o rastreio")

    elif not df.empty and rastreio in df["Rastreio"].astype(str).values:
        st.warning("Duplicado")

    else:

        motivo_final = f"{motivo} - {detalhe}" if detalhe else motivo

        sheet.append_row([
            str(data),
            responsavel,
            email,
            id_assinatura,
            rastreio,
            motivo_final,
            "Pendente",
            ""
        ])

        st.success("Enviado!")
        st.rerun()
