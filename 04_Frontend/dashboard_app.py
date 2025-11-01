import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'ts_component'))
from ts_component import ts_feedback_simulator

# --- 경로 설정 ---
# 현재 04_Frontend 폴더에서 상위 폴더(..)로 이동 후, 03_Scaling_Logic 폴더의 결과를 읽습니다.
RESULTS_PATH = '../03_Scaling_Logic/scaling_simulation_results.csv' 
MAX_CAPACITY_PER_SERVER_DEFAULT = 500 # config.yaml의 기본값

# ----------------------------------------------------
# 1. 데이터 로드 및 전처리 함수
# ----------------------------------------------------

def load_data():
    """시뮬레이션 결과를 로드합니다."""
    
    # DB 연동 후 3단계에서 생성된 최종 CSV 파일을 로드합니다.
    if not os.path.exists(RESULTS_PATH):
        st.error(f"❌ 오류: 결과 파일 '{RESULTS_PATH}'을 찾을 수 없습니다.")
        st.info("3단계 스크립트 (dynamic_scaler.py)를 먼저 실행하여 결과 파일을 생성했는지 확인하세요.")
        st.stop()
        
    df = pd.read_csv(RESULTS_PATH)
    df['ds'] = pd.to_datetime(df['ds'])
    
    # yhat 대신 predicted_load를 사용합니다.
    df.rename(columns={'predicted_load': 'yhat'}, inplace=True) 
    
    return df

def get_user_config():
    """Streamlit 사이드바에서 사용자 설정 (인프라 파라미터 + 헬스 목표)를 받습니다."""
    
    st.sidebar.header("⚙️ AI 시스템 시뮬레이터")
    
    # 🌟 헬스케어 서비스 컨텍스트 설정 🌟
    st.sidebar.subheader("1. 서비스 컨텍스트 설정")
    selected_goal = st.sidebar.selectbox(
        "사용자 군집 (가상 운동 목표)",
        ["체중 감량 (표준)", "근력 강화 (고부하)", "요가/명상 (저부하)"],
        help="선택된 목표에 따라 AI 예측 부하의 기본 패턴이 달라진다고 가정합니다."
    )
    
    st.sidebar.subheader("2. 인프라 파라미터 조정")
    
    # 서버당 최대 처리 용량 (안정성 vs 효율성)
    max_api = st.sidebar.slider(
        "서버당 최대 API 처리 수 (Capacity)",
        min_value=300, max_value=800, value=MAX_CAPACITY_PER_SERVER_DEFAULT, step=50,
        help="단일 서버가 감당할 수 있는 최대 부하입니다."
    )
    
    # 확장 안전 버퍼 (안정성 확보)
    expansion_buffer = st.sidebar.slider(
        "확장 안전 버퍼 (%)",
        min_value=100, max_value=150, value=110, step=5,
        help="예측 부하가 서버 용량의 이 비율을 초과할 때 확장 명령이 나갑니다."
    ) / 100
    
    # 최소/최대 서버 수 (자원 관리)
    min_servers = st.sidebar.number_input("최소 서버 수 (MIN_SERVERS)", min_value=1, value=2)
    max_servers = st.sidebar.number_input("최대 서버 수 (MAX_SERVERS)", min_value=5, value=15)
    
    return {
        'MAX_API_PER_SERVER': max_api,
        'EXPANSION_BUFFER_PERCENT': expansion_buffer,
        'MIN_SERVERS': min_servers,
        'MAX_SERVERS': max_servers,
        'SELECTED_GOAL': selected_goal
    }

def calculate_required_servers_dashboard(forecast_data, config):
    """
    대시보드에서 입력된 파라미터를 기반으로 필요한 서버 인스턴스 수를 재계산합니다.
    (dynamic_scaler.py의 핵심 로직을 간소화하여 반영)
    """
    
    max_api = config['MAX_API_PER_SERVER']
    min_servers = config['MIN_SERVERS']
    max_servers = config['MAX_SERVERS']
    expansion_factor = config['EXPANSION_BUFFER_PERCENT']

    # 1. 확장 임계치 계산 (안전 버퍼 포함)
    expansion_threshold = max_api * expansion_factor

    # 2. 필요한 서버 수 계산 및 제한 적용
    required_servers = np.ceil(forecast_data['yhat'] / expansion_threshold).astype(int)
    final_servers = np.clip(required_servers, min_servers, max_servers)
    
    # 3. 최대 용량 및 안전 버퍼 재계산
    forecast_data['max_capacity'] = final_servers * max_api

    return final_servers

def add_service_metrics(df):
    """
    서버 부하 및 용량 기반으로 가상의 서비스 안정성 및 성능 지표를 생성합니다.
    """
    
    # 서버 용량 대비 부하 비율
    load_ratio = df['yhat'] / df['max_capacity']
    
    # 1. 가상 신규 세션 수 (부하에 비례)
    df['new_sessions'] = (df['yhat'] * 0.05).round(0).astype(int)

    # 2. 자세 분석 API 오류율 (서버 용량 부족 시 급증 시나리오)
    # 부하 비율이 90%를 초과할 때 오류율 증가
    df['error_rate'] = np.where(load_ratio > 0.9, (load_ratio - 0.9) * 15 + 0.5, 0.5)
    df['error_rate'] = df['error_rate'].clip(upper=5.0) # 최대 5%로 제한

    # 3. 평균 응답 시간 (부하에 비례)
    df['response_time_ms'] = 100 + (load_ratio) * 150

    return df

def calculate_kpis(df):
    """핵심 KPI를 계산합니다."""
    
    # 안전 버퍼 (Calls)
    df['safety_buffer'] = df['max_capacity'] - df['yhat']
    
    # 총 서버 사용 시간 (서버-시간)
    total_server_hours = df['final_servers'].sum()
    
    # 정적 할당(최대 서버) 대비 절감 효과 (가상)
    max_servers_static = df['final_servers'].max()
    static_hours = max_servers_static * len(df)
    
    cost_savings_ratio = (static_hours - total_server_hours) / static_hours * 100

    return {
        '평균 안전 버퍼 (Calls)': f"{df['safety_buffer'].mean():,.0f}",
        '최대 필요 서버 수': df['final_servers'].max(),
        '총 서버 사용 시간': f"{total_server_hours:,.0f} (서버-시간)",
        '정적 할당 대비 절감': f"{cost_savings_ratio:.1f} %"
    }

# ----------------------------------------------------
# 2. 대시보드 시각화 함수
# ----------------------------------------------------

def visualize_dashboard(df, user_config):
    """Streamlit 대시보드를 생성합니다."""
    st.set_page_config(layout="wide")
    st.title("🧠 AI 기반 동적 인프라 관리 데모")
    st.markdown("AI 운동 웹 서비스의 부하 예측을 기반으로 인프라가 자동으로 관리되는 과정을 시뮬레이션하고, 설정 변경 시의 효과를 보여줍니다.")
    
    # ----------------------------------------------------
    # 1. 핵심 KPI 및 서비스 안정성 지표
    # ----------------------------------------------------
    kpis = calculate_kpis(df)
    
    st.header("✨ 운영 성과 및 서비스 안정성")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1: st.metric("최대 예측 부하", f"{df['yhat'].max():,.0f} Calls")
    with col2: st.metric("AI 기반 최대 서버", f"{kpis['최대 필요 서버 수']} 대")
    with col3: st.metric("총 서버 사용 시간", kpis['총 서버 사용 시간'])
    with col4: st.metric("정적 할당 대비 절감", kpis['정적 할당 대비 절감'], delta_color="normal", delta="비용 효율")
    with col5: st.metric("최대 API 오류율", f"{df['error_rate'].max():.1f} %", delta_color="inverse")
    
    st.markdown("---")

    # ----------------------------------------------------
    # 2. 종합 예측 및 확장 액션 그래프
    # ----------------------------------------------------
    st.header("📈 AI 예측 부하 vs. 동적 확장 액션")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. AI 예측 부하 (파란색 선)
    fig.add_trace(
        go.Scatter(x=df['ds'], y=df['yhat'], name='AI 예측 부하 (Calls)', line=dict(color='deepskyblue', width=2)),
        secondary_y=False,
    )

    # 2. 서버 총 처리 용량 (회색 점선 - 안정성 경계)
    fig.add_trace(
        go.Scatter(x=df['ds'], y=df['max_capacity'], name='총 서버 처리 용량', line=dict(color='lightgray', dash='dot', width=1.5)),
        secondary_y=False,
    )
    
    # 3. 결정된 서버 수 (빨간색 계단)
    fig.add_trace(
        go.Scatter(x=df['ds'], y=df['final_servers'], name='결정된 서버 수 (대)', mode='lines', line=dict(shape='hv', color='tomato', width=3)),
        secondary_y=True,
    )
    
    # 주석 추가: 챌린지 이벤트 기간 강조 (가상)
   # 🌟🌟🌟 인덱스를 데이터 길이(약 168)에 맞게 작은 값으로 수정 🌟🌟🌟
    event_start = df['ds'].iloc[20] 
    event_end = df['ds'].iloc[60]
    fig.add_vrect(x0=event_start, x1=event_end, fillcolor="yellow", opacity=0.1, layer="below", line_width=0)


    fig.update_layout(
        title_text=f"예측 기간: {df['ds'].min().strftime('%Y-%m-%d')} ~ {df['ds'].max().strftime('%Y-%m-%d')}",
        height=600,
        hovermode="x unified",
        margin=dict(t=50)
    )

    fig.update_yaxes(title_text="API 호출 수 (Calls)", secondary_y=False, range=[0, df['yhat'].max() * 1.1])
    fig.update_yaxes(title_text="서버 인스턴스 수", secondary_y=True, range=[0, user_config['MAX_SERVERS'] * 1.2], tickmode='array', tickvals=list(range(user_config['MAX_SERVERS'] + 1)))

    st.plotly_chart(fig, use_container_width=True)
    st.caption("빨간 계단선(서버 수)이 파란 선(부하)이 상승하기 전에 미리 올라가 안정성을 확보하는지 확인하세요.")
    
    st.markdown("---")
    
    # ----------------------------------------------------
    # 3. 헬스케어 서비스 기능 목업
    # ----------------------------------------------------
    st.header("🏋️ AI 운동 서비스 기능 목록 (프로젝트 컨텍스트)")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("📖 헬스 정보 및 교육 콘텐츠")
        st.markdown(f"""
        * **주요 기능:** 개인화된 운동 루틴 추천, AI 자세 교정 가이드 영상 스트리밍.
        * **트래픽 영향:** 콘텐츠 조회 시 **지속적인 API 호출 부하**를 유발합니다.
        """)
        st.info(f"현재 선택된 목표 군집은 **{user_config['SELECTED_GOAL']}** 이며, 부하 패턴에 반영되었습니다.")

    with col_b:
        st.subheader("👥 커뮤니티 및 랭킹 시스템")
        st.markdown("""
        * **주요 기능:** 주간 챌린지 참여, 운동 인증 게시, 사용자 간 랭킹 업데이트.
        * **트래픽 영향:** 챌린지 시작/종료 시점(그래프 노란 음영 구간)에 **이벤트성 피크**를 유발합니다.
        """)
        st.warning(f"최대 응답 시간: **{df['response_time_ms'].max():.0f} ms** (인프라 설정 변경 시 이 값이 민감하게 반응합니다.)")
    
    st.markdown("---")

    # 🌟🌟🌟 TypeScript 컴포넌트 호출 🌟🌟🌟
    # 현재 시뮬레이션 시간의 부하 값(yhat)을 추출하여 TS 컴포넌트에 전달
    # 시뮬레이션의 마지막 시간 부하를 현재 부하로 가정합니다.
    current_simulated_load = df['yhat'].iloc[-1].round(0).astype(int).item()
    
    ts_feedback_simulator(current_load=current_simulated_load, key="ts_feedback")


# ----------------------------------------------------
# 3. 메인 실행 블록
# ----------------------------------------------------

if __name__ == "__main__":
    
    # 1. 데이터 로드 (백엔드 결과 CSV)
    data = load_data() 
    
    # 2. 사용자 설정 받기 (사이드바)
    user_config = get_user_config()

    # 3. 헬스 목표에 따른 부하 패턴 조정 및 서버 수 재계산 (핵심 로직)
    # 헬스 목표에 따른 부하 조정
    if user_config['SELECTED_GOAL'] == "근력 강화 (고부하)":
        data['yhat'] = data['yhat'] * 1.15
    elif user_config['SELECTED_GOAL'] == "요가/명상 (저부하)":
        data['yhat'] = data['yhat'] * 0.85
    
    # 사용자 설정 기반으로 서버 수 재계산
    data['final_servers'] = calculate_required_servers_dashboard(data, user_config)
    
    # 서비스 지표 재계산 (서버 수와 부하가 바뀌었으므로 오류율/응답 시간도 다시 계산)
    data = add_service_metrics(data)
    
    # 4. 대시보드 시각화
    visualize_dashboard(data, user_config)