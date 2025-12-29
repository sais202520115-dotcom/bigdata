import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="간편 데이터 분석기", layout="wide")

st.title("📊 데이터 분석 및 시각화 대시보드")
st.markdown("CSV 파일을 업로드하여 데이터를 탐색하고 시각화해 보세요.")

# 파일 업로드 섹션
uploaded_file = st.file_uploader("CSV 파일을 선택하세요", type=["csv"])

if uploaded_file is not None:
    # 데이터 불러오기
    df = pd.read_csv(uploaded_file)
    
    # 탭 구성: 데이터 미리보기 / 통계 분석 / 시각화
    tab1, tab2, tab3 = st.tabs(["📄 데이터 확인", "📈 통계 요약", "🎨 시각화"])
    
    with tab1:
        st.subheader("데이터 미리보기")
        st.dataframe(df.head())
        
        st.subheader("데이터 정보")
        st.write(f"전체 행 수: {df.shape[0]} | 전체 열 수: {df.shape[1]}")

    with tab2:
        st.subheader("기초 통계량")
        st.write(df.describe())
        
        st.subheader("결측치 확인")
        st.write(df.isnull().sum())

    with tab3:
        st.subheader("상관관계 시각화")
        
        # 수치형 데이터만 추출
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            with col1:
                x_axis = st.selectbox("X축 선택", numeric_cols)
            with col2:
                y_axis = st.selectbox("Y축 선택", numeric_cols)
            
            color_col = st.selectbox("색상 기준 (선택사항)", [None] + df.columns.tolist())
            
            fig = px.scatter(df, x=x_axis, y=y_axis, color=color_col, 
                             title=f"{x_axis} vs {y_axis} 산점도",
                             template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("시각화를 위해 최소 2개 이상의 수치형 컬럼이 필요합니다.")

else:
    st.info("왼쪽 사이드바나 업로드 영역에 파일을 올려주세요.")
