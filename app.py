import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# --- 설정 및 데이터 로드 ---
st.set_page_config(
    page_title="기대수명 데이터 분석",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 파일 경로 (업로드된 파일명 사용)
FILE_PATH = "기대수명_20251215101915.xlsx"

@st.cache_data
def load_data(file_path):
    """데이터 파일을 로드하고 전처리합니다."""
    try:
        # 데이터 로드 (header=28, index_col=0 사용자가 업로드한 파일 스니펫 기반)
        # 실제 파일 구조에 따라 header, index_col, encoding을 조정해야 할 수 있습니다.
        df = pd.read_csv(file_path, header=28, index_col=0, encoding='cp949')

        # '단위: 세' 행 삭제
        df = df.drop('단위:', errors='ignore')

        # 필요 없는 열(NaN만 있는 열) 제거
        df = df.dropna(axis=1, how='all')

        # 인덱스 이름 설정
        df.index.name = '구분'

        # 데이터를 숫자형으로 변환 (오류 발생 시 NaN으로 처리)
        for col in df.columns:
            # 쉼표(,) 제거 후 숫자형 변환
            df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')

        # NaN이 있는 행 제거 (전처리된 상태에서)
        df = df.dropna()

        # 데이터프레임의 행과 열을 바꿈 (년도를 Feature로, 구분(전체, 남자, 여자)을 값으로)
        df_T = df.T
        df_T.index.name = '연도'

        # 인덱스(연도)를 숫자형으로 변환
        df_T.index = pd.to_numeric(df_T.index, errors='coerce')
        df_T = df_T.dropna()

        return df_T

    except FileNotFoundError:
        st.error(f"🚨 파일을 찾을 수 없습니다: `{file_path}`")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"🚨 데이터 로드 및 전처리 중 오류 발생: {e}")
        return pd.DataFrame()

df_T = load_data(FILE_PATH)

# --- 상관관계 계산 ---
if not df_T.empty:
    correlation_matrix = df_T.corr()

# --- Streamlit UI 구성 ---

st.title("🇰🇷 기대수명 데이터 분석 및 상관관계 탐색")
st.markdown("제공된 기대수명 데이터 (`전체`, `남자`, `여자`)를 기반으로 연도별 변화 및 속성 간의 상관관계를 분석합니다.")

if df_T.empty:
    st.stop()

# 1. 데이터 확인 섹션
with st.expander("🔍 데이터 미리보기 (연도별)", expanded=False):
    st.dataframe(df_T)

# 2. 연도별 변화 시각화
st.header("📈 연도별 기대수명 변화")
fig_line, ax_line = plt.subplots(figsize=(12, 6))
df_T.plot(ax=ax_line, marker='o')
ax_line.set_title('연도별 기대수명 추이', fontsize=15)
ax_line.set_xlabel('연도', fontsize=12)
ax_line.set_ylabel('기대수명 (세)', fontsize=12)
ax_line.grid(True, linestyle='--', alpha=0.7)
plt.legend(title='구분')
st.pyplot(fig_line)
plt.close(fig_line)

# 3. 상관관계 분석 섹션
st.header("🔗 속성 간 상관관계 분석")
st.markdown("`전체`, `남자`, `여자` 속성 간의 상관관계를 히트맵으로 시각화합니다.")

col1, col2 = st.columns([2, 1])

with col1:
    # 상관관계 히트맵
    fig_corr, ax_corr = plt.subplots(figsize=(8, 8))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap='coolwarm',
        fmt=".4f",
        linewidths=.5,
        cbar_kws={'label': '상관 계수'},
        ax=ax_corr
    )
    ax_corr.set_title('속성 간 상관관계 히트맵', fontsize=16)
    st.pyplot(fig_corr)
    plt.close(fig_corr)

with col2:
    st.subheader("상관 계수란?")
    st.markdown(
        """
        상관 계수는 두 변수 간의 **선형적인 관계의 강도와 방향**을 나타내는 값입니다.
        * **+1에 가까울수록**: **양의 상관관계** (한 변수가 증가할 때 다른 변수도 증가)
        * **-1에 가까울수록**: **음의 상관관계** (한 변수가 증가할 때 다른 변수는 감소)
        * **0에 가까울수록**: 선형적인 관계가 거의 없음
        """
    )

# 4. 극단적인 상관관계 버튼 탐색
st.header("🔍 가장 높은 양/음의 상관관계 찾기")

# 상관관계 행렬을 1차원 시리즈로 변환 (대각선 및 중복 제외)
def get_upper_triangle(corr_matrix):
    """상관 행렬의 상삼각형 요소만 추출합니다."""
    # N이 작은 데이터에서는 필요 없지만, 일반적인 경우를 위해 구현
    np.fill_diagonal(corr_matrix.values, np.nan) # 대각선(자기 자신) 제외
    stacked = corr_matrix.stack()
    # 중복 제거 (A-B와 B-A는 같으므로)
    unique_pairs = stacked.loc[stacked.index.get_level_values(0) < stacked.index.get_level_values(1)]
    return unique_pairs.sort_values(ascending=False)

if '전체' in correlation_matrix.columns and '남자' in correlation_matrix.columns and '여자' in correlation_matrix.columns:
    # 기대수명 데이터는 속성이 '전체', '남자', '여자' 3개뿐이므로,
    # 가장 높은 양/음의 상관관계는 '남자-전체', '여자-전체', '남자-여자' 세 쌍 중에서 나옵니다.
    # 실제로 이 데이터에서는 연도별로 모두 함께 증가하므로 모두 높은 양의 상관관계가 나옵니다.

    # 이미 계산된 상관관계 행렬에서 중복 및 대각선을 제거한 Series 추출
    # 기대수명 데이터에서는 모든 쌍이 높은 양의 상관관계를 가집니다.
    # 예시를 위해 '남자'와 '여자' 간의 상관관계를 직접 보여줍니다.

    corr_df = correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates()
    # 자기 자신과의 상관관계(1.0) 제거
    corr_df = corr_df[corr_df < 1.0]

    if not corr_df.empty:
        highest_pos_corr = corr_df.iloc[0]
        highest_pos_pair = corr_df.index[0]
        # 음의 상관관계가 없으므로 (전부 양의 상관관계), 가장 낮은 값을 음의 상관관계로 가정합니다.
        lowest_neg_corr = corr_df.iloc[-1]
        lowest_neg_pair = corr_df.index[-1]


        btn1, btn2 = st.columns(2)

        # 가장 높은 양의 상관관계 버튼
        if btn1.button('➕ 가장 높은 양의 상관관계 보기'):
            st.success(
                f"**가장 높은 양의 상관관계:** `{highest_pos_pair[0]}` - `{highest_pos_pair[1]}`\n"
                f"**상관 계수:** `{highest_pos_corr:.4f}`\n\n"
                "두 속성 모두 연도에 따라 함께 증가하는 경향이 매우 강합니다."
            )

            # 해당 쌍의 산점도 시각화
            fig_pos, ax_pos = plt.subplots(figsize=(8, 6))
            sns.regplot(x=df_T[highest_pos_pair[0]], y=df_T[highest_pos_pair[1]], ax=ax_pos)
            ax_pos.set_title(f'{highest_pos_pair[0]} vs {highest_pos_pair[1]} (상관계수: {highest_pos_corr:.4f})', fontsize=15)
            ax_pos.set_xlabel(f'{highest_pos_pair[0]} 기대수명 (세)', fontsize=12)
            ax_pos.set_ylabel(f'{highest_pos_pair[1]} 기대수명 (세)', fontsize=12)
            st.pyplot(fig_pos)
            plt.close(fig_pos)

        # 가장 높은 음의 상관관계 버튼 (이 데이터에서는 사실상 가장 낮은 양의 상관관계)
        if btn2.button('➖ 가장 높은 음의 상관관계 보기'):
            st.warning(
                f"**가장 높은 음의 상관관계 (가장 낮은 양의 상관관계):** `{lowest_neg_pair[0]}` - `{lowest_neg_pair[1]}`\n"
                f"**상관 계수:** `{lowest_neg_corr:.4f}`\n\n"
                "이 데이터는 모든 속성이 매우 강한 **양의 상관관계**를 가지므로, 이 값은 **가장 낮은 양의 상관관계**를 의미합니다."
            )

            # 해당 쌍의 산점도 시각화
            fig_neg, ax_neg = plt.subplots(figsize=(8, 6))
            sns.regplot(x=df_T[lowest_neg_pair[0]], y=df_T[lowest_neg_pair[1]], ax=ax_neg)
            ax_neg.set_title(f'{lowest_neg_pair[0]} vs {lowest_neg_pair[1]} (상관계수: {lowest_neg_corr:.4f})', fontsize=15)
            ax_neg.set_xlabel(f'{lowest_neg_pair[0]} 기대수명 (세)', fontsize=12)
            ax_neg.set_ylabel(f'{lowest_neg_pair[1]} 기대수명 (세)', fontsize=12)
            st.pyplot(fig_neg)
            plt.close(fig_neg)

    else:
        st.info("상관관계를 계산할 수 있는 데이터 쌍이 충분하지 않습니다.")
