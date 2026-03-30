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

# 📦 ESTOQUE ATUAL
estoque_atual = df[df["Produto"] == produto]["Quantidade_inicial"].values[0]

# 🔥 NOVOS CAMPOS
quantidade_total = df[df["Produto"] == produto]["Quantidade_total"].values[0]
percentual_meta = df[df["Produto"] == produto]["Percentual"].values[0]

st.info(f"📦 Estoque atual: {estoque_atual}")

# 🔥 CALCULO DE PERFORMANCE
consumido = int(quantidade_total) - int(estoque_atual)

if int(quantidade_total) > 0:
    percentual_consumido = (consumido / int(quantidade_total)) * 100
else:
    percentual_consumido = 0

percentual_restante = 100 - percentual_consumido

# 🎯 DASH DE CONTROLE
st.subheader("📊 Controle de Produção")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric("📦 Total", quantidade_total)

with col_b:
    st.metric("✅ Consumido", f"{percentual_consumido:.1f}%")

with col_c:
    st.metric("⏳ Restante", f"{percentual_restante:.1f}%")

st.divider()

# 🔢 QUANTIDADE
quantidade = st.number_input("Quantidade", min_value=1)

col1, col2 = st.columns(2)

# ➕ ENTRADA
with col1:
    if st.button("➕ Adicionar estoque"):

        nova_qtd = int(estoque_atual) + int(quantidade)

        df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd
        sheet_produtos.update([df.columns.tolist()] + df.values.tolist())

        # 🔥 HISTÓRICO
        sheet_log.append_row([
            str(datetime.now()),
            str(st.session_state.get("usuario")),
            str(produto),
            "Entrada",
            int(quantidade),
            int(nova_qtd)
        ])

        st.success(f"✅ Entrada realizada! Novo estoque: {nova_qtd}")
        st.rerun()

# ➖ BAIXA
with col2:
    if st.button("➖ Dar baixa"):

        if int(quantidade) > int(estoque_atual):
            st.error("❌ Quantidade maior que o estoque disponível")

        else:
            nova_qtd = int(estoque_atual) - int(quantidade)

            df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd
            sheet_produtos.update([df.columns.tolist()] + df.values.tolist())

            # 🔥 HISTÓRICO
            sheet_log.append_row([
                str(datetime.now()),
                str(st.session_state.get("usuario")),
                str(produto),
                "Baixa",
                int(quantidade),
                int(nova_qtd)
            ])

            st.success(f"✅ Baixa realizada! Novo estoque: {nova_qtd}")
            st.rerun()

# 📊 VISUALIZAÇÃO
st.subheader("📊 Estoque Atual")

st.dataframe(df, use_container_width=True)
