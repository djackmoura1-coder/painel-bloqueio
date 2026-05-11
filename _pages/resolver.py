import smtplib
from email.mime.text import MIMEText

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

# 🔒 BLOQUEIO DE LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login para acessar")
    st.stop()

st.title("🔧 Resolver Solicitações de Bloqueio")

# 🔒 CONTROLE DE PERMISSÃO
bloqueado_resolucao = st.session_state.get("departamento", "").lower() == "atendimento"

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

sheet = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).sheet1

# 📊 DADOS
dados = sheet.get_all_records()
df = pd.DataFrame(dados)

# 🔥 GARANTE COLUNAS
if "Email" not in df.columns:
    df["Email"] = ""

if "Resolvido Por" not in df.columns:
    df["Resolvido Por"] = ""

if df.empty:
    st.info("Nenhuma ocorrência registrada ainda.")
    st.stop()

# 📊 MÉTRICAS
total = len(df)

pendentes_df = df[
    (df["Status"] == "Pendente") |
    (df["Status"] == "Tratativa")
]

pendentes = len(pendentes_df)
bloqueados = len(df[df["Resultado"] == "Bloqueado"])
nao_bloqueados = len(df[df["Resultado"] == "Não bloqueado"])
cancelados = len(df[df["Status"] == "Cancelado"])

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total", total)
col2.metric("Pendentes 🟡", pendentes)
col3.metric("Bloqueados 🟢", bloqueados)
col4.metric("Não bloqueados 🔴", nao_bloqueados)
col5.metric("Cancelados ⚫", cancelados)

# 🔎 BUSCA
st.subheader("🔎 Buscar ocorrência")

busca = st.text_input("Buscar pelo rastreio")

if busca:
    resultado_busca = df[df["Rastreio"].astype(str).str.contains(busca)]
    st.dataframe(resultado_busca, use_container_width=True)

# 🔧 RESOLVER
st.subheader("Resolver ocorrência")

if not pendentes_df.empty:

    rastreio = st.selectbox(
        "Selecionar rastreio",
        pendentes_df["Rastreio"]
    )

    # 🔁 CONTROLE DE CONFIRMAÇÃO
    if "confirmar_cancelamento_bloqueio" not in st.session_state:
        st.session_state.confirmar_cancelamento_bloqueio = False

    if "ultimo_rastreio_bloqueio" not in st.session_state:
        st.session_state.ultimo_rastreio_bloqueio = ""

    if st.session_state.ultimo_rastreio_bloqueio != rastreio:
        st.session_state.confirmar_cancelamento_bloqueio = False
        st.session_state.ultimo_rastreio_bloqueio = rastreio

    # 🔎 STATUS
    status_atual = df.loc[df["Rastreio"] == rastreio, "Status"].values[0]

    # ❌ CANCELAR COM CONFIRMAÇÃO
    if status_atual == "Pendente":

        if not st.session_state.confirmar_cancelamento_bloqueio:
            if st.button("❌ Cancelar solicitação"):
                st.session_state.confirmar_cancelamento_bloqueio = True
                st.warning("⚠️ Tem certeza que deseja cancelar esta solicitação?")

        else:
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✅ Sim, cancelar"):

                    df.loc[df["Rastreio"] == rastreio, "Status"] = "Cancelado"
                    df.loc[df["Rastreio"] == rastreio, "Resultado"] = "Cancelado"
                    df.loc[df["Rastreio"] == rastreio, "Resolvido Por"] = st.session_state.get("nome", "Desconhecido")

                    sheet.update(
                        [df.columns.values.tolist()] + df.values.tolist()
                    )

                    st.success("🚫 Solicitação cancelada com sucesso!")
                    st.session_state.confirmar_cancelamento_bloqueio = False
                    st.rerun()

            with col2:
                if st.button("❌ Não, voltar"):
                    st.session_state.confirmar_cancelamento_bloqueio = False
                    st.info("Cancelamento abortado.")

    acao = st.radio(
        "Ação da ocorrência",
        ["Bloqueado", "Não bloqueado", "Tratativa com a logística"]
    )

    if bloqueado_resolucao:
        st.warning("🚫 Você não tem permissão para resolver ocorrências.")

    botao = st.button("Finalizar ocorrência", disabled=bloqueado_resolucao)

    if botao and not bloqueado_resolucao:

        if acao == "Tratativa com a logística":

            df.loc[df["Rastreio"] == rastreio, "Status"] = "Tratativa"
            df.loc[df["Rastreio"] == rastreio, "Resultado"] = ""
            df.loc[df["Rastreio"] == rastreio, "Resolvido Por"] = st.session_state.get("nome", "Desconhecido")

            sheet.update(
                [df.columns.values.tolist()] + df.values.tolist()
            )

            st.warning("⚠️ Ocorrência enviada para tratativa logística")
            st.rerun()

        else:

            df.loc[df["Rastreio"] == rastreio, "Status"] = "Finalizado"
            df.loc[df["Rastreio"] == rastreio, "Resultado"] = acao
            df.loc[df["Rastreio"] == rastreio, "Resolvido Por"] = st.session_state.get("nome", "Desconhecido")

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
                    st.warning("Finalizado, mas erro ao enviar email.")

            else:
                st.success("Ocorrência finalizada!")

            st.rerun()

else:
    st.info("Não existem ocorrências pendentes.")

# 📊 HISTÓRICO
st.subheader("📊 Histórico de ocorrências")

def status_color(row):

    if row["Status"] == "Pendente":
        return "🟡 Pendente"

    if row["Status"] == "Tratativa":
        return "🟠 Em tratativa logística"

    if row["Status"] == "Cancelado":
        return "⚫ Cancelado"

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
        "Resolvido Por",
        "Email",
        "ID Assinatura",
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
