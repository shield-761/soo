import streamlit as st
import pandas as pd

st.set_page_config(page_title="민방위 대피시설 지도", layout="wide")

st.title("🗺️ 민방위 대피시설 위치 시각화")

uploaded_file = st.file_uploader("📁 엑셀 파일 업로드 (.xlsx)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name=0)
    df.columns = df.columns.str.strip()

    # 필수 컬럼 확인
    if '위도(EPSG4326)' in df.columns and '경도(EPSG4326)' in df.columns:
        map_df = df.dropna(subset=['위도(EPSG4326)', '경도(EPSG4326)'])
        map_df = map_df.rename(columns={
            '위도(EPSG4326)': 'lat',
            '경도(EPSG4326)': 'lon'
        })

        st.success(f"✅ 지도에 표시할 수 있는 시설 수: {len(map_df)}개")

        with st.expander("📋 데이터 미리보기"):
            st.dataframe(map_df[['시설명', '도로명전체주소', 'lat', 'lon']])

        st.subheader("🗺️ 시설 위치 지도")
        st.map(map_df[['lat', 'lon']])

        # 수용인원 분석
        if '최대수용인원' in df.columns:
            st.subheader("👥 최대 수용인원 상위 시설")
            top_df = df[['시설명', '최대수용인원']].dropna().sort_values('최대수용인원', ascending=False).head(10)
            st.bar_chart(top_df.set_index('시설명'))
    else:
        st.error("❌ 위도(EPSG4326), 경도(EPSG4326) 컬럼이 없습니다.")
else:
    st.info("👆 위 파일을 업로드하세요 (.xlsx 형식)")
