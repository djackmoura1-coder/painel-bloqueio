import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("📦 Cadastro de Produtos")

# 🔐 CONTROLE DE PERMISSÃO
departamento = str(st.session_state.get("departamento", "")).lower()
pode_editar = departamento not in ["atendimento", "faturamento"]

if not pode_editar:
    st.warning("🔒 Apenas visualização")

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

sheet = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("produtos")

dados = sheet.get_all_records()
df = pd.DataFrame(dados)

# 🔥 NORMALIZA COLUNAS (IMPORTANTE)
if not df.empty:
    df.columns = df.columns.str.strip().str.lower()

# ===============================
# 📝 INPUTS
# ===============================
sku = st.text_input("SKU do produto", disabled=not pode_editar)

produto = st.text_input("Produto", disabled=not pode_editar)

trilha = st.selectbox(
    "Trilha",
    ["Gato","Essencial","Extra petisco","Extra brinquedo","Natural","Mordedor"],
    disabled=not pode_editar
)

quantidade = st.number_input(
    "Quantidade inicial",
    min_value=0,
    disabled=not pode_editar
)

# ===============================
# 🚀 CADASTRO
# ===============================
if st.button("Cadastrar", disabled=not pode_editar):

    if sku.strip() == "":
        st.warning("Informe o SKU")
        st.stop()

    if produto.strip() == "":
        st.warning("Informe o produto")
        st.stop()

    # 🔥 VALIDA SKU DUPLICADO
    if not df.empty:
        if sku in df["sku"].astype(str).values:
            st.error("❌ SKU já cadastrado")
            st.stop()

    # 🔥 SALVAR (ORDEM CORRETA DA PLANILHA)
    sheet.append_row([
        sku,
        produto,
        trilha,
        quantidade,
        quantidade,
        quantidade
    ])

    st.success("✅ Produto cadastrado com sucesso!")
    st.rerun()

# ===============================
# 📊 VISUALIZAÇÃO
# ===============================
st.subheader("📊 Produtos")
st.dataframe(df, use_container_width=True)
