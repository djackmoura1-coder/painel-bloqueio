import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("📦 Previsão de Postagem")

# ===============================
# 🔗 CONEXÃO
# ===============================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)
spreadsheet = client.open_by_key("1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao")

# ===============================
# 📊 CARREGAR DADOS
# ===============================
try:
    sheet = spreadsheet.worksheet("previsao_postagem")
    dados = sheet.get_all_records()
    df = pd.DataFrame(dados)
except:
    st.error("Erro ao carregar a aba previsao_postagem")
    st.stop()

# ===============================
# 🔥 NORMALIZAÇÃO
# ===============================
if not df.empty:
    df.columns = df.columns.str.strip().str.lower()

# ===============================
# 📊 VISUAL
# ===============================
st.subheader("📊 Planejamento de Expedição")

if df.empty:
    st.warning("Nenhuma previsão cadastrada")
else:

    st.dataframe(df, use_container_width=True)

    # 📈 Métricas
    col1, col2 = st.columns(2)

    col1.metric("Total de Registros", len(df))

    try:
        ultima_data = df["data_impressao"].iloc[-1]
    except:
        ultima_data = "-"

    col2.metric("Última Data de Impressão", ultima_data)
