import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from pandas import DataFrame
import os

# ----------------------------------------------------
# 1. DB 접속 정보 설정 (🌟🌟🌟 반드시 수정하세요! 🌟🌟🌟)
# ----------------------------------------------------
DB_HOST = "localhost"
DB_NAME = "AI_WebLoad_DB"
DB_USER = "postgres"
DB_PASS = "1234" # 당신의 비밀번호로 설정
# ----------------------------------------------------

# 2. 시뮬레이션 및 데이터 설정 (전역 변수로 먼저 정의)
START_DATE = datetime(2024, 1, 1)
DAYS_TO_SIMULATE = 365
DATE_COL = 'ds'
LOAD_COL = 'y'

# ----------------------------------------------------
# 3. 핵심 함수 정의
# ----------------------------------------------------

def generate_web_traffic_data():
    """
    현실적인 시계열 특성을 가진 가상의 웹 트래픽 데이터 (API 호출 수)를 생성합니다.
    """
    end_date = START_DATE + timedelta(days=DAYS_TO_SIMULATE)
    date_range = pd.date_range(start=START_DATE, end=end_date, freq='H')[:-1]
    
    df = pd.DataFrame(date_range, columns=[DATE_COL])
    df['hour'] = df[DATE_COL].dt.hour
    df['dayofweek'] = df[DATE_COL].dt.dayofweek

    base_load = (np.sin((df['hour'] - 8) / 24 * 2 * np.pi) + 1.2) * 50 + 100
    day_factor = np.where(df['dayofweek'] >= 5, 1.3, 1.0)
    base_load = base_load * day_factor

    noise = np.random.normal(0, 15, len(df))
    load_metric = base_load + noise
    
    for _ in range(3):
        event_start_day = np.random.randint(50, DAYS_TO_SIMULATE - 50)
        event_start = START_DATE + timedelta(days=event_start_day, hours=np.random.randint(0, 24))
        event_end = event_start + timedelta(hours=np.random.randint(24, 72))
        
        event_mask = (df[DATE_COL] >= event_start) & (df[DATE_COL] < event_end)
        if event_mask.any():
            event_peak = np.random.normal(500, 50, event_mask.sum())
            load_metric[event_mask] += event_peak

    load_metric[load_metric < 100] = 100 
    df[LOAD_COL] = load_metric.round().astype(int)
    
    return df[[DATE_COL, LOAD_COL]]

def save_to_database(df: DataFrame):
    """생성된 데이터를 PostgreSQL DB의 traffic_log 테이블에 저장합니다."""
    
    # SQLAlchemy 엔진 생성
    engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}')
    
    try:
        # 데이터프레임을 DB 테이블에 저장
        # if_exists='replace': 기존 테이블 데이터를 지우고 새로 만듭니다.
        df.to_sql('traffic_log', engine, if_exists='replace', index=False, method='multi')
        print("✅ 데이터가 PostgreSQL 'traffic_log' 테이블에 성공적으로 적재되었습니다.")
        
    except Exception as e:
        print(f"❌ DB 적재 실패: {e}")
        print("💡 DB 접속 정보(DB_PASS, DB_USER 등)와 PostgreSQL 서버 상태를 확인하세요.")

# ----------------------------------------------------
# 4. 스크립트 실행 시작 지점
# ----------------------------------------------------
if __name__ == "__main__":
    
    # 여기서 함수가 호출됩니다. 이제 위에서 정의되었으므로 문제가 없습니다.
    traffic_data = generate_web_traffic_data()
    
    # DB에 저장하는 함수 호출
    save_to_database(traffic_data) 
    
    print(f"✅ 가상 트래픽 데이터 생성 완료! (총 {len(traffic_data)}개 레코드)")
    print("\n--- 데이터 미리보기 ---")
    print(traffic_data.head())