import streamlit as st
import pandas as pd
import numpy as np

# 📊 가상의 데이터 생성 함수
@st.cache_data
def load_data():
    """가상의 판매 데이터를 생성합니다."""
    
    # 200개의 랜덤 데이터 포인트 생성
    DATA_COUNT = 200
    
    # 카테고리
    categories = ['전자제품', '의류', '식품', '도서']
    
    data = {
        '날짜': pd.to_datetime(pd.date_range(start='2024-01-01', periods=DATA_COUNT, freq='D').date),
        '카테고리': np.random.choice(categories, DATA_COUNT),
        # 판매액은 정규 분포를 따르도록 설정
        '판매액': np.random.randint(10000, 100000, DATA_COUNT) + np.random.randn(DATA_COUNT) * 5000,
        '수량': np.random.randint(1, 20, DATA_COUNT)
    }
    
    df = pd.DataFrame(data)
    # 판매액이 음수가 되는 경우를 대비해 0 이상으로 조정
    df['판매액'] = df['판매액'].apply(lambda x: max(0, int(x)))
    
    return df.set_index('날짜')

def main():
    st.title("📈 가상 판매 데이터 분석 대시보드")
    st.markdown("---")
    
    # 1. 데이터 로드
    df = load_data()
    
    # 2. 데이터 요약 표시 (사이드바)
    st.sidebar.header("📊 데이터 개요")
    st.sidebar.metric("총 데이터 수", f"{len(df)}개")
    st.sidebar.metric("총 판매액", f"₩{df['판매액'].sum():,}")
    
    # 3. 전체 데이터 표시 (체크박스)
    if st.checkbox("전체 원본 데이터 보기"):
        st.subheader("원본 데이터")
        st.dataframe(df)

    st.markdown("---")
    
    # 4. 분석 및 시각화
    st.header("카테고리별 분석")
    
    # 카테고리별 총 판매액 집계
    category_sales = df.groupby('카테고리')['판매액'].sum().sort_values(ascending=False).reset_index()
    category_sales.columns = ['카테고리', '총 판매액']
    
    st.subheader("카테고리별 총 판매액")
    
    # 집계된 데이터 표시
    st.dataframe(category_sales)
    
    # 막대 차트 시각화
    st.subheader("판매액 막대 차트")
    st.bar_chart(category_sales.set_index('카테고리'))
    
    st.markdown("---")
    
    # 5. 사용자 필터링 기능 (옵션)
    st.header("필터링")
    
    selected_category = st.selectbox(
        "분석할 카테고리를 선택하세요:",
        options=['전체'] + list(df['카테고리'].unique())
    )
    
    if selected_category != '전체':
        filtered_df = df[df['카테고리'] == selected_category]
        st.write(f"선택된 **{selected_category}** 카테고리의 데이터:")
        st.dataframe(filtered_df.describe())
        
        # 일별 판매액 라인 차트
        daily_sales = filtered_df.resample('W')['판매액'].sum()
        st.subheader(f"{selected_category} 주간 판매액 추이")
        st.line_chart(daily_sales)


if __name__ == "__main__":
    main()
