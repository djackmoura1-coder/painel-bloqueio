import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("📦 Movimentação de Estoque")

# 🔗 CONEXÃO GOOGLE
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(credentials)

# 🔗 PLANILHA
sheet = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("produtos")

# 📊 CARREGA DADOS
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

# 🔒 VALIDAÇÃO
if df.empty:
    st.warning("Nenhum produto cadastrado")
    st.stop()

# 🔍 SELECIONAR PRODUTO
produto = st.selectbox("Selecione o produto", df["Produto"])

# 📦 ESTOQUE ATUAL
estoque_atual = df[df["Produto"] == produto]["Quantidade_inicial"].values[0]

st.info(f"📦 Estoque atual: {estoque_atual}")

# 🔢 QUANTIDADE
quantidade = st.number_input("Quantidade", min_value=1)

st.divider()

# 🚀 BOTÕES
col1, col2 = st.columns(2)

# ➕ ENTRADA DE ESTOQUE
with col1:
    if st.button("➕ Adicionar estoque"):

        nova_qtd = estoque_atual + quantidade

        df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd

        sheet.update([df.columns.tolist()] + df.values.tolist())

        st.success(f"✅ Entrada realizada! Novo estoque: {nova_qtd}")

        st.rerun()

# ➖ BAIXA DE ESTOQUE
with col2:
    if st.button("➖ Dar baixa"):

        if quantidade > estoque_atual:
            st.error("❌ Quantidade maior que o estoque disponível")

        else:
            nova_qtd = estoque_atual - quantidade

            df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd

            sheet.update([df.columns.tolist()] + df.values.tolist())

            st.success(f"✅ Baixa realizada! Novo estoque: {nova_qtd}")

            st.rerun()

# 📊 VISUALIZAÇÃO
st.subheader("📊 Estoque Atual")

st.dataframe(df, use_container_width=True)
