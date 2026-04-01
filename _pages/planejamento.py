import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 Planejamento Operacional")

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

try:
    spreadsheet = client.open_by_key("1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao")
except:
    st.error("Erro ao conectar com a planilha")
    st.stop()

# ===============================
# 📊 CARREGAR DADOS
# ===============================
try:
    sheet_prev = spreadsheet.worksheet("previsao_pedidos")
    sheet_cap = spreadsheet.worksheet("capacidade_operacional")

    df_prev = pd.DataFrame(sheet_prev.get_all_records())
    df_cap = pd.DataFrame(sheet_cap.get_all_records())

except:
    st.error("Erro ao carregar abas da planilha")
    st.stop()

# ===============================
# 🔥 NORMALIZAÇÃO
# ===============================
if not df_prev.empty:
    df_prev.columns = df_prev.columns.str.strip().str.lower()

if not df_cap.empty:
    df_cap.columns = df_cap.columns.str.strip().str.lower()

# ===============================
# 📊 CAPACIDADE
# ===============================
st.subheader("⚙️ Capacidade Operacional")

try:
    montagem = int(
        df_cap[df_cap["tipo"] == "montagem_dia"]["quantidade"].values[0]
    )
except:
    st.error("Erro na aba capacidade_operacional (verifique colunas Tipo e Quantidade)")
    st.stop()

st.metric("Capacidade de Montagem/Dia", montagem)

# ===============================
# 📦 PREVISÃO
# ===============================
st.subheader("📦 Previsão de Pedidos")

if df_prev.empty:
    st.warning("Sem dados na aba previsao_pedidos")
    st.stop()

try:
    df_group = df_prev.groupby("data")["quantidade"].sum().reset_index()
except:
    st.error("Erro na aba previsao_pedidos (verifique colunas Data e Quantidade)")
    st.stop()

# ===============================
# 📊 SIMULAÇÃO
# ===============================
st.subheader("📈 Simulação da Operação")

acumulado = 0
resultados = []

for _, row in df_group.iterrows():

    pedidos = int(row["quantidade"])

    saldo = pedidos - montagem
    acumulado += saldo

    resultados.append({
        "Data": row["data"],
        "Pedidos": pedidos,
        "Capacidade": montagem,
        "Saldo do Dia": saldo,
        "Acumulado": acumulado
    })

df_result = pd.DataFrame(resultados)

st.dataframe(df_result, use_container_width=True)

# ===============================
# 🚨 ALERTA
# ===============================
if df_result["Acumulado"].max() > 0:
    st.error("🚨 RISCO DE ATRASO NA OPERAÇÃO")
else:
    st.success("✅ Operação dentro da capacidade")
