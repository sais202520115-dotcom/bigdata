import streamlit as st
import pandas as pd
import numpy as np

# 📊 가상의 데이터 생성 함수 (다양한 속성)
@st.cache_data
def load_data():
    """상관관계 분석을 위한 가상의 다차원 데이터를 생성합니다."""
    
    # 데이터 포인트 수
    N = 200
    
    # 5개의 독립된 속성 (Feature) 생성
    # 1. Temperature: 정규 분포
    np.random.seed(42)
    temp = np.random.normal(loc=20, scale=5, size=N)
    
    # 2. Humidity: Temp와 약한 음의 상관관계가 있도록 설정
    humidity = 90 - 2 * temp + np.random.normal(loc=0, scale=8, size=N)
    humidity = np.clip(humidity, 40, 100) # 40~100 사이로 클리핑
    
    # 3. Pressure: Temp와 약한 양의 상관관계가 있도록 설정
    pressure = 1000 + 1.5 * temp + np.random.normal(loc=0, scale=10, size=N)
    
    # 4. Sunlight_Hours: 독립적인 정규 분포
    sunlight = np.random.normal(loc=8, scale=2, size=N)
    sunlight = np.clip(sunlight, 0, 12)
    
    # 5. Sensor_Reading: Humidity와 강한 양의 상관관계가 있도록 설정
    sensor = 50 + 3 * humidity + np.random.normal(loc=0, scale=15, size=N)
    
    data = {
        'Temperature': temp.round(1),
        'Humidity': humidity.round(1),
        'Pressure': pressure.round(1),
        'Sunlight_Hours': sunlight.round(1),
        'Sensor_Reading': sensor.round(1)
    }
    
    df = pd.DataFrame(data)
    return df

def get_extreme_correlations(corr_matrix, positive=True):
    """상관관계 행렬에서 가장 높거나 낮은 쌍을 찾습니다."""
    
    # 상관관계 행렬을 1차원 시리즈로 변환 (자기 자신과의 관계 제외)
    corr_series = corr_matrix.unstack()
    corr_series = corr_series[corr_series.index.get_level_values(0) < corr_series.index.get_level_values(1)]
    
    if positive:
        # 양의 상관관계가 가장 높은 쌍
        highest = corr_series.sort_values(ascending=False).iloc[0]
        pair = corr_series.sort_values(ascending=False).index[0]
        return pair, highest
    else:
        # 음의 상관관계가 가장 높은 쌍 (가장 낮은 값)
        lowest = corr_series.sort_values(ascending=True).iloc[0]
        pair = corr_series.sort_values(ascending=True).index[0]
        return pair, lowest

def main():
    st.title("🔬 데이터 속성 간 상관관계 분석 대시보드")
    st.markdown("---")
    
    # 1. 데이터 로드 및 상관관계 계산
    df = load_data()
    corr_matrix = df.corr()
    
    # 2. 데이터 개요 및 원본 데이터 표시
    st.sidebar.header("데이터 개요")
    st.sidebar.write(f"속성 수: **{len(df.columns)}개**")
    st.sidebar.write(f"데이터 포인트 수: **{len(df)}개**")
    
    if st.sidebar.checkbox("원본 데이터 미리보기"):
        st.subheader("원본 데이터")
        st.dataframe(df.head())
        
    st.markdown("---")

    # 3. 상관관계 행렬 표시
    st.header("1. 전체 상관관계 행렬")
    st.info("값은 -1 (완벽한 음의 상관관계)에서 +1 (완벽한 양의 상관관계) 사이입니다.")
    st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm', axis=None).format(precision=2))
    
    # 4. 차트를 통한 시각화
    st.subheader("상관관계 히트맵")
    # Streamlit은 Matplotlib/Seaborn 차트도 잘 지원하지만, 여기서는 pandas style을 활용하여 간단히 표시
    
    st.markdown("---")

    # 5. 극단적인 상관관계 찾기 버튼
    st.header("2. 극단적인 상관관계 찾기")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ 양의 상관관계 최대 쌍 찾기", help="상관관계 계수가 +1에 가장 가까운 두 속성"):
            pair, value = get_extreme_correlations(corr_matrix, positive=True)
            st.success(f"### 최고 양의 상관관계")
            st.markdown(f"**속성 쌍:** `{pair[0]}` 와 `{pair[1]}`")
            st.markdown(f"**상관 계수:** `+{value:.4f}`")
            
            # 산점도 시각화
            st.subheader(f"'{pair[0]}' vs '{pair[1]}' 산점도")
            st.scatter_chart(df, x=pair[0], y=pair[1])
            
    with col2:
        if st.button("➖ 음의 상관관계 최대 쌍 찾기", help="상관관계 계수가 -1에 가장 가까운 두 속성"):
            pair, value = get_extreme_correlations(corr_matrix, positive=False)
            st.error(f"### 최고 음의 상관관계")
            st.markdown(f"**속성 쌍:** `{pair[0]}` 와 `{pair[1]}`")
            st.markdown(f"**상관 계수:** `{value:.4f}`")

            # 산점도 시각화
            st.subheader(f"'{pair[0]}' vs '{pair[1]}' 산점도")
            st.scatter_chart(df, x=pair[0], y=pair[1])

if __name__ == "__main__":
    main()
