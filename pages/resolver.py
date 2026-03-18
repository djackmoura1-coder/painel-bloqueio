import smtplib
from email.mime.text import MIMEText

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.title("🔧 Resolver Solicitações de Bloqueio")

# CONEXÃO GOOGLE SHEETS
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
).sheet1

# DADOS
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

if "Email" not in df.columns:
    df["Email"] = ""

if df.empty:
    st.info("Nenhuma ocorrência registrada ainda.")
    st.stop()

# MÉTRICAS
total = len(df)

pendentes_df = df[
    (df["Status"] == "Pendente") |
    (df["Status"] == "Tratativa")
]

pendentes = len(pendentes_df)
bloqueados = len(df[df["Resultado"] == "Bloqueado"])
nao_bloqueados = len(df[df["Resultado"] == "Não bloqueado"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total de ocorrências", total)
col2.metric("Pendentes 🟡", pendentes)
col3.metric("Bloqueados 🟢", bloqueados)
col4.metric("Não bloqueados 🔴", nao_bloqueados)

# BUSCA
st.subheader("🔎 Buscar ocorrência")

busca = st.text_input("Buscar pelo rastreio")

if busca:
    resultado_busca = df[df["Rastreio"].astype(str).str.contains(busca)]
    st.dataframe(resultado_busca, use_container_width=True)

# RESOLVER
st.subheader("Resolver ocorrência")

if not pendentes_df.empty:

    rastreio = st.selectbox(
        "Selecionar rastreio",
        pendentes_df["Rastreio"]
    )

    acao = st.radio(
        "Ação da ocorrência",
        ["Bloqueado", "Não bloqueado", "Tratativa com a logística"]
    )

    if st.button("Finalizar ocorrência"):

        if acao == "Tratativa com a logística":

            df.loc[df["Rastreio"] == rastreio, "Status"] = "Tratativa"
            df.loc[df["Rastreio"] == rastreio, "Resultado"] = ""

            sheet.update(
                [df.columns.values.tolist()] + df.values.tolist()
            )

            st.warning("⚠️ Ocorrência enviada para tratativa logística")

        else:

            df.loc[df["Rastreio"] == rastreio, "Status"] = "Finalizado"
            df.loc[df["Rastreio"] == rastreio, "Resultado"] = acao

            email_cliente = df.loc[df["Rastreio"] == rastreio, "Email"].values[0]

            sheet.update(
                [df.columns.values.tolist()] + df.values.tolist()
            )

            if email_cliente:

                mensagem = f"""
Olá,

A solicitação de bloqueio do pedido {rastreio} foi analisada.

Resultado: {acao}

Sistema de Bloqueio de Pedidos
"""

                msg = MIMEText(mensagem)
                msg["Subject"] = "Resultado da solicitação de bloqueio"
                msg["From"] = "djackmoura1@gmail.com"
                msg["To"] = email_cliente

                try:
                    servidor = smtplib.SMTP("smtp.gmail.com", 587)
                    servidor.starttls()
                    servidor.login("djackmoura1@gmail.com", "xssw hyhl tjao eeyj")
                    servidor.sendmail(
                        "djackmoura1@gmail.com",
                        email_cliente,
                        msg.as_string()
                    )
                    servidor.quit()

                    st.success("✅ Ocorrência finalizada e email enviado!")

                except:
                    st.warning("Ocorrência finalizada, mas não foi possível enviar email.")

            else:
                st.success("Ocorrência finalizada! (sem email cadastrado)")

else:
    st.info("Não existem ocorrências pendentes.")

# HISTÓRICO
st.subheader("📊 Histórico de ocorrências")

def status_color(row):

    if row["Status"] == "Pendente":
        return "🟡 Pendente"

    if row["Status"] == "Tratativa":
        return "🟠 Em tratativa logística"

    if row["Resultado"] == "Bloqueado":
        return "🟢 Bloqueado"

    if row["Resultado"] == "Não bloqueado":
        return "🔴 Não bloqueado"

    return ""

df["Status Visual"] = df.apply(status_color, axis=1)

tabela = df[
    [
        "Data",
        "Responsavel",
        "Rastreio",
        "Motivo",
        "Status Visual"
    ]
]

st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True
)
