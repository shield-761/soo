import streamlit as st
import pandas as pd

st.set_page_config(page_title="전국 시설 지도", layout="wide")
st.title("📍 전국 시설 위치 시각화")

uploaded_file = st.file_uploader("📁 CSV 또는 Excel 파일을 업로드하세요", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            # CSV 파일 인코딩 탐색
            tried_encodings = ['utf-8', 'cp949', 'euc-kr']
            for enc in tried_encodings:
                try:
                    df = pd.read_csv(uploaded_file, encoding=enc)
                    break
                except:
                    uploaded_file.seek(0)
        else:
            df = pd.read_excel(uploaded_file)

        df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

        # 위도 / 경도 / 시설명 컬럼 자동 감지
        lat_col = next((c for c in df.columns if '위도' in c or 'lat' in c.lower()), None)
        lon_col = next((c for c in df.columns if '경도' in c or 'lon' in c.lower()), None)
        name_col = next((c for c in df.columns if '시설명' in c or '측정소명' in c or '사업장명' in c or '명칭' in c), df.columns[0])

        if lat_col and lon_col:
            st.success(f"✅ 위치 컬럼 감지됨: `{lat_col}`, `{lon_col}`")
            df = df.dropna(subset=[lat_col, lon_col])

            # 검색창
            keyword = st.text_input("🔍 시설명 검색", "")
            if keyword:
                filtered_df = df[df[name_col].astype(str).str.contains(keyword, case=False)]
            else:
                filtered_df = df.copy()

            st.subheader("🗺️ 지도에 시설 위치 표시")
            st.map(filtered_df[[lat_col, lon_col]])

            st.subheader("📋 검색 결과 테이블")
            st.dataframe(filtered_df[[name_col, lat_col, lon_col]].reset_index(drop=True))

        else:
            st.error("❌ 위도/경도 컬럼이 존재하지 않습니다. CSV 파일에 위치 정보가 있는지 확인하세요.")
            st.write("컬럼 목록:", df.columns.tolist())

    except Exception as e:
        st.error(f"❌ 데이터를 불러오지 못했습니다. 파일을 다시 확인해 주세요.\n\n{e}")
else:
    st.info("📌 먼저 CSV 또는 Excel 파일을 업로드해 주세요.")
