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
        st.write("📌 현재 CSV 컬럼명:", df.columns.tolist())  # 여기서 확인 가능

        # 컬럼 자동 추론
        station_col = None
        pm10_col = None
        for col in df.columns:
            if 'station' in col.lower() or '지역' in col:
                station_col = col
            if 'pm10' in col.lower() or '미세먼지' in col:
                pm10_col = col

        if not station_col or not pm10_col:
            st.error("❌ '측정소(station)'와 '미세먼지(pm10)' 관련 컬럼을 찾지 못했습니다.")
        else:
            st.success(f"✅ 컬럼 자동 인식: '{station_col}' / '{pm10_col}'")
            st.dataframe(df[[station_col, pm10_col]])

            st.subheader("📊 지역별 미세먼지 농도 (막대 그래프)")
            df_sorted = df.sort_values(pm10_col, ascending=False)
            st.bar_chart(data=df_sorted, x=station_col, y=pm10_col)
else:
    st.info("먼저 미세먼지 CSV 파일을 업로드해주세요.")
