import streamlit as st
import pandas as pd
import gspread
import requests

from google.oauth2.service_account import Credentials
from datetime import date


# ===============================
# 🔒 LOGIN
# ===============================
if "logado" not in st.session_state or not st.session_state.logado:
    st.warning("🔒 Faça login")
    st.stop()


st.title("🏠 Solicitar Atualização de Endereço")

st.markdown("""
<style>

/* Botão principal */
div.stButton > button {
    background: #16a34a;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    border: none;
    height: 45px;
    width: 100%;
    transition: 0.25s;
}

/* Ao passar o mouse */
div.stButton > button:hover {
    background: #15803d;
    color: white;
}

/* Ao clicar */
div.stButton > button:active {
    background: #166534;
}

</style>
""", unsafe_allow_html=True)


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

sheet = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).worksheet("enderecos")


# ===============================
# 🧹 CONTROLE DE LIMPEZA
# ===============================
if "limpar_form_endereco" not in st.session_state:
    st.session_state.limpar_form_endereco = False


# ===============================
# 🧹 LIMPEZA SEGURA
# ===============================
if st.session_state.limpar_form_endereco:

    campos_para_limpar = [
        "responsavel",
        "id_assinatura",
        "rastreio",
        "cep",
        "rua",
        "numero",
        "complemento",
        "ponto_referencia",
        "bairro",
        "cidade",
        "uf"
    ]

    for campo in campos_para_limpar:
        if campo in st.session_state:
            st.session_state[campo] = ""

    st.session_state.cep_preenchido = ""
    st.session_state.limpar_form_endereco = False


# ===============================
# 📍 CONTROLE DO CEP
# ===============================
if "cep_preenchido" not in st.session_state:
    st.session_state.cep_preenchido = ""


# ===============================
# 📝 FORMULÁRIO
# ===============================
data = st.date_input(
    "Data",
    value=date.today()
)

responsavel = st.text_input(
    "Responsável",
    key="responsavel"
)

email = st.text_input(
    "Email",
    value=st.session_state.get("email", "")
)

id_assinatura = st.text_input(
    "ID Assinatura",
    key="id_assinatura"
)

rastreio = st.text_input(
    "Rastreio",
    key="rastreio"
)


# ===============================
# 📍 CEP INTELIGENTE
# ===============================
cep = st.text_input(
    "CEP",
    key="cep"
)

cep_limpo = cep.replace("-", "").replace(".", "").strip()

if (
    cep_limpo
    and len(cep_limpo) == 8
    and cep_limpo.isdigit()
    and cep_limpo != st.session_state.cep_preenchido
):

    try:
        url = f"https://viacep.com.br/ws/{cep_limpo}/json/"

        response = requests.get(
            url,
            timeout=10
        )

        if response.status_code == 200:

            dados_cep = response.json()

            if "erro" not in dados_cep:

                # Preenche somente os campos vazios
                if not st.session_state.get("rua"):
                    st.session_state["rua"] = dados_cep.get(
                        "logradouro",
                        ""
                    )

                if not st.session_state.get("bairro"):
                    st.session_state["bairro"] = dados_cep.get(
                        "bairro",
                        ""
                    )

                if not st.session_state.get("cidade"):
                    st.session_state["cidade"] = dados_cep.get(
                        "localidade",
                        ""
                    )

                if not st.session_state.get("uf"):
                    st.session_state["uf"] = dados_cep.get(
                        "uf",
                        ""
                    )

                st.session_state.cep_preenchido = cep_limpo

            else:
                st.warning(
                    "❌ CEP não encontrado. Preencha o endereço manualmente."
                )

        else:
            st.warning(
                "⚠️ Não foi possível consultar o CEP."
            )

    except requests.RequestException:
        st.warning(
            "⚠️ Falha ao consultar o CEP. Preencha o endereço manualmente."
        )


# ===============================
# 🏠 CAMPOS DO ENDEREÇO
# ===============================
rua = st.text_input(
    "Rua",
    key="rua"
)

numero = st.text_input(
    "Número",
    key="numero"
)

complemento = st.text_input(
    "Complemento",
    key="complemento"
)

# 🔥 NOVO CAMPO
ponto_referencia = st.text_input(
    "Ponto de Referência",
    key="ponto_referencia",
    placeholder="Ex.: Próximo ao mercado, portão azul, ao lado da praça"
)

bairro = st.text_input(
    "Bairro",
    key="bairro"
)

cidade = st.text_input(
    "Cidade",
    key="cidade"
)

uf = st.text_input(
    "UF",
    key="uf",
    max_chars=2
)


# ===============================
# 🚀 ENVIAR SOLICITAÇÃO
# ===============================
if st.button(
    "Enviar solicitação",
    use_container_width=True
):

    dados_planilha = sheet.get_all_values()

    if len(dados_planilha) < 2:
        df = pd.DataFrame()

    else:
        df = pd.DataFrame(
            dados_planilha[1:],
            columns=dados_planilha[0]
        )

        df.columns = (
            pd.Series(df.columns)
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace("á", "a")
            .str.replace("ã", "a")
            .str.replace("â", "a")
            .str.replace("ç", "c")
            .str.replace("é", "e")
            .str.replace("ê", "e")
            .str.replace("í", "i")
            .str.replace("ó", "o")
            .str.replace("ô", "o")
            .str.replace("ú", "u")
        )

    rastreio_limpo = rastreio.strip()

    if not rastreio_limpo:
        st.warning("Informe o rastreio.")

    elif (
        "rastreio" in df.columns
        and rastreio_limpo in df["rastreio"].astype(str).str.strip().values
    ):
        st.warning(
            "🚫 Já existe uma solicitação para este rastreio."
        )

    else:

        sheet.append_row(
            [
                str(data),
                responsavel.strip(),
                email.strip(),
                id_assinatura.strip(),
                rastreio_limpo,
                rua.strip(),
                numero.strip(),
                complemento.strip(),
                ponto_referencia.strip(),
                bairro.strip(),
                cidade.strip(),
                uf.strip().upper(),
                cep_limpo,
                "Pendente",
                ""
            ],
            value_input_option="USER_ENTERED"
        )

        st.success(
            "✅ Solicitação enviada com sucesso!"
        )

        st.session_state.limpar_form_endereco = True
        st.rerun()
