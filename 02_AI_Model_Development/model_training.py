# 02_AI_Model_Development/model_training.py 수정
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import performance_metrics, cross_validation
import matplotlib.pyplot as plt
import os
import pickle
# --- 새로 추가/수정 ---
from sqlalchemy import create_engine
from pandas import read_sql
# --------------------

# 1. DB 접속 정보 설정 (🌟🌟🌟 반드시 수정하세요! 🌟🌟🌟)
DB_HOST = "localhost"
DB_NAME = "AI_WebLoad_DB"
DB_USER = "postgres"
DB_PASS = "1234" 
# ----------------------------------------------------

# --- 경로 설정 ---
MODEL_DIR = './trained_model'
OUTPUT_DIR = './analytics_output'

def train_and_predict_prophet():
    """
    DB에서 데이터를 로드하여 Prophet 모델을 학습하고, 다음 7일간의 웹 트래픽을 예측합니다.
    """
    
    # 1. 데이터 로드 및 전처리 (DB에서 직접 읽기)
    print("✅ DB에서 데이터 로드 중...")
    try:
        engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:5432/{DB_NAME}')
        
        # SQL 쿼리를 통해 데이터를 가져옵니다. (SQL 분석 단계의 데이터 집계 역할 포함)
        sql_query = "SELECT ds, y FROM traffic_log ORDER BY ds"
        df = read_sql(sql_query, engine)
        
    except Exception as e:
        print(f"❌ DB 연결/쿼리 실패: {e}")
        print("💡 DB 접속 정보 및 PostgreSQL 서버 상태를 다시 확인하세요.")
        return

    if df.empty:
        print("❌ 오류: DB에서 데이터를 찾을 수 없습니다. web_traffic_simulator.py를 먼저 실행했는지 확인하세요.")
        return
        
    print(f"✅ DB 데이터 로드 완료. 총 {len(df)}개 레코드 사용.")
    
    # 2. Prophet 모델 생성 및 학습
    m = Prophet(
        yearly_seasonality=True, 
        weekly_seasonality=True, 
        daily_seasonality=True,
        seasonality_mode='additive' 
    )
    
    m.fit(df)
    print("✅ Prophet 모델 학습 완료.")
    
    # 3. 미래 예측
    future = m.make_future_dataframe(periods=7 * 24, freq='H') 
    forecast = m.predict(future)
    print(f"✅ 다음 7일 ({len(future) - len(df)}시간) 예측 완료.")

    # 4. 예측 결과 시각화 및 저장
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    fig = m.plot(forecast)
    plt.title('Web Load Prediction (Prophet)')
    plt.xlabel('Date')
    plt.ylabel('API Calls (Load)')
    fig.savefig(os.path.join(OUTPUT_DIR, 'prophet_forecast_plot.png'))
    plt.close(fig)
    print(f"✅ 예측 그래프 '{os.path.join(OUTPUT_DIR, 'prophet_forecast_plot.png')}' 저장 완료.")

    # 5. 모델 성능 평가 (교차 검증)
    print("\n--- 📊 모델 성능 평가 (교차 검증 시작) ---")
    cv_results = cross_validation(m, initial='180 days', period='90 days', horizon='30 days')
    df_p = performance_metrics(cv_results)
    
    mape = df_p['mape'].mean()
    print(f"🔍 모델 평균 MAPE (Mean Absolute Percentage Error): {mape:.4f} (낮을수록 좋음)")

    # 6. 예측 결과 저장 (다음 단계에서 사용)
    future_forecast = forecast[['ds', 'yhat']].iloc[-7*24:].copy()
    future_forecast.to_csv(os.path.join(OUTPUT_DIR, 'future_load_forecast.csv'), index=False)
    print(f"✅ 예측 결과 ('future_load_forecast.csv') 저장 완료.")

    # 7. 학습된 모델 저장
    model_path = os.path.join(MODEL_DIR, 'prophet_model.pkl')
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump(m, f)
    print(f"✅ 학습된 Prophet 모델이 '{model_path}'에 저장되었습니다.")
    
    return future_forecast

if __name__ == "__main__":
    train_and_predict_prophet()