import streamlit as st
import pandas as pd

arquivo = "dados_pedidos.xlsx"

df = pd.read_excel(arquivo)
total = len(df)
pendentes = len(df[df["Status"] == "Pendente"])
bloqueados = len(df[df["Resultado"] == "Bloqueado"])
nao_bloqueados = len(df[df["Resultado"] == "Não bloqueado"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de ocorrências", total)
col2.metric("Pendentes 🟡", pendentes)
col3.metric("Bloqueados 🟢", bloqueados)
col4.metric("Não bloqueados 🔴", nao_bloqueados)

st.title("Resolver Solicitações de Bloqueio")

# BUSCA

st.subheader("Buscar ocorrência")

busca = st.text_input("Buscar pelo rastreio")

if busca:
    resultado_busca = df[df["Rastreio"].astype(str).str.contains(busca)]
    st.dataframe(resultado_busca)

# SELECIONAR OCORRÊNCIA

st.subheader("Selecionar ocorrência para resolver")

pendentes = df[df["Status"] == "Pendente"]

if not pendentes.empty:

    rastreio = st.selectbox(
        "Selecionar rastreio",
        pendentes["Rastreio"]
    )

    resultado = st.radio(
        "Resultado do bloqueio",
        ["Bloqueado", "Não bloqueado"]
    )

    if st.button("Finalizar ocorrência"):

        df.loc[df["Rastreio"] == rastreio, "Status"] = "Finalizado"
        df.loc[df["Rastreio"] == rastreio, "Resultado"] = resultado

        df.to_excel(arquivo, index=False)

        st.success("Ocorrência finalizada!")

else:
    st.info("Não existem ocorrências pendentes.")

# HISTÓRICO

st.subheader("Histórico de ocorrências")


def status_color(row):

    if row["Status"] == "Pendente":
        return "🟡 Pendente"

    if row["Resultado"] == "Bloqueado":
        return "🟢 Bloqueado"

    if row["Resultado"] == "Não bloqueado":
        return "🔴 Não bloqueado"

    return ""


df["Status Visual"] = df.apply(status_color, axis=1)

tabela = df[[
    "Data",
    "Responsavel",
    "Rastreio",
    "Motivo",
    "Status Visual"
]]

st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True
)
