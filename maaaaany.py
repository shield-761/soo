import streamlit as st
import pandas as pd
import pydeck as pdk
import requests

# Streamlit 설정
st.set_page_config(page_title="지역 대피소 지도", layout="wide")
st.title("🛡️ 지역 민방위 대피소 지도 시각화")

# Kakao 지오코딩 함수
def geocode_address_kakao(address, api_key):
    try:
        url = "https://dapi.kakao.com/v2/local/search/address.json"
        headers = {"Authorization": f"KakaoAK {api_key}"}
        params = {"query": address}
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            result = res.json()
            if result["documents"]:
                loc = result["documents"][0]["address"]
                return float(loc["y"]), float(loc["x"])  # 위도, 경도
    except:
        pass
    return None, None

# Kakao API Key 입력
KAKAO_API_KEY = st.secrets.get("KAKAO_API_KEY", "")

# 파일 업로드
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
    st.dataframe(df.head())

    # 컬럼 자동 감지
    name_col = next((c for c in df.columns if '시설명' in c or '이름' in c or '명칭' in c), None)
    address_col = next((c for c in df.columns if '주소' in c), None)
    lat_col = next((c for c in df.columns if '위도' in c or 'lat' in c.lower()), None)
    lon_col = next((c for c in df.columns if '경도' in c or 'lon' in c.lower()), None)

    # 위도/경도 타입 변환
    if lat_col: df[lat_col] = pd.to_numeric(df[lat_col], errors='coerce')
    if lon_col: df[lon_col] = pd.to_numeric(df[lon_col], errors='coerce')

    # 위도/경도가 모두 37, 127인 경우 → 지오코딩으로 대체
    if (lat_col is None or lon_col is None or
        (df[lat_col].nunique() == 1 and df[lat_col].iloc[0] == 37 and
         df[lon_col].nunique() == 1 and df[lon_col].iloc[0] == 127)):
        
        if not address_col:
            st.error("❌ 위도/경도가 없거나 잘못되었고, 주소도 없습니다.")
            st.stop()

        st.info("📍 위도/경도가 무의미한 값입니다. 주소를 기반으로 좌표를 재생성합니다...")

        coords = df[address_col].apply(lambda addr: geocode_address_kakao(str(addr), KAKAO_API_KEY))
        df['위도'] = coords.apply(lambda x: x[0])
        df['경도'] = coords.apply(lambda x: x[1])
        df.dropna(subset=['위도', '경도'], inplace=True)

        lat_col, lon_col = '위도', '경도'
        st.success("✅ 지오코딩 완료: 유효한 좌표로 대체되었습니다.")

    # 좌표 없으면 중단
    if lat_col not in df.columns or lon_col not in df.columns:
        st.error("❌ 유효한 위도/경도 정보를 찾을 수 없습니다.")
        st.stop()

    df = df.dropna(subset=[lat_col, lon_col])

    # 전체 지도 표시
    st.subheader("🗺️ 전체 대피소 지도")
    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=pdk.ViewState(
            latitude=df[lat_col].mean(),
            longitude=df[lon_col].mean(),
            zoom=10,
            pitch=0
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=df,
                get_position=f"[{lon_col!r}, {lat_col!r}]",
                get_color='[0, 128, 255, 160]',
                get_radius=150,
                pickable=True
            )
        ],
        tooltip={
            "html": f"<b>대피소 이름:</b> {{{name_col}}}",
            "style": {"color": "black", "fontSize": "14px"}
        }
    ))

    # 지역 필터
    region = st.text_input("🏘️ 지역명 입력 (예: 경기도 양주시)").strip()
    if region:
        filtered_df = df[df.apply(lambda row: region.replace(" ", "") in str(row).replace(" ", ""), axis=1)]
        if filtered_df.empty:
            st.warning(f"❗ '{region}' 지역의 대피소를 찾을 수 없습니다.")
        else:
            st.success(f"✅ '{region}' 지역 대피소 {len(filtered_df)}개 표시됨")
            st.dataframe(filtered_df[[name_col, lat_col, lon_col]])
            st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=pdk.ViewState(
                    latitude=filtered_df[lat_col].mean(),
                    longitude=filtered_df[lon_col].mean(),
                    zoom=11,
                    pitch=0
                ),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=filtered_df,
                        get_position=f"[{lon_col!r}, {lat_col!r}]",
                        get_color='[255, 0, 0, 160]',
                        get_radius=200,
                        pickable=True
                    )
                ],
                tooltip={
                    "html": f"<b>대피소 이름:</b> {{{name_col}}}",
                    "style": {"color": "black", "fontSize": "14px"}
                }
            ))
else:
    st.info("📎 먼저 CSV 파일을 업로드해 주세요.")
