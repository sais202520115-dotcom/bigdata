import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="타이타닉 데이터 분석기", layout="wide")

@st.cache_data
def load_data():
    # 파일명이 다를 경우를 대비해 업로드된 실제 파일명으로 수정하세요.
    # 여기서는 업로드하신 파일명 규칙에 맞춰 'titanic.xls - titanic3.csv'를 시도합니다.
    file_path = 'titanic.xls'
    
    # 1. 데이터 읽기
    df = pd.read_excel(file_path)
    
    # 2. 데이터 클리닝: 모든 값이 비어있는 행 제거 및 필수 컬럼 형변환
    df = df.dropna(subset=['pclass', 'survived']) 
    return df

try:
    df = load_data()
    
    st.title("🚢 타이타닉 승객 데이터 분석 대시보드")
    st.markdown("이 대시보드는 타이타닉호 승객들의 데이터를 분석하여 생존 요인을 탐색합니다.")

    # 사이드바: 필터링
    st.sidebar.header("필터 설정")
    
    # 데이터 타입 문제 방지를 위해 정수형 변환 후 리스트화
    pclass_options = sorted(df["pclass"].unique().tolist())
    pclass = st.sidebar.multiselect(
        "객실 등급(Pclass) 선택",
        options=pclass_options,
        default=pclass_options
    )

    # 데이터 필터링 적용
    filtered_df = df[df["pclass"].isin(pclass)]

    # --- 상단 지표 (Metrics) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 승객 수", f"{len(filtered_df)}명")
    col2.metric("평균 운임", f"${filtered_df['fare'].mean():.2f}")
    col3.metric("평균 연령", f"{filtered_df['age'].mean():.1f}세")
    
    survival_rate = (filtered_df['survived'].mean() * 100)
    col4.metric("생존율", f"{survival_rate:.1f}%")

    st.divider()

    # --- 시각화 섹션 ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("성별에 따른 생존자 수")
        # survived를 문자열로 변환하여 범례를 보기 좋게 만듭니다.
        plot_df = filtered_df.copy()
        plot_df['survived'] = plot_df['survived'].map({1.0: '생존', 0.0: '사망'})
        fig_sex = px.histogram(plot_df, x="sex", color="survived",
                               barmode="group",
                               color_discrete_map={'생존': "#636EFA", '사망': "#EF553B"})
        st.plotly_chart(fig_sex, use_container_width=True)

    with col_right:
        st.subheader("객실 등급별 운임 분포")
        fig_fare = px.box(filtered_df, x="pclass", y="fare", color="pclass")
        st.plotly_chart(fig_fare, use_container_width=True)

    # --- 데이터 상세 보기 ---
    st.subheader("데이터 상세 보기")
    if st.checkbox("원본 데이터 표시"):
        st.dataframe(filtered_df)

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
