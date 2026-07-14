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

st.markdown("""
<style>

/* Todos os botões do Streamlit */
[data-testid="stButton"] > button {
    background-color: #16a34a !important;
    color: white !important;
    font-weight: 700;
    border-radius: 8px;
    border: none;
    height: 46px;
}

[data-testid="stButton"] > button:hover {
    background-color: #15803d !important;
    color: white !important;
}

[data-testid="stButton"] > button:active {
    background-color: #166534 !important;
}

</style>
""", unsafe_allow_html=True)

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

# 🚀 CACHE (SOMENTE VISUAL)
@st.cache_data(ttl=60)
def carregar_dados():
    dados = sheet.get_all_records()
    return pd.DataFrame(dados)

df = carregar_dados()

# 🔥 CONTROLE DE LIMPEZA
if "limpar_form" not in st.session_state:
    st.session_state.limpar_form = False

if st.session_state.limpar_form:
    st.session_state["responsavel"] = ""
    st.session_state["id_assinatura"] = ""
    st.session_state["rastreio"] = ""
    st.session_state["detalhe"] = ""
    st.session_state.limpar_form = False

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

    # 🔥 BUSCA ATUAL (SEM CACHE)
    dados_atualizados = sheet.get_all_records()
    df_atualizado = pd.DataFrame(dados_atualizados)

    if rastreio == "":
        st.warning("Informe o rastreio")

    elif responsavel.strip() == "":
        st.warning("Informe o responsável")

    elif email.strip() == "":
        st.warning("Informe o email")

    elif not df_atualizado.empty and rastreio in df_atualizado["Rastreio"].astype(str).values:
        st.warning("🚫 Já existe uma solicitação com este rastreio")

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

        # 🔥 LIMPA CAMPOS (MENOS EMAIL)
        st.session_state.limpar_form = True

        st.rerun()
