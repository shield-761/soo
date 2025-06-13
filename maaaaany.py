import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

# 🛑 여기에 직접 API 키 입력
API_KEY = "tJYB/P5zTt6sJJL5OKg9sf3VpXO=nw/73SYo9Q8U3U4="

# 📦 특허 검색 함수
def search_patents(keyword, num_of_rows=20):
    url = "http://plus.kipris.or.kr/openapi/rest/PatentInfoSearchService/getWordSearch"
    params = {
        'accessKey': API_KEY,
        'word': keyword,
        'numOfRows': num_of_rows,
        'pageNo': 1
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error("❌ API 요청 실패")
        return pd.DataFrame()

    root = ET.fromstring(response.content)
    items = root.findall('.//item')

    data = []
    for item in items:
        data.append({
            '출원일': item.findtext('applicationDate', ''),
            '출원인': item.findtext('applicantName', ''),
            '발명명칭': item.findtext('inventionTitle', ''),
            '요약': item.findtext('inventionSummary', '')
        })

    return pd.DataFrame(data)

# 🌐 Streamlit 웹 앱
st.set_page_config(page_title="지능정보기술 특허 분석", layout="wide")
st.title("💡 지능정보기술 관련 특허 출원 분석")
st.markdown("공공데이터포털의 KIPRIS API를 활용하여 지능정보기술 관련 특허를 분석합니다.")

keyword = st.text_input("🔍 검색할 특허 키워드를 입력하세요", value="인공지능")

if st.button("🔎 특허 검색"):
    with st.spinner("📡 데이터를 불러오는 중..."):
        df = search_patents(keyword)
        if df.empty:
            st.warning("❗ 검색 결과가 없습니다.")
        else:
            st.success(f"✅ {len(df)}건의 특허 데이터를 가져왔습니다.")
            st.dataframe(df)

            # 📊 출원연도 분석
            df['출원연도'] = df['출원일'].str[:4]
            year_counts = df['출원연도'].value_counts().sort_index()
            st.bar_chart(year_counts)
