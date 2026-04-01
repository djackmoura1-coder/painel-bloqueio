import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 Planejamento Operacional")

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

spreadsheet = client.open_by_key("1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao")

sheet_prev = spreadsheet.worksheet("previsao_pedidos")
sheet_cap = spreadsheet.worksheet("capacidade_operacional")

df_prev = pd.DataFrame(sheet_prev.get_all_records())
df_cap = pd.DataFrame(sheet_cap.get_all_records())

# ===============================
# 📊 CAPACIDADE
# ===============================
st.subheader("⚙️ Capacidade")

montagem = int(df_cap[df_cap["Tipo"] == "Montagem_dia"]["Quantidade"].values[0])

st.metric("Capacidade Montagem/Dia", montagem)

# ===============================
# 📦 PREVISÃO
# ===============================
df_group = df_prev.groupby("Data")["Quantidade"].sum().reset_index()

# ===============================
# 📊 SIMULAÇÃO
# ===============================
acumulado = 0
resultados = []

for _, row in df_group.iterrows():

    pedidos = int(row["Quantidade"])

    saldo = pedidos - montagem
    acumulado += saldo

    resultados.append({
        "Data": row["Data"],
        "Pedidos": pedidos,
        "Capacidade": montagem,
        "Saldo": saldo,
        "Acumulado": acumulado
    })

df_result = pd.DataFrame(resultados)

st.subheader("📈 Resultado")

st.dataframe(df_result, use_container_width=True)

# ===============================
# 🚨 ALERTA
# ===============================
if df_result["Acumulado"].max() > 0:
    st.error("🚨 Vai gerar atraso")
else:
    st.success("✅ Operação OK")
