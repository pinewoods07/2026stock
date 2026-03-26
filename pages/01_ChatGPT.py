import streamlit as st
import yfinance as yf
import pandas as pd

# ------------------ 기본 설정 ------------------
st.set_page_config(
    page_title="📊 글로벌 주식 비교",
    layout="wide"
)

# ------------------ 스타일 ------------------
st.markdown("""
<style>
.big-title {
    font-size: 40px;
    font-weight: 700;
}
.sub-title {
    font-size: 18px;
    color: gray;
}
.card {
    padding: 20px;
    border-radius: 15px;
    background-color: #f5f7fa;
}
</style>
""", unsafe_allow_html=True)

# ------------------ 타이틀 ------------------
st.markdown('<div class="big-title">📊 글로벌 주식 비교</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">한국 🇰🇷 vs 미국 🇺🇸 수익률 & 차트 비교</div>', unsafe_allow_html=True)

st.divider()

# ------------------ 입력 영역 ------------------
col1, col2, col3 = st.columns([1,1,1])

with col1:
    kor = st.text_input("🇰🇷 한국 주식", "005930.KS")

with col2:
    usa = st.text_input("🇺🇸 미국 주식", "AAPL")

with col3:
    period = st.selectbox("📅 기간", ["1mo", "3mo", "6mo", "1y", "3y"], index=3)

st.divider()

# ------------------ 데이터 분석 ------------------
if st.button("🚀 비교하기", use_container_width=True):
    with st.spinner("데이터 불러오는 중..."):

        try:
            kor_df = yf.Ticker(kor).history(period=period)
            usa_df = yf.Ticker(usa).history(period=period)

            if kor_df.empty or usa_df.empty:
                st.error("❌ 티커를 확인해주세요")
                st.stop()

            # 수익률 계산
            kor_return = (kor_df["Close"].iloc[-1] / kor_df["Close"].iloc[0] - 1) * 100
            usa_return = (usa_df["Close"].iloc[-1] / usa_df["Close"].iloc[0] - 1) * 100

            # ------------------ 수익률 카드 ------------------
            st.subheader("📊 수익률 비교")

            c1, c2 = st.columns(2)

            with c1:
                st.metric(
                    label=f"{kor}",
                    value=f"{kor_return:.2f}%",
                    delta=f"{kor_return:.2f}%"
                )

            with c2:
                st.metric(
                    label=f"{usa}",
                    value=f"{usa_return:.2f}%",
                    delta=f"{usa_return:.2f}%"
                )

            st.divider()

            # ------------------ 정규화 차트 ------------------
            st.subheader("📈 성장률 비교 (정규화)")

            kor_norm = kor_df["Close"] / kor_df["Close"].iloc[0]
            usa_norm = usa_df["Close"] / usa_df["Close"].iloc[0]

            compare_df = pd.DataFrame({
                kor: kor_norm,
                usa: usa_norm
            })

            st.line_chart(compare_df, use_container_width=True)

            st.divider()

            # ------------------ 실제 가격 차트 ------------------
            st.subheader("💰 실제 가격 흐름")

            price_df = pd.DataFrame({
                kor: kor_df["Close"],
                usa: usa_df["Close"]
            })

            st.line_chart(price_df, use_container_width=True)

        except Exception as e:
            st.error(f"🚨 오류 발생: {e}")
