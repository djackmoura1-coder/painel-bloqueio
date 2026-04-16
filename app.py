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
# 🎨 CSS FINAL PROFISSIONAL
# ===============================
st.markdown("""
<style>

/* 🔥 REMOVE LIMITAÇÃO DO STREAMLIT */
.block-container {
    padding-top: 80px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* 🔥 HEADER FIXO REAL */
.top-bar {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    width: 100%;
    background-color: #0e1117;
    z-index: 9999;
    padding: 10px 15px;
    border-bottom: 1px solid #262730;

    display: flex;
    justify-content: flex-end;
    align-items: center;
}

/* 🔔 BOTÃO */
.notif-btn {
    font-size: 22px;
    padding: 8px 14px;
    border-radius: 10px;
    background-color: #262730;
    color: white;
}

/* 🔥 ANIMAÇÃO */
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

# 🔥 LOGO
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

try:
    spreadsheet = client.open_by_key("1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao")
except:
    st.error("Erro ao conectar com a planilha")
    st.stop()

# ===============================
# 👤 USUÁRIOS
# ===============================
sheet_users = spreadsheet.worksheet("usuarios")
df_users = pd.DataFrame(sheet_users.get_all_records())

if not df_users.empty:
    df_users.columns = df_users.columns.str.strip().str.lower()

    for col in ["usuario", "senha", "email", "perfil", "departamento"]:
        if col not in df_users.columns:
            df_users[col] = ""

    df_users = df_users.fillna("").astype(str).apply(lambda x: x.str.strip())

# ===============================
# 🔐 SESSION
# ===============================
if "logado" not in st.session_state:
    st.session_state.logado = False

# ===============================
# 🔐 LOGIN
# ===============================
if not st.session_state.logado:

    st.title("🔐 Login do Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):

        usuario = usuario.strip()
        senha = senha.strip()

        if usuario == "admin" and senha == "123456":
            st.session_state.logado = True
            st.session_state.usuario = "admin"
            st.session_state.perfil = "admin"
            st.session_state.departamento = "Admin"
            st.session_state.email = "admin@empresa.com"
            st.rerun()

        user = df_users[df_users["usuario"] == usuario]

        if not user.empty:
            user = user.iloc[0]

            if user["senha"] == senha:
                st.session_state.logado = True
                st.session_state.usuario = usuario
                st.session_state.perfil = user["perfil"]
                st.session_state.departamento = user["departamento"]
                st.session_state.email = user["email"]
                st.rerun()
            else:
                st.error("Senha incorreta")
        else:
            st.error("Usuário não encontrado")

# ===============================
# 🚀 SISTEMA
# ===============================
else:

    # ===============================
    # 🔔 CONTROLE ESTADO
    # ===============================
    if "abrir_notif" not in st.session_state:
        st.session_state.abrir_notif = False

    def toggle_notif():
        st.session_state.abrir_notif = not st.session_state.abrir_notif

    # ===============================
    # 🔔 DADOS NOTIFICAÇÕES
    # ===============================
    try:
        sheet_notif = spreadsheet.worksheet("notificacoes")
        df_notif = pd.DataFrame(sheet_notif.get_all_records())

        if not df_notif.empty:
            df_notif.columns = df_notif.columns.str.strip().str.lower()

            usuario_logado = st.session_state.get("usuario")

            minhas = df_notif[df_notif["para"] == usuario_logado]
            nao_lidas = minhas[minhas["status"] == "nao lida"]

            qtd_notif = len(nao_lidas)
        else:
            qtd_notif = 0
            minhas = pd.DataFrame()

    except:
        qtd_notif = 0
        minhas = pd.DataFrame()

    # 🔥 animação
    classe_animacao = "notif-btn"
    if qtd_notif > 0:
        classe_animacao += " shake"

    # 🔔 TOPO VISUAL
    st.markdown(f"""
    <div class="top-bar">
        <div class="{classe_animacao}">
            🔔 {qtd_notif}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 🔔 BOTÃO FUNCIONAL
    st.button(
        f"🔔 {qtd_notif}",
        key="abrir_notif_btn",
        on_click=toggle_notif
    )

    # 🔔 PAINEL
    if st.session_state.abrir_notif:

        st.markdown("### 📩 Notificações")

        if minhas.empty:
            st.info("Sem notificações")
        else:
            for i, row in minhas.iterrows():

                if row["status"] == "nao lida":
                    st.warning(f"🔔 {row['mensagem']}")
                else:
                    st.info(f"🔕 {row['mensagem']}")

                if row["status"] == "nao lida":
                    if st.button(f"Marcar como lida {i}"):

                        df_notif.loc[i, "status"] = "lida"

                        sheet_notif.update(
                            [df_notif.columns.tolist()] + df_notif.values.tolist()
                        )

                        st.rerun()

    # ===============================
    # SIDEBAR
    # ===============================
    st.sidebar.image("assets/logo_petiko.png", width=150)

    st.sidebar.success(f"👤 {st.session_state.usuario}")
    st.sidebar.write(f"🏢 {st.session_state.departamento}")
    st.sidebar.write(f"📧 {st.session_state.email}")

    if st.sidebar.button("Sair"):
        st.session_state.clear()
        st.rerun()

    # ===============================
    # TÍTULO
    # ===============================
    st.markdown(
        "<h4 style='margin-top:-10px; color: gray;'>📦 Sistema Logístico</h4>",
        unsafe_allow_html=True
    )

    # ===============================
    # MENU
    # ===============================
    st.sidebar.divider()
    st.sidebar.subheader("📂 Menu")

    menu_principal = st.sidebar.radio(
        "Selecione o módulo:",
        ["Atendimento & Logística", "Estoque"]
    )

    if menu_principal == "Atendimento & Logística":
        pagina = st.sidebar.radio(
            "Páginas:",
            [
                "Endereço - Solicitar",
                "Endereço - Resolver",
                "Bloqueio - Solicitar",
                "Bloqueio - Resolver"
            ]
        )

    elif menu_principal == "Estoque":
        pagina = st.sidebar.radio(
            "Páginas:",
            [
                "Cadastro de Produtos",
                "Baixa de Estoque",
                "Planejamento Operacional",
                "Contador de Itens"
            ]
        )

    # ===============================
    # NAVEGAÇÃO
    # ===============================
    try:

        if pagina == "Endereço - Solicitar":
            exec(open("_pages/endereco_solicitar.py").read())

        elif pagina == "Endereço - Resolver":
            exec(open("_pages/endereco_resolver.py").read())

        elif pagina == "Bloqueio - Solicitar":
            exec(open("_pages/solicitar.py").read())

        elif pagina == "Bloqueio - Resolver":
            exec(open("_pages/resolver.py").read())

        elif pagina == "Cadastro de Produtos":
            exec(open("_pages/cadastro_produtos.py").read())

        elif pagina == "Baixa de Estoque":
            exec(open("_pages/baixa_estoque.py").read())

        elif pagina == "Planejamento Operacional":
            exec(open("_pages/planejamento.py").read())

        elif pagina == "Contador de Itens":
            exec(open("_pages/contador_itens.py").read())

    except Exception as e:
        st.error(f"Erro ao carregar página: {e}")
