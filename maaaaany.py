import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="지역별 대피소 위치", layout="wide")
st.title("🏠 지역별 대피소 위치 찾기")

uploaded_file = st.file_uploader("📁 CSV 또는 Excel 파일을 업로드하세요", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
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

        # 컬럼명 정리
        df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

        # 위치 컬럼 찾기
        lat_col = next((c for c in df.columns if '위도' in c or 'lat' in c.lower()), None)
        lon_col = next((c for c in df.columns if '경도' in c or 'lon' in c.lower()), None)
        addr_col = next((c for c in df.columns if '주소' in c or '소재지' in c or '지역' in c), None)

        if lat_col and lon_col and addr_col:
            df = df.rename(columns={lat_col: 'lat', lon_col: 'lon', addr_col: 'address'})
            df = df.dropna(subset=['lat', 'lon'])

            # 지역 검색
            keyword = st.text_input("📍 검색할 지역명을 입력하세요 (예: 경기도 양주시)")
            if keyword:
                filtered_df = df[df['address'].astype(str).str.contains(keyword, case=False)]
            else:
                filtered_df = df.copy()

            st.success(f"✅ 총 {len(filtered_df)}개의 시설이 검색되었습니다.")

            # 지도 시각화 (한국어 지도 스타일 사용)
            st.subheader("🗺️ 지도에 시설 위치 표시")

            view_state = pdk.ViewState(
                latitude=filtered_df['lat'].mean(),
                longitude=filtered_df['lon'].mean(),
                zoom=10,
                pitch=0,
            )

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=filtered_df,
                get_position='[lon, lat]',
                get_radius=200,
                get_fill_color='[255, 0, 0, 160]',
                pickable=True,
            )

            st.pydeck_chart(
                pdk.Deck(
                    map_style="mapbox://styles/mapbox/light-v11",
                    initial_view_state=view_state,
                    layers=[layer],
                    tooltip={"text": "{address}"},
                )
            )

            st.subheader("📋 시설 목록")
            st.dataframe(filtered_df[['address', 'lat', 'lon']].reset_index(drop=True))

        else:
            st.error("❌ 주소 또는 위도/경도 컬럼이 누락되어 있습니다.")
            st.write("감지된 컬럼 목록:", df.columns.tolist())

    except Exception as e:
        st.error(f"❌ 데이터를 불러오지 못했습니다.\n\n{e}")
else:
    st.info("📌 CSV 또는 Excel 파일을 업로드해 주세요.")
