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
# 🔥 RESET TOTAL
# ===============================
st.divider()
st.subheader("⚠️ Reset Completo da Operação")

col_reset1, col_reset2 = st.columns([2,1])

with col_reset2:
    if st.button("🗑️ RESET TOTAL", use_container_width=True):

        confirmar = st.checkbox("Confirmar exclusão TOTAL (não pode desfazer)")

        if confirmar:
            try:
                # limpa histórico
                sheet_log.clear()
                sheet_log.append_row([
                    "Data","Usuario","Produto","Tipo","Quantidade","Estoque_final"
                ])

                # limpa produtos
                sheet_produtos.clear()
                sheet_produtos.append_row([
                    "Produto","Trilha","Quantidade_inicial","Quantidade_total","Quantidade_base"
                ])

                st.success("✅ Sistema resetado com sucesso!")
                st.rerun()

            except:
                st.error("Erro ao executar reset")

st.divider()

# ===============================
# 📊 DADOS PRODUTOS
# ===============================
dados = sheet_produtos.get_all_records()

if len(dados) == 0:
    df = pd.DataFrame()
else:
    df = pd.DataFrame(dados)

if df.empty:
    st.warning("Nenhum produto cadastrado. Sistema vazio após reset.")
    st.stop()

# ===============================
# 🔧 FUNÇÃO SEGURA
# ===============================
def to_int(valor):
    try:
        return int(float(valor))
    except:
        return 0

# ===============================
# 🔍 PRODUTO
# ===============================
produto = st.selectbox("Selecione o produto", df["Produto"])

linha = df[df["Produto"] == produto].iloc[0]

estoque_atual = to_int(linha.get("Quantidade_inicial", 0))
quantidade_total = to_int(linha.get("Quantidade_total", 0))
quantidade_base = to_int(linha.get("Quantidade_base", 0))

st.info(f"📦 Estoque atual: {estoque_atual}")

# ===============================
# 📊 CONSUMO (HISTÓRICO)
# ===============================
dados_log = sheet_log.get_all_records()

if len(dados_log) == 0:
    df_log = pd.DataFrame()
else:
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
# 📊 RESTANTE (%)
# ===============================
if quantidade_total > 0:
    percentual_restante = (estoque_atual / quantidade_total) * 100
else:
    percentual_restante = 0

# ===============================
# 🎯 DASH
# ===============================
st.subheader("📊 Controle de Consumo")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Estoque Atual", estoque_atual)

with col2:
    st.metric("📊 Total Disponível", quantidade_total)

with col3:
    st.metric("🔥 Consumido (Qtd)", consumido)

with col4:
    st.metric("⏳ Restante (%)", f"{percentual_restante:.1f}%")

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
        novo_total = quantidade_total + int(quantidade)

        df.loc[df["Produto"] == produto, "Quantidade_inicial"] = nova_qtd
        df.loc[df["Produto"] == produto, "Quantidade_total"] = novo_total

        sheet_produtos.update([df.columns.tolist()] + df.values.tolist())

        sheet_log.append_row([
            str(datetime.now()),
            str(st.session_state.get("usuario")),
            str(produto),
            "Entrada",
            int(quantidade),
            int(nova_qtd)
        ])

        st.success(f"Entrada realizada! Novo estoque: {nova_qtd}")
        st.rerun()

# ===============================
# ➖ BAIXA
# ===============================
with col_b:
    if st.button("➖ Dar baixa"):

        if int(quantidade) > estoque_atual:
            st.error("Quantidade maior que o estoque")

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

            st.success(f"Baixa realizada! Novo estoque: {nova_qtd}")
            st.rerun()

# ===============================
# 📊 VISUAL
# ===============================
st.subheader("📊 Estoque Atual")
st.dataframe(df, use_container_width=True)
