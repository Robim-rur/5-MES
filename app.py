import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("Scanner Prob5M-Fase – +5% antes de -3% (sem filtro de tendência)")

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

lookahead = 21
alvo = 0.05
stop = 0.03

janela_fase = st.slider("Janela da fase do mês (± dias)", 0, 5, 2)

# =========================================================
# TESTE: alvo antes do stop
# =========================================================

def testa_trade(df, idx):

    entrada = df.iloc[idx]["Close"]
    alvo_px = entrada * (1 + alvo)
    stop_px = entrada * (1 - stop)

    for j in range(idx + 1, min(idx + 1 + lookahead, len(df))):

        hi = df.iloc[j]["High"]
        lo = df.iloc[j]["Low"]

        bate_alvo = hi >= alvo_px
        bate_stop = lo <= stop_px

        if bate_alvo and bate_stop:
            return 0

        if bate_alvo:
            return 1

        if bate_stop:
            return -1

    return 0

# =========================================================
# EXECUÇÃO
# =========================================================

if st.button("Rodar scanner"):

    hoje = datetime.now().day
    resultados = []

    barra = st.progress(0)
    total = len(ativos_scan)

    for i, ticker in enumerate(ativos_scan):

        barra.progress((i + 1) / total)

        try:
            df = yf.download(
                ticker,
                period="12y",
                progress=False,
                auto_adjust=False
            )
        except:
            continue

        if df is None or len(df) < 200:
            continue

        df = df.dropna().copy()

        dias_validos = []
        for d in df.index:
            if abs(d.day - hoje) <= janela_fase:
                dias_validos.append(d)

        ganhos = 0
        perdas = 0

        for d in dias_validos:

            if d not in df.index:
                continue

            idx = df.index.get_loc(d)

            if idx + lookahead >= len(df):
                continue

            r = testa_trade(df, idx)

            if r == 1:
                ganhos += 1
            elif r == -1:
                perdas += 1

        amostras = ganhos + perdas

        if amostras == 0:
            continue

        prob = ganhos / amostras * 100

        resultados.append({
            "Ativo": ticker,
            "Amostras": amostras,
            "Gains": ganhos,
            "Loss": perdas,
            "Probabilidade +5% antes -3% (%)": round(prob, 2)
        })

    if len(resultados) == 0:
        st.warning("Nenhum ativo gerou amostras válidas.")
    else:
        dfres = pd.DataFrame(resultados)
        dfres = dfres.sort_values(
            "Probabilidade +5% antes -3% (%)",
            ascending=False
        )

        st.dataframe(dfres, use_container_width=True)
