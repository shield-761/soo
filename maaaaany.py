import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🌫️ 대한민국 미세먼지(PM10) 시각화")

uploaded_file = st.file_uploader("📁 미세먼지 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    # 다양한 인코딩 시도
    encodings = ['utf-8', 'cp949', 'euc-kr']
    df = None
    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"✅ 파일을 성공적으로 읽었습니다! (인코딩: {enc})")
            break
        except Exception as e:
            continue

    if df is None:
        st.error("❌ CSV 파일을 읽는 데 실패했습니다. 인코딩을 확인하세요.")
    else:
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
    st.info("먼저 미세먼지 CSV 파일을 업로드해주세요.")
