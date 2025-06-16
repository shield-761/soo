import streamlit as st
import pandas as pd

# ✅ 특허 검색 함수 (결과 리턴만)
def search_patents_from_csv(df, keyword, num_of_rows=20):
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    col_list = df.columns.tolist()
    title_col = None
    summary_col = None

    for candidate in ['발명명칭', '명칭', '특허명', 'title', 'Title', '제공 제조AI데이터셋 명']:
        if candidate in col_list:
            title_col = candidate
            break

    for candidate in ['요약', '내용', '개요', 'summary', 'Summary', '제조AI데이터셋 내용']:
        if candidate in col_list:
            summary_col = candidate
            break

    if title_col or summary_col:
        cond = pd.Series([False] * len(df))
        if title_col:
            cond |= df[title_col].astype(str).str.contains(keyword, na=False, case=False)
        if summary_col:
            cond |= df[summary_col].astype(str).str.contains(keyword, na=False, case=False)
        filtered = df[cond].copy()
        return filtered.head(num_of_rows), title_col, summary_col
    else:
        st.error("❌ '발명명칭' 또는 '요약' 컬럼이 존재하지 않습니다.")
        st.write("📋 현재 CSV의 컬럼 목록:", col_list)
        return pd.DataFrame(), None, None

# ✅ Streamlit 앱 시작
st.set_page_config(page_title="지능정보기술 특허 출원 분석", layout="wide")
st.title("💡 지능정보기술 관련 특허 출원 분석 웹앱")

uploaded_file = st.file_uploader("📁 특허 CSV 또는 Excel 파일을 업로드하세요", type=["csv", "xls", "xlsx"])

if uploaded_file:
    preview_text = uploaded_file.read(500).decode('utf-8', errors='ignore')
    st.subheader("📄 파일 내용 미리보기")
    st.code(preview_text)
    uploaded_file.seek(0)

    df_csv = None
    tried_encodings = ['utf-8', 'cp949', 'euc-kr']
    tried_separators = [',', ';', '\t']
    success = False

    for enc in tried_encodings:
        for sep in tried_separators:
            try:
                df = pd.read_csv(uploaded_file, encoding=enc, sep=sep)
                if df.shape[1] > 1:
                    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)
                    df_csv = df
                    st.success(f"✅ CSV 파일을 성공적으로 열었습니다. (인코딩: {enc}, 구분자: {repr(sep)})")
                    success = True
                    break
            except:
                uploaded_file.seek(0)
        if success:
            break

    if not success:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)
            df_csv = df
            st.success("✅ 엑셀 파일로 인식하여 성공적으로 열었습니다.")
        except Exception as e:
            st.error(f"❌ 파일 열기에 실패했습니다: {e}")

    if df_csv is not None:
        keyword = st.text_input("🔍 검색할 키워드를 입력하세요", value="인공지능")
        if st.button("🔎 검색 시작"):
            result_df, title_col, summary_col = search_patents_from_csv(df_csv, keyword)

            if not result_df.empty:
                st.success(f"✅ 총 {len(result_df)}건의 특허가 검색되었습니다.")
                st.subheader("📄 검색 결과 (카드 형식)")

                for idx, row in result_df.iterrows():
                    with st.container():
                        st.markdown("---")
                        st.markdown(f"### 📌 {row[title_col]}")
                        if '출원일' in df_csv.columns:
                            st.markdown(f"**📅 출원일**: {row['출원일']}")
                        if summary_col:
                            with st.expander("📝 요약 보기"):
                                st.write(str(row[summary_col])[:1000])  # 너무 긴 경우 자르기

                # 연도별 분석
                if '출원일' in df_csv.columns:
                    df_csv['출원연도'] = df_csv['출원일'].astype(str).str[:4]
                    year_counts = df_csv['출원연도'].value_counts().sort_index()
                    st.subheader("📊 연도별 출원 건수")
                    st.bar_chart(year_counts)
                else:
                    st.warning("⚠️ '출원일' 컬럼이 없어 연도별 분석은 불가합니다.")
            else:
                st.warning("🔍 해당 키워드에 대한 결과가 없습니다.")
else:
    st.info("📌 먼저 CSV 또는 Excel 파일을 업로드해주세요.")
