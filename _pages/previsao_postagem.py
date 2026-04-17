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
# 📊 DADOS
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
# 📢 AVISO
# ===============================
st.info("""
📢 **Importante:**
- A previsão refere-se ao envio do pedido
- O prazo de entrega começa após a postagem
- Em caso de atraso (🔴), acionar o time de logística
""")

# ===============================
# 📅 DATA DE ATUALIZAÇÃO
# ===============================
if "data_atualizacao" in df.columns:
    try:
        ultima_atualizacao = df["data_atualizacao"].dropna().iloc[-1]
    except:
        ultima_atualizacao = "-"
else:
    ultima_atualizacao = "Não informado"

st.success(f"📅 Última atualização: {ultima_atualizacao}")

# ===============================
# 🔄 RENOMEAR COLUNAS
# ===============================
df = df.rename(columns={
    "data_impressao": "Data do Pedido",
    "previsao_expedicao": "Previsão de Envio",
    "status": "Status"
})

# ===============================
# 🔎 BUSCA
# ===============================
busca = st.text_input("🔎 Buscar por data do pedido")

if busca:
    df = df[df["Data do Pedido"].astype(str).str.contains(busca)]

# ===============================
# 🎯 STATUS COM BOLINHA
# ===============================
def formatar_status(valor):
    if not isinstance(valor, str):
        return "-"
    
    valor = valor.lower().strip()

    if valor == "atrasado":
        return "🔴 Atrasado"
    elif valor == "atenção":
        return "🟡 Atenção"
    elif valor == "no prazo":
        return "🟢 No prazo"
    else:
        return valor

if "Status" in df.columns:
    df["Status"] = df["Status"].apply(formatar_status)

# ===============================
# 📊 ORDENAÇÃO
# ===============================
if "Previsão de Envio" in df.columns:
    try:
        df = df.sort_values(by="Previsão de Envio")
    except:
        pass

# ===============================
# 📊 TABELA FINAL
# ===============================
if df.empty:
    st.warning("Nenhuma previsão cadastrada")
else:
    st.dataframe(df, use_container_width=True)
