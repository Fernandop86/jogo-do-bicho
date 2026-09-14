"""
Dashboard Jogo do Bicho 2024 — Visual profissional + Backtest.
Tema escuro com cards coloridos e análise de ganhos/perdas.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from motor.importacao import importar_csv_largo


st.set_page_config(
    page_title="Jogo do Bicho 2024",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =============================================================
# CONSTANTES DO BACKTEST
# =============================================================
VALOR_MILHAR = 2.00
VALOR_CENTENA = 1.00
VALOR_GRUPO = 1.00
VALOR_DEZENA = 1.00
CUSTO_DIARIO = 5.00

RETORNO_MILHAR = 4000.0
RETORNO_CENTENA = 600.0
RETORNO_GRUPO = 18.0
RETORNO_DEZENA = 60.0


# =============================================================
# CSS CUSTOMIZADO
# =============================================================
CSS = """
<style>
  .stApp {
    background: linear-gradient(180deg, #0B0F19 0%, #0F1422 100%);
  }
  .main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1400px;
  }

  .titulo-principal {
    font-size: 38px;
    font-weight: 800;
    background: linear-gradient(90deg, #A78BFA 0%, #60A5FA 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
  }
  .subtitulo-principal {
    color: #94A3B8;
    font-size: 15px;
    margin-top: 4px;
    margin-bottom: 24px;
  }

  .kpi-card {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
    border-radius: 16px;
    padding: 20px 22px;
    border: 1px solid #312E81;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 32px rgba(124, 58, 237, 0.3);
  }
  .kpi-card.roxo { background: linear-gradient(135deg, #4C1D95 0%, #6D28D9 100%); border-color: #7C3AED; }
  .kpi-card.azul { background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%); border-color: #3B82F6; }
  .kpi-card.verde { background: linear-gradient(135deg, #064E3B 0%, #059669 100%); border-color: #10B981; }
  .kpi-card.laranja { background: linear-gradient(135deg, #7C2D12 0%, #EA580C 100%); border-color: #F97316; }
  .kpi-card.vermelho { background: linear-gradient(135deg, #7F1D1D 0%, #DC2626 100%); border-color: #EF4444; }

  .kpi-icone { font-size: 24px; margin-bottom: 8px; display: block; }
  .kpi-label {
    color: rgba(255,255,255,0.75);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-weight: 600;
    margin-bottom: 6px;
  }
  .kpi-valor {
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 800;
    font-family: 'Courier New', monospace;
    letter-spacing: 1px;
    line-height: 1.1;
  }
  .kpi-sub { color: rgba(255,255,255,0.6); font-size: 12px; margin-top: 6px; }

  .secao-titulo {
    color: #E5E7EB;
    font-size: 20px;
    font-weight: 700;
    margin-top: 24px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .secao-titulo::before {
    content: '';
    display: inline-block;
    width: 4px;
    height: 22px;
    background: linear-gradient(180deg, #A78BFA, #60A5FA);
    border-radius: 2px;
  }

  .footer {
    text-align: center;
    color: #64748B;
    font-size: 12px;
    padding: 20px 0;
    margin-top: 20px;
    border-top: 1px solid #1E293B;
  }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# =============================================================
# FUNÇÕES
# =============================================================
def encontrar_csv():
    candidatos = [
        Path("dados/jogo_do_bicho_2024.csv"),
        Path("jogo_do_bicho_2024.csv"),
        Path(r"D:\Jogo do bicho\dados\jogo_do_bicho_2024.csv"),
        Path(r"D:\Raspagem de Dados jogo do bicho\dados\jogo_do_bicho_2024.csv"),
    ]
    for c in candidatos:
        if c.exists():
            return c
    raise FileNotFoundError("CSV não encontrado.")


@st.cache_data(show_spinner=False)
def carregar_dados(caminho_str):
    df = importar_csv_largo(caminho_str)

    rename_map = {}
    for antigo, novo in [("grupo_csv", "grupo"), ("bicho_csv", "bicho"), ("centena_csv", "centena")]:
        if antigo in df.columns and novo not in df.columns:
            rename_map[antigo] = novo
    if rename_map:
        df = df.rename(columns=rename_map)

    if "dezena" not in df.columns:
        df["dezena"] = df["milhar"].astype(str).str[-2:]

    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df = df.dropna(subset=["data"])
    df = df.sort_values(["data", "modalidade", "premio"]).reset_index(drop=True)
    return df


def calcular_sugestoes(df, data_ref):
    passado = df[df["data"].dt.date < data_ref]
    if len(passado) < 50:
        return None
    return {
        "milhar": passado["milhar"].astype(str).value_counts().idxmax(),
        "milhar_freq": int(passado["milhar"].astype(str).value_counts().max()),
        "grupo": passado["grupo"].astype(str).value_counts().idxmax(),
        "grupo_freq": int(passado["grupo"].astype(str).value_counts().max()),
        "dezena": passado["dezena"].astype(str).value_counts().idxmax(),
        "dezena_freq": int(passado["dezena"].astype(str).value_counts().max()),
        "centena": passado["centena"].astype(str).value_counts().idxmax(),
        "centena_freq": int(passado["centena"].astype(str).value_counts().max()),
        "n_passado": len(passado),
    }


@st.cache_data(show_spinner=False)
def executar_backtest(caminho_str):
    """
    Executa backtest dia a dia:
    - Calcula sugestões usando APENAS dados anteriores
    - Compara com o resultado real do dia
    - Retorna DataFrame com data, ganho, lucro, acertos
    """
    df = carregar_dados(caminho_str)
    datas = sorted(df["data"].dt.date.unique())

    registros = []

    for i, data in enumerate(datas):
        if i < 5:
            continue

        sugestoes = calcular_sugestoes(df, data)
        if sugestoes is None:
            continue

        resultado_dia = df[df["data"].dt.date == data]
        if resultado_dia.empty:
            continue

        milhares_dia = set(resultado_dia["milhar"].astype(str).str.zfill(4))
        centenas_dia = set(resultado_dia["centena"].astype(str).str.zfill(3))
        dezenas_dia = set(resultado_dia["dezena"].astype(str).str.zfill(2))
        grupos_dia = set(resultado_dia["grupo"].astype(str).str.zfill(2))

        ganho = 0.0
        acertos = []

        if sugestoes["milhar"].zfill(4) in milhares_dia:
            ganho += VALOR_MILHAR * RETORNO_MILHAR
            acertos.append("milhar")
        if sugestoes["centena"].zfill(3) in centenas_dia:
            ganho += VALOR_CENTENA * RETORNO_CENTENA
            acertos.append("centena")
        if sugestoes["dezena"].zfill(2) in dezenas_dia:
            ganho += VALOR_DEZENA * RETORNO_DEZENA
            acertos.append("dezena")
        if sugestoes["grupo"].zfill(2) in grupos_dia:
            ganho += VALOR_GRUPO * RETORNO_GRUPO
            acertos.append("grupo")

        registros.append({
            "data": data,
            "milhar_sug": sugestoes["milhar"],
            "grupo_sug": sugestoes["grupo"],
            "dezena_sug": sugestoes["dezena"],
            "centena_sug": sugestoes["centena"],
            "ganho": round(ganho, 2),
            "lucro": round(ganho - CUSTO_DIARIO, 2),
            "acertos": ", ".join(acertos) if acertos else "—",
        })

    resultado = pd.DataFrame(registros)
    return resultado


# =============================================================
# CARREGAR DADOS
# =============================================================
try:
    caminho_csv = encontrar_csv()
    df = carregar_dados(str(caminho_csv))
except Exception as e:
    st.error(f"Erro ao carregar: {e}")
    st.stop()


# =============================================================
# CABEÇALHO
# =============================================================
st.markdown(
    '<h1 class="titulo-principal">🎰 Jogo do Bicho 2024</h1>'
    '<p class="subtitulo-principal">Análise estatística honesta — sem promessas, só dados.</p>',
    unsafe_allow_html=True,
)


# =============================================================
# FILTROS
# =============================================================
st.markdown('<div class="secao-titulo">🎛️ Filtros</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([1, 1, 1, 1])

data_min = df["data"].min().date()
data_max = df["data"].max().date()

with f1:
    data_inicio = st.date_input(
        "📅 Data inicial", value=data_min,
        min_value=data_min, max_value=data_max
    )
with f2:
    data_fim = st.date_input(
        "📅 Data final", value=data_max,
        min_value=data_min, max_value=data_max
    )
with f3:
    modalidades = ["Todas"] + sorted(df["modalidade"].unique().tolist())
    modalidade_sel = st.selectbox("🏆 Modalidade", modalidades)
with f4:
    data_ref = st.date_input(
        "🎯 Data de referência",
        value=data_max, min_value=data_min, max_value=data_max
    )


df_filtrado = df[
    (df["data"].dt.date >= data_inicio) &
    (df["data"].dt.date <= data_fim)
].copy()

if modalidade_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["modalidade"] == modalidade_sel]


# =============================================================
# SUGESTÕES DO DIA
# =============================================================
st.markdown(
    f'<div class="secao-titulo">💡 Sugestões para {data_ref.strftime("%d/%m/%Y")}</div>',
    unsafe_allow_html=True,
)

sug = calcular_sugestoes(df, data_ref)

if sug:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card roxo">
          <span class="kpi-icone">💡</span>
          <div class="kpi-label">Milhar</div>
          <div class="kpi-valor">{sug['milhar']}</div>
          <div class="kpi-sub">Freq. histórica: {sug['milhar_freq']}x</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card azul">
          <span class="kpi-icone">🎯</span>
          <div class="kpi-label">Grupo</div>
          <div class="kpi-valor">{sug['grupo']}</div>
          <div class="kpi-sub">Freq. histórica: {sug['grupo_freq']}x</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card verde">
          <span class="kpi-icone">🎲</span>
          <div class="kpi-label">Dezena</div>
          <div class="kpi-valor">{sug['dezena']}</div>
          <div class="kpi-sub">Freq. histórica: {sug['dezena_freq']}x</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card laranja">
          <span class="kpi-icone">💎</span>
          <div class="kpi-label">Centena</div>
          <div class="kpi-valor">{sug['centena']}</div>
          <div class="kpi-sub">Freq. histórica: {sug['centena_freq']}x</div>
        </div>
        """, unsafe_allow_html=True)

    st.caption(f"Baseado em {sug['n_passado']:,} prêmios anteriores à data selecionada.")


# =============================================================
# BACKTEST — GANHOS E LUCROS
# =============================================================
st.markdown('<div class="secao-titulo">💰 Backtest — Ganhos e Lucros</div>', unsafe_allow_html=True)

with st.spinner("Executando backtest..."):
    bt = executar_backtest(str(caminho_csv))


if bt.empty:
    st.warning("Backtest sem dados suficientes.")
else:
    bt_filtrado = bt[
        (bt["data"] >= data_inicio) &
        (bt["data"] <= data_fim)
    ].copy()

    total_dias = len(bt_filtrado)
    total_gasto = total_dias * CUSTO_DIARIO
    total_ganho = bt_filtrado["ganho"].sum()
    lucro_liquido = total_ganho - total_gasto
    dias_com_acerto = (bt_filtrado["ganho"] > 0).sum()
    maior_ganho = bt_filtrado["ganho"].max()
    retorno_pct = (total_ganho / total_gasto * 100) if total_gasto > 0 else 0

    # Cor do card de lucro: verde se positivo, vermelho se negativo
    classe_lucro = "verde" if lucro_liquido >= 0 else "vermelho"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card azul">
          <span class="kpi-icone">💸</span>
          <div class="kpi-label">Total Gasto</div>
          <div class="kpi-valor">R$ {total_gasto:,.0f}</div>
          <div class="kpi-sub">{total_dias} dias × R$ 5,00</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card roxo">
          <span class="kpi-icone">🏆</span>
          <div class="kpi-label">Total Ganho</div>
          <div class="kpi-valor">R$ {total_ganho:,.0f}</div>
          <div class="kpi-sub">{retorno_pct:.1f}% do gasto</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card {classe_lucro}">
          <span class="kpi-icone">📊</span>
          <div class="kpi-label">Lucro Líquido</div>
          <div class="kpi-valor">R$ {lucro_liquido:,.0f}</div>
          <div class="kpi-sub">resultado final</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card laranja">
          <span class="kpi-icone">🎯</span>
          <div class="kpi-label">Dias com Acerto</div>
          <div class="kpi-valor">{dias_com_acerto}</div>
          <div class="kpi-sub">de {total_dias} dias ({100*dias_com_acerto/total_dias:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------- Gráfico de lucro acumulado ----------
    bt_filtrado = bt_filtrado.sort_values("data").reset_index(drop=True)
    bt_filtrado["lucro_acumulado"] = bt_filtrado["lucro"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bt_filtrado["data"],
        y=bt_filtrado["lucro_acumulado"],
        mode="lines",
        line=dict(
            color="#A78BFA" if lucro_liquido >= 0 else "#EF4444",
            width=2.5,
        ),
        fill="tozeroy",
        fillcolor=(
            "rgba(124, 58, 237, 0.15)"
            if lucro_liquido >= 0
            else "rgba(220, 38, 38, 0.15)"
        ),
        name="Lucro acumulado",
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,27,46,0.5)",
        font=dict(color="#E5E7EB"),
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(gridcolor="#1E293B", title="Lucro (R$)"),
        hovermode="x unified",
        title=dict(
            text="📈 Lucro Acumulado ao Longo do Tempo",
            font=dict(size=16, color="#A78BFA"),
            x=0.02,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ---------- Tabela de backtest ----------
    st.markdown('<div class="secao-titulo">📋 Detalhamento do Backtest</div>', unsafe_allow_html=True)

    bt_exibir = bt_filtrado[[
        "data", "milhar_sug", "grupo_sug", "dezena_sug", "centena_sug",
        "ganho", "lucro", "acertos"
    ]].copy()
    bt_exibir = bt_exibir.sort_values("data", ascending=False).head(50)

    st.dataframe(
        bt_exibir,
        use_container_width=True,
        height=400,
    )
    st.caption(f"Mostrando 50 registros mais recentes de {len(bt_filtrado):,} dias analisados.")


# =============================================================
# PANORAMA
# =============================================================
st.markdown('<div class="secao-titulo">📊 Panorama do período</div>', unsafe_allow_html=True)

n_concursos = df_filtrado.groupby(["data", "modalidade"]).ngroups
top_grupo = df_filtrado["grupo"].astype(str).value_counts().idxmax()
top_grupo_freq = df_filtrado["grupo"].astype(str).value_counts().max()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="kpi-card azul">
      <span class="kpi-icone">🎰</span>
      <div class="kpi-label">Total de Prêmios</div>
      <div class="kpi-valor">{len(df_filtrado):,}</div>
      <div class="kpi-sub">no período filtrado</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card roxo">
      <span class="kpi-icone">📅</span>
      <div class="kpi-label">Concursos</div>
      <div class="kpi-valor">{n_concursos:,}</div>
      <div class="kpi-sub">extrações no período</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card verde">
      <span class="kpi-icone">🎯</span>
      <div class="kpi-label">Grupo Top</div>
      <div class="kpi-valor">{top_grupo}</div>
      <div class="kpi-sub">{top_grupo_freq}x ocorrências</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card laranja">
      <span class="kpi-icone">📈</span>
      <div class="kpi-label">Modalidades</div>
      <div class="kpi-valor">{df_filtrado['modalidade'].nunique()}</div>
      <div class="kpi-sub">tipos distintos</div>
    </div>
    """, unsafe_allow_html=True)


# =============================================================
# GRÁFICOS
# =============================================================
st.markdown('<div class="secao-titulo">📈 Análise Visual</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    freq_grupo = (
        df_filtrado["grupo"].astype(str)
        .value_counts().sort_index().reset_index()
    )
    freq_grupo.columns = ["grupo", "ocorrencias"]

    fig = px.bar(
        freq_grupo, x="grupo", y="ocorrencias",
        title="Frequência por Grupo",
        color="ocorrencias",
        color_continuous_scale=["#312E81", "#7C3AED", "#A78BFA"],
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,27,46,0.5)",
        font=dict(color="#E5E7EB"),
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        title_font=dict(size=16, color="#A78BFA"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#1E293B")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    freq_dezena = (
        df_filtrado["dezena"].astype(str)
        .value_counts().head(20).reset_index()
    )
    freq_dezena.columns = ["dezena", "ocorrencias"]

    fig = px.bar(
        freq_dezena, x="dezena", y="ocorrencias",
        title="Top 20 Dezenas",
        color="ocorrencias",
        color_continuous_scale=["#1E3A8A", "#2563EB", "#60A5FA"],
    )
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,27,46,0.5)",
        font=dict(color="#E5E7EB"),
        showlegend=False,
        height=400,
        margin=dict(l=20, r=20, t=50, b=20),
        title_font=dict(size=16, color="#60A5FA"),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#1E293B")
    st.plotly_chart(fig, use_container_width=True)


# =============================================================
# EVOLUÇÃO TEMPORAL
# =============================================================
st.markdown('<div class="secao-titulo">📉 Evolução Temporal</div>', unsafe_allow_html=True)

evolucao = (
    df_filtrado.groupby(df_filtrado["data"].dt.date)
    .size()
    .reset_index(name="premios")
)
evolucao.columns = ["data", "premios"]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=evolucao["data"],
    y=evolucao["premios"],
    mode="lines",
    line=dict(color="#A78BFA", width=2.5),
    fill="tozeroy",
    fillcolor="rgba(124, 58, 237, 0.15)",
    name="Prêmios por dia",
))
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(22,27,46,0.5)",
    font=dict(color="#E5E7EB"),
    height=350,
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(showgrid=False, title=""),
    yaxis=dict(gridcolor="#1E293B", title="Prêmios/dia"),
    hovermode="x unified",
)
st.plotly_chart(fig, use_container_width=True)


# =============================================================
# TABELA
# =============================================================
st.markdown('<div class="secao-titulo">📋 Dados Detalhados</div>', unsafe_allow_html=True)

st.dataframe(
    df_filtrado[["data", "modalidade", "premio", "milhar", "grupo", "bicho"]]
    .head(200),
    use_container_width=True,
    height=400,
)

st.caption(f"Mostrando até 200 de {len(df_filtrado):,} registros filtrados.")


# =============================================================
# FOOTER
# =============================================================
st.markdown(
    '<div class="footer">🎰 Jogo do Bicho 2024 • Análise estatística honesta • '
    'Sem promessas, só dados.</div>',
    unsafe_allow_html=True,
)