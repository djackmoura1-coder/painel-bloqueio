import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("📊 Planejamento por Trilha")

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
    sheet_cap = spreadsheet.worksheet("capacidade_trilha")

    df_prev = pd.DataFrame(sheet_prev.get_all_records())
    df_cap = pd.DataFrame(sheet_cap.get_all_records())

except:
    st.error("Erro ao carregar abas")
    st.stop()

# ===============================
# 🔥 NORMALIZAÇÃO
# ===============================
df_prev.columns = df_prev.columns.astype(str)

df_cap.columns = df_cap.columns.str.strip().str.lower()
df_cap["trilha"] = df_cap["trilha"].astype(str).str.strip()
df_cap["quantidade_media"] = pd.to_numeric(df_cap["quantidade_media"], errors="coerce").fillna(0)

# ===============================
# 📦 TRANSFORMAR MATRIZ
# ===============================
coluna_trilha = df_prev.columns[0]

df_melt = df_prev.melt(
    id_vars=[coluna_trilha],
    var_name="data",
    value_name="pedidos"
)

df_melt["pedidos"] = pd.to_numeric(df_melt["pedidos"], errors="coerce").fillna(0)
df_melt = df_melt.rename(columns={coluna_trilha: "trilha"})

# ===============================
# 🔗 JUNÇÃO
# ===============================
df_final = df_melt.merge(df_cap, on="trilha", how="left")

df_final["quantidade_media"] = df_final["quantidade_media"].fillna(0)

# ===============================
# 📊 CÁLCULO
# ===============================
df_final["diferenca"] = df_final["quantidade_media"] - df_final["pedidos"]

# ===============================
# 🚩 STATUS
# ===============================
def status(row):
    if row["diferenca"] < 0:
        return "🔴 Falta"
    else:
        return "🟢 OK"

df_final["status"] = df_final.apply(status, axis=1)

# ===============================
# 📊 TABELA FINAL
# ===============================
st.subheader("📊 Análise por Trilha")

st.dataframe(
    df_final[
        ["data", "trilha", "pedidos", "quantidade_media", "diferenca", "status"]
    ],
    use_container_width=True
)

# ===============================
# 🚨 ALERTA GERAL
# ===============================
if (df_final["diferenca"] < 0).any():
    st.error("🚨 Existe risco de falta em algumas trilhas")
else:
    st.success("✅ Todas as trilhas estão dentro da capacidade")
