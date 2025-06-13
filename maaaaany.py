import streamlit as st
import pandas as pd

# ✅ 1. CSV 파일을 이용한 특허 검색 함수 정의
def search_patents_from_csv(keyword, csv_path="patents.csv", num_of_rows=20):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        st.error("❌ CSV 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"⚠️ CSV 파일 로딩 중 오류 발생: {e}")
        return pd.DataFrame()

    # 키워드로 발명명칭 또는 요약 필터링
    filtered = df[
        df['발명명칭'].str.contains(keyword, na=False) |
        df['요약'].str.contains(keyword, na=False)
    ].copy()

    return filtered.head(num_of_rows)

# ✅ 2. Streamlit 웹앱 시작
st.set_page_config(page_title="지능정보기술 특허 출원 분석", layout="wide")
st.title("💡 지능정보기술 관련 특허 출원 분석 웹앱")
st.markdown("CSV 파일을 활용한 특허 정보 검색 및 분석 도구입니다.")

# 사용자 입력
keyword = st.text_input("🔎 검색할 특허 키워드를 입력하세요", value="인공지능")

if st.button("🔍 특허 검색"):
    with st.spinner("📂 데이터를 불러오는 중..."):
        df = search_patents_from_csv(keyword)

    if not df.empty:
        st.success(f"✅ {len(df)}건의 특허 데이터를 가져왔습니다.")
        st.dataframe(df)

        # 출원연도 시각화
        if '출원일' in df.columns:
            df['출원연도'] = df['출원일'].astype(str).str[:4]
            year_counts = df['출원연도'].value_counts().sort_index()
            st.subheader("📊 연도별 출원 건수")
            st.bar_chart(year_counts)
        else:
            st.warning("⚠️ '출원일' 컬럼이 없어 연도별 시각화를 건너뜁니다.")
    else:
        st.warning("🔍 해당 키워드에 대한 결과가 없습니다.")
