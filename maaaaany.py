import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="지역 대피소 지도", layout="wide")
st.title("🛡️ 지역 민방위 대피소 지도 시각화")

uploaded_file = st.file_uploader("📁 민방위 대피소 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    tried_encodings = ['utf-8', 'cp949', 'euc-kr']
    df = None
    for enc in tried_encodings:
        try:
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"✅ '{enc}' 인코딩으로 불러옴")
            break
        except:
            uploaded_file.seek(0)
    if df is None:
        st.error("❌ 파일을 읽을 수 없습니다. 인코딩 확인 필요")
        st.stop()

    df.columns = df.columns.str.strip()
    st.subheader("📄 데이터 미리보기")

    # 위도/경도/시설명 컬럼 자동 탐색
    lat_col = next((c for c in df.columns if '위도' in c or 'lat' in c.lower()), None)
    lon_col = next((c for c in df.columns if '경도' in c or 'lon' in c.lower()), None)
    name_col = next((c for c in df.columns if '시설명' in c or '이름' in c or '명칭' in c), None)

    if not lat_col or not lon_col:
        st.error("❌ 위도/경도 컬럼을 찾을 수 없습니다.")
        st.stop()

    df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
    df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
    df = df.dropna(subset=[lat_col, lon_col])

    # 소수점 14자리로 포맷팅된 위도/경도 열 추가
    df["위도_정밀"] = df[lat_col].apply(lambda x: f"{x:.14f}")
    df["경도_정밀"] = df[lon_col].apply(lambda x: f"{x:.14f}")

    st.dataframe(df[[name_col, "위도_정밀", "경도_정밀"]].head())

    # 전체 지도 시각화
    st.subheader("🗺️ 전체 대피소 지도 (Folium 사용)")
    center = [df[lat_col].mean(), df[lon_col].mean()]
    folium_map = folium.Map(location=center, zoom_start=10)

    for _, row in df.iterrows():
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=f"{row[name_col]}<br>위도: {row['위도_정밀']}<br>경도: {row['경도_정밀']}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(folium_map)

    st_folium(folium_map, width=1000)

    # 지역 필터
    region = st.text_input("🏘️ 지역명 입력 (예: 경기도 양주시)").strip()
    if region:
        filtered_df = df[df.apply(lambda row: region.replace(" ", "") in str(row).replace(" ", ""), axis=1)]

        if filtered_df.empty:
            st.warning(f"❗ '{region}' 지역의 대피소를 찾을 수 없습니다.")
        else:
            st.success(f"✅ '{region}' 지역 대피소 {len(filtered_df)}개 표시됨")
            st.dataframe(filtered_df[[name_col, "위도_정밀", "경도_정밀"]])

            region_map = folium.Map(
                location=[filtered_df[lat_col].mean(), filtered_df[lon_col].mean()],
                zoom_start=11
            )

            for _, row in filtered_df.iterrows():
                folium.Marker(
                    location=[row[lat_col], row[lon_col]],
                    popup=f"{row[name_col]}<br>위도: {row['위도_정밀']}<br>경도: {row['경도_정밀']}",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(region_map)

            st_folium(region_map, width=1000)

else:
    st.info("📎 먼저 CSV 파일을 업로드해 주세요.")
