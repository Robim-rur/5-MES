import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("Scanner – Probabilidade de Gain antes do Loss (21 pregões)")

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
# FUNÇÃO DE TESTE DE TRADE
# =========================================================

def testa_trade(df, i, gain, loss, max_bars=21):

    entrada = df["Close"].iloc[i]

    alvo = entrada * (1 + gain)
    stop = entrada * (1 - loss)

    max_i = min(i + max_bars, len(df) - 1)

    for j in range(i + 1, max_i + 1):

        h = df["High"].iloc[j]
        l = df["Low"].iloc[j]

        bate_alvo = h >= alvo
        bate_stop = l <= stop

        if bate_alvo and bate_stop:
            # pior caso: stop primeiro
            return 0

        if bate_stop:
            return 0

        if bate_alvo:
            return 1

    return None   # nenhum dos dois aconteceu


# =========================================================
# FUNÇÃO DE BACKTEST
# =========================================================

def roda_estudo(df, gain, loss, max_bars=21):

    resultados = []

    for i in range(len(df) - max_bars - 1):

        r = testa_trade(df, i, gain, loss, max_bars)

        if r is not None:
            resultados.append(r)

    if len(resultados) == 0:
        return None, 0

    prob = np.mean(resultados)

    return prob, len(resultados)


# =========================================================
# EXECUÇÃO
# =========================================================

st.info("Cenários avaliados: 5% x 4%  e  6% x 4%  | janela: 21 pregões")

dados = []

progress = st.progress(0)

for n, ticker in enumerate(ativos_scan):

    progress.progress((n + 1) / len(ativos_scan))

    try:

        df = yf.download(
            ticker,
            period="8y",
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if df is None or df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        colunas = ["Open", "High", "Low", "Close"]

        if not all(c in df.columns for c in colunas):
            continue

        df = df[colunas].dropna().copy()

        if len(df) < 200:
            continue

        p54, am54 = roda_estudo(df, gain=0.05, loss=0.04, max_bars=21)
        p64, am64 = roda_estudo(df, gain=0.06, loss=0.04, max_bars=21)

        if p54 is None and p64 is None:
            continue

        dados.append({
            "Ativo": ticker.replace(".SA", ""),
            "Prob 5%/4%": None if p54 is None else round(p54 * 100, 2),
            "Amostras 5%/4%": am54,
            "Prob 6%/4%": None if p64 is None else round(p64 * 100, 2),
            "Amostras 6%/4%": am64
        })

    except Exception:
        continue


df_res = pd.DataFrame(dados)

if df_res.empty:
    st.warning("Nenhum ativo gerou amostras válidas.")
else:

    df_res = df_res.sort_values(
        by=["Prob 5%/4%", "Prob 6%/4%"],
        ascending=False,
        na_position="last"
    )

    st.dataframe(df_res, use_container_width=True)
