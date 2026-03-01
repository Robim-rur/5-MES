import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Scanner Prob5M-Fase (com filtro semanal EMA 69)")

# =========================================================
# LISTA FIXA DE ATIVOS
# =========================================================

ativos_scan = sorted(set([
"RRRP3.SA","ALOS3.SA","ALPA4.SA","ABEV3.SA","ARZZ3.SA","ASAI3.SA","AZUL4.SA","B3SA3.SA","BBAS3.SA","BBDC3.SA",
"BBDC4.SA","BBSE3.SA","BEEF3.SA","BPAC11.SA","BRAP4.SA","BRFS3.SA","BRKM5.SA","CCRO3.SA","CMIG4.SA","CMIN3.SA",
"COGN3.SA","CPFE3.SA","CPLE6.SA","CRFB3.SA","CSAN3.SA","CSNA3.SA","CYRE3.SA","DXCO3.SA","EGIE3.SA","ELET3.SA",
"ELET6.SA","EMBR3.SA","ENEV3.SA","ENGI11.SA","EQTL3.SA","EZTC3.SA","FLRY3.SA","GGBR4.SA","GOAU4.SA","GOLL4.SA",
"HAPV3.SA","HYPE3.SA","ITSA4.SA","ITUB4.SA","JBSS3.SA","KLBN11.SA","LREN3.SA","LWSA3.SA","MGLU3.SA","MRFG3.SA",
"MRVE3.SA","MULT3.SA","NTCO3.SA","PETR3.SA","PETR4.SA","PRIO3.SA","RADL3.SA","RAIL3.SA","RAIZ4.SA","RENT3.SA",
"RECV3.SA","SANB11.SA","SBSP3.SA","SLCE3.SA","SMTO3.SA","SUZB3.SA","TAEE11.SA","TIMS3.SA","TOTS3.SA","TRPL4.SA",
"UGPA3.SA","USIM5.SA","VALE3.SA","VIVT3.SA","VIVA3.SA","WEGE3.SA","YDUQ3.SA","AURE3.SA","BHIA3.SA","CASH3.SA",
"CVCB3.SA","DIRR3.SA","ENAT3.SA","GMAT3.SA","IFCM3.SA","INTB3.SA","JHSF3.SA","KEPL3.SA","MOVI3.SA","ORVR3.SA",
"PETZ3.SA","PLAS3.SA","POMO4.SA","POSI3.SA","RANI3.SA","RAPT4.SA","STBP3.SA","TEND3.SA","TUPY3.SA",
"BRSR6.SA","CXSE3.SA","AAPL34.SA","AMZO34.SA","GOGL34.SA","MSFT34.SA","TSLA34.SA","META34.SA","NFLX34.SA",
"NVDC34.SA","MELI34.SA","BABA34.SA","DISB34.SA","PYPL34.SA","JNJB34.SA","PGCO34.SA","KOCH34.SA","VISA34.SA",
"WMTB34.SA","NIKE34.SA","ADBE34.SA","AVGO34.SA","CSCO34.SA","COST34.SA","CVSH34.SA","GECO34.SA","GSGI34.SA",
"HDCO34.SA","INTC34.SA","JPMC34.SA","MAEL34.SA","MCDP34.SA","MDLZ34.SA","MRCK34.SA","ORCL34.SA","PEP334.SA",
"PFIZ34.SA","PMIC34.SA","QCOM34.SA","SBUX34.SA","TGTB34.SA","TMOS34.SA","TXN34.SA","UNHH34.SA","UPSB34.SA",
"VZUA34.SA","ABTT34.SA","AMGN34.SA","AXPB34.SA","BAOO34.SA","CATP34.SA","HONB34.SA","BOVA11.SA","IVVB11.SA",
"SMAL11.SA","HASH11.SA","GOLD11.SA","GARE11.SA","HGLG11.SA","XPLG11.SA","VILG11.SA","BRCO11.SA","BTLG11.SA",
"XPML11.SA","VISC11.SA","HSML11.SA","MALL11.SA","KNRI11.SA","JSRE11.SA","PVBI11.SA","HGRE11.SA","MXRF11.SA",
"KNCR11.SA","KNIP11.SA","CPTS11.SA","IRDM11.SA","DIVO11.SA","NDIV11.SA","SPUB11.SA"
]))

# =========================================================
# PARÂMETROS
# =========================================================

st.sidebar.header("Parâmetros")

janela_fase = st.sidebar.slider(
    "Janela da fase do mês (± dias)",
    min_value=0,
    max_value=5,
    value=2
)

anos_historico = st.sidebar.slider(
    "Anos de histórico",
    min_value=3,
    max_value=15,
    value=8
)

dias_alvo = 21
alvo = 1.05
ema_periodos = 69

st.sidebar.write("Sucesso: +5% em até 21 pregões")
st.sidebar.write("Filtro: semanal acima da EMA 69")

# =========================================================

hoje = datetime.now().date()
dia_referencia = hoje.day

# =========================================================
# FUNÇÃO: FILTRO SEMANAL EMA 69
# =========================================================

def passa_filtro_semanal(ticker):

    dfw = yf.download(
        ticker,
        period="5y",
        interval="1wk",
        auto_adjust=False,
        progress=False
    )

    if dfw is None or len(dfw) < ema_periodos + 5:
        return False

    dfw = dfw.dropna()

    dfw["EMA69"] = dfw["Close"].ewm(span=ema_periodos, adjust=False).mean()

    close_atual = dfw["Close"].iloc[-1]
    ema_atual = dfw["EMA69"].iloc[-1]

    return close_atual > ema_atual


# =========================================================
# FUNÇÃO PRINCIPAL
# =========================================================

@st.cache_data(show_spinner=False)
def calcula_probabilidades(tickers, anos, janela_fase, dia_ref):

    fim = pd.Timestamp.today()
    inicio = fim - pd.DateOffset(years=anos)

    dados = yf.download(
        tickers,
        start=inicio,
        end=fim,
        group_by="ticker",
        auto_adjust=False,
        threads=True,
        progress=False
    )

    resultados = []

    for ticker in tickers:

        try:
            df = dados[ticker].copy()
        except Exception:
            continue

        if df is None or len(df) < 150:
            continue

        # -----------------------------
        # filtro semanal EMA 69
        # -----------------------------
        try:
            if not passa_filtro_semanal(ticker):
                continue
        except Exception:
            continue

        df = df.dropna()
        df["day"] = df.index.day

        mask_fase = (
            (df["day"] >= dia_ref - janela_fase) &
            (df["day"] <= dia_ref + janela_fase)
        )

        idx_validos = df[mask_fase].index

        total = 0
        sucessos = 0

        for data in idx_validos:

            pos = df.index.get_loc(data)

            if isinstance(pos, slice):
                continue

            if pos + 1 >= len(df):
                continue

            fim_janela = min(pos + dias_alvo, len(df) - 1)

            close_entrada = df.iloc[pos]["Close"]
            max_high = df.iloc[pos + 1:fim_janela + 1]["High"].max()

            total += 1

            if max_high >= close_entrada * alvo:
                sucessos += 1

        if total == 0:
            continue

        prob = sucessos / total * 100.0

        resultados.append({
            "Ativo": ticker,
            "Amostras": total,
            "Sucessos": sucessos,
            "Probabilidade_%": round(prob, 2)
        })

    df_res = pd.DataFrame(resultados)

    if df_res.empty:
        return df_res

    df_res = df_res.sort_values(
        by=["Probabilidade_%", "Amostras"],
        ascending=[False, False]
    ).reset_index(drop=True)

    df_res.insert(0, "Rank", df_res.index + 1)

    return df_res


# =========================================================
# EXECUÇÃO
# =========================================================

st.write(f"Dia de referência da fase do mês: **{dia_referencia}**")

if st.button("Rodar scanner"):

    with st.spinner("Baixando dados e calculando probabilidades..."):
        tabela = calcula_probabilidades(
            ativos_scan,
            anos_historico,
            janela_fase,
            dia_referencia
        )

    if tabela.empty:
        st.warning("Nenhum ativo passou no filtro semanal.")
    else:
        st.dataframe(tabela, use_container_width=True)

        st.download_button(
            "Baixar CSV",
            tabela.to_csv(index=False).encode("utf-8"),
            "scanner_prob5m_fase_semanal.csv",
            "text/csv"
        )
