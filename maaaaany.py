import streamlit as st
import pandas as pd

st.set_page_config(page_title="민방위 대피시설 지도", layout="wide")
st.title("🗺️ 민방위 대피시설 위치 시각화")

uploaded_file = st.file_uploader("📁 CSV 또는 Excel 파일 업로드", type=["csv", "xls", "xlsx"])

if uploaded_file:
    df = None
    success = False

    # 1. Try reading CSV with multiple encodings
    if uploaded_file.name.endswith('.csv'):
        tried_encodings = ['utf-8', 'cp949', 'euc-kr']
        for enc in tried_encodings:
            try:
                df = pd.read_csv(uploaded_file, encoding=enc)
                success = True
                break
            except:
                uploaded_file.seek(0)

    # 2. If not CSV or failed, try Excel
    if not success:
        try:
            df = pd.read_excel(uploaded_file, sheet_name=0)
            success = True
        except Exception as e:
            st.error(f"❌ 파일을 읽을 수 없습니다: {e}")

    if success and df is not None:
        df.columns = df.columns.str.strip()
        
        # 위도/경도 컬럼 자동 인식
        lat_col = next((col for col in df.columns if '위도' in col), None)
        lon_col = next((col for col in df.columns if '경도' in col), None)

        if lat_col and lon_col:
            df = df.dropna(subset=[lat_col, lon_col])
            df = df.rename(columns={lat_col: 'lat', lon_col: 'lon'})

            st.success(f"✅ 지도에 표시할 수 있는 시설 수: {len(df)}개")

            with st.expander("📋 데이터 미리보기"):
                st.dataframe(df.head(20))

            st.subheader("🗺️ 지도에서 시설 위치 보기")
            st.map(df[['lat', 'lon']])

            if '최대수용인원' in df.columns:
                st.subheader("👥 최대 수용인원 상위 10개 시설")
                top10 = df[['시설명', '최대수용인원']].dropna().sort_values('최대수용인원', ascending=False).head(10)
                st.bar_chart(top10.set_index('시설명'))
        else:
            st.warning("⚠️ 위도 또는 경도 정보가 포함된 컬럼을 찾을 수 없습니다.")
    else:
        st.error("❌ 데이터를 불러오지 못했습니다. 파일을 다시 확인해 주세요.")
else:
    st.info("👆 먼저 CSV 또는 Excel 파일을 업로드해주세요.")
