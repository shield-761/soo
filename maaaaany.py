import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("🌫️ 대한민국 미세먼지(PM10) 시각화 대시보드")

uploaded_file = st.file_uploader("📁 미세먼지 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    required_cols = {'stationName', 'pm10Value', 'lat', 'lon'}
    if not required_cols.issubset(df.columns):
        st.error("❌ 필요한 컬럼이 누락되었습니다. 필요한 컬럼: stationName, pm10Value, lat, lon")
    else:
        st.success("✅ 파일 업로드 및 로드 성공")
        st.dataframe(df.head())

        # 지도 시각화
        st.subheader("🗺️ 미세먼지 지도 시각화")

        m = folium.Map(location=[36.5, 127.5], zoom_start=7)
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df.iterrows():
            pm = row['pm10Value']
            color = "green" if pm <= 30 else "orange" if pm <= 80 else "red"
            folium.CircleMarker(
                location=[row['lat'], row['lon']],
                radius=8,
                popup=f"{row['stationName']}: {pm} ㎍/㎥",
                color=color,
                fill=True,
                fill_opacity=0.7
            ).add_to(marker_cluster)

        st_folium(m, width=1000, height=600)

        # 막대 그래프
        st.subheader("📊 지역별 미세먼지 농도 비교")

        fig, ax = plt.subplots(figsize=(10, 5))
        df_sorted = df.sort_values("pm10Value", ascending=False)
        ax.bar(df_sorted['stationName'], df_sorted['pm10Value'], color='skyblue')
        ax.set_ylabel("PM10 농도 (㎍/㎥)")
        ax.set_xlabel("지역명")
        ax.set_title("지역별 미세먼지 농도")
        st.pyplot(fig)
else:
    st.info("CSV 파일을 업로드하면 시각화가 시작됩니다.")
