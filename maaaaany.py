import streamlit as st
import pandas as pd

# ✅ 특허 검색 함수 - 컬럼명 유연하게 인식
def search_patents_from_csv(df, keyword, num_of_rows=20):
    # 컬럼명 전처리
    df.columns = df.columns.str.strip().str.replace('\ufeff', '', regex=False)

    col_list = df.columns.tolist()
    title_col = None
    summary_col = None

    # ➕ title 후보 컬럼 확장
    for candidate in ['발명명칭', '명칭', '특허명', 'title', 'Title', '제공 제조AI데이터셋 명']:
        if candidate in col_list:
            title_col = candidate
            break

    # ➕ summary 후보 컬럼 확장
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
        return filtered.head(num_of_rows)
    else:
        st.error("❌ '발명명칭' 또는 '요약' 컬럼이 존재하지 않습니다.")
        st.write("📋 현재 CSV의 컬럼 목록:", col_list)
        return pd.DataFrame()

# ✅ Streamlit 앱 시작
st.set_page_config(page_title="지능정보기술 특허 출원 분석", layout="wide")
st.title("💡 지능정보기술 관련 특허 출원 분석 웹앱")
st.markdown("CSV 또는 Excel 파일을 업로드하여 특허 데이터를 검색하고 분석합니다.")

# ✅ 파일 업로드
uploaded_file = st.file_uploader("📁 특허 CSV 또는 Excel 파일을 업로드하세요", type=["csv", "xls", "xlsx"])

if uploaded_file:
    df_csv = None
    preview_text = uploaded_file.read(500).decode('utf-8', errors='ignore')
    st.subheader("📄 파일 내용 미리보기")
    st.code(preview_text)
    uploaded_file.seek(0)

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
            success = True
        except Exception as e:
            st.error(f"❌ CSV/엑셀 파일 모두 실패: {e}")

    if df_csv is not None:
        st.write("📋 실제 컬럼명:", df_csv.columns.tolist())
        keyword = st.text_input("🔎 검색할 특허 키워드를 입력하세요", value="인공지능")

        if st.button("🔍 특허 검색"):
            with st.spinner("📂 데이터를 불러오는 중..."):
                result_df = search_patents_from_csv(df_csv, keyword)

            if not result_df.empty:
                st.success(f"✅ {len(result_df)}건의 특허 데이터를 가져왔습니다.")
                st.dataframe(result_df)

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
        st.error("❌ 파일을 읽을 수 없습니다. 인코딩 또는 형식 문제일 수 있습니다.")
else:
    st.info("📌 먼저 CSV 또는 Excel 파일을 업로드해주세요.")
