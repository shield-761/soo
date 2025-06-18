import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("🌫️ 대한민국 미세먼지(PM10) 시각화")

uploaded_file = st.file_uploader("📁 미세먼지 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # 필수 컬럼 확인
    if not {'stationName', 'pm10Value'}.issubset(df.columns):
        st.error("❌ 'stationName', 'pm10Value' 컬럼이 있어야 합니다.")
    else:
        st.success("✅ 데이터 불러오기 성공!")
        st.dataframe(df.head())

        # PM10 막대 그래프
        st.subheader("📊 지역별 미세먼지(PM10) 농도")

        df_sorted = df.sort_values("pm10Value", ascending=False)
        fig_bar = px.bar(
            df_sorted,
            x='stationName',
            y='pm10Value',
            color='pm10Value',
            color_continuous_scale='RdYlGn_r',
            labels={'stationName': '지역', 'pm10Value': 'PM10 농도 (㎍/㎥)'},
            title="지역별 PM10 농도 비교"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # PM10 선형 트렌드 (선택적으로 시간 순 정렬 시 사용 가능)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            st.subheader("📈 시간별 PM10 변화 추이 (선택)")
            fig_line = px.line(
                df.sort_values("date"),
                x='date',
                y='pm10Value',
                color='stationName',
                title="시간별 PM10 추이"
            )
            st.plotly_chart(fig_line, use_container_width=True)
else:
    st.info("📌 미세먼지 CSV 파일을 업로드하면 분석이 시작됩니다.")
