import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.title("📌 Solicitar Bloqueio de Pedido")

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
).sheet1

# 📋 CARREGA DADOS
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

# 📝 FORMULÁRIO
data = st.date_input("Data da solicitação", value=date.today())
responsavel = st.text_input("Responsável solicitante")
email = st.text_input("Email do solicitante")
id_assinatura = st.text_input("ID Assinatura")
rastreio = st.text_input("Rastreio do pedido")

# 🎯 MOTIVOS PADRÃO
motivo_padrao = st.selectbox(
    "Motivo do bloqueio",
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

# ✏️ COMPLEMENTO
motivo_extra = st.text_area("Detalhes adicionais (opcional)")

# 🚀 ENVIO
if st.button("Enviar solicitação"):

    if rastreio == "":
        st.warning("Informe o rastreio")

    elif not df.empty and rastreio in df["Rastreio"].astype(str).values:
        st.warning("Já existe uma solicitação com este rastreio")

    else:

        motivo_final = (
            f"{motivo_padrao} - {motivo_extra}"
            if motivo_extra
            else motivo_padrao
        )

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

        st.success("✅ Solicitação enviada com sucesso!")
        st.rerun()
