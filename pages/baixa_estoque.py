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

# ===============================
# 🔥 BOTÃO LIMPAR HISTÓRICO
# ===============================
st.divider()
st.subheader("⚠️ Controle de Histórico")

col_reset1, col_reset2 = st.columns([2,1])

with col_reset2:
    if st.button("🗑️ Limpar histórico", use_container_width=True):

        confirmar = st.checkbox("Confirmar exclusão total")

        if confirmar:
            try:
                sheet_log.clear()

                # recria cabeçalho
                sheet_log.append_row([
                    "Data",
                    "Usuario",
                    "Produto",
                    "Tipo",
                    "Quantidade",
                    "Estoque_final"
                ])

                st.success("✅ Histórico apagado com sucesso!")
                st.rerun()

            except:
                st.error("Erro ao limpar histórico")

st.divider()

# ===============================
# 📊 DADOS
# ===============================
dados = sheet_produtos.get_all_records()
df = pd.DataFrame(dados)

if df.empty:
    st.warning("Nenhum produto cadastrado")
    st.stop()

# 🔥 FUNÇÃO SEGURA
def to_int(valor):
    try:
        return int(float(valor))
    except:
        return 0

# 🔍 PRODUTO
produto = st.selectbox("Selecione o produto", df["Produto"])

linha = df[df["Produto"] == produto].iloc[0]

estoque_atual = to_int(linha.get("Quantidade_inicial", 0))
quantidade_total = to_int(linha.get("Quantidade_total", 0))

st.info(f"📦 Estoque atual: {estoque_atual}")

# ===============================
# 🔥 CONSUMO REAL
# ===============================
dados_log = sheet_log.get_all_records()
df_log = pd.DataFrame(dados_log)

if not df_log.empty:
    df_log = df_log[df_log["Produto"] == produto]
    df_log = df_log[df_log["Tipo"] == "Baixa"]

    if not df_log.empty:
        consumido = df_log["Quantidade"].apply(to_int).sum()
    else:
        consumido = 0
else:
    consumido = 0

# ===============================
# 🔥 PERCENTUAL
# ===============================
if quantidade_total > 0:
    percentual_consumido = (consumido / quantidade_total) * 100
else:
    percentual_consumido = 0

percentual_restante = 100 - percentual_consumido

# ===============================
# 🎯 DASH
# ===============================
st.subheader("📊 Controle de Consumo")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📦 Total", quantidade_total)

with col2:
    st.metric("🔥 Consumido", f"{percentual_consumido:.1f}%")

with col3:
    st.metric("⏳ Restante", f"{percentual_restante:.1f}%")

st.divider()

# ===============================
# 🔢 QUANTIDADE
# ===============================
quantidade = st.number_input("Quantidade", min_value=1)

col_a, col_b = st.columns(2)

# ===============================
# ➕ ENTRADA
# ===============================
with col_a:
    if st.button("➕ Adicionar estoque"):

        nova_qtd = estoque_atual + int(quantidade)

        df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd
        sheet_produtos.update([df.columns.tolist()] + df.values.tolist())

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

# ===============================
# ➖ BAIXA
# ===============================
with col_b:
    if st.button("➖ Dar baixa"):

        if int(quantidade) > estoque_atual:
            st.error("❌ Quantidade maior que o estoque")

        else:
            nova_qtd = estoque_atual - int(quantidade)

            df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd
            sheet_produtos.update([df.columns.tolist()] + df.values.tolist())

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

# ===============================
# 📊 VISUAL
# ===============================
st.subheader("📊 Estoque Atual")
st.dataframe(df, use_container_width=True)
