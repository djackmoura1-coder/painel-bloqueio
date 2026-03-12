import json
from google.oauth2.service_account import Credentials

scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = Credentials.from_service_account_info(
    json.loads(st.secrets["gcp_service_account"]),
    scopes=scope
)

client = gspread.authorize(credentials)

sheet = client.open_by_key(
    "1IGKJfifqmCdyptPT7INeSjjkW9VnfbQhc4yjKKfwyao"
).sheet1

# LER DADOS

dados = sheet.get_all_records()
df = pd.DataFrame(dados)

if df.empty:
    st.info("Nenhuma ocorrência registrada ainda.")
    st.stop()

# MÉTRICAS

total = len(df)
pendentes = len(df[df["Status"] == "Pendente"])
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

# RESOLVER OCORRÊNCIA

st.subheader("Resolver ocorrência")

pendentes_df = df[df["Status"] == "Pendente"]

if not pendentes_df.empty:

    rastreio = st.selectbox(
        "Selecionar rastreio",
        pendentes_df["Rastreio"]
    )

    resultado = st.radio(
        "Resultado do bloqueio",
        ["Bloqueado", "Não bloqueado"]
    )

    if st.button("Finalizar ocorrência"):

        df.loc[df["Rastreio"] == rastreio, "Status"] = "Finalizado"
        df.loc[df["Rastreio"] == rastreio, "Resultado"] = resultado

        sheet.update(
            [df.columns.values.tolist()] + df.values.tolist()
        )

        st.success("✅ Ocorrência finalizada!")

else:
    st.info("Não existem ocorrências pendentes.")

# HISTÓRICO

st.subheader("📊 Histórico de ocorrências")


def status_color(row):

    if row["Status"] == "Pendente":
        return "🟡 Pendente"

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
