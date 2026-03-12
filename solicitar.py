import streamlit as st
import pandas as pd
from datetime import date
import os

arquivo = "dados_pedidos.xlsx"

if not os.path.exists(arquivo):
    df = pd.DataFrame(columns=[
        "Data",
        "Responsavel",
        "Rastreio",
        "Motivo",
        "Status",
        "Resultado"
    ])
    df.to_excel(arquivo, index=False)

df = pd.read_excel(arquivo)

st.title("Solicitar Bloqueio de Pedido")

data = st.date_input("Data", value=date.today())

responsavel = st.text_input("Responsável solicitante")

rastreio = st.text_input("Rastreio do pedido")

motivo = st.text_area("Motivo do bloqueio")

if st.button("Enviar solicitação"):

    novo = pd.DataFrame({
        "Data": [data],
        "Responsavel": [responsavel],
        "Rastreio": [rastreio],
        "Motivo": [motivo],
        "Status": ["Pendente"],
        "Resultado": [""]
    })

    df = pd.concat([df, novo], ignore_index=True)

    df.to_excel(arquivo, index=False)

    st.success("Solicitação enviada!")