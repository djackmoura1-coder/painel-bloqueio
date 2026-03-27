import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("📦 Movimentação de Estoque")

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

sheet_produtos = spreadsheet.worksheet("produtos")
sheet_log = spreadsheet.worksheet("movimentacoes")

# 📊 DADOS
dados = sheet_produtos.get_all_records()
df = pd.DataFrame(dados)

if df.empty:
    st.warning("Nenhum produto cadastrado")
    st.stop()

# 🔍 PRODUTO
produto = st.selectbox("Selecione o produto", df["Produto"])

estoque_atual = df[df["Produto"] == produto]["Quantidade_inicial"].values[0]

st.info(f"📦 Estoque atual: {estoque_atual}")

# 🔢 QUANTIDADE
quantidade = st.number_input("Quantidade", min_value=1)

st.divider()

col1, col2 = st.columns(2)

# ➕ ENTRADA
with col1:
    if st.button("➕ Adicionar estoque"):

        nova_qtd = estoque_atual + quantidade

        df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd
        sheet_produtos.update([df.columns.tolist()] + df.values.tolist())

        # 🔥 REGISTRO
        sheet_log.append_row([
            str(datetime.now()),
            st.session_state.get("usuario"),
            produto,
            "Entrada",
            quantidade,
            nova_qtd
        ])

        st.success(f"✅ Entrada realizada! Novo estoque: {nova_qtd}")
        st.rerun()

# ➖ BAIXA
with col2:
    if st.button("➖ Dar baixa"):

        if quantidade > estoque_atual:
            st.error("❌ Quantidade maior que o estoque disponível")

        else:
            nova_qtd = estoque_atual - quantidade

            df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd
            sheet_produtos.update([df.columns.tolist()] + df.values.tolist())

            # 🔥 REGISTRO
            sheet_log.append_row([
                str(datetime.now()),
                st.session_state.get("usuario"),
                produto,
                "Baixa",
                quantidade,
                nova_qtd
            ])

            st.success(f"✅ Baixa realizada! Novo estoque: {nova_qtd}")
            st.rerun()

# 📊 VISUAL
st.subheader("📊 Estoque Atual")
st.dataframe(df, use_container_width=True)
