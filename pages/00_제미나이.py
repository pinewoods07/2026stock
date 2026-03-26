import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="한미 주식 비교 분석", layout="wide")
st.title("📈 한미 주요 주식 수익률 비교 분석기")
st.markdown("한국과 미국의 주요 주식 및 ETF의 수익률을 한눈에 비교해 보세요.")

# 2. 분석할 주요 주식 리스트 (이름: 티커)
TICKERS = {
    "미국 주식": {
        "애플 (AAPL)": "AAPL",
        "마이크로소프트 (MSFT)": "MSFT",
        "엔비디아 (NVDA)": "NVDA",
        "테슬라 (TSLA)": "TSLA",
        "S&P 500 ETF (SPY)": "SPY",
        "나스닥 100 ETF (QQQ)": "QQQ"
    },
    "한국 주식": {
        "삼성전자": "005930.KS",
        "SK하이닉스": "000660.KS",
        "현대차": "005380.KS",
        "NAVER": "035420.KS",
        "카카오": "035720.KS",
        "KODEX 200": "069500.KS"
    }
}

# 딕셔너리를 평탄화하여 선택지에 사용
all_tickers = {**TICKERS["미국 주식"], **TICKERS["한국 주식"]}

# 3. 사이드바 설정
st.sidebar.header("⚙️ 검색 설정")

selected_names = st.sidebar.multiselect(
    "비교할 종목을 선택하세요:",
    options=list(all_tickers.keys()),
    default=["애플 (AAPL)", "엔비디아 (NVDA)", "삼성전자", "SK하이닉스"]
)

period = st.sidebar.selectbox(
    "조회 기간 선택:",
    options=["1개월", "3개월", "6개월", "1년", "3년", "5년"],
    index=3 # 기본값: 1년
)

# yfinance API가 이해하는 기간 포맷으로 변환
period_map = {
    "1개월": "1mo", "3개월": "3mo", "6개월": "6mo", 
    "1년": "1y", "3년": "3y", "5년": "5y"
}

# 4. 데이터 로드 및 차트 그리기
if selected_names:
    selected_tickers = [all_tickers[name] for name in selected_names]

    # 데이터 캐싱 (앱 속도 향상)
    @st.cache_data
    def load_data(tickers, period):
        # 종목들의 종가(Close) 데이터만 다운로드
        df = yf.download(tickers, period=period)['Close']
        # 선택한 종목이 1개일 경우 데이터프레임 형태로 변환
        if isinstance(df, pd.Series):
            df = df.to_frame(name=tickers[0])
        return df

    with st.spinner('데이터를 불러오는 중입니다...'):
        data = load_data(selected_tickers, period_map[period])

    # 누락된 데이터(결측치) 처리 (휴장일 등이 다를 수 있으므로)
    data = data.ffill().dropna()

    # 컬럼명을 티커에서 한글 종목명으로 다시 변경
    ticker_to_name = {v: k for k, v in all_tickers.items()}
    data.rename(columns=ticker_to_name, inplace=True)

    # 누적 수익률 계산 (시작일 = 0% 기준)
    returns = ((data / data.iloc[0]) - 1) * 100

    # 차트 출력
    st.subheader(f"📊 누적 수익률 차트 (최근 {period})")
    st.line_chart(returns)

    # 데이터 요약 표 출력
    st.subheader("📋 상세 데이터 요약")
    summary = pd.DataFrame({
        "시작일 종가": data.iloc[0],
        "최근 종가": data.iloc[-1],
        "수익률 (%)": returns.iloc[-1]
    })
    
    # 숫자 포맷 예쁘게 다듬기
    st.dataframe(
        summary.style.format({
            "시작일 종가": "{:,.2f}", 
            "최근 종가": "{:,.2f}", 
            "수익률 (%)": "{:,.2f}%"
        }),
        use_container_width=True
    )

else:
    st.info("👈 왼쪽 사이드바에서 비교할 종목을 하나 이상 선택해 주세요.")
