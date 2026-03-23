import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("🔧 Resolver Atualização de Endereço")

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
).worksheet("enderecos")

df = pd.DataFrame(sheet.get_all_records())

pendentes = df[df["Status"] == "Pendente"]

if not pendentes.empty:

    rastreio = st.selectbox("Selecionar rastreio", pendentes["Rastreio"])

    acao = st.radio("Resultado", ["Atualizado", "Não atualizado"])

    if st.button("Finalizar"):

        df.loc[df["Rastreio"] == rastreio, "Status"] = "Finalizado"
        df.loc[df["Rastreio"] == rastreio, "Resultado"] = acao

        sheet.update([df.columns.values.tolist()] + df.values.tolist())

        st.success("Atualização concluída!")
        st.rerun()

else:
    st.info("Sem solicitações pendentes")

st.subheader("Histórico")
st.dataframe(df)
