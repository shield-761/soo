import streamlit as st
import pandas as pd
import requests
import xml.etree.ElementTree as ET

# ✅ 1. API 키 직접 삽입 (주의: 공개 저장소에는 업로드 금지)
API_KEY = "tJYB/P5zTt6sJJL5OKg9sf3VpXO=nw/73SYo9Q8U3U4="

# ✅ 2. 특허 검색 함수 정의
def search_patents(keyword, num_of_rows=20):
    url = "http://plus.kipris.or.kr/openapi/rest/PatentInfoSearchService/getWordSearch"
    params = {
        'accessKey': API_KEY,
        'word': keyword,
        'numOfRows': num_of_rows,
        'pageNo': 1
    }

    response = requests.get(url, params=params)

    # 응답 상태 확인
    if response.status_code != 200:
        st.error(f"❌ API 요청 실패: 상태코드 {response.status_code}")
        st.code(response.text)
        return pd.DataFrame()

    # XML 파싱 예외 처리
    try:
        root = ET.fromstring(response.content)
    except ET.ParseError:
        st.error("⚠️ XML 파싱 오류 발생 (아래 응답 확인)")
        st.code(response.text)
        return pd.DataFrame()

    items = root.findall('.//item')

    if not items:
        st.warning("🔍 검색 결과가 없습니다.")
        return pd.DataFrame()

    data = []
    for item in items:
        data.append({
            '출원일': item.findtext('applicationDate', ''),
            '출원인': item.findtext('applicantName', ''),
            '발명명칭': item.findtext('inventionTitle', ''),
            '요약': item.findtext('inventionSummary', '')
        })

    return pd.DataFrame(data)

# ✅ 3. Streamlit 웹앱 시작
st.set_page_config(page_title="지능정보기술 특허 출원 분석", layout="wide")
st.title("💡 지능정보기술 관련 특허 출원 분석 웹앱")
st.markdown("공공데이터포털(KIPRIS API)를 활용한 실시간 특허 정보 검색 및 분석 도구입니다.")

# 사용자 입력
keyword = st.text_input("🔎 검색할 특허 키워드를 입력하세요", value="인공지능")

if st.button("🔍 특허 검색"):
    with st.spinner("📡 데이터를 불러오는 중..."):
        df = search_patents(keyword)

    if not df.empty:
        st.success(f"✅ {len(df)}건의 특허 데이터를 가져왔습니다.")
        st.dataframe(df)

        # 출원연도 시각화
        df['출원연도'] = df['출원일'].str[:4]
        year_counts = df['출원연도'].value_counts().sort_index()
        st.subheader("📊 연도별 출원 건수")
        st.bar_chart(year_counts)
