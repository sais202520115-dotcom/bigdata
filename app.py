import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# matplotlib에서 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic' # Windows 사용자
# plt.rcParams['font.family'] = 'AppleGothic' # Mac 사용자 (필요에 따라 주석 해제)
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

# --- 설정 및 데이터 로드 ---
st.set_page_config(
    page_title="서울 눈일수 상관관계 분석",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 데이터 파일 경로 (업로드된 파일명 사용)
FILE_PATH = "STCS_눈일수_ANL_20251215120418.csv"

@st.cache_data
def load_and_preprocess_data(file_path):
    """데이터 파일을 로드하고 전처리합니다."""
    try:
        # 데이터 로드: 헤더가 7번째 행(인덱스 6)에 있으며, 한국어 인코딩(cp949) 사용
        df = pd.read_csv(file_path, header=6, encoding='cp949')

        # '연도'를 인덱스로 설정하고, 불필요한 '순위' 열 제거
        df = df.set_index('연도')
        df = df.drop(columns=['순위'], errors='ignore')
        
        # '연합계' 컬럼 이름 변경 (분석의 편의를 위해)
        df = df.rename(columns={'연합계': '연간총합'})

        # 결측값 ('―')을 NaN으로 대체
        df = df.replace('―', np.nan)

        # 모든 데이터 열을 숫자형으로 변환 (오류 발생 시 NaN으로 처리)
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # NaN이 포함된 행 (불완전한 연도 데이터) 제거
        df = df.dropna(how='any')

        return df

    except FileNotFoundError:
        st.error(f"🚨 파일을 찾을 수 없습니다: `{file_path}`. 파일이 `app.py`와 같은 위치에 있는지 확인해 주세요.")
        return pd.DataFrame()
    except UnicodeDecodeError:
        st.error("🚨 인코딩 오류가 발생했습니다. 파일 인코딩이 `cp949`가 아닐 수 있습니다. `utf-8`로 변경하여 다시 시도해 보세요.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"🚨 데이터 로드 및 전처리 중 오류 발생: {e}")
        return pd.DataFrame()

df = load_and_preprocess_data(FILE_PATH)

# --- 상관관계 계산 ---
if not df.empty:
    correlation_matrix = df.corr()

# --- Streamlit UI 구성 ---

st.title("🌨️ 서울 눈일수 월별 상관관계 분석")
st.markdown("제공된 서울 지역의 연도별 월별 눈일수 데이터를 기반으로 속성(월) 간의 상관관계를 분석합니다.")

if df.empty:
    st.stop()

# 1. 데이터 확인 섹션
with st.expander("🔍 전처리된 데이터 미리보기 (연도별)", expanded=False):
    st.dataframe(df.astype(str))
    st.info(f"분석에 사용된 기간: {df.index.min()}년 ~ {df.index.max()}년 ({len(df)}개 연도)")

# 2. 상관관계 분석 섹션
st.header("🔗 속성(월) 간 상관관계 분석")

col1, col2 = st.columns([2, 1])

with col1:
    # 상관관계 히트맵
    fig_corr, ax_corr = plt.subplots(figsize=(10, 9))
    sns.heatmap(
        correlation_matrix,
        annot=True,
        cmap='coolwarm',
        fmt=".2f",
        linewidths=.5,
        cbar_kws={'label': '상관 계수'},
        ax=ax_corr
    )
    ax_corr.set_title('월별 눈일수 상관관계 히트맵', fontsize=16)
    st.pyplot(fig_corr)
    plt.close(fig_corr)

with col2:
    st.subheader("상관 계수란?")
    st.markdown(
        """
        상관 계수는 두 변수 간의 **선형적인 관계의 강도와 방향**을 나타내는 값입니다.
        * **+1에 가까울수록**: **양의 상관관계** (함께 증가하는 경향)
        * **-1에 가까울수록**: **음의 상관관계** (하나는 증가할 때 다른 하나는 감소하는 경향)
        * **0에 가까울수록**: 선형적 관계가 거의 없음
        """
    )
    st.subheader("분석 속성")
    st.markdown(f"`{', '.join(df.columns)}`")

# 3. 극단적인 상관관계 버튼 탐색
st.header("🔍 가장 높은 양/음의 상관관계 쌍 찾기")

# 상관관계 행렬에서 자기 자신과의 상관관계(1.0) 및 중복 쌍 제거
corr_df = correlation_matrix.unstack().sort_values(ascending=False).drop_duplicates()
corr_df = corr_df[corr_df < 1.0]
corr_df = corr_df.dropna() # NaN이 있는 쌍 제거

if not corr_df.empty:
    # 가장 높은 양의 상관관계
    highest_pos_corr = corr_df.iloc[0]
    highest_pos_pair = corr_df.index[0]
    
    # 가장 높은 음의 상관관계 (가장 낮은 값)
    highest_neg_corr = corr_df.iloc[-1]
    highest_neg_pair = corr_df.index[-1]


    btn1, btn2 = st.columns(2)

    # 가장 높은 양의 상관관계 버튼
    if btn1.button('➕ 가장 높은 양의 상관관계 보기'):
        st.success(
            f"**가장 높은 양의 상관관계:** `{highest_pos_pair[0]}` - `{highest_pos_pair[1]}`\n"
            f"**상관 계수:** `{highest_pos_corr:.4f}`\n\n"
            f"두 속성({highest_pos_pair[0]}, {highest_pos_pair[1]})의 눈일수는 연도별로 함께 증가하거나 감소하는 경향이 **가장 강합니다**."
        )

        # 해당 쌍의 산점도 시각화
        fig_pos, ax_pos = plt.subplots(figsize=(8, 6))
        sns.regplot(x=df[highest_pos_pair[0]], y=df[highest_pos_pair[1]], ax=ax_pos, scatter_kws={'alpha':0.6})
        ax_pos.set_title(f'{highest_pos_pair[0]} vs {highest_pos_pair[1]} (상관계수: {highest_pos_corr:.4f})', fontsize=15)
        ax_pos.set_xlabel(f'{highest_pos_pair[0]} 눈일수', fontsize=12)
        ax_pos.set_ylabel(f'{highest_pos_pair[1]} 눈일수', fontsize=12)
        st.pyplot(fig_pos)
        plt.close(fig_pos)

    # 가장 높은 음의 상관관계 버튼
    if btn2.button('➖ 가장 높은 음의 상관관계 보기'):
        
        if highest_neg_corr < 0:
            st.error(
                f"**가장 높은 음의 상관관계:** `{highest_neg_pair[0]}` - `{highest_neg_pair[1]}`\n"
                f"**상관 계수:** `{highest_neg_corr:.4f}`\n\n"
                f"두 속성({highest_neg_pair[0]}, {highest_neg_pair[1]})은 한쪽이 증가할 때 다른 쪽이 감소하는 경향이 **가장 강합니다**."
            )
        else:
            st.warning(
                f"**가장 높은 음의 상관관계 (가장 낮은 양의 상관관계):** `{highest_neg_pair[0]}` - `{highest_neg_pair[1]}`\n"
                f"**상관 계수:** `{highest_neg_corr:.4f}`\n\n"
                "데이터 내에서 뚜렷한 음의 상관관계는 발견되지 않았으며, 이 값은 **가장 약한 양의 상관관계**를 나타냅니다."
            )

        # 해당 쌍의 산점도 시각화
        fig_neg, ax_neg = plt.subplots(figsize=(8, 6))
        sns.regplot(x=df[highest_neg_pair[0]], y=df[highest_neg_pair[1]], ax=ax_neg, scatter_kws={'alpha':0.6})
        ax_neg.set_title(f'{highest_neg_pair[0]} vs {highest_neg_pair[1]} (상관계수: {highest_neg_corr:.4f})', fontsize=15)
        ax_neg.set_xlabel(f'{highest_neg_pair[0]} 눈일수', fontsize=12)
        ax_neg.set_ylabel(f'{highest_neg_pair[1]} 눈일수', fontsize=12)
        st.pyplot(fig_neg)
        plt.close(fig_neg)

else:
    st.info("상관관계를 계산할 수 있는 유효한 데이터 쌍이 충분하지 않습니다.")
