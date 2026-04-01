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
if not df_cap.empty:
    df_cap.columns = df_cap.columns.str.strip().str.lower()

# ===============================
# 📊 CAPACIDADE
# ===============================
st.subheader("⚙️ Capacidade Operacional")

try:
    df_cap["tipo"] = df_cap["tipo"].astype(str).str.strip().str.lower()
    df_cap["quantidade"] = df_cap["quantidade"].astype(str).str.strip()

    df_cap["quantidade"] = df_cap["quantidade"].replace("", "0")
    df_cap["quantidade"] = df_cap["quantidade"].astype(float)

    linha_montagem = df_cap[df_cap["tipo"].str.contains("montagem")]

    if linha_montagem.empty:
        st.error("❌ Não encontrou capacidade de montagem")
        st.stop()

    montagem = int(linha_montagem["quantidade"].values[0])

except Exception as e:
    st.error(f"Erro na capacidade_operacional: {e}")
    st.stop()

st.metric("Capacidade de Montagem/Dia", montagem)

# ===============================
# 📦 PREVISÃO (MATRIZ)
# ===============================
st.subheader("📦 Previsão de Pedidos")

if df_prev.empty:
    st.warning("⚠️ Sem dados na aba previsao_pedidos")
    st.stop()

try:
    df_prev.columns = df_prev.columns.astype(str)

    coluna_trilha = df_prev.columns[0]

    # 🔥 transforma matriz → formato padrão
    df_melt = df_prev.melt(
        id_vars=[coluna_trilha],
        var_name="data",
        value_name="quantidade"
    )

    df_melt["quantidade"] = pd.to_numeric(
        df_melt["quantidade"],
        errors="coerce"
    ).fillna(0)

    # 🔥 agrupa por data
    df_group = df_melt.groupby("data")["quantidade"].sum().reset_index()

except Exception as e:
    st.error(f"Erro ao processar previsão: {e}")
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
