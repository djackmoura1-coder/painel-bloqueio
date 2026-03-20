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

df = pd.DataFrame(sheet.get_all_records())

# 🔥 CONTROLE DE LIMPEZA
if "limpar_form" not in st.session_state:
    st.session_state.limpar_form = False

# 🔥 LIMPEZA SEGURA (ANTES DE RENDERIZAR CAMPOS)
if st.session_state.limpar_form:
    st.session_state["responsavel"] = ""
    st.session_state["id_assinatura"] = ""
    st.session_state["rastreio"] = ""
    st.session_state["detalhe"] = ""
    st.session_state["limpar_form"] = False

# 📝 FORMULÁRIO
data = st.date_input("Data", value=date.today())

responsavel = st.text_input("Responsável", key="responsavel")

email = st.text_input(
    "Email",
    value=st.session_state.get("email", "")
)

id_assinatura = st.text_input("ID Assinatura", key="id_assinatura")

rastreio = st.text_input("Rastreio", key="rastreio")

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

detalhe = st.text_area("Detalhes", key="detalhe")

# 🚀 ENVIO
if st.button("Enviar"):

    if rastreio == "":
        st.warning("Informe o rastreio")

    elif responsavel.strip() == "":
        st.warning("Informe o responsável")

    elif not df.empty and rastreio in df["Rastreio"].astype(str).values:
        st.warning("Já existe uma solicitação com este rastreio")

    else:

        motivo_final = f"{motivo} - {detalhe}" if detalhe else motivo

        sheet.append_row([
            str(data),
            responsavel.strip(),
            email.strip(),
            id_assinatura,
            rastreio,
            motivo_final,
            "Pendente",
            ""
        ])

        st.success("✅ Solicitação enviada com sucesso!")

        # 🔥 ATIVA LIMPEZA
        st.session_state.limpar_form = True

        st.rerun()
