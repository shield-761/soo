import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="지역 대피소 지도", layout="wide")
st.title("📍 지역 민방위 대피소 지도")

uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    tried_encodings = ['utf-8', 'cp949', 'euc-kr']
    df = None
    for enc in tried_encodings:
        try:
            df = pd.read_csv(uploaded_file, encoding=enc)
            break
        except:
            uploaded_file.seek(0)
    if df is None:
        st.error("파일을 읽을 수 없습니다.")
        st.stop()

    df.columns = df.columns.str.strip()
    
    # 컬럼 자동 탐색
    lat_col = next((c for c in df.columns if '위도' in c or 'lat' in c.lower()), None)
    lon_col = next((c for c in df.columns if '경도' in c or 'lon' in c.lower()), None)
    name_col = next((c for c in df.columns if '시설명' in c or '이름' in c or '명칭' in c), None)

    if not lat_col or not lon_col:
        st.error("위도/경도 컬럼을 찾을 수 없습니다.")
        st.stop()

    # 좌표 처리
    df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
    df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')
    df = df.dropna(subset=[lat_col, lon_col])

    # 지역 검색
    region = st.text_input("예: 경기도 양주시").strip()
    if region:
        filtered_df = df[df.apply(lambda row: region.replace(" ", "") in str(row).replace(" ", ""), axis=1)]

        if filtered_df.empty:
            st.warning(f"'{region}' 지역 대피소를 찾을 수 없습니다.")
        else:
            st.success(f"{region} 지역 대피소 {len(filtered_df)}개 표시됨")
            st.dataframe(filtered_df[[name_col, lat_col, lon_col]])

            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=pdk.ViewState(
                    latitude=filtered_df[lat_col].mean(),
                    longitude=filtered_df[lon_col].mean(),
                    zoom=12,
                    pitch=0
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=filtered_df,
                        get_position=f"[{lon_col!r}, {lat_col!r}]",
                        get_color='[255, 0, 0, 200]',  # 빨간색 마커
                        get_radius=300,
                        pickable=True
                    )
                ],
                tooltip={
                    "html": f"<b>대피소 이름:</b> {{{name_col}}}",
                    "style": {"color": "black", "fontSize": "14px"}
                }
