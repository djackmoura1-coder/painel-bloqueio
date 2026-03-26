import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date
import requests

# 🔒 LOGIN
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()

st.title("🏠 Solicitar Atualização de Endereço")

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

sheet = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("enderecos")

# 🔥 CONTROLE DE LIMPEZA
if "limpar_form_endereco" not in st.session_state:
    st.session_state.limpar_form_endereco = False

# 🔥 LIMPEZA SEGURA
if st.session_state.limpar_form_endereco:
    for campo in [
        "responsavel",
        "id_assinatura",
        "rastreio",
        "rua",
        "numero",
        "complemento",
        "bairro",
        "cidade",
        "uf",
        "cep"
    ]:
        if campo in st.session_state:
            st.session_state[campo] = ""

    st.session_state.limpar_form_endereco = False

# 🔥 CONTROLE CEP (IMPORTANTE)
if "cep_preenchido" not in st.session_state:
    st.session_state.cep_preenchido = ""

# 📝 FORMULÁRIO
data = st.date_input("Data", value=date.today())

responsavel = st.text_input("Responsável", key="responsavel")

email = st.text_input(
    "Email",
    value=st.session_state.get("email", "")
)

id_assinatura = st.text_input("ID Assinatura", key="id_assinatura")
rastreio = st.text_input("Rastreio", key="rastreio")

# 🔥 CEP INTELIGENTE (CORRIGIDO)
cep = st.text_input("CEP", key="cep")

if cep and len(cep.replace("-", "")) == 8 and cep != st.session_state.cep_preenchido:

    try:
        url = f"https://viacep.com.br/ws/{cep}/json/"
        response = requests.get(url)

        if response.status_code == 200:
            dados_cep = response.json()

            if "erro" not in dados_cep:

                # 🔥 SÓ PREENCHE SE ESTIVER VAZIO (NÃO SOBRESCREVE)
                if not st.session_state.get("rua"):
                    st.session_state["rua"] = dados_cep.get("logradouro", "")

                if not st.session_state.get("bairro"):
                    st.session_state["bairro"] = dados_cep.get("bairro", "")

                if not st.session_state.get("cidade"):
                    st.session_state["cidade"] = dados_cep.get("localidade", "")

                if not st.session_state.get("uf"):
                    st.session_state["uf"] = dados_cep.get("uf", "")

                st.session_state.cep_preenchido = cep

            else:
                st.warning("❌ CEP não encontrado. Preencha manualmente.")

        else:
            st.warning("⚠️ Erro ao consultar CEP")

    except:
        st.warning("⚠️ Falha ao consultar CEP")

# 📝 CAMPOS DE ENDEREÇO (EDITÁVEIS)
rua = st.text_input("Rua", key="rua")
numero = st.text_input("Número", key="numero")
complemento = st.text_input("Complemento", key="complemento")
bairro = st.text_input("Bairro", key="bairro")
cidade = st.text_input("Cidade", key="cidade")
uf = st.text_input("UF", key="uf")

# 🚀 ENVIO
if st.button("Enviar solicitação"):

    dados = sheet.get_all_values()

    if len(dados) < 2:
        df = pd.DataFrame()
    else:
        df = pd.DataFrame(dados[1:], columns=dados[0])

        df.columns = (
            pd.Series(df.columns)
            .str.strip()
            .str.lower()
            .str.replace("á", "a")
            .str.replace("ã", "a")
            .str.replace("ç", "c")
            .str.replace("é", "e")
            .str.replace("í", "i")
            .str.replace("ó", "o")
            .str.replace("ú", "u")
        )

    if rastreio == "":
        st.warning("Informe o rastreio")

    elif "rastreio" in df.columns and rastreio in df["rastreio"].astype(str).values:
        st.warning("🚫 Já existe solicitação para este rastreio")

    else:

        sheet.append_row([
            str(data),
            responsavel,
            email,
            id_assinatura,
            rastreio,
            rua,
            numero,
            complemento,
            bairro,
            cidade,
            uf,
            cep,
            "Pendente",
            ""
        ])

        st.success("✅ Solicitação enviada!")

        # 🔥 LIMPA FORMULÁRIO
        st.session_state.limpar_form_endereco = True

        st.rerun()
