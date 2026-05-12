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

# 🔐 CONTROLE DE PERMISSÃO
departamento = str(st.session_state.get("departamento", "")).lower()
pode_editar = departamento not in ["atendimento", "faturamento"]

if not pode_editar:
    st.warning("🔒 Você possui acesso apenas de visualização")

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

sheet_produtos = spreadsheet.worksheet("produtos")
sheet_log = spreadsheet.worksheet("movimentacoes")

# ===============================
# 🔥 RESET TOTAL
# ===============================
st.divider()
st.subheader("⚠️ Reset Completo da Operação")

col_reset1, col_reset2 = st.columns([2,1])

with col_reset2:
    if st.button("🗑️ RESET TOTAL", use_container_width=True, disabled=not pode_editar):

        confirmar = st.checkbox("Confirmar exclusão TOTAL")

        if confirmar:
            sheet_log.clear()
            sheet_log.append_row(["data","usuario","produto","tipo","quantidade","estoque_final"])

            sheet_produtos.clear()
            sheet_produtos.append_row([
                "produto",
                "trilha",
                "quantidade_inicial",
                "quantidade_total",
                "quantidade_base"
            ])

            st.success("Sistema resetado!")
            st.rerun()

st.divider()

# ===============================
# 📊 DADOS
# ===============================
dados = sheet_produtos.get_all_records()
df = pd.DataFrame(dados)

if df.empty:
    st.warning("Nenhum produto cadastrado.")
    st.stop()

df.columns = df.columns.str.strip().str.lower()

def to_int(valor):
    try:
        return int(float(valor))
    except:
        return 0

# ===============================
# 🚨 ALERTA GERAL
# ===============================
itens_criticos = df[df["quantidade_inicial"].apply(to_int) <= 200]

if not itens_criticos.empty:
    st.warning(f"⚠️ {len(itens_criticos)} itens com estoque baixo (≤ 200 unidades)")

# ===============================
# 🔍 PRODUTO
# ===============================
produto = st.selectbox("Selecione o produto", df["produto"])

linha = df[df["produto"] == produto].iloc[0]

# 🔥 CONCEITOS
estoque_atual = to_int(linha.get("quantidade_inicial", 0))
quantidade_total = to_int(linha.get("quantidade_total", 0))
quantidade_base = to_int(linha.get("quantidade_base", 0))

# 🚨 ALERTA INDIVIDUAL
if estoque_atual <= 200:
    st.warning(f"⚠️ Estoque baixo: {estoque_atual} unidades disponíveis")
else:
    st.info(f"📦 Saldo disponível: {estoque_atual} unidades")

# ===============================
# 📊 CONSUMO
# ===============================
dados_log = sheet_log.get_all_records()
df_log = pd.DataFrame(dados_log)

if not df_log.empty:

    df_log.columns = df_log.columns.str.strip().str.lower()

    df_log = df_log[
        (df_log["produto"] == produto) &
        (df_log["tipo"] == "baixa")
    ]

    consumido = (
        df_log["quantidade"].apply(to_int).sum()
        if not df_log.empty else 0
    )

else:
    consumido = 0

# ===============================
# 🎯 DASH
# ===============================
st.subheader("📊 Controle")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📦 Saldo Atual", estoque_atual)
col2.metric("📥 Quantidade Total", quantidade_total)
col3.metric("🏁 Quantidade Base", quantidade_base)
col4.metric("📤 Consumido", consumido)

st.divider()

# ===============================
# 🔢 INPUT
# ===============================
quantidade = st.number_input(
    "Quantidade",
    min_value=1,
    disabled=not pode_editar
)

col_a, col_b = st.columns(2)

# ===============================
# ➕ ENTRADA
# ===============================
with col_a:

    if st.button("➕ Entrada", disabled=not pode_editar):

        # 🔥 SALDO DISPONÍVEL
        nova_qtd = estoque_atual + quantidade

        # 🔥 TOTAL ACUMULADO
        novo_total = quantidade_total + quantidade

        df.loc[df["produto"] == produto, "quantidade_inicial"] = nova_qtd
        df.loc[df["produto"] == produto, "quantidade_total"] = novo_total

        sheet_produtos.update(
            [df.columns.tolist()] + df.values.tolist()
        )

        sheet_log.append_row([
            str(datetime.now()),
            st.session_state.get("usuario"),
            produto,
            "entrada",
            quantidade,
            nova_qtd
        ])

        st.success("Entrada realizada com sucesso!")
        st.rerun()

# ===============================
# ➖ BAIXA
# ===============================
with col_b:

    if st.button("➖ Baixa", disabled=not pode_editar):

        if quantidade > estoque_atual:

            st.error("Quantidade maior que o estoque")

        else:

            # 🔥 REDUZ SOMENTE O SALDO
            nova_qtd = estoque_atual - quantidade

            df.loc[df["produto"] == produto, "quantidade_inicial"] = nova_qtd

            sheet_produtos.update(
                [df.columns.tolist()] + df.values.tolist()
            )

            sheet_log.append_row([
                str(datetime.now()),
                st.session_state.get("usuario"),
                produto,
                "baixa",
                quantidade,
                nova_qtd
            ])

            st.success("Baixa realizada com sucesso!")
            st.rerun()

# ===============================
# 📊 TABELA
# ===============================
st.subheader("📊 Visão Geral do Estoque")

def destacar_estoque(row):

    if to_int(row["quantidade_inicial"]) <= 200:
        return ["background-color: yellow; color: black"] * len(row)

    return [""] * len(row)

st.dataframe(
    df.style.apply(destacar_estoque, axis=1),
    use_container_width=True
)
