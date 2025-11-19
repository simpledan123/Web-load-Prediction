import pandas as pd
import matplotlib.pyplot as plt
import os
from sqlalchemy import create_engine
from pandas import read_sql
# ---------------------------------

# ----------------------------------------------------
# 1. DB 접속 정보 설정 (web_traffic_simulator.py와 동일하게 설정)
# 🌟🌟🌟 반드시 당신의 비밀번호로 수정하세요! 🌟🌟🌟
# ----------------------------------------------------
DB_HOST = "localhost"
DB_NAME = "AI_WebLoad_DB"
DB_USER = "postgres"
DB_PASS = "1234" 
# ----------------------------------------------------

# 분석 결과를 저장할 폴더
OUTPUT_DIR = './analytics_output'

def perform_sql_simulation_analysis():
    """
    DB에서 데이터를 로드하여 SQL 쿼리 실행을 시뮬레이션하고 트래픽 패턴을 분석합니다.
    """
    
    # 1. DB에서 데이터 로드 (DB에서 SELECT 하는 상황 가정)
    print("✅ DB에서 데이터 로드 중...")
    try:
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}')
        
        # SQL 쿼리를 통해 데이터를 가져옵니다.
        sql_query = "SELECT ds, y FROM traffic_log ORDER BY ds"
        df = read_sql(sql_query, engine)
        
    except Exception as e:
        print(f"❌ DB 연결/쿼리 실패: {e}")
        print("💡 DB 접속 정보 및 PostgreSQL 서버 상태를 확인하세요.")
        return

    if df.empty:
        print("❌ 오류: DB에서 데이터를 찾을 수 없습니다. web_traffic_simulator.py를 먼저 실행하여 DB에 데이터를 적재했는지 확인하세요.")
        return

    print(f"✅ DB 데이터 로드 완료. 총 {len(df)}개 레코드 분석 시작.")

    # 분석 결과를 저장할 디렉토리 생성
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ----------------------------------------------------
    # 2. SQL 쿼리 1: '요일별 평균 API 호출 수' 분석
    # SQL 시뮬레이션: 요일별 그룹화 및 평균 계산
    # ----------------------------------------------------
    df['dayofweek'] = df['ds'].dt.dayofweek # 0=월요일, 6=일요일
    avg_by_day = df.groupby('dayofweek')['y'].mean().reset_index()
    
    print("\n--- 📊 SQL 분석 1: 요일별 평균 API 호출 수 (0=월, 6=일) ---")
    print(avg_by_day)

    # 시각화: 요일별 부하 패턴
    plt.figure(figsize=(8, 4))
    plt.bar(avg_by_day['dayofweek'], avg_by_day['y'], color='skyblue')
    plt.xticks(range(7), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'])
    plt.title('Average API Calls by Day of Week (From DB)')
    plt.xlabel('Day of Week')
    plt.ylabel('Average API Calls (Load)')
    plt.grid(axis='y', alpha=0.5)
    plt.savefig(os.path.join(OUTPUT_DIR, 'avg_calls_by_day_db.png'))
    plt.close()

    # ----------------------------------------------------
    # 3. SQL 쿼리 2: '시간대별 평균 API 호출 수' 분석
    # SQL 시뮬레이션: 시간대별 그룹화 및 평균 계산
    # ----------------------------------------------------
    df['hour'] = df['ds'].dt.hour
    avg_by_hour = df.groupby('hour')['y'].mean().reset_index()
    
    print("\n--- 📊 SQL 분석 2: 시간대별 평균 API 호출 수 (0=자정, 23=23시) ---")
    print(avg_by_hour)

    # 시각화: 시간대별 부하 패턴
    plt.figure(figsize=(10, 5))
    plt.plot(avg_by_hour['hour'], avg_by_hour['y'], marker='o', linestyle='-', color='coral')
    plt.xticks(range(24))
    plt.title('Average API Calls by Hour of Day (From DB)')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average API Calls (Load)')
    plt.grid(axis='both', alpha=0.5)
    plt.savefig(os.path.join(OUTPUT_DIR, 'avg_calls_by_hour_db.png'))
    plt.close()
    
    print(f"\n✅ SQL 분석 시뮬레이션 완료! 결과 그래프는 '{OUTPUT_DIR}' 폴더에 저장되었습니다.")

if __name__ == "__main__":
    perform_sql_simulation_analysis()