import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("🌫️ 대한민국 미세먼지(PM10) 시각화")

uploaded_file = st.file_uploader("📁 미세먼지 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    encodings = ['utf-8', 'cp949', 'euc-kr']
    df = None
    for enc in encodings:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"✅ 파일을 성공적으로 읽었습니다! (인코딩: {enc})")
            break
        except:
            continue

    if df is None:
        st.error("❌ CSV 파일을 읽는 데 실패했습니다.")
    else:
        df.columns = df.columns.str.strip()
        st.write("📌 현재 CSV 컬럼명:", df.columns.tolist())

        station_col = st.selectbox("📍 측정소(지역) 컬럼 선택", options=df.columns.tolist())
        pm10_col = st.selectbox("🌫️ 미세먼지(PM10) 컬럼 선택", options=df.columns.tolist())

        if station_col and pm10_col:
            st.success(f"✅ 선택된 컬럼: {station_col} / {pm10_col}")
            st.dataframe(df[[station_col, pm10_col]])

            st.subheader("📊 지역별 미세먼지 농도")
            df_sorted = df.sort_values(pm10_col, ascending=False)
            st.bar_chart(data=df_sorted, x=station_col, y=pm10_col)
else:
    st.info("먼저 미세먼지 CSV 파일을 업로드해주세요.")
