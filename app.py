import streamlit as st
import pandas as pd
import plotly.express as px

# 페이지 설정
st.set_page_config(page_title="타이타닉 데이터 분석기", layout="wide")

@st.cache_data
def load_data():
    # 파일명은 실제 환경에 맞춰 수정하세요.
    file_path = 'titanic.xls - titanic3.csv'
    try:
        df = pd.read_csv(file_path)
    except:
        df = pd.read_excel(file_path)
    return df

try:
    df = load_data()
    
    st.title("🚢 타이타닉 데이터 품질 및 분포 분석")

    # --- 탭 구성 (분석 내용 분리) ---
    tab1, tab2, tab3 = st.tabs(["📊 기본 통계 및 필터", "🔍 결측치 분석", "📈 이상치 분석"])

    with tab1:
        st.header("기본 분석")
        # 필터링 및 지표 (기존 코드 유지)
        pclass_options = sorted(df["pclass"].dropna().unique().tolist())
        pclass = st.multiselect("객실 등급 선택", options=pclass_options, default=pclass_options)
        
        filtered_df = df[df["pclass"].isin(pclass)].copy()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("총 승객 수", len(filtered_df))
        col2.metric("평균 운임", f"${filtered_df['fare'].mean():.2f}")
        col3.metric("평균 연령", f"{filtered_df['age'].mean():.1f}세")
        
        st.subheader("성별/생존 데이터 시각화")
        plot_df = filtered_df.dropna(subset=['survived']).copy()
        plot_df['survived'] = plot_df['survived'].map({1.0: '생존', 0.0: '사망'})
        fig = px.histogram(plot_df, x="sex", color="survived", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("데이터 결측치(Missing Values) 현황")
        # 결측치 계산
        null_info = df.isnull().sum().reset_index()
        null_info.columns = ['Column', 'Missing_Count']
        null_info = null_info[null_info['Missing_Count'] > 0].sort_values(by='Missing_Count', ascending=False)

        if not null_info.empty:
            c1, c2 = st.columns([1, 2])
            with c1:
                st.write("컬럼별 결측치 개수")
                st.table(null_info)
            with c2:
                fig_null = px.bar(null_info, x='Column', y='Missing_Count', title="결측치 발생 컬럼")
                st.plotly_chart(fig_null, use_container_width=True)
        else:
            st.success("결측치가 없는 깨끗한 데이터입니다!")

    with tab3:
        st.header("수치형 데이터 이상치(Outliers) 감지")
        st.write("박스플롯의 수염(Whiskers) 범위를 벗어나는 점들이 이상치입니다.")
        
        # 이상치를 확인할 수치형 컬럼 선택
        target_col = st.selectbox("분석할 컬럼 선택", ["fare", "age"])
        
        # Plotly Boxplot은 이상치를 자동으로 점으로 표시해줍니다.
        fig_outlier = px.box(filtered_df, y=target_col, points="all", 
                             title=f"{target_col} 컬럼의 분포 및 이상치",
                             color_discrete_sequence=['#AB63FA'])
        st.plotly_chart(fig_out
