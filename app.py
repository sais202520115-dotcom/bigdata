import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="타이타닉 데이터 분석기", layout="wide")

@st.cache_data
def load_data():
    # 데이터 로드 (파일명이 titanic3.csv인 경우)
    df = pd.read_csv('titanic.xls')
    return df

# 데이터 불러오기
try:
    df = load_data()
    
    st.title("🚢 타이타닉 승객 데이터 분석 대시보드")
    st.markdown("이 대시보드는 타이타닉호 승객들의 데이터를 분석하여 생존 요인을 탐색합니다.")

    # 사이드바: 필터링
    st.sidebar.header("필터 설정")
    pclass = st.sidebar.multiselect(
        "객실 등급(Pclass) 선택",
        options=df["pclass"].unique().tolist(),
        default=df["pclass"].unique().tolist()
    )

    # 데이터 필터링 적용
    mask = df["pclass"].isin(pclass)
    filtered_df = df[mask]

    # --- 상단 지표 (Metrics) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 승객 수", len(filtered_df))
    col2.metric("평균 운임", f"${filtered_df['fare'].mean():.2f}")
    col3.metric("평균 연령", f"{filtered_df['age'].mean():.1f}세")
    survival_rate = (filtered_df['survived'].mean() * 100)
    col4.metric("생존율", f"{survival_rate:.1f}%")

    st.divider()

    # --- 시각화 섹션 ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("성별에 따른 생존자 수")
        fig_sex = px.histogram(filtered_df, x="sex", color="survived", 
                               barmode="group", color_discrete_map={0: "#EF553B", 1: "#636EFA"},
                               labels={"survived": "생존 여부 (1=생존)"})
        st.plotly_chart(fig_sex, use_container_width=True)

    with col_right:
        st.subheader("객실 등급별 운임 분포")
        fig_fare = px.box(filtered_df, x="pclass", y="fare", color="pclass",
                          title="Pclass vs Fare")
        st.plotly_chart(fig_fare, use_container_width=True)

    # --- 데이터 상세 보기 ---
    st.subheader("데이터 상세 보기")
    if st.checkbox("원본 데이터 표시"):
        st.dataframe(filtered_df)

except FileNotFoundError:
    st.error("데이터 파일(titanic3.csv)을 찾을 수 없습니다. 파일 이름을 확인해 주세요.")
