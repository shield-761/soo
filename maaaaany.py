import streamlit as st
import pandas as pd

# 파일 미리보기
st.text("🔍 파일 내용 미리보기")
preview = uploaded_file.read(500).decode('utf-8', errors='ignore')
st.code(preview)
uploaded_file.seek(0)  # 다시 읽기 위해 위치 초기화


# ✅ CSV 기반 특허 검색 함수
def search_patents_from_csv(df, keyword, num_of_rows=20):
    # 키워드 필터링
    filtered = df[
        df['발명명칭'].str.contains(keyword, na=False) |
        df['요약'].str.contains(keyword, na=False)
    ].copy()
    return filtered.head(num_of_rows)

# ✅ Streamlit 앱
st.set_page_config(page_title="지능정보기술 특허 출원 분석", layout="wide")
st.title("💡 지능정보기술 관련 특허 출원 분석 웹앱")
st.markdown("CSV 파일을 업로드하여 특허 데이터를 검색하고 분석합니다.")

# ✅ CSV 업로드
uploaded_file = st.file_uploader("📁 특허 CSV 파일을 업로드하세요", type=["csv"])

if uploaded_file:
    df_csv = None
    tried_encodings = ['utf-8', 'cp949', 'euc-kr']
    for enc in tried_encodings:
        try:
            df_csv = pd.read_csv(uploaded_file, encoding=enc)
            st.success(f"✅ CSV 파일을 성공적으로 읽었습니다. (인코딩: {enc})")
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            st.error(f"❌ CSV 파일 처리 중 예기치 못한 오류 발생: {e}")
            break

    if df_csv is not None:
        keyword = st.text_input("🔎 검색할 특허 키워드를 입력하세요", value="인공지능")

        if st.button("🔍 특허 검색"):
            with st.spinner("📂 데이터를 불러오는 중..."):
                result_df = search_patents_from_csv(df_csv, keyword)

            if not result_df.empty:
                st.success(f"✅ {len(result_df)}건의 특허 데이터를 가져왔습니다.")
                st.dataframe(result_df)

                if '출원일' in result_df.columns:
                    result_df['출원연도'] = result_df['출원일'].astype(str).str[:4]
                    year_counts = result_df['출원연도'].value_counts().sort_index()
                    st.subheader("📊 연도별 출원 건수")
                    st.bar_chart(year_counts)
                else:
                    st.warning("⚠️ '출원일' 컬럼이 없어 연도별 분석은 불가합니다.")
            else:
                st.warning("🔍 해당 키워드에 대한 결과가 없습니다.")
    else:
        st.error("❌ CSV 파일을 읽을 수 없습니다. UTF-8, CP949, EUC-KR 인코딩인지 확인해주세요.")
else:
    st.info("📌 먼저 CSV 파일을 업로드해주세요.")
