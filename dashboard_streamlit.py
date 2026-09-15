"""
Dashboard Jogo do Bicho — Completo com auto-refresh, próximo sorteio,
animais, alertas, backtests e histórico mensal.
"""
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from motor.importacao import importar_csv_largo
from motor.grupos import grupo_para_animal, dezena_para_grupo


# =============================================================
# AUTO-REFRESH (a cada 60 segundos)
# =============================================================
st_autorefresh(interval=60_000, key="auto_refresh_dashboard")

TZ_BR = ZoneInfo("America/Sao_Paulo")
agora = datetime.now(TZ_BR)


# =============================================================
# HORÁRIOS OFICIAIS DOS SORTEIOS
# 0=Segunda, 1=Terça, 2=Quarta, 3=Quinta, 4=Sexta, 5=Sábado, 6=Domingo
# =============================================================
HORARIOS_OFICIAIS = {
    0: [  # Segunda
        ("PPT", "09:30"), ("PTM", "11:30"), ("PT",  "14:30"),
        ("PTV", "16:30"), ("PTN", "18:20"), ("COR", "21:30"),
    ],
    1: [  # Terça
        ("PPT", "09:30"), ("PTM", "11:30"), ("PT",  "14:30"),
        ("PTV", "16:30"), ("PTN", "18:20"), ("COR", "21:30"),
    ],
    2: [  # Quarta
        ("PPT", "09:30"), ("PTM", "11:30"), ("PT",  "14:30"),
        ("PTV", "16:30"), ("FED", "20:00"), ("COR", "21:30"),
    ],
    3: [  # Quinta
        ("PPT", "09:30"), ("PTM", "11:30"), ("PT",  "14:30"),
        ("PTV", "16:30"), ("PTN", "18:20"), ("COR", "21:30"),
    ],
    4: [  # Sexta
        ("PPT", "09:30"), ("PTM", "11:30"), ("PT",  "14:30"),
        ("PTV", "16:30"), ("PTN", "18:20"), ("COR", "21:30"),
    ],
    5: [  # Sábado
        ("PPT", "09:30"), ("PTM", "11:30"), ("PT",  "14:30"),
        ("PTV", "16:30"), ("PTN", "19:30"), ("COR", "21:30"),
    ],
    6: [  # Domingo
        ("FED", "11:30"), ("PT",  "14:30"), ("PTV", "16:30"),
    ],
}

DIAS_SEMANA = [
    "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
    "Sexta-feira", "Sábado", "Domingo",
]

DIAS_CURTOS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]


def proximo_sorteio(agora_dt):
    """Retorna (modalidade, horario, momento, dia)."""
    dia_semana = agora_dt.weekday()
    horarios_hoje = HORARIOS_OFICIAIS[dia_semana]

    for modalidade, horario in horarios_hoje:
        hora, minuto = map(int, horario.split(":"))
        momento = agora_dt.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        if momento > agora_dt:
            return (modalidade, horario, momento, DIAS_SEMANA[dia_semana])

    proximo_dia = (dia_semana + 1) % 7
    modalidade, horario = HORARIOS_OFICIAIS[proximo_dia][0]
    hora, minuto = map(int, horario.split(":"))
    momento = (agora_dt + timedelta(days=1)).replace(
        hour=hora, minute=minuto, second=0, microsecond=0
    )
    return (modalidade, horario, momento, DIAS_SEMANA[proximo_dia])


def ultimo_sorteio(agora_dt):
    """Retorna (modalidade, horario, momento) do último sorteio hoje, ou None."""
    dia_semana = agora_dt.weekday()
    ultimo = None
    for modalidade, horario in HORARIOS_OFICIAIS[dia_semana]:
        hora, minuto = map(int, horario.split(":"))
        momento = agora_dt.replace(hour=hora, minute=minuto, second=0, microsecond=0)
        if momento <= agora_dt:
            ultimo = (modalidade, horario, momento)
    return ultimo


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

MODALIDADES_ALVO = ["PPT", "PTM", "PT", "PTV", "PTN", "COR"]

HORARIOS_MAP = {
    "PPT": "09:30", "PTM": "11:30", "PT":  "14:30",
    "PTV": "16:30", "PTN": "18:20", "COR": "21:30", "FED": "20:00",
}


# =============================================================
# EMOJIS POR GRUPO
# =============================================================
EMOJIS_GRUPO = {
    1: "🦤", 2: "🦅", 3: "🐴", 4: "🦋", 5: "🐶",
    6: "🐐", 7: "🐑", 8: "🐪", 9: "🐍", 10: "🐰",
    11: "🐎", 12: "🐘", 13: "🐓", 14: "🐱", 15: "🐊",
    16: "🦁", 17: "🐵", 18: "🐷", 19: "🦚", 20: "🦃",
    21: "🐂", 22: "🐯", 23: "🐻", 24: "🦌", 25: "🐄",
}


def info_animal(grupo):
    try:
        g = int(str(grupo).lstrip("0") or "0")
    except (ValueError, AttributeError):
        return ("Desconhecido", "❓")
    return (grupo_para_animal(g), EMOJIS_GRUPO.get(g, "❓"))


def grupo_de_milhar(milhar):
    milhar = str(milhar).zfill(4)
    return dezena_para_grupo(int(milhar[-2:]))


def grupo_de_dezena(dezena):
    return dezena_para_grupo(int(dezena))


def grupo_de_centena(centena):
    centena = str(centena).zfill(3)
    return dezena_para_grupo(int(centena[-2:]))


def analisar_historico(df, tipo, valor):
    if tipo == "milhar":
        mask = df["milhar"].astype(str).str.zfill(4) == str(valor).zfill(4)
    elif tipo == "grupo":
        mask = df["grupo"].astype(str).str.zfill(2) == str(valor).zfill(2)
    elif tipo == "dezena":
        mask = df["dezena"].astype(str).str.zfill(2) == str(valor).zfill(2)
    elif tipo == "centena":
        mask = df["centena"].astype(str).str.zfill(3) == str(valor).zfill(3)
    else:
        return (0, [])

    ocorrencias = df[mask].copy()
    total = len(ocorrencias)
    ultimas = ocorrencias.sort_values("data", ascending=False).head(5)

    detalhes = []
    for _, r in ultimas.iterrows():
        detalhes.append({
            "data": r["data"].strftime("%d/%m/%Y"),
            "modalidade": r["modalidade"],
            "premio": int(r["premio"]),
        })
    return (total, detalhes)


# =============================================================
# CSS
# =============================================================
CSS = """
<style>
  .stApp { background: linear-gradient(180deg, #0B0F19 0%, #0F1422 100%); }
  .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1400px; }

  .titulo-principal {
    font-size: 38px; font-weight: 800;
    background: linear-gradient(90deg, #A78BFA 0%, #60A5FA 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin: 0; letter-spacing: -0.5px;
  }
  .subtitulo-principal { color: #94A3B8; font-size: 15px; margin-top: 4px; margin-bottom: 24px; }

  .kpi-card {
    background: linear-gradient(135deg, #1E1B4B 0%, #312E81 100%);
    border-radius: 16px; padding: 20px 22px;
    border: 1px solid #312E81;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    height: 100%;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(124, 58, 237, 0.3); }
  .kpi-card.roxo { background: linear-gradient(135deg, #4C1D95 0%, #6D28D9 100%); border-color: #7C3AED; }
  .kpi-card.azul { background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%); border-color: #3B82F6; }
  .kpi-card.verde { background: linear-gradient(135deg, #064E3B 0%, #059669 100%); border-color: #10B981; }
  .kpi-card.laranja { background: linear-gradient(135deg, #7C2D12 0%, #EA580C 100%); border-color: #F97316; }
  .kpi-card.vermelho { background: linear-gradient(135deg, #7F1D1D 0%, #DC2626 100%); border-color: #EF4444; }

  .kpi-icone { font-size: 28px; margin-bottom: 8px; display: block; }
  .kpi-label {
    color: rgba(255,255,255,0.75); font-size: 12px;
    text-transform: uppercase; letter-spacing: 1.5px;
    font-weight: 600; margin-bottom: 6px;
  }
  .kpi-valor {
    color: #FFFFFF; font-size: 30px; font-weight: 800;
    font-family: 'Courier New', monospace;
    letter-spacing: 1px; line-height: 1.1;
  }
  .kpi-sub { color: rgba(255,255,255,0.6); font-size: 12px; margin-top: 6px; }

  .kpi-animal {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,0,0,0.25); padding: 4px 10px;
    border-radius: 8px; margin-top: 8px;
    font-size: 13px; color: rgba(255,255,255,0.9); font-weight: 500;
  }

  .alerta-sorteado {
    background: rgba(0,0,0,0.25); border-left: 3px solid #FBBF24;
    padding: 6px 10px; margin-top: 10px; border-radius: 6px;
    font-size: 11px; color: rgba(255,255,255,0.85); line-height: 1.4;
  }
  .alerta-sorteado .titulo { color: #FBBF24; font-weight: 700; display: block; margin-bottom: 4px; }
  .alerta-sorteado .data { color: rgba(255,255,255,0.65); font-family: 'Courier New', monospace; }

  .proximo-sorteio {
    background: linear-gradient(135deg, #7C3AED 0%, #2563EB 100%);
    border-radius: 16px; padding: 20px 26px; margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(124, 58, 237, 0.4);
    display: flex; justify-content: space-between; align-items: center;
    flex-wrap: wrap; gap: 12px;
  }
  .proximo-sorteio .titulo {
    color: rgba(255,255,255,0.85); font-size: 13px;
    text-transform: uppercase; letter-spacing: 2px; font-weight: 600;
  }
  .proximo-sorteio .valor {
    color: #FFFFFF; font-size: 26px; font-weight: 800;
    font-family: 'Courier New', monospace;
  }
  .proximo-sorteio .meta { color: rgba(255,255,255,0.75); font-size: 13px; text-align: right; }
  .proximo-sorteio .meta strong { color: #FFFFFF; font-size: 16px; }

  .secao-titulo {
    color: #E5E7EB; font-size: 20px; font-weight: 700;
    margin-top: 24px; margin-bottom: 12px;
    display: flex; align-items: center; gap: 10px;
  }
  .secao-titulo::before {
    content: ''; display: inline-block;
    width: 4px; height: 22px;
    background: linear-gradient(180deg, #A78BFA, #60A5FA); border-radius: 2px;
  }
  .footer {
    text-align: center; color: #64748B; font-size: 12px;
    padding: 20px 0; margin-top: 20px; border-top: 1px solid #1E293B;
  }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# =============================================================
# LOCALIZAR CSVs
# =============================================================
def encontrar_csvs():
    pastas_candidatas = [
        Path(__file__).parent / "dados",
        Path("dados"),
        Path(r"D:\Jogo do bicho\dados"),
        Path(r"D:\Raspagem de Dados jogo do bicho\dados"),
    ]
    for pasta in pastas_candidatas:
        if pasta.exists():
            arquivos = sorted(pasta.glob("jogo_do_bicho_*.csv"))
            if arquivos:
                return tuple(str(a) for a in arquivos)
    raise FileNotFoundError("Nenhum arquivo jogo_do_bicho_*.csv encontrado em 'dados/'.")


@st.cache_data(show_spinner=False)
def carregar_dados(caminhos):
    if isinstance(caminhos, str):
        caminhos = (caminhos,)

    partes = []
    for caminho in caminhos:
        try:
            partes.append(importar_csv_largo(caminho))
        except Exception as e:
            st.warning(f"Erro ao carregar {caminho}: {e}")

    if not partes:
        raise ValueError("Nenhum dado foi carregado dos CSVs.")

    df = pd.concat(partes, ignore_index=True)

    rename_map = {}
    for antigo, novo in [
        ("grupo_csv", "grupo"),
        ("bicho_csv", "bicho"),
        ("centena_csv", "centena"),
    ]:
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

    milhar = passado["milhar"].astype(str).value_counts()
    grupo = passado["grupo"].astype(str).value_counts()
    dezena = passado["dezena"].astype(str).value_counts()
    centena = passado["centena"].astype(str).value_counts()

    grupo_top = grupo.idxmax()
    nome_grupo, emoji_grupo = info_animal(grupo_top)

    milhar_top = str(milhar.idxmax()).zfill(4)
    dezena_top = str(dezena.idxmax()).zfill(2)
    centena_top = str(centena.idxmax()).zfill(3)

    nome_milhar, emoji_milhar = info_animal(grupo_de_milhar(milhar_top))
    nome_dezena, emoji_dezena = info_animal(grupo_de_dezena(dezena_top))
    nome_centena, emoji_centena = info_animal(grupo_de_centena(centena_top))

    return {
        "milhar": milhar_top, "milhar_freq": int(milhar.max()),
        "milhar_nome": nome_milhar, "milhar_emoji": emoji_milhar,
        "grupo": str(grupo_top).zfill(2), "grupo_freq": int(grupo.max()),
        "grupo_nome": nome_grupo, "grupo_emoji": emoji_grupo,
        "dezena": dezena_top, "dezena_freq": int(dezena.max()),
        "dezena_nome": nome_dezena, "dezena_emoji": emoji_dezena,
        "centena": centena_top, "centena_freq": int(centena.max()),
        "centena_nome": nome_centena, "centena_emoji": emoji_centena,
        "n_passado": len(passado),
    }


# =============================================================
# BACKTEST REALISTA
# =============================================================
@st.cache_data(show_spinner=False)
def executar_backtest_por_modalidade(caminhos):
    df = carregar_dados(caminhos)
    datas = sorted(df["data"].dt.date.unique())
    registros = []

    for i, data in enumerate(datas):
        if i < 5:
            continue
        sugestoes = calcular_sugestoes(df, data)
        if sugestoes is None:
            continue
        resultado_dia = df[df["data"].dt.date == data]

        for modalidade in MODALIDADES_ALVO:
            resultado_mod = resultado_dia[resultado_dia["modalidade"] == modalidade]
            if resultado_mod.empty:
                continue

            milhares_mod = set(resultado_mod["milhar"].astype(str).str.zfill(4))
            centenas_mod = set(resultado_mod["centena"].astype(str).str.zfill(3))
            dezenas_mod = set(resultado_mod["dezena"].astype(str).str.zfill(2))
            grupos_mod = set(resultado_mod["grupo"].astype(str).str.zfill(2))

            ganho = 0.0
            acertos = []

            if sugestoes["milhar"].zfill(4) in milhares_mod:
                ganho += VALOR_MILHAR * RETORNO_MILHAR
                acertos.append("milhar")
            if sugestoes["centena"].zfill(3) in centenas_mod:
                ganho += VALOR_CENTENA * RETORNO_CENTENA
                acertos.append("centena")
            if sugestoes["dezena"].zfill(2) in dezenas_mod:
                ganho += VALOR_DEZENA * RETORNO_DEZENA
                acertos.append("dezena")
            if sugestoes["grupo"].zfill(2) in grupos_mod:
                ganho += VALOR_GRUPO * RETORNO_GRUPO
                acertos.append("grupo")

            registros.append({
                "data": data, "modalidade": modalidade,
                "horario": HORARIOS_MAP.get(modalidade, "—"),
                "milhar_sug": sugestoes["milhar"],
                "grupo_sug": sugestoes["grupo"],
                "dezena_sug": sugestoes["dezena"],
                "centena_sug": sugestoes["centena"],
                "ganho": round(ganho, 2),
                "lucro": round(ganho - CUSTO_DIARIO, 2),
                "acertos": ", ".join(acertos) if acertos else "—",
            })

    return pd.DataFrame(registros)


# =============================================================
# BACKTEST OTIMISTA
# =============================================================
@st.cache_data(show_spinner=False)
def executar_backtest_otimista(caminhos):
    df = carregar_dados(caminhos)
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
            "ganho": round(ganho, 2),
            "lucro": round(ganho - CUSTO_DIARIO, 2),
            "acertos": ", ".join(acertos) if acertos else "—",
        })

    return pd.DataFrame(registros)


# =============================================================
# CARREGAR
# =============================================================
try:
    caminhos_csv = encontrar_csvs()
    df = carregar_dados(caminhos_csv)
except Exception as e:
    st.error(f"Erro ao carregar: {e}")
    st.stop()


# =============================================================
# BANNER DE AVISO LEGAL
# =============================================================
st.markdown("""
<div style="
    background: linear-gradient(90deg, #7F1D1D 0%, #DC2626 100%);
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 20px;
    border-left: 5px solid #FBBF24;
    color: #FFFFFF;
    font-size: 13px;
    line-height: 1.6;
    box-shadow: 0 4px 16px rgba(220, 38, 38, 0.3);
">
  <strong style="font-size: 15px;">⚠️ AVISO LEGAL / LEGAL DISCLAIMER</strong><br>
  Este software é uma ferramenta <strong>educacional</strong> de análise estatística.
  <strong>NÃO incentiva apostas.</strong> O Jogo do Bicho é estatisticamente uniforme
  (chi²=19.74, p=0.71) — <strong>nenhum software pode prever resultados</strong>.<br>
  <span style="font-size: 12px; opacity: 0.9;">
    This software is an <strong>educational</strong> statistical analysis tool.
    <strong>It does NOT encourage gambling.</strong> No software can predict random results.
  </span>
</div>
""", unsafe_allow_html=True)


# =============================================================
# CABEÇALHO
# =============================================================
st.markdown(
    '<h1 class="titulo-principal">🎰 Jogo do Bicho</h1>'
    '<p class="subtitulo-principal">Análise estatística honesta — sem promessas, só dados.</p>',
    unsafe_allow_html=True,
)

st.caption(
    f"📂 {len(caminhos_csv)} arquivo(s): "
    + ", ".join(Path(c).name for c in caminhos_csv)
    + f"  ·  🕒 Agora: **{agora.strftime('%d/%m/%Y %H:%M:%S')}** (Brasília)"
)


# =============================================================
# PRÓXIMO SORTEIO
# =============================================================
modalidade_prox, horario_prox, momento_prox, dia_prox = proximo_sorteio(agora)
ultimo = ultimo_sorteio(agora)

if momento_prox:
    delta = momento_prox - agora
    total_seg = int(delta.total_seconds())
    h = total_seg // 3600
    m = (total_seg % 3600) // 60
    s = total_seg % 60
    contagem = f"{h:02d}h {m:02d}m {s:02d}s"
else:
    contagem = "—"

if ultimo:
    mod_ant, hor_ant, momento_ant = ultimo
    delta_ant = agora - momento_ant
    min_ant = int(delta_ant.total_seconds() // 60)
    info_anterior = (
        f"Último: <strong>{mod_ant}</strong> às {hor_ant} "
        f"(há {min_ant} min)"
    )
else:
    info_anterior = "Nenhum sorteio hoje ainda"

st.markdown(f"""
<div class="proximo-sorteio">
  <div>
    <div class="titulo">⏰ Próximo sorteio</div>
    <div class="valor">{modalidade_prox} — {horario_prox}</div>
    <div class="meta">{dia_prox}</div>
  </div>
  <div class="meta">
    Faltam <strong>{contagem}</strong><br>
    <span style="font-size:12px;">{info_anterior}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# =============================================================
# FILTROS
# =============================================================
st.markdown('<div class="secao-titulo">🎛️ Filtros</div>', unsafe_allow_html=True)

f1, f2, f3, f4 = st.columns([1, 1, 1, 1])

data_min = df["data"].min().date()
data_max = df["data"].max().date()

with f1:
    data_inicio = st.date_input("📅 Data inicial", value=data_min,
                                min_value=data_min, max_value=data_max)
with f2:
    data_fim = st.date_input("📅 Data final", value=data_max,
                             min_value=data_min, max_value=data_max)
with f3:
    modalidades = ["Todas"] + sorted(df["modalidade"].unique().tolist())
    modalidade_sel = st.selectbox("🏆 Modalidade", modalidades)
with f4:
    data_ref = st.date_input("🎯 Data de referência", value=data_max,
                             min_value=data_min, max_value=data_max)


df_filtrado = df[
    (df["data"].dt.date >= data_inicio) &
    (df["data"].dt.date <= data_fim)
].copy()

if modalidade_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["modalidade"] == modalidade_sel]


# =============================================================
# SUGESTÕES
# =============================================================
st.markdown(
    f'<div class="secao-titulo">💡 Sugestões para {data_ref.strftime("%d/%m/%Y")}</div>',
    unsafe_allow_html=True,
)

sug = calcular_sugestoes(df, data_ref)

if sug:
    hist_milhar = analisar_historico(df, "milhar", sug["milhar"])
    hist_grupo = analisar_historico(df, "grupo", sug["grupo"])
    hist_dezena = analisar_historico(df, "dezena", sug["dezena"])
    hist_centena = analisar_historico(df, "centena", sug["centena"])

    def montar_alerta(total, detalhes):
        if total == 0:
            return '<div class="alerta-sorteado"><span class="titulo">🆕 Nunca sorteado no histórico</span></div>'
        datas_txt = " · ".join(
            f"{d['data']} ({d['modalidade']} P{d['premio']})"
            for d in detalhes[:5]
        )
        return f'''
        <div class="alerta-sorteado">
          <span class="titulo">✅ Já sorteado {total}x</span>
          <span class="data">{datas_txt}</span>
        </div>
        '''

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card roxo">
          <span class="kpi-icone">💡</span>
          <div class="kpi-label">Milhar</div>
          <div class="kpi-valor">{sug['milhar']}</div>
          <div class="kpi-animal">{sug['milhar_emoji']} {sug['milhar_nome']}</div>
          <div class="kpi-sub">Freq. histórica: {sug['milhar_freq']}x</div>
          {montar_alerta(*hist_milhar)}
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card azul">
          <span class="kpi-icone" style="font-size:42px;">{sug['grupo_emoji']}</span>
          <div class="kpi-label">Grupo — {sug['grupo_nome']}</div>
          <div class="kpi-valor">{sug['grupo']}</div>
          <div class="kpi-sub">Freq. histórica: {sug['grupo_freq']}x</div>
          {montar_alerta(*hist_grupo)}
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card verde">
          <span class="kpi-icone">🎲</span>
          <div class="kpi-label">Dezena</div>
          <div class="kpi-valor">{sug['dezena']}</div>
          <div class="kpi-animal">{sug['dezena_emoji']} {sug['dezena_nome']}</div>
          <div class="kpi-sub">Freq. histórica: {sug['dezena_freq']}x</div>
          {montar_alerta(*hist_dezena)}
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card laranja">
          <span class="kpi-icone">💎</span>
          <div class="kpi-label">Centena</div>
          <div class="kpi-valor">{sug['centena']}</div>
          <div class="kpi-animal">{sug['centena_emoji']} {sug['centena_nome']}</div>
          <div class="kpi-sub">Freq. histórica: {sug['centena_freq']}x</div>
          {montar_alerta(*hist_centena)}
        </div>
        """, unsafe_allow_html=True)

    st.caption(f"Baseado em {sug['n_passado']:,} prêmios anteriores à data selecionada.")


# =============================================================
# BACKTEST REALISTA
# =============================================================
st.markdown(
    '<div class="secao-titulo">🎯 Backtest Realista (R$ 30/dia · 6 modalidades)</div>',
    unsafe_allow_html=True,
)

with st.spinner("Executando backtest realista..."):
    bt_real = executar_backtest_por_modalidade(caminhos_csv)

if bt_real.empty:
    st.warning("Backtest realista sem dados.")
else:
    bt_real_filtrado = bt_real[
        (bt_real["data"] >= data_inicio) & (bt_real["data"] <= data_fim)
    ].copy()

    total_apostas = len(bt_real_filtrado)
    total_gasto_real = total_apostas * CUSTO_DIARIO
    total_ganho_real = bt_real_filtrado["ganho"].sum()
    lucro_real = total_ganho_real - total_gasto_real
    acertos_real = (bt_real_filtrado["ganho"] > 0).sum()
    retorno_real_pct = (total_ganho_real / total_gasto_real * 100) if total_gasto_real > 0 else 0
    classe_real = "verde" if lucro_real >= 0 else "vermelho"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card azul">
          <span class="kpi-icone">💸</span>
          <div class="kpi-label">Total Gasto</div>
          <div class="kpi-valor">R$ {total_gasto_real:,.0f}</div>
          <div class="kpi-sub">{total_apostas:,} apostas × R$ 5</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="kpi-card roxo">
          <span class="kpi-icone">🏆</span>
          <div class="kpi-label">Total Ganho</div>
          <div class="kpi-valor">R$ {total_ganho_real:,.0f}</div>
          <div class="kpi-sub">{retorno_real_pct:.1f}% do gasto</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="kpi-card {classe_real}">
          <span class="kpi-icone">📊</span>
          <div class="kpi-label">Lucro Líquido (Realista)</div>
          <div class="kpi-valor">R$ {lucro_real:,.0f}</div>
          <div class="kpi-sub">resultado final</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card laranja">
          <span class="kpi-icone">🎯</span>
          <div class="kpi-label">Apostas com Acerto</div>
          <div class="kpi-valor">{acertos_real:,}</div>
          <div class="kpi-sub">de {total_apostas:,} ({100*acertos_real/total_apostas:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    bt_real_acum = bt_real_filtrado.groupby("data", as_index=False)["lucro"].sum()
    bt_real_acum["lucro_acumulado"] = bt_real_acum["lucro"].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=bt_real_acum["data"], y=bt_real_acum["lucro_acumulado"],
        mode="lines",
        line=dict(color="#EF4444" if lucro_real < 0 else "#10B981", width=2.5),
        fill="tozeroy",
        fillcolor=("rgba(239, 68, 68, 0.15)" if lucro_real < 0 else "rgba(16, 185, 129, 0.15)"),
        name="Lucro acumulado",
    ))
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,27,46,0.5)",
        font=dict(color="#E5E7EB"),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(gridcolor="#1E293B", title="Lucro (R$)"),
        hovermode="x unified",
        title=dict(
            text="📈 Lucro Acumulado — Backtest Realista",
            font=dict(size=16, color="#EF4444" if lucro_real < 0 else "#10B981"),
            x=0.02,
        ),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="secao-titulo">📋 Backtest por Modalidade (últimos 50)</div>', unsafe_allow_html=True)
    bt_exibir = bt_real_filtrado[[
        "data", "modalidade", "horario", "milhar_sug", "grupo_sug",
        "dezena_sug", "centena_sug", "ganho", "lucro", "acertos"
    ]].copy()
    bt_exibir = bt_exibir.sort_values(["data", "modalidade"], ascending=[False, True]).head(50)
    st.dataframe(bt_exibir, use_container_width=True, height=400)
    st.caption(f"Mostrando 50 de {total_apostas:,} apostas analisadas.")

    st.markdown('<div class="secao-titulo">📊 Resumo por Modalidade</div>', unsafe_allow_html=True)
    resumo_modalidade = bt_real_filtrado.groupby("modalidade").agg(
        apostas=("lucro", "count"),
        acertos=("ganho", lambda x: (x > 0).sum()),
        total_gasto=("lucro", lambda x: len(x) * CUSTO_DIARIO),
        total_ganho=("ganho", "sum"),
    ).reset_index()
    resumo_modalidade["lucro"] = resumo_modalidade["total_ganho"] - resumo_modalidade["total_gasto"]
    resumo_modalidade["retorno_pct"] = (resumo_modalidade["total_ganho"] / resumo_modalidade["total_gasto"] * 100).round(1)
    resumo_modalidade["taxa_acerto_pct"] = (resumo_modalidade["acertos"] / resumo_modalidade["apostas"] * 100).round(2)
    resumo_modalidade = resumo_modalidade.sort_values("lucro", ascending=False)
    st.dataframe(
        resumo_modalidade[[
            "modalidade", "apostas", "acertos", "taxa_acerto_pct",
            "total_gasto", "total_ganho", "lucro", "retorno_pct"
        ]],
        use_container_width=True,
    )


# =============================================================
# BACKTEST OTIMISTA
# =============================================================
st.markdown(
    '<div class="secao-titulo">💰 Backtest Otimista (R$ 5/dia · qualquer modalidade)</div>',
    unsafe_allow_html=True,
)

with st.spinner("Executando backtest otimista..."):
    bt_otim = executar_backtest_otimista(caminhos_csv)

if bt_otim.empty:
    st.warning("Backtest otimista sem dados.")
else:
    bt_otim_filtrado = bt_otim[
        (bt_otim["data"] >= data_inicio) & (bt_otim["data"] <= data_fim)
    ].copy()

    total_dias = len(bt_otim_filtrado)
    total_gasto = total_dias * CUSTO_DIARIO
    total_ganho = bt_otim_filtrado["ganho"].sum()
    lucro = total_ganho - total_gasto
    dias_acerto = (bt_otim_filtrado["ganho"] > 0).sum()
    retorno_pct = (total_ganho / total_gasto * 100) if total_gasto > 0 else 0
    classe = "verde" if lucro >= 0 else "vermelho"

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="kpi-card azul">
          <span class="kpi-icone">💸</span>
          <div class="kpi-label">Total Gasto</div>
          <div class="kpi-valor">R$ {total_gasto:,.0f}</div>
          <div class="kpi-sub">{total_dias} dias × R$ 5</div>
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
        <div class="kpi-card {classe}">
          <span class="kpi-icone">📊</span>
          <div class="kpi-label">Lucro (Otimista)</div>
          <div class="kpi-valor">R$ {lucro:,.0f}</div>
          <div class="kpi-sub">resultado final</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-card laranja">
          <span class="kpi-icone">🎯</span>
          <div class="kpi-label">Dias com Acerto</div>
          <div class="kpi-valor">{dias_acerto}</div>
          <div class="kpi-sub">de {total_dias} ({100*dias_acerto/total_dias:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)

    st.caption(
        "⚠️ O backtest otimista conta acerto em QUALQUER modalidade do dia. "
        "Na prática, você joga em UMA modalidade específica — use o backtest realista acima."
    )


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
        showlegend=False, height=400,
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
        showlegend=False, height=400,
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
    .size().reset_index(name="premios")
)
evolucao.columns = ["data", "premios"]

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=evolucao["data"], y=evolucao["premios"],
    mode="lines", line=dict(color="#A78BFA", width=2.5),
    fill="tozeroy", fillcolor="rgba(124, 58, 237, 0.15)",
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
    df_filtrado[["data", "modalidade", "premio", "milhar", "grupo", "bicho"]].head(200),
    use_container_width=True,
    height=400,
)
st.caption(f"Mostrando até 200 de {len(df_filtrado):,} registros filtrados.")


# =============================================================
# GRADE DE HORÁRIOS DA SEMANA
# =============================================================
st.markdown(
    '<div class="secao-titulo">📅 Grade de Horários da Semana</div>',
    unsafe_allow_html=True,
)

dias_grade = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
modalidades_grade = ["PPT", "PTM", "PT", "PTV", "PTN", "COR", "FED"]

grade = []
for dia_idx, dia in enumerate(dias_grade):
    linha = {"Dia": dia}
    horarios_dia = {m: "—" for m in modalidades_grade}
    for modalidade, horario in HORARIOS_OFICIAIS[dia_idx]:
        horarios_dia[modalidade] = horario
    linha.update(horarios_dia)
    grade.append(linha)

df_grade = pd.DataFrame(grade)

st.dataframe(
    df_grade,
    use_container_width=True,
    hide_index=True,
    height=290,
)
st.caption(f"📍 Hoje é **{DIAS_SEMANA[agora.weekday()]}** — horários no fuso de Brasília (apuração).")


# =============================================================
# RESULTADOS DO MÊS SELECIONADO
# =============================================================
st.markdown(
    '<div class="secao-titulo">📆 Resultados do Mês</div>',
    unsafe_allow_html=True,
)

df["ano_mes"] = df["data"].dt.to_period("M")
meses_disponiveis = sorted(df["ano_mes"].unique(), reverse=True)

MESES_PT = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro",
}

meses_formatados = {
    p: f"{MESES_PT[p.month]}/{p.year}"
    for p in meses_disponiveis
}

col_mes1, col_mes2 = st.columns([1, 3])

with col_mes1:
    mes_escolhido_str = st.selectbox(
        "📅 Escolha o mês",
        options=[meses_formatados[p] for p in meses_disponiveis],
        index=0,
    )

mes_escolhido = next(
    p for p in meses_disponiveis
    if meses_formatados[p] == mes_escolhido_str
)

df_mes = df[df["ano_mes"] == mes_escolhido].copy()

if df_mes.empty:
    st.warning(f"Nenhum dado encontrado para {mes_escolhido_str}.")
else:
    total_premios_mes = len(df_mes)
    total_concursos_mes = df_mes.groupby(["data", "modalidade"]).ngroups
    dias_com_sorteio = df_mes["data"].dt.date.nunique()
    modalidades_mes = df_mes["modalidade"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="kpi-card azul">
          <span class="kpi-icone">🎰</span>
          <div class="kpi-label">Total de Prêmios</div>
          <div class="kpi-valor">{total_premios_mes:,}</div>
          <div class="kpi-sub">em {mes_escolhido_str}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="kpi-card roxo">
          <span class="kpi-icone">📅</span>
          <div class="kpi-label">Concursos</div>
          <div class="kpi-valor">{total_concursos_mes:,}</div>
          <div class="kpi-sub">extrações no mês</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="kpi-card verde">
          <span class="kpi-icone">🗓️</span>
          <div class="kpi-label">Dias com Sorteio</div>
          <div class="kpi-valor">{dias_com_sorteio}</div>
          <div class="kpi-sub">dias úteis do mês</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="kpi-card laranja">
          <span class="kpi-icone">📈</span>
          <div class="kpi-label">Modalidades</div>
          <div class="kpi-valor">{modalidades_mes}</div>
          <div class="kpi-sub">tipos distintos</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        f'<div class="secao-titulo">📊 Prêmios por dia — {mes_escolhido_str}</div>',
        unsafe_allow_html=True,
    )

    premios_por_dia = (
        df_mes.groupby(df_mes["data"].dt.date)
        .size()
        .reset_index(name="premios")
    )
    premios_por_dia.columns = ["data", "premios"]

    fig_mes = go.Figure()
    fig_mes.add_trace(go.Bar(
        x=premios_por_dia["data"],
        y=premios_por_dia["premios"],
        marker=dict(
            color=premios_por_dia["premios"],
            colorscale=[[0, "#312E81"], [0.5, "#7C3AED"], [1, "#A78BFA"]],
            line=dict(width=0),
        ),
        name="Prêmios",
    ))
    fig_mes.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(22,27,46,0.5)",
        font=dict(color="#E5E7EB"),
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, title=""),
        yaxis=dict(gridcolor="#1E293B", title="Prêmios/dia"),
        hovermode="x unified",
        showlegend=False,
    )
    st.plotly_chart(fig_mes, use_container_width=True)

    st.markdown(
        f'<div class="secao-titulo">📋 Resultados completos — {mes_escolhido_str}</div>',
        unsafe_allow_html=True,
    )

    df_mes_exibir = df_mes[[
        "data", "modalidade", "premio", "milhar", "grupo", "bicho"
    ]].copy()
    df_mes_exibir["horario"] = df_mes_exibir["modalidade"].map(HORARIOS_MAP).fillna("—")
    df_mes_exibir["data_str"] = df_mes_exibir["data"].dt.strftime("%d/%m/%Y")

    df_mes_exibir = df_mes_exibir[[
        "data_str", "modalidade", "horario", "premio", "milhar", "grupo", "bicho"
    ]].rename(columns={
        "data_str": "Data",
        "modalidade": "Modalidade",
        "horario": "Horário",
        "premio": "Prêmio",
        "milhar": "Milhar",
        "grupo": "Grupo",
        "bicho": "Bicho",
    })
    df_mes_exibir = df_mes_exibir.sort_values(
        ["Data", "Modalidade", "Prêmio"],
        ascending=[False, True, True],
    )

    st.dataframe(
        df_mes_exibir,
        use_container_width=True,
        height=500,
    )
    st.caption(f"Total: **{len(df_mes_exibir):,}** prêmios em {mes_escolhido_str}.")

    st.markdown(
        f'<div class="secao-titulo">📊 Resumo por Modalidade — {mes_escolhido_str}</div>',
        unsafe_allow_html=True,
    )

    resumo_mes = df_mes.groupby("modalidade").agg(
        premios=("milhar", "count"),
        grupos_distintos=("grupo", "nunique"),
        bichos_distintos=("bicho", "nunique"),
    ).reset_index()

    resumo_mes["horario"] = resumo_mes["modalidade"].map(HORARIOS_MAP).fillna("—")
    resumo_mes = resumo_mes[[
        "modalidade", "horario", "premios", "grupos_distintos", "bichos_distintos"
    ]].rename(columns={
        "modalidade": "Modalidade",
        "horario": "Horário",
        "premios": "Prêmios",
        "grupos_distintos": "Grupos distintos",
        "bichos_distintos": "Bichos distintos",
    })
    resumo_mes = resumo_mes.sort_values("Modalidade")

    st.dataframe(
        resumo_mes,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        f'<div class="secao-titulo">🎯 Top 5 Grupos — {mes_escolhido_str}</div>',
        unsafe_allow_html=True,
    )

    top_grupos_mes = df_mes["grupo"].astype(str).str.zfill(2).value_counts().head(5)

    cols = st.columns(5)
    for i, (grupo, freq) in enumerate(top_grupos_mes.items()):
        nome, emoji = info_animal(grupo)
        with cols[i]:
            st.markdown(f"""
            <div class="kpi-card roxo">
              <span class="kpi-icone" style="font-size:42px;">{emoji}</span>
              <div class="kpi-label">{nome}</div>
              <div class="kpi-valor">{grupo}</div>
              <div class="kpi-sub">{freq}x no mês</div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================
# FOOTER
# =============================================================
st.markdown(
    '<div class="footer">🎰 Jogo do Bicho • Análise estatística honesta • '
    'Auto-atualiza a cada 60 segundos.</div>',
    unsafe_allow_html=True,
)