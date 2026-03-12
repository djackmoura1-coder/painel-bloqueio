import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 Dashboard Operacional")

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

dados = sheet.get_all_records()

df = pd.DataFrame(dados)

if df.empty:
    st.warning("Ainda não existem ocorrências registradas.")
    st.stop()


col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total de ocorrências",
        value=len(df)
    )

with col2:
    st.metric(
        label="Pendentes",
        value=len(df[df["Status"] == "Pendente"])
    )

with col3:
    st.metric(
        label="Bloqueados",
        value=len(df[df["Resultado"] == "Bloqueado"])
    )


st.divider()

st.subheader("Ocorrências por responsável")

grafico = df.groupby("Responsavel").size()

st.bar_chart(grafico)
