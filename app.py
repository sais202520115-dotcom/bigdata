import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler  # 정규화 도구 추가

# 페이지 설정
st.set_page_config(page_title="타이타닉 데이터 분석기", layout="wide")

@st.cache_data
def load_data():
    file_path = 'titanic.xls' # 환경에 맞게 수정
    try:
        df = pd.read_csv(file_path)
    except:
        df = pd.read_excel(file_path)
    return df

try:
    df = load_data()
    st.title("🚢 타이타닉 데이터 품질 및 분포 분석")

    # --- 탭 구성 (정규화 탭 추가) ---
    tab1, tab2, tab3, tab4 = st.tabs(["📊 기본 통계 및 필터", "🔍 결측치 분석", "📈 이상치 분석", "🔢 데이터 정규화"])

    # [기존 tab1, tab2, tab3 코드는 그대로 유지됩니다]
    with tab1:
        st.header("기본 분석")
        pclass_options = sorted(df["pclass"].dropna().unique().tolist())
        pclass = st.multiselect("객실 등급 선택", options=pclass_options, default=pclass_options)
        filtered_df = df[df["pclass"].isin(pclass)].copy()
        
        col1, col2, col3 = st.columns(3)
        col1.metric("총 승객 수", len(filtered_df))
        col2.metric("평균 운임", f"${filtered_df['fare'].mean():.2f}")
        col3.metric("평균 연령", f"{filtered_df['age'].mean():.1f}세")
        
        plot_df = filtered_df.dropna(subset=['survived']).copy()
        plot_df['survived'] = plot_df['survived'].map({1.0: '생존', 0.0: '사망'})
        fig = px.histogram(plot_df, x="sex", color="survived", barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.header("데이터 결측치(Missing Values) 현황")
        null_info = df.isnull().sum().reset_index()
        null_info.columns = ['Column', 'Missing_Count']
        null_info = null_info[null_info['Missing_Count'] > 0].sort_values(by='Missing_Count', ascending=False)
        if not null_info.empty:
            c1, c2 = st.columns([1, 2])
            with c1: st.table(null_info)
            with c2: st.plotly_chart(px.bar(null_info, x='Column', y='Missing_Count'), use_container_width=True)
        else:
            st.success("결측치가 없습니다!")

    with tab3:
        st.header("수치형 데이터 이상치(Outliers) 감지")
        target_col = st.selectbox("분석할 컬럼 선택", ["fare", "age"])
        fig_outlier = px.box(filtered_df, y=target_col, points="all", color_discrete_sequence=['#AB63FA'])
        st.plotly_chart(fig_outlier, use_container_width=True)
        
        Q1, Q3 = filtered_df[target_col].quantile([0.25, 0.75])
        IQR = Q3 - Q1
        outliers = filtered_df[(filtered_df[target_col] < Q1 - 1.5 * IQR) | (filtered_df[target_col] > Q3 + 1.5 * IQR)]
        st.warning(f"**{target_col}**의 이상치 개수: {len(outliers)}개")

    # --- 신규 탭: 데이터 정규화 (Min-Max Scaling) ---
    with tab4:
        st.header("🔢 수치형 데이터 정규화 (Min-Max Scaling)")
        st.write("데이터의 범위를 0과 1 사이로 변환하여 변수 간 영향력을 균등하게 조정합니다.")
        
        # 1. 정규화 대상 수치형 컬럼 선택
        norm_cols = filtered_df.select_dtypes(include=['float64', 'int64']).columns.tolist()
        # 분석에 부적절한 컬럼(ID, 생존 여부 등) 제외 (선택 사항)
        exclude_cols = ['survived', 'pclass', 'sibsp', 'parch']
        default_cols = [c for c in norm_cols if c not in exclude_cols]
        
        selected_norm_cols = st.multiselect("정규화할 컬럼을 선택하세요", options=norm_cols, default=default_cols)
        
        if selected_norm_cols:
            # 2. 정규화 수행 (결측치는 평균값으로 임시 채움)
            df_norm_target = filtered_df[selected_norm_cols].copy()
            df_norm_target = df_norm_target.fillna(df_norm_target.mean()) # 정규화 전 결측치 처리 필수
            
            scaler = MinMaxScaler()
            scaled_data = scaler.fit_transform(df_norm_target)
            df_scaled = pd.DataFrame(scaled_data, columns=selected_norm_cols)
            
            # 3. 결과 출력
            c1, c2 = st.columns([1, 1])
            with c1:
                st.subheader("✅ 변환 전 (Original)")
                st.dataframe(filtered_df[selected_norm_cols].head(10))
            with c2:
                st.subheader("🚀 변환 후 (Normalized)")
                st.dataframe(df_scaled.head(10))
            
            # 4. 정규화 후 분포 시각화 (비교용)
            st.subheader("정규화 후 데이터 분포 확인")
            fig_norm = px.box(df_scaled, title="Min-Max 스케일링 적용 결과")
            st.plotly_chart(fig_norm, use_container_width=True)
        else:
            st.info("정규화를 진행할 컬럼을 하나 이상 선택해주세요.")

except Exception as e:
    st.error(f"오류 발생: {e}")
