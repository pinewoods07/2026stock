import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np

# ── 페이지 설정 ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="글로벌 주식 비교 분석기",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Noto+Sans+KR:wght@300;400;700&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --border: #1f2f4a;
    --accent-blue: #3b82f6;
    --accent-green: #22c55e;
    --accent-red: #ef4444;
    --accent-yellow: #eab308;
    --text: #f5f0e8;
    --text-muted: #b0bec5;
    --kr-color: #f97316;
    --us-color: #818cf8;
}

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* 전체 배경 */
.stApp { background-color: var(--bg); }
.block-container { padding: 2rem 2rem 4rem; }

/* 헤더 */
.hero {
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #fff;
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
}
.hero-sub {
    color: #c9d1d9;
    font-size: 0.95rem;
    margin: 0;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    margin-right: 6px;
}
.badge-kr { background: rgba(249,115,22,0.2); color: var(--kr-color); border: 1px solid rgba(249,115,22,0.4); }
.badge-us { background: rgba(129,140,248,0.2); color: var(--us-color); border: 1px solid rgba(129,140,248,0.4); }

/* 메트릭 카드 */
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1rem; margin: 1.5rem 0; }
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: var(--accent-blue); }
.metric-card .label { font-size: 0.72rem; color: #b0bec5; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 0.4rem; }
.metric-card .value { font-family: 'IBM Plex Mono', monospace; font-size: 1.5rem; font-weight: 600; }
.metric-card .sub { font-size: 0.78rem; color: #c9d1d9; margin-top: 0.2rem; }
.pos { color: var(--accent-green); }
.neg { color: var(--accent-red); }
.neu { color: var(--text); }

/* 섹션 */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    color: #c9d1d9;
    text-transform: uppercase;
    border-left: 3px solid var(--accent-blue);
    padding-left: 0.8rem;
    margin: 2rem 0 1rem;
}

/* 테이블 */
.styled-table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
.styled-table th {
    background: var(--surface2);
    color: #b0bec5;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 0.8rem 1rem;
    text-align: right;
    border-bottom: 1px solid var(--border);
}
.styled-table th:first-child { text-align: left; }
.styled-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid rgba(31,47,74,0.5);
    text-align: right;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
}
.styled-table td:first-child { text-align: left; font-family: 'Noto Sans KR', sans-serif; font-size: 0.88rem; }
.styled-table tr:hover td { background: rgba(59,130,246,0.05); }

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: var(--surface);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .stSlider > div { color: var(--text); }

/* Streamlit 기본 오버라이드 */
.stMultiSelect [data-baseweb="tag"] { background-color: rgba(59,130,246,0.3) !important; }
div[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1rem; }

/* 구분선 */
hr { border-color: var(--border); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)


# ── 종목 데이터 ───────────────────────────────────────────────────────────────
KR_STOCKS = {
    "삼성전자":   "005930.KS",
    "SK하이닉스": "000660.KS",
    "LG에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대차":     "005380.KS",
    "POSCO홀딩스": "005490.KS",
    "카카오":     "035720.KS",
    "NAVER":      "035420.KS",
    "셀트리온":   "068270.KS",
    "기아":       "000270.KS",
    "KB금융":     "105560.KS",
    "신한지주":   "055550.KS",
}

US_STOCKS = {
    "Apple":      "AAPL",
    "Microsoft":  "MSFT",
    "NVIDIA":     "NVDA",
    "Amazon":     "AMZN",
    "Alphabet":   "GOOGL",
    "Meta":       "META",
    "Tesla":      "TSLA",
    "Berkshire":  "BRK-B",
    "JPMorgan":   "JPM",
    "Eli Lilly":  "LLY",
    "Broadcom":   "AVGO",
    "Visa":       "V",
}

INDEX_MAP = {
    "KOSPI":  "^KS11",
    "KOSDAQ": "^KQ11",
    "S&P500": "^GSPC",
    "NASDAQ": "^IXIC",
    "DOW":    "^DJI",
}

PERIOD_MAP = {
    "1개월":  30,
    "3개월":  90,
    "6개월":  180,
    "1년":    365,
    "2년":    730,
    "3년":    1095,
}


# ── 유틸 ─────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=600, show_spinner=False)
def fetch_data(tickers: list, start: str, end: str) -> pd.DataFrame:
    if not tickers:
        return pd.DataFrame()
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        close = raw[["Close"]] if "Close" in raw.columns else raw
    close = close.dropna(how="all")
    return close


def calc_metrics(prices: pd.Series) -> dict:
    prices = prices.dropna()
    if len(prices) < 2:
        return {}
    ret = prices.pct_change().dropna()
    total_ret = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
    annual_vol = ret.std() * np.sqrt(252) * 100
    sharpe = (ret.mean() / ret.std() * np.sqrt(252)) if ret.std() > 0 else 0
    dd = (prices / prices.cummax() - 1).min() * 100
    return {
        "수익률": total_ret,
        "연변동성": annual_vol,
        "샤프지수": sharpe,
        "최대낙폭": dd,
        "최근가": prices.iloc[-1],
    }


def fmt_pct(v, decimals=2):
    if v is None or np.isnan(v):
        return "-"
    sign = "+" if v > 0 else ""
    color = "pos" if v > 0 else ("neg" if v < 0 else "neu")
    return f'<span class="{color}">{sign}{v:.{decimals}f}%</span>'


def fmt_num(v, decimals=2):
    if v is None or np.isnan(v):
        return "-"
    return f"{v:,.{decimals}f}"


# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    st.markdown("---")

    period_label = st.selectbox("📅 조회 기간", list(PERIOD_MAP.keys()), index=3)
    days = PERIOD_MAP[period_label]
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days)

    st.markdown("---")
    st.markdown("**🇰🇷 한국 종목** (최대 6개)")
    kr_selected = st.multiselect(
        "한국 종목 선택",
        list(KR_STOCKS.keys()),
        default=["삼성전자", "SK하이닉스", "NAVER"],
        max_selections=6,
        label_visibility="collapsed",
    )

    st.markdown("**🇺🇸 미국 종목** (최대 6개)")
    us_selected = st.multiselect(
        "미국 종목 선택",
        list(US_STOCKS.keys()),
        default=["Apple", "NVIDIA", "Microsoft"],
        max_selections=6,
        label_visibility="collapsed",
    )

    st.markdown("---")
    show_index = st.checkbox("지수 비교 포함", value=True)
    if show_index:
        idx_selected = st.multiselect(
            "비교 지수",
            list(INDEX_MAP.keys()),
            default=["KOSPI", "S&P500"],
        )
    else:
        idx_selected = []

    normalize = st.checkbox("정규화 차트 (100 기준)", value=True)


# ── 데이터 로드 ───────────────────────────────────────────────────────────────
all_tickers = (
    [KR_STOCKS[n] for n in kr_selected]
    + [US_STOCKS[n] for n in us_selected]
    + [INDEX_MAP[n] for n in idx_selected]
)
name_map = (
    {KR_STOCKS[n]: n for n in kr_selected}
    | {US_STOCKS[n]: n for n in us_selected}
    | {INDEX_MAP[n]: n for n in idx_selected}
)

start_str = start_date.strftime("%Y-%m-%d")
end_str   = end_date.strftime("%Y-%m-%d")

if not all_tickers:
    st.warning("왼쪽 사이드바에서 종목을 하나 이상 선택해 주세요.")
    st.stop()

with st.spinner("📡 데이터 불러오는 중..."):
    prices_raw = fetch_data(all_tickers, start_str, end_str)

# 단일 종목이면 Series → DataFrame
if isinstance(prices_raw, pd.Series):
    prices_raw = prices_raw.to_frame(name=all_tickers[0])

# 열 이름 → 표시 이름
prices = prices_raw.rename(columns=name_map)
available = [c for c in prices.columns if prices[c].notna().any()]
prices = prices[available]

if prices.empty:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()


# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="hero-title">📈 글로벌 주식 비교 분석기</div>
  <p class="hero-sub">
    <span class="badge badge-kr">🇰🇷 KR</span>
    <span class="badge badge-us">🇺🇸 US</span>
    &nbsp;{period_label} 기간 &nbsp;·&nbsp; {start_str} → {end_str}
  </p>
</div>
""", unsafe_allow_html=True)


# ── 수익률 요약 카드 ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">📊 수익률 요약</div>', unsafe_allow_html=True)

metrics_all = {}
for col in available:
    m = calc_metrics(prices[col])
    if m:
        metrics_all[col] = m

if metrics_all:
    sorted_names = sorted(metrics_all.keys(), key=lambda x: metrics_all[x]["수익률"], reverse=True)
    cols_per_row = 4
    rows = [sorted_names[i:i+cols_per_row] for i in range(0, len(sorted_names), cols_per_row)]

    for row in rows:
        cols = st.columns(len(row))
        for col_el, name in zip(cols, row):
            m = metrics_all[name]
            ret = m["수익률"]
            arrow = "▲" if ret >= 0 else "▼"
            color = "#22c55e" if ret >= 0 else "#ef4444"
            is_kr = name in kr_selected
            is_idx = name in idx_selected
            badge_html = ""
            if is_kr:
                badge_html = '<span style="font-size:0.65rem;background:rgba(249,115,22,0.2);color:#f97316;border:1px solid rgba(249,115,22,0.3);border-radius:4px;padding:1px 6px;">KR</span>'
            elif not is_idx:
                badge_html = '<span style="font-size:0.65rem;background:rgba(129,140,248,0.2);color:#818cf8;border:1px solid rgba(129,140,248,0.3);border-radius:4px;padding:1px 6px;">US</span>'

            col_el.markdown(f"""
<div class="metric-card">
  <div class="label">{badge_html} {name}</div>
  <div class="value" style="color:{color}">{arrow} {abs(ret):.1f}%</div>
  <div class="sub">변동성 {m['연변동성']:.1f}% &nbsp;·&nbsp; MDD {m['최대낙폭']:.1f}%</div>
</div>""", unsafe_allow_html=True)


# ── 수익률 비교 차트 ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">📉 가격 추이 비교</div>', unsafe_allow_html=True)

# 색상 팔레트
KR_PALETTE = ["#f97316","#fb923c","#fdba74","#fed7aa","#fbbf24","#fcd34d"]
US_PALETTE = ["#818cf8","#a78bfa","#60a5fa","#34d399","#f472b6","#fb7185"]
IDX_PALETTE = ["#94a3b8","#64748b"]

color_map = {}
kr_i, us_i, idx_i = 0, 0, 0
for name in available:
    if name in kr_selected:
        color_map[name] = KR_PALETTE[kr_i % len(KR_PALETTE)]; kr_i += 1
    elif name in idx_selected:
        color_map[name] = IDX_PALETTE[idx_i % len(IDX_PALETTE)]; idx_i += 1
    else:
        color_map[name] = US_PALETTE[us_i % len(US_PALETTE)]; us_i += 1

fig = go.Figure()

for name in available:
    series = prices[name].dropna()
    if series.empty:
        continue
    y = (series / series.iloc[0] * 100) if normalize else series
    is_idx = name in idx_selected
    fig.add_trace(go.Scatter(
        x=series.index,
        y=y,
        name=name,
        line=dict(
            color=color_map[name],
            width=1.5 if is_idx else 2,
            dash="dot" if is_idx else "solid",
        ),
        hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>{'수익률: %{y:.1f}' if normalize else '가격: %{y:,.0f}'}<extra></extra>",
    ))

fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.8)",
    font=dict(family="IBM Plex Mono", color="#dce3ea", size=11),
    legend=dict(
        bgcolor="rgba(17,24,39,0.9)",
        bordercolor="#1f2f4a",
        borderwidth=1,
        font=dict(size=11, color="#dce3ea"),
        orientation="h",
        yanchor="bottom", y=1.01,
        xanchor="left", x=0,
    ),
    xaxis=dict(
        showgrid=True, gridcolor="rgba(31,47,74,0.5)",
        showline=True, linecolor="#1f2f4a",
        tickfont=dict(size=10, color="#dce3ea"),
    ),
    yaxis=dict(
        showgrid=True, gridcolor="rgba(31,47,74,0.5)",
        showline=True, linecolor="#1f2f4a",
        tickfont=dict(size=10, color="#dce3ea"),
        ticksuffix="%" if normalize else "",
    ),
    hovermode="x unified",
    height=460,
    margin=dict(l=0, r=0, t=40, b=0),
)

if normalize:
    fig.add_hline(y=100, line_dash="dash", line_color="rgba(255,255,255,0.15)", line_width=1)

st.plotly_chart(fig, use_container_width=True)


# ── 바 차트: 수익률 순위 ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">🏆 수익률 순위</div>', unsafe_allow_html=True)

if metrics_all:
    bar_data = pd.DataFrame([
        {"종목": n, "수익률(%)": m["수익률"], "색상": color_map.get(n, "#64748b")}
        for n, m in metrics_all.items()
    ]).sort_values("수익률(%)", ascending=True)

    fig_bar = go.Figure(go.Bar(
        x=bar_data["수익률(%)"],
        y=bar_data["종목"],
        orientation="h",
        marker=dict(
            color=bar_data["색상"].tolist(),
            line=dict(color="rgba(0,0,0,0)", width=0),
        ),
        hovertemplate="<b>%{y}</b><br>수익률: %{x:.2f}%<extra></extra>",
    ))
    fig_bar.add_vline(x=0, line_color="rgba(255,255,255,0.2)", line_width=1)
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.8)",
        font=dict(family="IBM Plex Mono", color="#dce3ea", size=11),
        xaxis=dict(
            showgrid=True, gridcolor="rgba(31,47,74,0.5)",
            ticksuffix="%", showline=True, linecolor="#1f2f4a",
            tickfont=dict(color="#dce3ea"),
        ),
        yaxis=dict(showgrid=False, showline=True, linecolor="#1f2f4a",
            tickfont=dict(color="#dce3ea"),
        ),
        height=max(200, len(bar_data) * 38 + 60),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ── 상세 지표 테이블 ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">📋 종목별 상세 지표</div>', unsafe_allow_html=True)

rows_html = ""
for name in sorted_names:
    m = metrics_all[name]
    is_kr = name in kr_selected
    is_us = name not in kr_selected and name not in idx_selected
    region_badge = ""
    if is_kr:
        region_badge = '<span style="font-size:0.65rem;background:rgba(249,115,22,0.2);color:#f97316;padding:1px 6px;border-radius:3px;">KR</span>'
    elif is_us:
        region_badge = '<span style="font-size:0.65rem;background:rgba(129,140,248,0.2);color:#818cf8;padding:1px 6px;border-radius:3px;">US</span>'
    else:
        region_badge = '<span style="font-size:0.65rem;background:rgba(100,116,139,0.2);color:#94a3b8;padding:1px 6px;border-radius:3px;">IDX</span>'

    ticker_str = ""
    if name in kr_selected:
        ticker_str = KR_STOCKS[name]
    elif name in us_selected:
        ticker_str = US_STOCKS[name]
    elif name in idx_selected:
        ticker_str = INDEX_MAP[name]

    sharpe_color = "pos" if m["샤프지수"] > 1 else ("neg" if m["샤프지수"] < 0 else "neu")
    rows_html += f"""
<tr>
  <td>{region_badge} <b>{name}</b><br><span style="color:#8899aa;font-size:0.72rem;">{ticker_str}</span></td>
  <td>{fmt_pct(m['수익률'])}</td>
  <td>{fmt_num(m['연변동성'])}%</td>
  <td><span class="{sharpe_color}">{fmt_num(m['샤프지수'])}</span></td>
  <td>{fmt_pct(m['최대낙폭'])}</td>
  <td>{fmt_num(m['최근가'], 0 if m['최근가'] > 500 else 2)}</td>
</tr>"""

st.markdown(f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.2rem;overflow-x:auto;">
<table class="styled-table">
  <thead>
    <tr>
      <th>종목</th>
      <th>수익률</th>
      <th>연환산 변동성</th>
      <th>샤프지수</th>
      <th>최대낙폭(MDD)</th>
      <th>최근 종가</th>
    </tr>
  </thead>
  <tbody>{rows_html}</tbody>
</table>
</div>
""", unsafe_allow_html=True)


# ── 상관관계 히트맵 ───────────────────────────────────────────────────────────
if len(available) >= 2:
    st.markdown('<div class="section-label">🔗 상관관계 히트맵</div>', unsafe_allow_html=True)
    returns = prices[available].pct_change().dropna()
    corr = returns.corr()

    fig_heat = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns.tolist(),
        y=corr.index.tolist(),
        colorscale=[
            [0.0, "#ef4444"],
            [0.5, "#1e293b"],
            [1.0, "#22c55e"],
        ],
        zmin=-1, zmax=1,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}",
        textfont=dict(size=11, family="IBM Plex Mono"),
        hovertemplate="<b>%{y} ↔ %{x}</b><br>상관계수: %{z:.3f}<extra></extra>",
        showscale=True,
        colorbar=dict(
            thickness=12,
            tickfont=dict(color="#dce3ea", size=10, family="IBM Plex Mono"),
            outlinewidth=0,
        ),
    ))
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(17,24,39,0.8)",
        font=dict(family="Noto Sans KR", color="#dce3ea", size=11),
        xaxis=dict(tickangle=-30, showgrid=False, showline=False, tickfont=dict(color="#dce3ea")),
        yaxis=dict(showgrid=False, showline=False, tickfont=dict(color="#dce3ea")),
        height=max(300, len(available) * 50 + 80),
        margin=dict(l=0, r=0, t=10, b=0),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ── 푸터 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr>
<div style="text-align:center;color:#8899aa;font-size:0.75rem;font-family:'IBM Plex Mono',monospace;">
  데이터 제공: Yahoo Finance (yfinance) &nbsp;·&nbsp; 본 앱은 투자 권유가 아닙니다 &nbsp;·&nbsp; 투자 결정은 본인 책임입니다
</div>
""", unsafe_allow_html=True)
