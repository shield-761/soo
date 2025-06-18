import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="지역 대피소 지도", layout="wide")
st.title("🗺️ 지역 대피소 위치 시각화")

uploaded_file = st.file_uploader("📁 대피소 CSV 파일을 업로드하세요", type=["csv"])

# 파일 업로드 후 처리
if uploaded_file:
    # 인코딩 자동 감지 로딩
    tried_encodings = ['utf-8', 'cp949', 'euc-kr']
    df = None
    for enc in tried_encodings:
        try:
            df = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"✅ '{enc}' 인코딩으로 파일을 성공적으로 불러왔습니다.")
            break
        except:
            uploaded_file.seek(0)
    if df is None:
        st.error("❌ 파일 인코딩 문제로 데이터를 불러올 수 없습니다.")
        st.stop()

    # 열 이름 정리
    df.columns = df.columns.str.strip()
    preview_cols = df.columns.tolist()
    st.write("📄 데이터 미리보기", df.head())

    # 지역명 입력
    region = st.text_input("🏘️ 지역명 입력 (예: 경기도 양주시)").strip()
    if region:
        # 해당 지역 필터링
        cond = df.apply(lambda row: region in str(row).replace(" ", ""), axis=1)
        region_df = df[cond].copy()

        if region_df.empty:
            st.warning("❗ 해당 지역의 데이터를 찾을 수 없습니다.")
        else:
            st.success(f"✅ '{region}' 지역의 대피소 {len(region_df)}곳이 검색되었습니다.")
            st.dataframe(region_df)

            # 위도, 경도 컬럼 자동 탐색
            lat_col = next((col for col in df.columns if '위도' in col or 'latitude' in col.lower()), None)
            lon_col = next((col for col in df.columns if '경도' in col or 'longitude' in col.lower()), None)

            if not lat_col or not lon_col:
                st.error("❌ 위도/경도 정보를 찾을 수 없습니다.")
            else:
                # 지도 표시
                st.subheader("📍 지도에서 대피소 위치 확인")
                region_df = region_df[[lat_col, lon_col]].dropna()
                region_df[lat_col] = pd.to_numeric(region_df[lat_col], errors='coerce')
                region_df[lon_col] = pd.to_numeric(region_df[lon_col], errors='coerce')

                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v10',
                    initial_view_state=pdk.ViewState(
                        latitude=region_df[lat_col].mean(),
                        longitude=region_df[lon_col].mean(),
                        zoom=11,
                        pitch=0,
                    ),
                    layers=[
                        pdk.Layer(
                            'ScatterplotLayer',
                            data=region_df,
                            get_position=f'[{lon_col}, {lat_col}]',
                            get_color='[0, 128, 255, 160]',
                            get_radius=100,
                        ),
                    ],
                ))
else:
    st.info("⬆️ 먼저 CSV 파일을 업로드해 주세요.")
