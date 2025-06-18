import streamlit as st
import pandas as pd

st.set_page_config(page_title="전국 시설 위치 지도", layout="wide")
st.title("📍 전국 시설 위치 시각화")

uploaded_file = st.file_uploader("📁 CSV 또는 Excel 파일을 업로드하세요", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        # 파일 확장자에 따라 처리
        if uploaded_file.name.endswith(".csv"):
            tried_encodings = ['utf-8', 'cp949', 'euc-kr']
            for enc in tried_encodings:
                try:
                    df = pd.read_csv(uploaded_file, encoding=enc)
                    break
                except:
                    uploaded_file.seek(0)
        else:
            df = pd.read_excel(uploaded_file, engine='openpyxl')

        # 컬럼 이름 정리
        df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

        # 위도/경도 컬럼 찾기
        lat_col = next((c for c in df.columns if '위도' in c or 'latitude' in c.lower()), None)
        lon_col = next((c for c in df.columns if '경도' in c or 'longitude' in c.lower()), None)
        name_col = next((c for c in df.columns if '시설명' in c or '측정소명' in c or '사업장명' in c or '명칭' in c), df.columns[0])

        if lat_col and lon_col:
            df = df.rename(columns={lat_col: 'lat', lon_col: 'lon'})
            df = df.dropna(subset=['lat', 'lon'])

            st.success("✅ 위치 정보를 기반으로 시각화 준비 완료!")

            # 검색 기능
            keyword = st.text_input("🔍 시설명 검색", "")
            if keyword:
                filtered_df = df[df[name_col].astype(str).str.contains(keyword, case=False)]
            else:
                filtered_df = df.copy()

            st.subheader("🗺️ 시설 위치 지도")
            st.map(filtered_df[['lat', 'lon']])

            st.subheader("📋 시설 정보 목록")
            st.dataframe(filtered_df[[name_col, 'lat', 'lon']].reset_index(drop=True))

        else:
            st.error("❌ 위도/경도 컬럼을 찾을 수 없습니다.")
            st.write("컬럼 목록:", df.columns.tolist())

    except Exception as e:
        st.error(f"❌ 데이터를 불러오지 못했습니다. 파일을 다시 확인해 주세요.\n\n{e}")
else:
    st.info("📌 먼저 CSV 또는 Excel 파일을 업로드하세요.")
