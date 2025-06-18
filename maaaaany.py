import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="지역별 대피소 위치 찾기", layout="wide")
st.title("🏠 지역별 대피소 위치 찾기")

uploaded_file = st.file_uploader("📁 CSV 또는 Excel 파일을 업로드하세요", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding="utf-8", low_memory=False)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")

        df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

        # 위도, 경도, 주소 컬럼 자동 찾기
        lat_col = next((c for c in df.columns if '위도' in c or 'lat' in c.lower()), None)
        lon_col = next((c for c in df.columns if '경도' in c or 'lon' in c.lower()), None)
        addr_col = next((c for c in df.columns if '주소' in c or '소재지' in c or '지역' in c), None)

        if lat_col and lon_col and addr_col:
            df = df.rename(columns={lat_col: 'lat', lon_col: 'lon', addr_col: 'address'})
            df = df.dropna(subset=['lat', 'lon'])
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            df = df.dropna(subset=['lat', 'lon'])

            # 검색 기능
            keyword = st.text_input("📍 지역명을 입력하세요 (예: 경기도 양주시)", value="")
            if keyword:
                filtered = df[df['address'].astype(str).str.contains(keyword)]
            else:
                filtered = df

            st.success(f"🔎 총 {len(filtered)}개의 대피소가 검색되었습니다.")

            if not filtered.empty:
                # pydeck으로 지도 시각화
                view_state = pdk.ViewState(
                    latitude=filtered['lat'].mean(),
                    longitude=filtered['lon'].mean(),
                    zoom=11
                )

                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=filtered,
                    get_position='[lon, lat]',
                    get_radius=200,
                    get_fill_color='[255, 0, 0, 160]',
                    pickable=True,
                )

                # OpenStreetMap 타일을 써서 한국어 지도로 보이게 설정
                st.pydeck_chart(
                    pdk.Deck(
                        layers=[layer],
                        initial_view_state=view_state,
                        map_provider='carto',  # OpenStreetMap 기반 (한국어 라벨 가능)
                        map_style='light',
                        tooltip={"text": "{address}"}
                    )
                )

                st.dataframe(filtered[['address', 'lat', 'lon']].reset_index(drop=True))

            else:
                st.warning("해당 지역의 대피소를 찾을 수 없습니다.")
        else:
            st.error("❌ 위도/경도/주소 컬럼이 누락되어 있습니다.")
            st.write("컬럼 목록:", df.columns.tolist())

    except Exception as e:
        st.error(f"❌ 파일을 불러오지 못했습니다.\n\n에러: {e}")

else:
    st.info("📌 CSV 또는 Excel 파일을 업로드해 주세요.")
