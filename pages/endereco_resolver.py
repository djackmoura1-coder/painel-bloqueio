import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("🔧 Resolver Atualização de Endereço")

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
).worksheet("enderecos")

# 📊 DADOS
df = pd.DataFrame(sheet.get_all_records())

# 🔥 NORMALIZAÇÃO DAS COLUNAS (ANTI-ERRO)
if not df.empty:
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace("á", "a")
        .str.replace("ã", "a")
        .str.replace("ç", "c")
        .str.replace("é", "e")
        .str.replace("í", "i")
        .str.replace("ó", "o")
        .str.replace("ú", "u")
    )

# 🔒 VALIDAÇÃO
if "status" not in df.columns:
    st.error("❌ Coluna 'Status' não encontrada na planilha.")
    st.stop()

if "rastreio" not in df.columns:
    st.error("❌ Coluna 'Rastreio' não encontrada.")
    st.stop()

# 📌 FILTRO
pendentes = df[df["status"] == "Pendente"]

if not pendentes.empty:

    rastreio = st.selectbox(
        "Selecionar rastreio",
        pendentes["rastreio"]
    )

    acao = st.radio(
        "Resultado",
        ["Atualizado", "Não atualizado"]
    )

    if st.button("Finalizar"):

        df.loc[df["rastreio"] == rastreio, "status"] = "Finalizado"
        df.loc[df["rastreio"] == rastreio, "resultado"] = acao

        # 🔄 ATUALIZA PLANILHA
        sheet.update([df.columns.tolist()] + df.values.tolist())

        st.success("✅ Atualização concluída!")
        st.rerun()

else:
    st.info("Sem solicitações pendentes")

# 📊 HISTÓRICO
st.subheader("📊 Histórico de solicitações")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
