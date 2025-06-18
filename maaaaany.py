import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🌫️ 대한민국 미세먼지(PM10) 시각화")

uploaded_file = st.file_uploader("📁 미세먼지 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    if 'stationName' not in df.columns or 'pm10Value' not in df.columns:
        st.error("❌ 'stationName', 'pm10Value' 컬럼이 포함되어야 합니다.")
    else:
        st.success("✅ 데이터 로드 완료!")
        st.dataframe(df)

        st.subheader("📊 지역별 미세먼지 농도 (막대 그래프)")
        df_sorted = df.sort_values("pm10Value", ascending=False)
        st.bar_chart(data=df_sorted, x="stationName", y="pm10Value")
else:
    st.info("먼저 CSV 파일을 업로드하세요.")
