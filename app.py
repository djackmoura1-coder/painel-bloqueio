import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="Sistema de Bloqueio",
    page_icon="assets/logo_petiko.png",
    layout="wide"
)

# ===============================
# 🎨 CSS
# ===============================
st.markdown("""
<style>
.block-container {
    padding-top: 80px !important;
}

.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background-color: #0e1117;
    z-index: 9999;
    padding: 10px 15px;
    border-bottom: 1px solid #262730;
    display: flex;
    justify-content: flex-end;
}

.notif-btn {
    font-size: 22px;
    padding: 8px 14px;
    border-radius: 10px;
    background-color: #262730;
    color: white;
}

@keyframes shake {
    0% { transform: rotate(0deg); }
    25% { transform: rotate(10deg); }
    50% { transform: rotate(-10deg); }
    75% { transform: rotate(8deg); }
    100% { transform: rotate(0deg); }
}

.shake {
    animation: shake 0.8s infinite;
}
</style>
""", unsafe_allow_html=True)

st.image("assets/logo_petiko.png", width=180)

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

# ===============================
# 🔐 LOGIN MOCK (ajuste se quiser)
# ===============================
if "logado" not in st.session_state:
    st.session_state.logado = True
    st.session_state.usuario = "Djack"
    st.session_state.email = "djack-moura@petiko.com.br"

# ===============================
# 🔔 CONTROLE
# ===============================
if "abrir_notif" not in st.session_state:
    st.session_state.abrir_notif = False

def toggle_notif():
    st.session_state.abrir_notif = not st.session_state.abrir_notif

# ===============================
# 🔔 DADOS
# ===============================
try:
    sheet_notif = spreadsheet.worksheet("notificacoes")
    df_notif = pd.DataFrame(sheet_notif.get_all_records())

    if not df_notif.empty:

        df_notif.columns = df_notif.columns.str.strip().str.lower()

        # 🔥 CORRIGE NOME
        if "menssagem" in df_notif.columns:
            df_notif["mensagem_final"] = df_notif["menssagem"]
        else:
            df_notif["mensagem_final"] = df_notif.get("mensagem", "")

        # 🔥 GARANTE STATUS
        if "status" not in df_notif.columns:
            df_notif["status"] = "nao lida"

        usuario = st.session_state.usuario.lower()
        email = st.session_state.email.lower()

        # 🔥 FILTRO FLEXÍVEL
        df_notif["para"] = df_notif["para"].astype(str).str.lower()

        minhas = df_notif[
            (df_notif["para"] == usuario) |
            (df_notif["para"] == email)
        ]

        nao_lidas = minhas[minhas["status"] == "nao lida"]

        qtd_notif = len(nao_lidas)

    else:
        qtd_notif = 0
        minhas = pd.DataFrame()

except:
    qtd_notif = 0
    minhas = pd.DataFrame()

# ===============================
# 🔔 TOPO
# ===============================
classe = "notif-btn"
if qtd_notif > 0:
    classe += " shake"

st.markdown(f"""
<div class="top-bar">
    <div class="{classe}">
        🔔 {qtd_notif}
    </div>
</div>
""", unsafe_allow_html=True)

st.button("🔔", on_click=toggle_notif)

# ===============================
# 🔔 PAINEL
# ===============================
if st.session_state.abrir_notif:

    st.subheader("📩 Notificações")

    if minhas.empty:
        st.warning("Nenhuma notificação encontrada para você")
    else:
        for i, row in minhas.iterrows():

            msg = row.get("mensagem_final", "")

            if row["status"] == "nao lida":
                st.warning(f"🔔 {msg}")
            else:
                st.info(f"🔕 {msg}")
