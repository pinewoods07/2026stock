import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="주식 비교 분석 앱", layout="wide")

st.title("📊 한국 🇰🇷 vs 미국 🇺🇸 주식 비교 분석")

st.markdown("원하는 종목을 입력하면 수익률과 차트를 비교해줘요!")

# 기본 종목
default_kor = "005930.KS"  # 삼성전자
default_usa = "AAPL"       # 애플

col1, col2 = st.columns(2)

with col1:
    kor_ticker = st.text_input("🇰🇷 한국 주식 티커", default_kor)

with col2:
    usa_ticker = st.text_input("🇺🇸 미국 주식 티커", default_usa)

# 기간 선택
period = st.selectbox(
    "📅 기간 선택",
    ["1mo", "3mo", "6mo", "1y", "3y", "5y"],
    index=3
)

if st.button("📈 분석 시작"):
    try:
        # 데이터 가져오기
        kor_data = yf.Ticker(kor_ticker).history(period=period)
        usa_data = yf.Ticker(usa_ticker).history(period=period)

        # 데이터 체크
        if kor_data.empty or usa_data.empty:
            st.error("⚠️ 티커를 확인해주세요!")
        else:
            # 수익률 계산
            kor_return = (kor_data["Close"][-1] / kor_data["Close"][0] - 1) * 100
            usa_return = (usa_data["Close"][-1] / usa_data["Close"][0] - 1) * 100

            st.subheader("📊 수익률 비교")

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label=f"{kor_ticker} 수익률",
                    value=f"{kor_return:.2f}%"
                )

            with col2:
                st.metric(
                    label=f"{usa_ticker} 수익률",
                    value=f"{usa_return:.2f}%"
                )

            # 차트 정규화 (같은 기준으로 비교)
            kor_norm = kor_data["Close"] / kor_data["Close"].iloc[0]
            usa_norm = usa_data["Close"] / usa_data["Close"].iloc[0]

            df = pd.DataFrame({
                kor_ticker: kor_norm,
                usa_ticker: usa_norm
            })

            st.subheader("📉 가격 흐름 비교 (정규화)")

            fig, ax = plt.subplots()
            df.plot(ax=ax)
            ax.set_ylabel("정규화 가격 (시작=1)")
            ax.grid()

            st.pyplot(fig)

            # 원본 가격 차트
            st.subheader("📈 실제 가격 차트")

            fig2, ax2 = plt.subplots()
            kor_data["Close"].plot(ax=ax2, label=kor_ticker)
            usa_data["Close"].plot(ax=ax2, label=usa_ticker)
            ax2.legend()
            ax2.grid()

            st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")
